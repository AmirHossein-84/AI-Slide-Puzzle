#!/usr/bin/env python3
"""CLI utility for running comparative solver performance benchmarks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict

from src.solvers.astar_solver import AStarSolver
from src.solvers.base_solver import BaseSolver
from src.solvers.hierarchical_solver import HierarchicalSolver
from src.solvers.idastar_solver import IDAStarSolver
from src.solvers.neural_solver import NeuralAStarSolver
from src.utils.benchmark_runner import format_benchmark_table, run_solver_benchmark


def parse_args() -> argparse.Namespace:
    """Parses benchmark CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run comparative performance benchmarks across sliding tile puzzle solvers."
    )
    parser.add_argument("--rows", "-r", type=int, default=3, help="Grid rows (default: 3)")
    parser.add_argument("--cols", "-c", type=int, default=3, help="Grid columns (default: 3)")
    parser.add_argument("--num-puzzles", "-n", type=int, default=20, help="Number of test puzzles (default: 20)")
    parser.add_argument("--depth", "-d", type=int, default=15, help="Scramble depth per puzzle (default: 15)")
    parser.add_argument("--timeout", "-t", type=float, default=5.0, help="Timeout in seconds per puzzle (default: 5.0)")
    parser.add_argument("--model", "-m", type=str, default="", help="Path to trained PyTorch model weights")
    parser.add_argument("--export-md", type=str, default="", help="Optional markdown file to export results table")
    return parser.parse_args()


def main() -> int:
    """Runs benchmark suite."""
    args = parse_args()

    print("[*] ===================================================")
    print("[*] Sliding Tile Puzzle - Multi-Solver Benchmark Suite")
    print("[*] ===================================================")
    print(f"Grid Dimensions : {args.rows} rows x {args.cols} cols ({args.rows * args.cols} tiles)")
    print(f"Puzzles Count   : {args.num_puzzles} randomly scrambled states")
    print(f"Scramble Depth  : {args.depth} steps")
    print(f"Timeout / Puzzle: {args.timeout}s")
    print("[*] ===================================================\n")

    # Initialize Solvers
    solvers: Dict[str, BaseSolver] = {
        "A* (Manhattan)": AStarSolver(name="A* (Manhattan)", use_linear_conflict=False),
        "A* (Linear Conflict)": AStarSolver(name="A* (Linear Conflict)", use_linear_conflict=True),
        "IDA* (Linear Conflict)": IDAStarSolver(name="IDA* (Linear Conflict)", use_linear_conflict=True),
        "Hierarchical Solver": HierarchicalSolver(name="Hierarchical Solver"),
    }

    # Include Neural Solver if weights exist or requested
    model_file = args.model or f"models/puzzle_ai_{args.rows}x{args.cols}.pt"
    if Path(model_file).exists():
        print(f"[+] Loaded neural weights from {model_file} into Neural AI solver.")
        solvers["Neural AI"] = NeuralAStarSolver(
            model_path=model_file,
            rows=args.rows,
            cols=args.cols,
            name="Neural AI (DeepCubeA)",
        )
    else:
        print(f"[*] Note: Neural weights not found at '{model_file}'. Skipping Neural AI in benchmark.")

    print("\n[*] Running benchmarks, please wait...")
    summaries = run_solver_benchmark(
        solvers=solvers,
        rows=args.rows,
        cols=args.cols,
        num_puzzles=args.num_puzzles,
        scramble_depth=args.depth,
        time_limit_per_puzzle=args.timeout,
    )

    table_str = format_benchmark_table(summaries, table_format="github")
    print("\n" + table_str + "\n")

    if args.export_md:
        out_file = Path(args.export_md)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"# Solver Benchmark ({args.rows}x{args.cols})\n\n")
            f.write(table_str + "\n")
        print(f"[+] Exported benchmark table to {out_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
