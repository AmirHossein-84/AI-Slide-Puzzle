"""Unit tests for benchmarking runner."""

import pytest

from src.solvers.astar_solver import AStarSolver
from src.solvers.hierarchical_solver import HierarchicalSolver
from src.utils.benchmark_runner import format_benchmark_table, run_solver_benchmark


def test_benchmark_runner_execution():
    """Verifies that benchmark runner aggregates metrics without errors."""
    solvers = {
        "A*": AStarSolver(),
        "Hierarchical": HierarchicalSolver(),
    }
    summaries = run_solver_benchmark(
        solvers=solvers,
        rows=3,
        cols=3,
        num_puzzles=4,
        scramble_depth=8,
        time_limit_per_puzzle=2.0,
    )
    assert len(summaries) == 2
    assert all(s.success_rate_pct == 100.0 for s in summaries)
    assert all(s.avg_duration_ms > 0 for s in summaries)

    # Test markdown table formatting
    md_table = format_benchmark_table(summaries, table_format="github")
    assert "Solver Name" in md_table
    assert "A*" in md_table
    assert "Hierarchical" in md_table
