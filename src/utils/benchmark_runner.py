"""Solver benchmarking harness and statistics generator."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
from tabulate import tabulate

from src.environment.puzzle_state import PuzzleState
from src.solvers.base_solver import BaseSolver, SolverResult


@dataclass
class BenchmarkSummary:
    """Aggregated performance metrics for a single solver."""

    solver_name: str
    total_puzzles: int
    solved_count: int
    success_rate_pct: float
    avg_duration_ms: float
    avg_moves: float
    avg_nodes: float
    min_moves: int
    max_moves: int


def run_solver_benchmark(
    solvers: Dict[str, BaseSolver],
    rows: int = 3,
    cols: int = 3,
    num_puzzles: int = 20,
    scramble_depth: int = 15,
    time_limit_per_puzzle: float = 5.0,
    seed: int = 42,
) -> List[BenchmarkSummary]:
    """Runs a comparative benchmark across multiple solvers on identical test states.

    Args:
        solvers: Dictionary mapping solver names to BaseSolver instances.
        rows: Grid row count.
        cols: Grid column count.
        num_puzzles: Number of randomized test puzzles to generate.
        scramble_depth: Scramble depth for each puzzle.
        time_limit_per_puzzle: Timeout in seconds for each solver on each puzzle.
        seed: Random seed for reproducibility.

    Returns:
        List of BenchmarkSummary objects.
    """
    goal = PuzzleState.create_goal(rows=rows, cols=cols)

    # 1. Generate identical benchmark test suite
    test_states: List[PuzzleState] = []
    for i in range(num_puzzles):
        state, _ = goal.scramble(steps=scramble_depth, seed=seed + i)
        test_states.append(state)

    summaries: List[BenchmarkSummary] = []

    # 2. Benchmark each solver
    for name, solver in solvers.items():
        durations_ms: List[float] = []
        move_counts: List[int] = []
        nodes_expanded: List[int] = []
        solved_count = 0

        for state in test_states:
            res: SolverResult = solver.solve(state, time_limit=time_limit_per_puzzle)

            if res.success:
                solved_count += 1
                durations_ms.append(res.duration_sec * 1000.0)
                move_counts.append(len(res.actions))
                nodes_expanded.append(res.nodes_expanded)

        success_rate = (solved_count / num_puzzles) * 100.0
        avg_dur = float(np.mean(durations_ms)) if durations_ms else 0.0
        avg_m = float(np.mean(move_counts)) if move_counts else 0.0
        avg_n = float(np.mean(nodes_expanded)) if nodes_expanded else 0.0
        min_m = min(move_counts) if move_counts else 0
        max_m = max(move_counts) if move_counts else 0

        summary = BenchmarkSummary(
            solver_name=name,
            total_puzzles=num_puzzles,
            solved_count=solved_count,
            success_rate_pct=success_rate,
            avg_duration_ms=avg_dur,
            avg_moves=avg_m,
            avg_nodes=avg_n,
            min_moves=min_m,
            max_moves=max_m,
        )
        summaries.append(summary)

    return summaries


def format_benchmark_table(
    summaries: List[BenchmarkSummary],
    table_format: str = "github",
) -> str:
    """Formats benchmark summaries into a printable markdown or console table."""
    headers = [
        "Solver Name",
        "Success (%)",
        "Avg Time (ms)",
        "Avg Moves",
        "Min / Max Moves",
        "Avg Nodes Exp.",
    ]
    rows = []
    for s in summaries:
        rows.append([
            s.solver_name,
            f"{s.success_rate_pct:.1f}% ({s.solved_count}/{s.total_puzzles})",
            f"{s.avg_duration_ms:.2f} ms",
            f"{s.avg_moves:.1f}",
            f"{s.min_moves} / {s.max_moves}",
            f"{s.avg_nodes:,.0f}",
        ])

    return tabulate(rows, headers=headers, tablefmt=table_format)
