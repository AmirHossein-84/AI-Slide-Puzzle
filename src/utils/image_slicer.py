"""Tile image extraction and procedural asset generation module.

Implements deep module design: callers interact with a simple interface
while orientation, cropping, grid calculation, tile slicing, and procedural
fallbacks are encapsulated within.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageOps


class TileExtractor:
    """Encapsulates image slicing, grid extraction, and procedural tile generation."""

    DEFAULT_TILE_SIZE: int = 128

    @staticmethod
    def crop_grid_region(
        image: Image.Image,
        normalized_box: Tuple[float, float, float, float] = (0.285, 0.235, 0.805, 0.845),
    ) -> Image.Image:
        """Crops the inner puzzle tile grid from the whole board image using normalized coordinates.
        
        Args:
            image: Source PIL Image.
            normalized_box: (left, top, right, bottom) ratios between 0.0 and 1.0.

        Returns:
            Cropped grid PIL Image.
        """
        width, height = image.size
        left = int(normalized_box[0] * width)
        top = int(normalized_box[1] * height)
        right = int(normalized_box[2] * width)
        bottom = int(normalized_box[3] * height)
        return image.crop((left, top, right, bottom))

    @staticmethod
    def slice_grid_tiles(
        grid_image: Image.Image,
        rows: int = 7,
        cols: int = 6,
        target_tile_size: int = DEFAULT_TILE_SIZE,
    ) -> List[Image.Image]:
        """Subdivides a cropped grid image into individual tile images.
        
        Args:
            grid_image: PIL Image of the cropped grid area.
            rows: Number of grid rows.
            cols: Number of grid columns.
            target_tile_size: Target square pixel dimension for each tile.

        Returns:
            List of PIL Image objects in row-major order (Tile 1 to rows*cols).
        """
        grid_width, grid_height = grid_image.size
        tile_width = grid_width / cols
        tile_height = grid_height / rows

        tiles: List[Image.Image] = []
        for r in range(rows):
            for c in range(cols):
                box = (
                    int(c * tile_width),
                    int(r * tile_height),
                    int((c + 1) * tile_width),
                    int((r + 1) * tile_height),
                )
                tile_crop = grid_image.crop(box)
                resized_tile = tile_crop.resize(
                    (target_tile_size, target_tile_size), Image.Resampling.LANCZOS
                )
                tiles.append(resized_tile)

        return tiles

    @staticmethod
    def generate_procedural_tiles(
        rows: int,
        cols: int,
        tile_size: int = DEFAULT_TILE_SIZE,
    ) -> List[Image.Image]:
        """Generates clean procedural retro numbered tiles for any NxM grid size.
        
        Args:
            rows: Number of grid rows.
            cols: Number of grid columns.
            tile_size: Square dimension in pixels for each tile.

        Returns:
            List of PIL Image objects in row-major order.
        """
        total_tiles = rows * cols
        tiles: List[Image.Image] = []

        # Font configuration
        font_size = int(tile_size * 0.4)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        for tile_num in range(1, total_tiles + 1):
            tile = Image.new("RGB", (tile_size, tile_size), color=(50, 115, 220))
            draw = ImageDraw.Draw(tile)

            # Bevel 3D effect border
            border_width = max(2, tile_size // 24)
            # Light top/left border
            draw.line([(0, 0), (tile_size - 1, 0)], fill=(120, 180, 255), width=border_width)
            draw.line([(0, 0), (0, tile_size - 1)], fill=(120, 180, 255), width=border_width)
            # Dark bottom/right border
            draw.line(
                [(0, tile_size - border_width), (tile_size - 1, tile_size - border_width)],
                fill=(20, 60, 140),
                width=border_width,
            )
            draw.line(
                [(tile_size - border_width, 0), (tile_size - border_width, tile_size - 1)],
                fill=(20, 60, 140),
                width=border_width,
            )

            # Center number text
            text = str(tile_num)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            text_x = (tile_size - text_w) // 2
            text_y = (tile_size - text_h) // 2 - (bbox[1] // 2)

            # Text shadow
            draw.text((text_x + 2, text_y + 2), text, fill=(10, 30, 80), font=font)
            # Text foreground
            draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

            tiles.append(tile)

        return tiles

    @classmethod
    def save_debug_preview(
        cls,
        tiles: List[Image.Image],
        rows: int,
        cols: int,
        output_path: Path,
        gap: int = 4,
    ) -> None:
        """Assembles sliced tiles into a composite debug sheet with grid gaps.
        
        Args:
            tiles: List of tile PIL Images.
            rows: Number of grid rows.
            cols: Number of grid columns.
            output_path: File path to save preview image.
            gap: Pixel spacing between tiles.
        """
        if not tiles:
            return

        tile_w, tile_h = tiles[0].size
        sheet_w = cols * tile_w + (cols + 1) * gap
        sheet_h = rows * tile_h + (rows + 1) * gap

        preview_image = Image.new("RGB", (sheet_w, sheet_h), color=(30, 35, 45))

        for idx, tile in enumerate(tiles):
            r = idx // cols
            c = idx % cols
            x = gap + c * (tile_w + gap)
            y = gap + r * (tile_h + gap)
            preview_image.paste(tile, (x, y))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        preview_image.save(output_path, quality=95)


def extract_tiles_pipeline(
    source_image_path: Optional[Path | str] = None,
    output_dir: Path | str = "assets/tiles",
    rows: int = 7,
    cols: int = 6,
    target_tile_size: int = 128,
    use_procedural: bool = False,
    grid_box: Optional[Tuple[float, float, float, float]] = None,
) -> List[Path]:
    """Main deep interface for asset extraction and tile generation.

    Args:
        source_image_path: Optional path to raw source board image.
        output_dir: Destination folder for exported .png tile sprites.
        rows: Grid row count (default 7).
        cols: Grid column count (default 6).
        target_tile_size: Square tile resolution (default 128px).
        use_procedural: If True, generates clean procedural numbered tiles.
        grid_box: Optional custom normalized bounding box (left, top, right, bottom).

    Returns:
        List of Paths to saved tile images in row-major order (`tile_01.png` ...).
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tiles: List[Image.Image] = []

    if not use_procedural and source_image_path:
        src_path = Path(source_image_path)
        if src_path.exists():
            with Image.open(src_path) as raw_img:
                oriented_img = ImageOps.exif_transpose(raw_img).convert("RGB")
                box = grid_box or (0.285, 0.235, 0.805, 0.845)
                grid_crop = TileExtractor.crop_grid_region(oriented_img, box)
                tiles = TileExtractor.slice_grid_tiles(
                    grid_crop, rows=rows, cols=cols, target_tile_size=target_tile_size
                )

    if not tiles:
        # Fallback to procedural tiles
        tiles = TileExtractor.generate_procedural_tiles(
            rows=rows, cols=cols, tile_size=target_tile_size
        )

    # Save individual tile PNGs
    saved_paths: List[Path] = []
    for idx, tile in enumerate(tiles, start=1):
        tile_filename = f"tile_{idx:02d}.png"
        tile_path = out_dir / tile_filename
        tile.save(tile_path, format="PNG")
        saved_paths.append(tile_path)

    # Save debug sheet for verification
    debug_sheet_path = out_dir / "debug_grid_preview.png"
    TileExtractor.save_debug_preview(tiles, rows, cols, debug_sheet_path)

    return saved_paths
