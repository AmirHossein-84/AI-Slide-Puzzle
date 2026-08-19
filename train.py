#!/usr/bin/env python3
"""Machine Learning Training Pipeline: Autodidactic Iteration (ADI) for Sliding Tile Puzzles."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from src.environment.puzzle_state import Action, PuzzleState
from src.models.heuristic_net import PuzzleHeuristicNet
from src.solvers.neural_solver import NeuralAStarSolver


def parse_args() -> argparse.Namespace:
    """Parses training command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train a PyTorch Neural Network using Autodidactic Iteration (ADI) to solve sliding puzzles."
    )
    parser.add_argument("--rows", "-r", type=int, default=3, help="Grid rows (default: 3)")
    parser.add_argument("--cols", "-c", type=int, default=3, help="Grid columns (default: 3)")
    parser.add_argument("--epochs", "-e", type=int, default=20, help="Training epochs (default: 20)")
    parser.add_argument("--steps-per-epoch", type=int, default=30, help="Training batches per epoch (default: 30)")
    parser.add_argument("--batch-size", "-b", type=int, default=256, help="Batch size (default: 256)")
    parser.add_argument("--max-depth", "-d", type=int, default=25, help="Max scramble depth during curriculum (default: 25)")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate (default: 0.001)")
    parser.add_argument("--save-model", "-s", type=str, default="", help="Path to save trained weights")
    parser.add_argument("--device", type=str, default="", help="Device: 'cuda' or 'cpu' (default: auto)")
    return parser.parse_args()


def generate_adi_batch(
    goal: PuzzleState,
    model: PuzzleHeuristicNet,
    batch_size: int,
    max_depth: int,
    device: str,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Generates an Autodidactic Iteration training batch.
    
    Returns:
        inputs: (batch_size, num_tiles, rows, cols) one-hot tensor
        targets: (batch_size, 1) float tensor of Bellman cost targets
    """
    model.eval()
    states: List[PuzzleState] = []
    all_successors: List[List[PuzzleState]] = []
    is_solved_flags: List[bool] = []

    # 1. Generate scrambled states backwards from goal
    for _ in range(batch_size):
        k = np.random.randint(1, max_depth + 1)
        scrambled_state, _ = goal.scramble(steps=k)
        states.append(scrambled_state)
        is_solved_flags.append(scrambled_state.is_solved())

        # Collect successors for Bellman min update
        succs = [scrambled_state.apply_action(a) for a in scrambled_state.get_valid_actions()]
        all_successors.append(succs)

    # 2. Flatten and evaluate all successors in a single batch
    flat_succs: List[PuzzleState] = [s for sublist in all_successors for s in sublist]
    with torch.no_grad():
        flat_preds = model.predict_states(flat_succs, device=device)

    # 3. Compute Bellman targets: y(s) = 0 if solved else 1 + min_a h(s')
    targets = np.zeros((batch_size, 1), dtype=np.float32)
    idx = 0
    for i in range(batch_size):
        if is_solved_flags[i]:
            targets[i, 0] = 0.0
            idx += len(all_successors[i])
        else:
            n_succs = len(all_successors[i])
            succ_preds = flat_preds[idx : idx + n_succs]
            targets[i, 0] = 1.0 + float(np.min(succ_preds))
            idx += n_succs

    # 4. Prepare input one-hot tensors
    input_arrays = np.stack([s.to_one_hot() for s in states])
    inputs = torch.from_numpy(input_arrays).to(device)
    targets_tensor = torch.from_numpy(targets).to(device)

    return inputs, targets_tensor


def evaluate_model(
    goal: PuzzleState,
    model: PuzzleHeuristicNet,
    device: str,
    num_tests: int = 10,
    test_depth: int = 15,
) -> float:
    """Evaluates the solve rate of the neural solver on test scrambles."""
    solver = NeuralAStarSolver(model=model, rows=goal.rows, cols=goal.cols, device=device)
    solved_count = 0

    for seed in range(num_tests):
        test_state, _ = goal.scramble(steps=test_depth, seed=1000 + seed)
        res = solver.solve(test_state, time_limit=1.5, max_nodes=5000)
        if res.success:
            solved_count += 1

    return (solved_count / num_tests) * 100.0


def main() -> int:
    """Main training loop."""
    args = parse_args()

    # Determine device
    if args.device:
        device = args.device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    save_path = args.save_model
    if not save_path:
        save_path = f"models/puzzle_ai_{args.rows}x{args.cols}.pt"
    save_file = Path(save_path)
    save_file.parent.mkdir(parents=True, exist_ok=True)

    print("[*] ===================================================")
    print("[*] Sliding Tile Puzzle - Deep Learning Trainer (ADI)")
    print("[*] ===================================================")
    print(f"Grid Dimensions : {args.rows} rows x {args.cols} cols ({args.rows * args.cols} tiles)")
    print(f"Hardware Device : {device.upper()} {'(' + torch.cuda.get_device_name(0) + ')' if device == 'cuda' else ''}")
    print(f"Curriculum Depth: 1 to {args.max_depth} scramble steps")
    print(f"Batch Size      : {args.batch_size}")
    print(f"Total Epochs    : {args.epochs} ({args.steps_per_epoch} batches/epoch)")
    print(f"Model Save Path : {save_file}")
    print("[*] ===================================================\n")

    goal = PuzzleState.create_goal(rows=args.rows, cols=args.cols)
    model = PuzzleHeuristicNet(rows=args.rows, cols=args.cols).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    loss_fn = nn.SmoothL1Loss()
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_loss = float("inf")
    total_start_time = time.perf_counter()

    for epoch in range(1, args.epochs + 1):
        epoch_start = time.perf_counter()
        model.train()
        epoch_losses: List[float] = []

        # Curriculum depth scaling across training
        curr_depth = max(3, int(args.max_depth * (epoch / args.epochs)))

        for _ in range(args.steps_per_epoch):
            inputs, targets = generate_adi_batch(
                goal=goal,
                model=model,
                batch_size=args.batch_size,
                max_depth=curr_depth,
                device=device,
            )

            model.train()
            optimizer.zero_grad()
            preds = model(inputs)
            loss = loss_fn(preds, targets)
            loss.backward()
            optimizer.step()

            epoch_losses.append(loss.item())

        scheduler.step()
        avg_loss = float(np.mean(epoch_losses))
        epoch_duration = time.perf_counter() - epoch_start

        # Periodic test evaluation
        if epoch % 5 == 0 or epoch == args.epochs:
            solve_rate = evaluate_model(goal, model, device=device, num_tests=10, test_depth=min(12, curr_depth))
            eval_str = f" | Test Solve Rate: {solve_rate:5.1f}%"
        else:
            eval_str = ""

        print(
            f"Epoch [{epoch:3d}/{args.epochs:3d}] | Loss: {avg_loss:.5f} | "
            f"Depth: {curr_depth:2d} | Time: {epoch_duration:.2f}s{eval_str}"
        )

        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), save_file)

    total_duration = time.perf_counter() - total_start_time
    print(f"\n[+] Training completed in {total_duration:.2f}s!")
    print(f"[+] Best Model Checkpoint saved to: {save_file}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
