"""Tile asset loader and procedural surface renderer for Pygame."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple
import pygame


class TileAssetLoader:
    """Loads and caches Pygame tile surfaces for both Digimon sprites and procedural tiles."""

    def __init__(
        self,
        assets_dir: Path | str = "assets/tiles",
        tile_size: int = 96,
    ) -> None:
        self.assets_dir = Path(assets_dir)
        self.tile_size = tile_size
        self._sprite_cache: Dict[int, pygame.Surface] = {}
        self._font: Optional[pygame.font.Font] = None

    def _get_font(self, size: int) -> pygame.font.Font:
        if not pygame.font.get_init():
            pygame.font.init()
        return pygame.font.SysFont("arial", size, bold=True)

    def get_tile_surface(
        self,
        tile_num: int,
        tile_size: int,
        show_numbers: bool = True,
        use_procedural: bool = False,
    ) -> pygame.Surface:
        """Retrieves or creates a Pygame surface for the given tile number.

        Args:
            tile_num: Value of the tile (1 .. total_tiles).
            tile_size: Target square pixel dimension.
            show_numbers: Whether to render a number badge.
            use_procedural: Force procedural retro style instead of artwork.

        Returns:
            Rendered pygame.Surface.
        """
        cache_key = (tile_num, tile_size, show_numbers, use_procedural)
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]

        surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        tile_file = self.assets_dir / f"tile_{tile_num:02d}.png"

        # Attempt to load sprite image
        loaded = False
        if not use_procedural and tile_file.exists():
            try:
                raw_img = pygame.image.load(str(tile_file)).convert_alpha()
                surface = pygame.transform.smoothscale(raw_img, (tile_size, tile_size))
                loaded = True
            except Exception:
                loaded = False

        if not loaded:
            # Render procedural retro bevel tile
            surface = self._render_procedural_surface(tile_num, tile_size)

        # Optional number badge
        if show_numbers:
            self._render_number_badge(surface, tile_num, tile_size)

        # Border outline
        pygame.draw.rect(surface, (20, 25, 35), surface.get_rect(), width=max(1, tile_size // 32))

        self._sprite_cache[cache_key] = surface
        return surface

    def _render_procedural_surface(self, tile_num: int, size: int) -> pygame.Surface:
        """Draws a clean retro shaded tile."""
        surf = pygame.Surface((size, size))
        # Blue gradient base
        surf.fill((45, 110, 215))

        # Light bevel (top and left)
        b_width = max(2, size // 20)
        pygame.draw.rect(surf, (110, 175, 255), (0, 0, size, b_width))
        pygame.draw.rect(surf, (110, 175, 255), (0, 0, b_width, size))

        # Dark bevel (bottom and right)
        pygame.draw.rect(surf, (20, 55, 130), (0, size - b_width, size, b_width))
        pygame.draw.rect(surf, (20, 55, 130), (size - b_width, 0, b_width, size))

        # Large center number
        font = self._get_font(int(size * 0.42))
        text_str = str(tile_num)
        # Shadow
        shadow_surf = font.render(text_str, True, (15, 35, 80))
        shadow_rect = shadow_surf.get_rect(center=(size // 2 + 2, size // 2 + 2))
        surf.blit(shadow_surf, shadow_rect)
        # Foreground
        text_surf = font.render(text_str, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(size // 2, size // 2))
        surf.blit(text_surf, text_rect)

        return surf

    def _render_number_badge(self, surface: pygame.Surface, tile_num: int, size: int) -> None:
        """Draws a neat translucent circular number badge in the top-left corner."""
        badge_radius = max(9, size // 7)
        badge_center = (badge_radius + 4, badge_radius + 4)

        # Translucent badge background
        badge_surf = pygame.Surface((badge_radius * 2, badge_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(badge_surf, (15, 20, 30, 210), (badge_radius, badge_radius), badge_radius)
        pygame.draw.circle(badge_surf, (255, 255, 255, 180), (badge_radius, badge_radius), badge_radius, width=1)
        surface.blit(badge_surf, (badge_center[0] - badge_radius, badge_center[1] - badge_radius))

        # Number text
        font = self._get_font(int(badge_radius * 1.25))
        text = font.render(str(tile_num), True, (255, 255, 255))
        text_rect = text.get_rect(center=badge_center)
        surface.blit(text, text_rect)
