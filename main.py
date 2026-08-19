#!/usr/bin/env python3
"""Main application entry point for the Digimon Sliding Tile Puzzle game."""

from __future__ import annotations

import argparse
import sys

from src.ui.game_view import GameView


def parse_args() -> argparse.Namespace:
    """Parses command-line options."""
    parser = argparse.ArgumentParser(
        description="Launch the interactive Digimon Sliding Tile Puzzle game with AI solvers."
    )
    parser.add_argument(
        "--rows",
        "-r",
        type=int,
        default=7,
        help="Number of rows on the board (default: 7 for Digimon puzzle)",
    )
    parser.add_argument(
        "--cols",
        "-c",
        type=int,
        default=6,
        help="Number of columns on the board (default: 6 for Digimon puzzle)",
    )
    return parser.parse_args()


def main() -> int:
    """Launches the Pygame interactive application."""
    args = parse_args()
    print("[*] Starting Digimon Sliding Tile Puzzle Game...")
    print(f"[*] Grid: {args.rows} rows x {args.cols} cols ({args.rows * args.cols} tiles)")

    try:
        app = GameView(rows=args.rows, cols=args.cols)
        app.run()
        return 0
    except Exception as exc:
        print(f"[-] Error launching game: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
