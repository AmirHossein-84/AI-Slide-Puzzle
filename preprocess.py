#!/usr/bin/env python3
"""CLI utility for preprocessing puzzle board images and generating tile assets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.utils.image_slicer import extract_tiles_pipeline


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract and slice puzzle tile sprites from a reference image or generate procedural tiles."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="assets/raw/digimon_clean_board.jpg",
        help="Path to source image (default: assets/raw/digimon_clean_board.jpg)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="assets/tiles",
        help="Output directory for generated tiles (default: assets/tiles)",
    )
    parser.add_argument(
        "--rows",
        "-r",
        type=int,
        default=7,
        help="Number of rows in puzzle grid (default: 7)",
    )
    parser.add_argument(
        "--cols",
        "-c",
        type=int,
        default=6,
        help="Number of columns in puzzle grid (default: 6)",
    )
    parser.add_argument(
        "--size",
        "-s",
        type=int,
        default=128,
        help="Square tile size in pixels (default: 128)",
    )
    parser.add_argument(
        "--procedural",
        action="store_true",
        help="Generate clean procedural numbered tiles instead of slicing from image",
    )
    return parser.parse_args()


def main() -> int:
    """Executes tile extraction pipeline from CLI arguments."""
    args = parse_args()
    input_path = Path(args.input) if not args.procedural else None

    print("[*] ===========================================")
    print("[*] Sliding Tile Puzzle - Asset Preprocessor")
    print("[*] ===========================================")
    print(f"Grid Dimensions : {args.rows} rows x {args.cols} cols ({args.rows * args.cols} tiles)")
    print(f"Tile Resolution : {args.size}x{args.size} px")
    print(f"Target Output   : {args.output}")
    print(f"Mode            : {'Procedural Generated' if args.procedural else f'Image Slicing ({args.input})'}")

    try:
        saved_paths = extract_tiles_pipeline(
            source_image_path=input_path,
            output_dir=args.output,
            rows=args.rows,
            cols=args.cols,
            target_tile_size=args.size,
            use_procedural=args.procedural,
        )
        print(f"\n[+] Successfully generated {len(saved_paths)} tile sprites:")
        print(f"    - First tile : {saved_paths[0]}")
        print(f"    - Last tile  : {saved_paths[-1]}")
        print(f"    - Debug sheet: {Path(args.output) / 'debug_grid_preview.png'}")
        return 0
    except Exception as exc:
        print(f"\n[-] Error during preprocessing: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
