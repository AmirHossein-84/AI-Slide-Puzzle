"""Iterative Deepening A* (IDA*) search solver with Linear Conflict heuristic."""

from __future__ import annotations

import time
from typing import List, Optional, Set, Tuple

from src.environment.puzzle_state import Action, PuzzleState
from src.solvers.base_solver import BaseSolver, SolverResult


class IDAStarSolver(BaseSolver):
    """Adaptive Iterative Deepening A* (IDA*) solver with linear conflict heuristic."""

    def __init__(
        self,
        name: str = "IDA* Search",
        use_linear_conflict: bool = True,
        weight: float = 2.0,
    ) -> None:
        super().__init__(name=name)
        self.use_linear_conflict = use_linear_conflict
        self.weight = weight

    def _heuristic(self, state: PuzzleState) -> int:
        if self.use_linear_conflict:
            return state.heuristic_cost()
        return state.manhattan_distance()

    def solve(
        self,
        initial_state: PuzzleState,
        time_limit: float = 30.0,
        max_nodes: int = 300_000,
    ) -> SolverResult:
        """Executes IDA* search from initial state to goal."""
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

        bound = int(self.weight * self._heuristic(initial_state))
        nodes_expanded = 0
        path_actions: List[Action] = []
        path_states: List[PuzzleState] = [initial_state]

        while True:
            t, nodes = self._search(
                path_states,
                path_actions,
                g=0,
                bound=bound,
                start_time=start_time,
                time_limit=time_limit,
                max_nodes=max_nodes - nodes_expanded,
            )
            nodes_expanded += nodes

            if t == -1:  # Found goal
                return SolverResult(
                    success=True,
                    actions=list(path_actions),
                    states=list(path_states),
                    nodes_expanded=nodes_expanded,
                    duration_sec=time.perf_counter() - start_time,
                    solver_name=self.name,
                    message="Solution found.",
                )

            if t == float("inf"):
                return SolverResult(
                    success=False,
                    actions=[],
                    states=[initial_state],
                    nodes_expanded=nodes_expanded,
                    duration_sec=time.perf_counter() - start_time,
                    solver_name=self.name,
                    message="Search time limit exceeded.",
                )

            if nodes_expanded >= max_nodes or time.perf_counter() - start_time > time_limit:
                return SolverResult(
                    success=False,
                    actions=[],
                    states=[initial_state],
                    nodes_expanded=nodes_expanded,
                    duration_sec=time.perf_counter() - start_time,
                    solver_name=self.name,
                    message="Search time limit exceeded.",
                )

            bound = int(t)

    def _search(
        self,
        path_states: List[PuzzleState],
        path_actions: List[Action],
        g: int,
        bound: int,
        start_time: float,
        time_limit: float,
        max_nodes: int,
    ) -> Tuple[float, int]:
        current = path_states[-1]
        h = self._heuristic(current)
        f = g + int(self.weight * h)

        if f > bound:
            return float(f), 1

        if current.is_solved():
            return -1.0, 1

        if time.perf_counter() - start_time > time_limit or max_nodes <= 0:
            return float("inf"), 1

        min_bound = float("inf")
        nodes_expanded = 1

        # Order valid actions by heuristic of resulting state (Best-First IDA*)
        successors = []
        for action in current.get_valid_actions():
            nxt = current.apply_action(action)
            if nxt not in path_states:
                successors.append((self._heuristic(nxt), action, nxt))
        successors.sort(key=lambda item: item[0])

        for _, action, nxt in successors:
            path_states.append(nxt)
            path_actions.append(action)

            t, n = self._search(
                path_states,
                path_actions,
                g + 1,
                bound,
                start_time,
                time_limit,
                max_nodes - nodes_expanded,
            )
            nodes_expanded += n

            if t == -1.0:
                return -1.0, nodes_expanded

            if t < min_bound:
                min_bound = t

            path_states.pop()
            path_actions.pop()

            if time.perf_counter() - start_time > time_limit or nodes_expanded >= max_nodes:
                return float("inf"), nodes_expanded

        return min_bound, nodes_expanded
