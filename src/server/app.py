"""FastAPI & WebSocket server exposing Puzzle environment, Multi-Solver suite, and AI Training Studio."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.environment.puzzle_state import Action, PuzzleState
from src.server.schemas import (
    BenchmarkRequest,
    DeployRequest,
    DeployResponse,
    ModelInfo,
    MoveRequest,
    PuzzleStateResponse,
    ScrambleRequest,
    SolveRequest,
    SolveResponse,
    TrainStartRequest,
    TrainStartResponse,
    TrainStatusResponse,
    TrainStopResponse,
)
from src.server.training_manager import TrainingManager
from src.solvers.astar_solver import AStarSolver
from src.solvers.hierarchical_solver import HierarchicalSolver
from src.solvers.idastar_solver import IDAStarSolver
from src.solvers.neural_solver import NeuralAStarSolver, _get_phase_tag
from src.utils.benchmark_runner import run_solver_benchmark

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PuzzleServer")


class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder handling NumPy scalars and arrays."""

    def default(self, o: Any) -> Any:
        if isinstance(o, (bool, np.bool_)):
            return bool(o)
        if isinstance(o, (int, np.integer)):
            return int(o)
        if isinstance(o, (float, np.floating)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


app = FastAPI(
    title="Digimon 43-Slot Sliding Puzzle AI Server",
    description="Multi-solver AI engine and live PyTorch training studio backend.",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory puzzle state (defaults to solved 43-slot Digimon goal state)
current_game_state: PuzzleState = PuzzleState.create_goal(rows=7, cols=6, has_pocket=True)

# Global active deployed neural checkpoint path
active_neural_model_path: Optional[str] = "models/digimon_ai.pt" if Path("models/digimon_ai.pt").exists() else None

# Registry of solver instances
solvers: Dict[str, Any] = {
    "Hierarchical Subgoal Solver": HierarchicalSolver(),
    "A* Search (Linear Conflict)": AStarSolver(name="A* Search (Linear Conflict)", use_linear_conflict=True, weight=2.5),
    "IDA* Search": IDAStarSolver(name="IDA* Search", use_linear_conflict=True, weight=2.0),
}


def _state_to_response(state: PuzzleState) -> PuzzleStateResponse:
    """Converts a PuzzleState to a PuzzleStateResponse."""
    return PuzzleStateResponse(
        board=state.to_list(),
        rows=state.rows,
        cols=state.cols,
        has_pocket=state.has_pocket,
        blank_pos=list(state.blank_pos),
        is_solved=state.is_solved(),
        is_solvable=state.is_solvable(),
        manhattan=state.manhattan_distance(),
        linear_conflicts=state.linear_conflicts(),
    )


@app.get("/api/state", response_model=PuzzleStateResponse)
async def get_state() -> PuzzleStateResponse:
    """Returns the current puzzle game state."""
    global current_game_state
    return _state_to_response(current_game_state)


@app.post("/api/reset", response_model=PuzzleStateResponse)
async def reset_board() -> PuzzleStateResponse:
    """Resets the puzzle board to the solved 43-slot goal state."""
    global current_game_state
    current_game_state = PuzzleState.create_goal(rows=7, cols=6, has_pocket=True)
    return _state_to_response(current_game_state)


@app.post("/api/move", response_model=PuzzleStateResponse)
async def make_move(req: MoveRequest) -> PuzzleStateResponse:
    """Applies a manual move to the current board state."""
    global current_game_state
    try:
        action = Action(req.action)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action {req.action}")

    if not current_game_state.is_valid_action(action):
        raise HTTPException(
            status_code=400,
            detail=f"Illegal move {action.name} from blank position {current_game_state.blank_pos}",
        )

    current_game_state = current_game_state.apply_action(action)
    return _state_to_response(current_game_state)


@app.post("/api/scramble", response_model=PuzzleStateResponse)
async def scramble_board(req: ScrambleRequest) -> PuzzleStateResponse:
    """Scrambles the puzzle board via random walk, ensuring solvability."""
    global current_game_state
    current_game_state, _ = current_game_state.scramble(steps=req.steps, seed=req.seed)
    return _state_to_response(current_game_state)


@app.post("/api/solve", response_model=SolveResponse)
async def solve_puzzle(req: SolveRequest) -> SolveResponse:
    """Solves the current or provided puzzle state using chosen solver engine."""
    global current_game_state, active_neural_model_path
    target_state = current_game_state
    if req.board is not None:
        target_state = PuzzleState(req.board, rows=7, cols=6, has_pocket=True)

    if req.solver == "Neural AI (PyTorch)":
        solver_inst = NeuralAStarSolver(
            model_path=active_neural_model_path,
            rows=7,
            cols=6,
            has_pocket=True,
            weight=2.5,
        )
    else:
        solver_inst = solvers.get(req.solver, solvers["Hierarchical Subgoal Solver"])

    result = solver_inst.solve(target_state, time_limit=req.time_limit)
    phase_names = [_get_phase_tag(s) for s in result.states[1:]] if result.success else []

    return SolveResponse(
        success=result.success,
        actions=[int(a) for a in result.actions],
        action_names=[a.name for a in result.actions],
        phase_names=phase_names,
        states=[s.to_list() for s in result.states],
        duration_ms=round(result.duration_sec * 1000.0, 2),
        nodes_expanded=result.nodes_expanded,
        solver_name=result.solver_name,
        message=result.message,
    )


@app.post("/api/train/deploy", response_model=DeployResponse)
async def deploy_trained_model(req: DeployRequest) -> DeployResponse:
    """Deploys a trained PyTorch model checkpoint into the active game solver suite."""
    global active_neural_model_path
    model_path = req.model_path
    if not model_path or not Path(model_path).exists():
        raise HTTPException(status_code=404, detail=f"Model checkpoint '{model_path}' not found.")

    active_neural_model_path = model_path
    logger.info(f"Deployed new neural model checkpoint: {model_path}")
    return DeployResponse(status="deployed", model_path=model_path)


# ---------------------------------------------------------------------------
# Training API Endpoints
# ---------------------------------------------------------------------------

training_manager = TrainingManager()


@app.post("/api/train/start", response_model=TrainStartResponse)
async def start_training_session(req: TrainStartRequest) -> TrainStartResponse:
    """Starts background PyTorch ADI training session."""
    loop = asyncio.get_running_loop()
    started = training_manager.start_training(
        loop=loop,
        rows=req.rows,
        cols=req.cols,
        has_pocket=req.has_pocket,
        epochs=req.epochs,
        steps_per_epoch=req.steps_per_epoch,
        batch_size=req.batch_size,
        max_depth=req.max_depth,
        lr=req.lr,
        save_path=req.save_path,
    )
    if not started:
        raise HTTPException(status_code=400, detail="Training is already in progress.")
    return TrainStartResponse(status="started", message="Background training initiated.")


@app.post("/api/train/stop", response_model=TrainStopResponse)
async def stop_training_session() -> TrainStopResponse:
    """Stops the ongoing training session."""
    stopped = training_manager.stop_training()
    return TrainStopResponse(stopped=stopped)


@app.get("/api/train/status", response_model=TrainStatusResponse)
async def get_training_status() -> TrainStatusResponse:
    """Returns current training manager status."""
    st = training_manager.get_status()
    return TrainStatusResponse(
        is_training=training_manager.is_training,
        status=st.get("status", "idle"),
        epoch=st.get("epoch", 0),
        total_epochs=st.get("total_epochs", 0),
        current_depth=st.get("current_depth", 0),
        loss=st.get("loss", 0.0),
        test_solve_rate=st.get("test_solve_rate", 0.0),
        device=st.get("device", "cpu"),
    )


@app.get("/api/train/models", response_model=List[ModelInfo])
async def list_trained_models() -> List[ModelInfo]:
    """Lists saved PyTorch neural heuristic model checkpoints."""
    models_dir = Path("models")
    if not models_dir.exists():
        return []

    result: List[ModelInfo] = []
    for f in sorted(models_dir.glob("*.pt"), key=lambda p: p.stat().st_mtime, reverse=True):
        st = f.stat()
        import datetime
        dt_str = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
        result.append(
            ModelInfo(
                name=f.name,
                path=str(f),
                size_kb=round(st.st_size / 1024.0, 1),
                modified_time=dt_str,
            )
        )
    return result


# ---------------------------------------------------------------------------
# WebSocket Endpoints
# ---------------------------------------------------------------------------

@app.websocket("/ws/train")
async def ws_training_stream(websocket: WebSocket) -> None:
    """WebSocket for bi-directional live AI training control and telemetry streaming."""
    await websocket.accept()
    queue = training_manager.subscribe()
    logger.info("Training WebSocket client connected.")

    # Send initial status
    init_status = {
        "type": "init",
        "is_training": training_manager.is_training,
        "status": training_manager.get_status(),
    }
    await websocket.send_text(json.dumps(init_status, cls=NumpyJSONEncoder))

    async def sender_loop() -> None:
        try:
            while True:
                event = await queue.get()
                await websocket.send_text(json.dumps(event, cls=NumpyJSONEncoder))
        except (WebSocketDisconnect, asyncio.CancelledError):
            pass

    sender_task = asyncio.create_task(sender_loop())

    try:
        while True:
            text = await websocket.receive_text()
            data = json.loads(text)
            action = data.get("action")

            if action == "start":
                loop = asyncio.get_running_loop()
                training_manager.start_training(
                    loop=loop,
                    rows=int(data.get("rows", 3)),
                    cols=int(data.get("cols", 3)),
                    has_pocket=bool(data.get("has_pocket", False)),
                    epochs=int(data.get("epochs", 20)),
                    steps_per_epoch=int(data.get("steps_per_epoch", 25)),
                    batch_size=int(data.get("batch_size", 256)),
                    max_depth=int(data.get("max_depth", 20)),
                    lr=float(data.get("lr", 1e-3)),
                    save_path=str(data.get("save_path", "models/trained_ai.pt")),
                )
            elif action == "stop":
                training_manager.stop_training()

    except WebSocketDisconnect:
        logger.info("Training WebSocket client disconnected.")
    finally:
        sender_task.cancel()
        training_manager.unsubscribe(queue)


@app.websocket("/ws/solve")
async def ws_solve_stream(websocket: WebSocket) -> None:
    """WebSocket for animated step-by-step puzzle solution streaming."""
    await websocket.accept()
    try:
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)

            board_arr = data.get("board", current_game_state.to_list())
            solver_name = data.get("solver", "Hierarchical Subgoal Solver")
            step_delay = float(data.get("step_delay", 0.1))

            state = PuzzleState(board_arr, rows=7, cols=6, has_pocket=True)

            if solver_name == "Neural AI (PyTorch)":
                solver_inst = NeuralAStarSolver(
                    model_path=active_neural_model_path,
                    rows=7,
                    cols=6,
                    has_pocket=True,
                    weight=2.5,
                )
            else:
                solver_inst = solvers.get(solver_name, solvers["Hierarchical Subgoal Solver"])

            result = solver_inst.solve(state, time_limit=30.0)

            if not result.success:
                await websocket.send_text(
                    json.dumps({
                        "type": "error",
                        "message": result.message or "Solver failed to find path.",
                    }, cls=NumpyJSONEncoder)
                )
                continue

            curr = state
            for idx, action in enumerate(result.actions):
                curr = curr.apply_action(action)
                payload = {
                    "type": "step",
                    "step_index": idx + 1,
                    "total_steps": len(result.actions),
                    "action": int(action),
                    "action_name": action.name,
                    "phase_name": _get_phase_tag(curr),
                    "board": curr.to_list(),
                    "blank_pos": list(curr.blank_pos),
                    "is_solved": bool(curr.is_solved()),
                }
                await websocket.send_text(json.dumps(payload, cls=NumpyJSONEncoder))
                await asyncio.sleep(step_delay)

            await websocket.send_text(
                json.dumps({
                    "type": "complete",
                    "total_steps": len(result.actions),
                    "duration_ms": round(result.duration_sec * 1000.0, 2),
                    "nodes_expanded": result.nodes_expanded,
                }, cls=NumpyJSONEncoder)
            )

    except WebSocketDisconnect:
        logger.info("Solve WebSocket client disconnected.")


# Static file serving for React frontend and assets
web_dist_dir = Path(__file__).resolve().parent.parent.parent / "web" / "dist"
if web_dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_dist_dir), html=True), name="frontend")
