"""Unit tests for image slicer and asset extractor."""

from pathlib import Path
from PIL import Image
import pytest

from src.utils.image_slicer import TileExtractor, extract_tiles_pipeline


def test_procedural_tile_generation_count():
    """Verifies that procedural generator produces exactly rows * cols tiles."""
    rows, cols = 7, 6
    tiles = TileExtractor.generate_procedural_tiles(rows=rows, cols=cols, tile_size=64)
    assert len(tiles) == 42
    assert all(isinstance(tile, Image.Image) for tile in tiles)
    assert all(tile.size == (64, 64) for tile in tiles)


def test_procedural_tile_custom_dimensions():
    """Verifies procedural generator handles variable grid sizes (e.g. 3x3, 4x4)."""
    tiles_3x3 = TileExtractor.generate_procedural_tiles(rows=3, cols=3, tile_size=96)
    assert len(tiles_3x3) == 9

    tiles_4x4 = TileExtractor.generate_procedural_tiles(rows=4, cols=4, tile_size=96)
    assert len(tiles_4x4) == 16


def test_slice_synthetic_grid_image():
    """Verifies slicing on a synthetic grid image."""
    rows, cols = 4, 3
    synth_image = Image.new("RGB", (300, 400), color=(100, 150, 200))
    tiles = TileExtractor.slice_grid_tiles(synth_image, rows=rows, cols=cols, target_tile_size=64)
    assert len(tiles) == 12
    assert all(tile.size == (64, 64) for tile in tiles)


def test_debug_preview_generation(tmp_path: Path):
    """Verifies debug preview sheet is saved properly."""
    tiles = TileExtractor.generate_procedural_tiles(rows=3, cols=3, tile_size=32)
    preview_file = tmp_path / "test_preview.png"
    TileExtractor.save_debug_preview(tiles, rows=3, cols=3, output_path=preview_file, gap=2)
    assert preview_file.exists()
    with Image.open(preview_file) as img:
        assert img.size[0] > 32 * 3
        assert img.size[1] > 32 * 3


def test_extract_tiles_pipeline_fallback(tmp_path: Path):
    """Verifies pipeline cleanly falls back to procedural generation when image is missing."""
    out_dir = tmp_path / "tiles"
    paths = extract_tiles_pipeline(
        source_image_path="non_existent_file.jpg",
        output_dir=out_dir,
        rows=4,
        cols=4,
        target_tile_size=64,
    )
    assert len(paths) == 16
    assert (out_dir / "tile_01.png").exists()
    assert (out_dir / "tile_16.png").exists()
    assert (out_dir / "debug_grid_preview.png").exists()


def test_extract_tiles_pipeline_with_real_image(tmp_path: Path):
    """Verifies extraction pipeline runs successfully on existing board image."""
    raw_board = Path("assets/raw/digimon_clean_board.jpg")
    if not raw_board.exists():
        pytest.skip("assets/raw/digimon_clean_board.jpg not found")

    out_dir = tmp_path / "real_tiles"
    paths = extract_tiles_pipeline(
        source_image_path=raw_board,
        output_dir=out_dir,
        rows=7,
        cols=6,
        target_tile_size=128,
    )
    assert len(paths) == 42
    assert (out_dir / "tile_01.png").exists()
    assert (out_dir / "tile_42.png").exists()
