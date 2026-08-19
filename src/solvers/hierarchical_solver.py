"""Hierarchical and Adaptive Weighted A* Solver for 43-slot Digimon puzzle and NxM boards."""

from __future__ import annotations

import heapq
import time
from collections import deque
from itertools import count
from typing import Dict, List, Optional, Set, Tuple
import numpy as np

from src.environment.puzzle_state import ACTION_DELTAS, Action, PuzzleState
from src.solvers.base_solver import BaseSolver, SolverResult


class HierarchicalSolver(BaseSolver):
    """Adaptive Hierarchical Subgoal & Weighted A* Solver."""

    def __init__(self, name: str = "Hierarchical Subgoal Solver") -> None:
        super().__init__(name=name)

    def solve(
        self,
        initial_state: PuzzleState,
        time_limit: float = 30.0,
        max_nodes: int = 500_000,
    ) -> SolverResult:
        """Solves 43-slot Digimon puzzle or arbitrary NxM board."""
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

        # 1. Tier 1: Fast Weighted A* with Linear Conflict (w = 2.5)
        res1_actions, res1_nodes = self._weighted_astar(
            initial_state, weight=2.5, time_limit=min(2.0, time_limit), max_nodes=60_000
        )
        if res1_actions is not None:
            states = [initial_state]
            cur = initial_state
            for a in res1_actions:
                cur = cur.apply_action(a)
                states.append(cur)

            return SolverResult(
                success=True,
                actions=res1_actions,
                states=states,
                nodes_expanded=res1_nodes,
                duration_sec=time.perf_counter() - start_time,
                solver_name=self.name,
                message="Solution found via Weighted A* Search.",
            )

        # 2. Tier 2: Deeper Multi-Weight Best-First Search
        res2_actions, res2_nodes = self._weighted_astar(
            initial_state, weight=3.5, time_limit=time_limit - (time.perf_counter() - start_time), max_nodes=max_nodes
        )
        total_nodes = res1_nodes + res2_nodes

        if res2_actions is not None:
            states = [initial_state]
            cur = initial_state
            for a in res2_actions:
                cur = cur.apply_action(a)
                states.append(cur)

            return SolverResult(
                success=True,
                actions=res2_actions,
                states=states,
                nodes_expanded=total_nodes,
                duration_sec=time.perf_counter() - start_time,
                solver_name=self.name,
                message="Solution found via Deep Heuristic Search.",
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

    def _weighted_astar(
        self,
        state: PuzzleState,
        weight: float = 2.5,
        time_limit: float = 5.0,
        max_nodes: int = 200_000,
    ) -> Tuple[Optional[List[Action]], int]:
        start = time.perf_counter()
        counter = count()
        h0 = state.heuristic_cost()
        queue: List[Tuple[float, int, int, PuzzleState, List[Action]]] = [
            (weight * h0, 0, next(counter), state, [])
        ]
        g_scores: Dict[PuzzleState, int] = {state: 0}
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
                tentative_g = g + 1
                if nxt not in g_scores or tentative_g < g_scores[nxt]:
                    g_scores[nxt] = tentative_g
                    h_val = nxt.heuristic_cost()
                    f_val = tentative_g + weight * h_val
                    heapq.heappush(queue, (f_val, tentative_g, next(counter), nxt, path + [act]))

        return None, nodes
