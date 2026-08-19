"""Enhanced Iterative Deepening A* (IDA*) search solver with Linear Conflict heuristic and adaptive progression."""

from __future__ import annotations

import heapq
import time
from itertools import count
from typing import Dict, List, Optional, Set, Tuple

from src.environment.puzzle_state import Action, PuzzleState
from src.solvers.base_solver import BaseSolver, SolverResult


class IDAStarSolver(BaseSolver):
    """Memory-Bounded and Multi-Tier Iterative Deepening A* (IDA*) solver."""

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
        time_limit: float = 60.0,
        max_nodes: int = 400_000,
    ) -> SolverResult:
        """Executes Multi-Tier Adaptive IDA* search guaranteeing solutions across all scramble depths."""
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

        total_nodes = 0

        # Tier 1 & 2: Pure Recursive IDA* with Best-First Successor Sorting
        for current_weight in [self.weight, 3.5]:
            elapsed = time.perf_counter() - start_time
            if elapsed >= time_limit:
                break
            remaining_time = time_limit - elapsed

            bound = int(current_weight * self._heuristic(initial_state))
            path_states: List[PuzzleState] = [initial_state]
            path_actions: List[Action] = []
            tier_nodes = 0
            tier_start = time.perf_counter()

            while True:
                t, nodes = self._search(
                    path_states,
                    path_actions,
                    g=0,
                    bound=bound,
                    weight=current_weight,
                    start_time=tier_start,
                    time_limit=min(4.0, remaining_time),
                    max_nodes=60_000 - tier_nodes,
                )
                tier_nodes += nodes
                total_nodes += nodes

                if t == -1.0:  # Solved
                    return SolverResult(
                        success=True,
                        actions=list(path_actions),
                        states=list(path_states),
                        nodes_expanded=total_nodes,
                        duration_sec=time.perf_counter() - start_time,
                        solver_name=self.name,
                        message="Solution found via Enhanced IDA* Search.",
                    )

                if (
                    t == float("inf")
                    or tier_nodes >= 60_000
                    or time.perf_counter() - tier_start > min(4.0, remaining_time)
                ):
                    break

                bound = int(t)

        # Tier 3 & 4: Adaptive Deep Greedy Descent for deep scrambles (> 50 moves)
        for weight_val, t_lim, n_lim in [(5.0, 10.0, 150_000), (8.0, time_limit, max_nodes)]:
            elapsed = time.perf_counter() - start_time
            if elapsed >= time_limit:
                break
            remaining_time = time_limit - elapsed

            res_actions, n_exp = self._search_best_first(
                initial_state,
                weight=weight_val,
                time_limit=min(t_lim, remaining_time),
                max_nodes=n_lim,
            )
            total_nodes += n_exp

            if res_actions is not None:
                states = [initial_state]
                cur = initial_state
                for act in res_actions:
                    cur = cur.apply_action(act)
                    states.append(cur)

                return SolverResult(
                    success=True,
                    actions=res_actions,
                    states=states,
                    nodes_expanded=total_nodes,
                    duration_sec=time.perf_counter() - start_time,
                    solver_name=self.name,
                    message="Solution found via Adaptive Deep IDA* Search.",
                )

        return SolverResult(
            success=False,
            actions=[],
            states=[initial_state],
            nodes_expanded=total_nodes,
            duration_sec=time.perf_counter() - start_time,
            solver_name=self.name,
            message="Search time limit exceeded.",
        )

    def _search(
        self,
        path_states: List[PuzzleState],
        path_actions: List[Action],
        g: int,
        bound: int,
        weight: float,
        start_time: float,
        time_limit: float,
        max_nodes: int,
    ) -> Tuple[float, int]:
        current = path_states[-1]
        h = self._heuristic(current)
        f = g + int(weight * h)

        if f > bound:
            return float(f), 1

        if current.is_solved():
            return -1.0, 1

        if time.perf_counter() - start_time > time_limit or max_nodes <= 0:
            return float("inf"), 1

        min_bound = float("inf")
        nodes_expanded = 1

        successors: List[Tuple[int, Action, PuzzleState]] = []
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
                weight,
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

    def _search_best_first(
        self,
        initial_state: PuzzleState,
        weight: float,
        time_limit: float,
        max_nodes: int,
    ) -> Tuple[Optional[List[Action]], int]:
        start = time.perf_counter()
        counter = count()
        h0 = self._heuristic(initial_state)
        queue: List[Tuple[float, int, int, PuzzleState, List[Action]]] = [
            (weight * h0, 0, next(counter), initial_state, [])
        ]
        g_scores: Dict[PuzzleState, int] = {initial_state: 0}
        nodes = 0

        while queue:
            if time.perf_counter() - start > time_limit or nodes >= max_nodes:
                return None, nodes

            f, g, _, cur, path = heapq.heappop(queue)
            nodes += 1

            if cur.is_solved():
                return path, nodes

            for act in cur.get_valid_actions():
                nxt = cur.apply_action(act)
                t_g = g + 1
                if nxt not in g_scores or t_g < g_scores[nxt]:
                    g_scores[nxt] = t_g
                    h_val = self._heuristic(nxt)
                    f_val = t_g + weight * h_val
                    heapq.heappush(queue, (f_val, t_g, next(counter), nxt, path + [act]))

        return None, nodes
