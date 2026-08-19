"""Asynchronous PyTorch Autodidactic Iteration (ADI) Training Manager and Telemetry Streamer."""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from src.environment.puzzle_state import Action, PuzzleState
from src.models.heuristic_net import PuzzleHeuristicNet
from src.solvers.neural_solver import NeuralAStarSolver

logger = logging.getLogger("TrainingManager")


def _sanitize_for_json(obj: Any) -> Any:
    """Recursively converts NumPy types to native Python types for JSON serialization."""
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(item) for item in obj]
    return obj


class TrainingManager:
    """Manages background PyTorch ADI training sessions and broadcasts live telemetry."""

    def __init__(self) -> None:
        self.is_training: bool = False
        self.stop_requested: bool = False
        self._thread: Optional[threading.Thread] = None
        self._subscribers: Set[asyncio.Queue] = set()
        self._current_status: Dict[str, Any] = {
            "status": "idle",
            "epoch": 0,
            "total_epochs": 0,
            "current_depth": 0,
            "loss": 0.0,
            "test_solve_rate": 0.0,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        }

    def subscribe(self) -> asyncio.Queue:
        """Subscribes a WebSocket client queue for live telemetry updates."""
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        """Removes a subscriber queue."""
        self._subscribers.discard(q)

    def broadcast(self, event: Dict[str, Any]) -> None:
        """Broadcasts a sanitized event payload to all active WebSocket subscriber queues."""
        clean_event = _sanitize_for_json(event)
        dead: List[asyncio.Queue] = []
        for q in self._subscribers:
            try:
                q.put_nowait(clean_event)
            except (asyncio.QueueFull, Exception):
                dead.append(q)
        for d in dead:
            self._subscribers.discard(d)

    def get_status(self) -> Dict[str, Any]:
        """Returns the current training status."""
        return _sanitize_for_json(self._current_status)

    def stop_training(self) -> bool:
        """Requests cancellation of ongoing training."""
        if self.is_training:
            self.stop_requested = True
            return True
        return False

    def start_training(
        self,
        loop: asyncio.AbstractEventLoop,
        rows: int = 3,
        cols: int = 3,
        has_pocket: bool = False,
        epochs: int = 20,
        steps_per_epoch: int = 25,
        batch_size: int = 256,
        max_depth: int = 20,
        lr: float = 1e-3,
        save_path: str = "models/trained_ai.pt",
    ) -> bool:
        """Initiates an asynchronous background training worker thread."""
        if self.is_training:
            return False

        self.is_training = True
        self.stop_requested = False

        self._thread = threading.Thread(
            target=self._run_training_worker,
            args=(
                loop,
                rows,
                cols,
                has_pocket,
                epochs,
                steps_per_epoch,
                batch_size,
                max_depth,
                lr,
                save_path,
            ),
            daemon=True,
        )
        self._thread.start()
        return True

    def _run_training_worker(
        self,
        loop: asyncio.AbstractEventLoop,
        rows: int,
        cols: int,
        has_pocket: bool,
        epochs: int,
        steps_per_epoch: int,
        batch_size: int,
        max_depth: int,
        lr: float,
        save_path: str,
    ) -> None:
        """Worker thread executing PyTorch Autodidactic Iteration (ADI)."""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        device_name = torch.cuda.get_device_name(0) if device == "cuda" else "CPU"

        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)

        goal = PuzzleState.create_goal(rows=rows, cols=cols, has_pocket=has_pocket)
        model = PuzzleHeuristicNet(rows=rows, cols=cols, has_pocket=has_pocket).to(device)
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
        loss_fn = nn.SmoothL1Loss()
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

        def emit(event: Dict[str, Any]) -> None:
            loop.call_soon_threadsafe(self.broadcast, event)

        emit({
            "type": "start",
            "rows": rows,
            "cols": cols,
            "has_pocket": has_pocket,
            "epochs": epochs,
            "batch_size": batch_size,
            "max_depth": max_depth,
            "device": device,
            "device_name": device_name,
            "save_path": save_path,
        })

        best_loss = float("inf")
        start_time = time.perf_counter()

        try:
            for epoch in range(1, epochs + 1):
                if self.stop_requested:
                    emit({"type": "stopped", "epoch": epoch, "message": "Training stopped by user."})
                    break

                epoch_start = time.perf_counter()
                epoch_losses: List[float] = []

                # Curriculum depth progression
                curr_depth = max(1, int(round((epoch / epochs) * max_depth)))

                self._current_status.update({
                    "status": "training",
                    "epoch": epoch,
                    "total_epochs": epochs,
                    "current_depth": curr_depth,
                })

                for step in range(steps_per_epoch):
                    if self.stop_requested:
                        break

                    # 1. Generate Training Batch via reverse random walk
                    scrambled_states: List[PuzzleState] = []
                    for _ in range(batch_size):
                        steps = np.random.randint(1, curr_depth + 1)
                        scrambled, _ = goal.scramble(steps=steps)
                        scrambled_states.append(scrambled)

                    # 2. ADI Bellman Target Computation: y(s) = 1 + min_a h(s')
                    model.eval()
                    all_successors: List[PuzzleState] = []
                    state_succ_slices: List[Tuple[int, int]] = []
                    curr_idx = 0

                    for s in scrambled_states:
                        valid_acts = s.get_valid_actions()
                        succs = [s.apply_action(a) for a in valid_acts]
                        all_successors.extend(succs)
                        state_succ_slices.append((curr_idx, curr_idx + len(succs)))
                        curr_idx += len(succs)

                    with torch.no_grad():
                        succ_tensors = torch.stack(
                            [torch.from_numpy(s.to_one_hot()) for s in all_successors]
                        ).to(device)
                        succ_preds = model(succ_tensors).squeeze(-1).cpu().numpy()

                    # Zero cost if goal state
                    for idx, succ in enumerate(all_successors):
                        if succ.is_solved():
                            succ_preds[idx] = 0.0

                    # Compute Bellman targets
                    targets_np = np.zeros(batch_size, dtype=np.float32)
                    sample_succ_values: List[Dict[str, Any]] = []

                    for i, (start_i, end_i) in enumerate(state_succ_slices):
                        if start_i < end_i:
                            min_h = float(np.min(succ_preds[start_i:end_i]))
                            targets_np[i] = 1.0 + min_h

                            # Save candidate move predictions for live Brain Vision telemetry
                            if i == 0:
                                valid_acts = scrambled_states[0].get_valid_actions()
                                for act_idx, act in enumerate(valid_acts):
                                    sample_succ_values.append({
                                        "action": int(act),
                                        "action_name": act.name,
                                        "predicted_cost": float(1.0 + succ_preds[start_i + act_idx]),
                                    })
                        else:
                            targets_np[i] = 0.0

                    # 3. Optimize Network
                    model.train()
                    optimizer.zero_grad()
                    state_tensors = torch.stack(
                        [torch.from_numpy(s.to_one_hot()) for s in scrambled_states]
                    ).to(device)
                    target_tensors = torch.from_numpy(targets_np).float().unsqueeze(-1).to(device)

                    preds = model(state_tensors)
                    loss = loss_fn(preds, target_tensors)
                    loss.backward()
                    optimizer.step()

                    loss_val = float(loss.item())
                    epoch_losses.append(loss_val)

                    # Emit live step event every 2 steps or on last step
                    if step % 2 == 0 or step == steps_per_epoch - 1:
                        sample_state = scrambled_states[0]
                        emit({
                            "type": "step",
                            "epoch": epoch,
                            "total_epochs": epochs,
                            "step": step + 1,
                            "total_steps": steps_per_epoch,
                            "current_depth": curr_depth,
                            "loss": loss_val,
                            "running_avg_loss": float(np.mean(epoch_losses)),
                            "learning_rate": float(optimizer.param_groups[0]["lr"]),
                            "brain_vision": {
                                "board": sample_state.to_list(),
                                "blank_pos": [int(x) for x in sample_state.blank_pos],
                                "candidate_moves": sample_succ_values,
                            },
                        })

                scheduler.step()
                avg_loss = float(np.mean(epoch_losses)) if epoch_losses else 0.0
                epoch_duration = float(time.perf_counter() - epoch_start)

                # 4. End-of-Epoch Evaluation & Demonstration Solve
                test_depth = min(curr_depth, 15)
                solve_rate, demo_initial, demo_actions, demo_states = self._evaluate_and_generate_demo(
                    goal=goal,
                    model=model,
                    device=device,
                    rows=rows,
                    cols=cols,
                    has_pocket=has_pocket,
                    test_depth=test_depth,
                )

                self._current_status.update({
                    "loss": avg_loss,
                    "test_solve_rate": float(solve_rate),
                })

                emit({
                    "type": "epoch_complete",
                    "epoch": epoch,
                    "total_epochs": epochs,
                    "current_depth": curr_depth,
                    "avg_loss": avg_loss,
                    "test_solve_rate": float(solve_rate),
                    "duration_sec": epoch_duration,
                    "demo": {
                        "initial_board": demo_initial.to_list(),
                        "actions": [int(a) for a in demo_actions],
                        "action_names": [a.name for a in demo_actions],
                        "states": [s.to_list() for s in demo_states],
                        "solved": bool(len(demo_states) > 0 and demo_states[-1].is_solved()),
                    },
                })

                if avg_loss < best_loss:
                    best_loss = avg_loss
                    torch.save(model.state_dict(), save_file)

            total_duration = float(time.perf_counter() - start_time)
            if not self.stop_requested:
                emit({
                    "type": "completed",
                    "total_epochs": epochs,
                    "best_loss": float(best_loss),
                    "total_duration_sec": total_duration,
                    "save_path": save_path,
                })
        except Exception as e:
            logger.exception("Training error")
            emit({"type": "error", "message": str(e)})
        finally:
            self.is_training = False
            self.stop_requested = False
            self._current_status["status"] = "idle"

    def _evaluate_and_generate_demo(
        self,
        goal: PuzzleState,
        model: PuzzleHeuristicNet,
        device: str,
        rows: int,
        cols: int,
        has_pocket: bool,
        test_depth: int,
        num_eval_puzzles: int = 5,
    ) -> Tuple[float, PuzzleState, List[Action], List[PuzzleState]]:
        """Evaluates neural heuristic on test scrambles and produces one demonstration trajectory."""
        solved_count = 0
        demo_initial = goal
        demo_actions: List[Action] = []
        demo_states: List[PuzzleState] = [goal]

        solver = NeuralAStarSolver(
            model=model,
            rows=rows,
            cols=cols,
            has_pocket=has_pocket,
            device=device,
            weight=2.0,
        )

        for i in range(num_eval_puzzles):
            test_state, _ = goal.scramble(steps=test_depth, seed=1000 + i)
            res = solver.solve(test_state, time_limit=2.0, max_nodes=20_000)

            if res.success:
                solved_count += 1

            if i == 0:
                demo_initial = test_state
                demo_actions = res.actions
                demo_states = res.states

        solve_rate = float((solved_count / num_eval_puzzles) * 100.0)
        return solve_rate, demo_initial, demo_actions, demo_states
