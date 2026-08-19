"""Abstract solver interface and result data structures."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from src.environment.puzzle_state import Action, PuzzleState


@dataclass
class SolverResult:
    """Encapsulates the output and performance metrics of a puzzle solver."""

    success: bool
    actions: List[Action] = field(default_factory=list)
    states: List[PuzzleState] = field(default_factory=list)
    nodes_expanded: int = 0
    duration_sec: float = 0.0
    solver_name: str = "BaseSolver"
    message: str = ""

    @property
    def cost(self) -> int:
        """Total move count of the solution path."""
        return len(self.actions)


class BaseSolver(ABC):
    """Abstract base class for all puzzle solvers."""

    def __init__(self, name: str = "BaseSolver") -> None:
        self.name = name

    @abstractmethod
    def solve(
        self,
        initial_state: PuzzleState,
        time_limit: float = 30.0,
        max_nodes: int = 1_000_000,
    ) -> SolverResult:
        """Solves the given puzzle state.

        Args:
            initial_state: Starting PuzzleState.
            time_limit: Maximum allowed execution time in seconds.
            max_nodes: Maximum node expansions allowed.

        Returns:
            SolverResult instance.
        """
        pass
