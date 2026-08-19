"""Pydantic data schemas for FastAPI REST API and WebSocket communication."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MoveRequest(BaseModel):
    """Payload for making a manual move."""
    action: int = Field(..., ge=0, le=3, description="Action index: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT")


class ScrambleRequest(BaseModel):
    """Payload for scrambling the board."""
    steps: int = Field(20, ge=1, le=500, description="Number of random walk steps")
    seed: Optional[int] = Field(None, description="Optional random seed for reproducibility")


class SolveRequest(BaseModel):
    """Payload for requesting puzzle solution."""
    board: Optional[List[int]] = Field(None, description="Optional custom 43-slot board state")
    solver: str = Field("Hierarchical Subgoal Solver", description="Solver engine name")
    time_limit: float = Field(60.0, ge=0.1, le=120.0, description="Time limit in seconds")


class BenchmarkRequest(BaseModel):
    """Payload for running multi-solver tournament benchmark."""
    solvers: List[str] = Field(
        default=["Hierarchical Subgoal Solver", "A* Search (Linear Conflict)"],
        description="Solvers to benchmark",
    )
    num_puzzles: int = Field(5, ge=1, le=50, description="Number of test puzzles")
    scramble_depth: int = Field(15, ge=1, le=50, description="Scramble depth per puzzle")


class PuzzleStateResponse(BaseModel):
    """Data response representing full puzzle state."""
    board: List[int]
    rows: int
    cols: int
    has_pocket: bool
    blank_pos: List[int]
    is_solved: bool
    is_solvable: bool
    manhattan: int
    linear_conflicts: int


class SolveResponse(BaseModel):
    """Response containing search solution steps and diagnostics."""
    success: bool
    actions: List[int]
    action_names: List[str]
    phase_names: Optional[List[str]] = None
    states: List[List[int]]
    duration_ms: float
    nodes_expanded: int
    solver_name: str
    message: str


class TrainStartRequest(BaseModel):
    """Request payload to initiate AI training session."""
    rows: int = Field(3, ge=2, le=7)
    cols: int = Field(3, ge=2, le=6)
    has_pocket: bool = Field(False)
    epochs: int = Field(20, ge=1, le=100)
    steps_per_epoch: int = Field(25, ge=1, le=100)
    batch_size: int = Field(256, ge=16, le=2048)
    max_depth: int = Field(20, ge=1, le=50)
    lr: float = Field(1e-3, ge=1e-5, le=1e-1)
    save_path: str = Field("models/trained_ai.pt")


class TrainStartResponse(BaseModel):
    """Response returned when a training session starts."""
    status: str
    message: str


class TrainStopResponse(BaseModel):
    """Response returned when stopping training."""
    stopped: bool


class DeployRequest(BaseModel):
    """Payload for deploying a trained model."""
    model_path: str


class DeployResponse(BaseModel):
    """Response returned after model deployment."""
    status: str
    model_path: str


class TrainStatusResponse(BaseModel):
    """Current training manager status."""
    is_training: bool
    status: str
    epoch: int
    total_epochs: int
    current_depth: int
    loss: float
    test_solve_rate: float
    device: str


class ModelInfo(BaseModel):
    """Metadata for a saved neural network checkpoint."""
    name: str
    path: str
    size_kb: float
    modified_time: str
