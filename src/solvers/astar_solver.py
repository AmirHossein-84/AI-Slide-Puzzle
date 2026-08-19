"""A* and Weighted A* search solver using Manhattan Distance and Linear Conflict heuristics."""

from __future__ import annotations

import heapq
import time
from itertools import count
from typing import Callable, Dict, List, Optional, Tuple

from src.environment.puzzle_state import Action, PuzzleState
from src.solvers.base_solver import BaseSolver, SolverResult


class AStarSolver(BaseSolver):
    """Adaptive A* / Weighted A* optimal search solver."""

    def __init__(
        self,
        name: str = "A* Search (Linear Conflict)",
        use_linear_conflict: bool = True,
        weight: float = 2.5,
    ) -> None:
        super().__init__(name=name)
        self.use_linear_conflict = use_linear_conflict
        self.weight = weight

    def _heuristic(self, state: PuzzleState) -> int:
        """Evaluates heuristic function."""
        if self.use_linear_conflict:
            return state.heuristic_cost()
        return state.manhattan_distance()

    def solve(
        self,
        initial_state: PuzzleState,
        time_limit: float = 30.0,
        max_nodes: int = 300_000,
    ) -> SolverResult:
        """Executes Weighted A* search from initial state to goal."""
        start_time = time.perf_counter()

        if initial_state.is_solved():
            return SolverResult(
                success=True,
                actions=[],
                states=[initial_state],
                nodes_expanded=0,
                duration_sec=time.perf_counter() - start_time,
                solver_name=self.name,
                message="Already solved.",
            )

        if not initial_state.is_solvable():
            return SolverResult(
                success=False,
                actions=[],
                states=[initial_state],
                nodes_expanded=0,
                duration_sec=time.perf_counter() - start_time,
                solver_name=self.name,
                message="Board is mathematically unsolvable.",
            )

        tie_counter = count()
        start_h = self._heuristic(initial_state)

        open_set: List[Tuple[float, int, int, PuzzleState, List[Action]]] = []
        heapq.heappush(open_set, (self.weight * start_h, start_h, next(tie_counter), initial_state, []))

        g_scores: Dict[PuzzleState, int] = {initial_state: 0}
        nodes_expanded = 0

        while open_set:
            if time.perf_counter() - start_time > time_limit:
                return SolverResult(
                    success=False,
                    actions=[],
                    states=[initial_state],
                    nodes_expanded=nodes_expanded,
                    duration_sec=time.perf_counter() - start_time,
                    solver_name=self.name,
                    message="Search time limit exceeded.",
                )

            if nodes_expanded >= max_nodes:
                return SolverResult(
                    success=False,
                    actions=[],
                    states=[initial_state],
                    nodes_expanded=nodes_expanded,
                    duration_sec=time.perf_counter() - start_time,
                    solver_name=self.name,
                    message="Max node expansion limit reached.",
                )

            f, h, _, current_state, path = heapq.heappop(open_set)
            nodes_expanded += 1

            if current_state.is_solved():
                states: List[PuzzleState] = [initial_state]
                reconstructed = initial_state
                for action in path:
                    reconstructed = reconstructed.apply_action(action)
                    states.append(reconstructed)

                return SolverResult(
                    success=True,
                    actions=path,
                    states=states,
                    nodes_expanded=nodes_expanded,
                    duration_sec=time.perf_counter() - start_time,
                    solver_name=self.name,
                    message="Solution found.",
                )

            current_g = g_scores[current_state]

            for action in current_state.get_valid_actions():
                neighbor = current_state.apply_action(action)
                tentative_g = current_g + 1

                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    neighbor_h = self._heuristic(neighbor)
                    neighbor_f = tentative_g + self.weight * neighbor_h
                    heapq.heappush(
                        open_set,
                        (neighbor_f, neighbor_h, next(tie_counter), neighbor, path + [action]),
                    )

        return SolverResult(
            success=False,
            actions=[],
            states=[initial_state],
            nodes_expanded=nodes_expanded,
            duration_sec=time.perf_counter() - start_time,
            solver_name=self.name,
            message="Exhausted search space without finding solution.",
        )
