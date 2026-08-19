"""Unit tests for UI components and Pygame game view."""

import os
import pygame
import pytest

# Ensure headless Pygame testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

from src.environment.puzzle_state import Action, PuzzleState
from src.ui.assets_loader import TileAssetLoader
from src.ui.controls import Button, Dropdown, Slider
from src.ui.game_view import GameView


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_asset_loader_procedural_and_sprites():
    """Verifies TileAssetLoader generates valid Pygame surfaces."""
    loader = TileAssetLoader(assets_dir="assets/tiles")
    # Procedural tile
    surf_proc = loader.get_tile_surface(tile_num=1, tile_size=64, use_procedural=True)
    assert isinstance(surf_proc, pygame.Surface)
    assert surf_proc.get_size() == (64, 64)

    # Standard tile (Digimon sprite or fallback)
    surf_sprite = loader.get_tile_surface(tile_num=42, tile_size=96, show_numbers=True)
    assert isinstance(surf_sprite, pygame.Surface)
    assert surf_sprite.get_size() == (96, 96)


def test_ui_widgets_render():
    """Verifies UI Button, Slider, Dropdown render cleanly onto canvas."""
    canvas = pygame.Surface((400, 400))

    btn = Button(pygame.Rect(10, 10, 100, 30), "Test Button")
    btn.render(canvas)

    slider = Slider(pygame.Rect(10, 50, 100, 16), min_val=1, max_val=10, initial_val=5, label="Speed")
    slider.render(canvas)

    dropdown = Dropdown(pygame.Rect(10, 80, 120, 30), options=["Option A", "Option B"])
    dropdown.render(canvas)
    dropdown.is_open = True
    dropdown.render_overlay(canvas)


def test_game_view_initialization():
    """Verifies GameView initializes full board and solvers without error."""
    view = GameView(rows=7, cols=6)
    assert view.rows == 7
    assert view.cols == 6
    assert len(view.solvers) >= 4
    assert view.state.is_solved()

    # Trigger a render cycle to verify drawing passes
    view._render()
