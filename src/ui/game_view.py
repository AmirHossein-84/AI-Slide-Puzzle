"""Interactive Pygame GUI for Sliding Tile Puzzle with AI Solvers and Animated Replay."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pygame

from src.environment.puzzle_state import ACTION_DELTAS, Action, PuzzleState
from src.solvers.astar_solver import AStarSolver
from src.solvers.base_solver import BaseSolver, SolverResult
from src.solvers.hierarchical_solver import HierarchicalSolver
from src.solvers.idastar_solver import IDAStarSolver
from src.solvers.neural_solver import NeuralAStarSolver
from src.ui.assets_loader import TileAssetLoader
from src.ui.controls import Button, Dropdown, Slider


class GameView:
    """Main Pygame application window and interactive game controller."""

    WINDOW_WIDTH: int = 1060
    WINDOW_HEIGHT: int = 740
    FPS: int = 60

    # Color Theme (Retro Green Toy Frame + Modern Dark UI)
    COLOR_BG: Tuple[int, int, int] = (20, 24, 32)
    COLOR_FRAME: Tuple[int, int, int] = (32, 140, 68)      # Digimon green toy plastic
    COLOR_FRAME_BORDER: Tuple[int, int, int] = (20, 95, 45)
    COLOR_BOARD_BG: Tuple[int, int, int] = (15, 18, 25)
    COLOR_PANEL_BG: Tuple[int, int, int] = (28, 34, 46)
    COLOR_TEXT: Tuple[int, int, int] = (240, 245, 255)
    COLOR_ACCENT: Tuple[int, int, int] = (60, 130, 240)
    COLOR_SUCCESS: Tuple[int, int, int] = (40, 180, 90)

    def __init__(self, rows: int = 7, cols: int = 6) -> None:
        pygame.init()
        pygame.display.set_caption("Digimon Sliding Tile Puzzle - AI Multi-Solver Suite")
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.rows = rows
        self.cols = cols
        self.state: PuzzleState = PuzzleState.create_goal(self.rows, self.cols)
        self.asset_loader = TileAssetLoader(assets_dir="assets/tiles")

        # Board rendering geometry
        self.board_margin_left = 40
        self.board_margin_top = 80
        # Compute tile size to fit available height
        max_board_h = self.WINDOW_HEIGHT - self.board_margin_top - 60
        max_board_w = 560
        self.tile_size = min(max_board_w // self.cols, max_board_h // self.rows)
        self.board_w = self.cols * self.tile_size
        self.board_h = self.rows * self.tile_size

        # Animation states
        self.animating_tile: Optional[int] = None
        self.anim_start_pos: Tuple[float, float] = (0, 0)
        self.anim_target_pos: Tuple[float, float] = (0, 0)
        self.anim_progress: float = 1.0  # 1.0 = finished
        self.anim_speed: float = 10.0    # units per second

        # Solvers
        self.solvers: Dict[str, BaseSolver] = {
            "Hierarchical Solver": HierarchicalSolver(),
            "A* (Linear Conflict)": AStarSolver(use_linear_conflict=True),
            "IDA* (Linear Conflict)": IDAStarSolver(use_linear_conflict=True),
            "Neural AI": NeuralAStarSolver(rows=self.rows, cols=self.cols),
        }
        self.current_solver_name: str = "Hierarchical Solver"

        # AI Playback state
        self.solution_actions: List[Action] = []
        self.playback_index: int = 0
        self.is_auto_playing: bool = False
        self.last_step_time: float = 0.0
        self.playback_speed: float = 8.0  # moves per second

        # Metrics
        self.move_count: int = 0
        self.last_solve_duration: float = 0.0
        self.last_nodes_expanded: int = 0
        self.status_message: str = "Welcome! Click tiles or press Auto-Solve."
        self.show_numbers: bool = True
        self.use_procedural: bool = False
        self.scramble_depth: int = 20

        # UI Controls
        self._init_ui_controls()

    def _init_ui_controls(self) -> None:
        """Sets up interactive buttons, dropdowns, and sliders in right panel."""
        panel_x = self.board_margin_left + self.board_w + 50
        panel_w = self.WINDOW_WIDTH - panel_x - 40
        y = 90

        # Scramble Button & Slider
        self.btn_scramble = Button(
            pygame.Rect(panel_x, y, panel_w, 38),
            "🔀 Scramble Board",
            callback=self._on_scramble_click,
            bg_color=(50, 70, 100),
            hover_color=(70, 95, 135),
        )
        y += 65

        self.slider_scramble = Slider(
            pygame.Rect(panel_x, y, panel_w, 16),
            min_val=3,
            max_val=40,
            initial_val=20,
            label="Scramble Depth",
            on_change=lambda v: setattr(self, "scramble_depth", int(v)),
        )
        y += 45

        # Solver Selection Dropdown
        self.dropdown_solver = Dropdown(
            pygame.Rect(panel_x, y, panel_w, 36),
            options=list(self.solvers.keys()),
            selected_index=0,
            on_select=self._on_solver_selected,
        )
        y += 50

        # Auto-Solve Button
        self.btn_solve = Button(
            pygame.Rect(panel_x, y, panel_w, 42),
            "🧠 Solve with AI",
            callback=self._on_solve_click,
            bg_color=(35, 125, 70),
            hover_color=(45, 155, 90),
        )
        y += 60

        # Playback Controls: [ Play/Pause ] [ Step Fwd ] [ Reset ]
        btn_w = (panel_w - 16) // 3
        self.btn_play_pause = Button(
            pygame.Rect(panel_x, y, btn_w, 36),
            "▶ Play",
            callback=self._on_play_pause_click,
            bg_color=(45, 60, 80),
        )
        self.btn_step_fwd = Button(
            pygame.Rect(panel_x + btn_w + 8, y, btn_w, 36),
            "⏭ Step",
            callback=self._on_step_fwd_click,
            bg_color=(45, 60, 80),
        )
        self.btn_reset = Button(
            pygame.Rect(panel_x + (btn_w + 8) * 2, y, btn_w, 36),
            "↺ Reset",
            callback=self._on_reset_click,
            bg_color=(80, 45, 55),
            hover_color=(110, 55, 70),
        )
        y += 65

        # Speed Slider
        self.slider_speed = Slider(
            pygame.Rect(panel_x, y, panel_w, 16),
            min_val=1,
            max_val=25,
            initial_val=8,
            label="Playback Speed",
            format_str="{:.0f}x moves/s",
            on_change=lambda v: setattr(self, "playback_speed", float(v)),
        )
        y += 45

        # Toggles: Numbers and Procedural
        self.btn_toggle_numbers = Button(
            pygame.Rect(panel_x, y, (panel_w - 10) // 2, 34),
            "🔢 Numbers: ON",
            callback=self._on_toggle_numbers,
            bg_color=(40, 50, 68),
            font_size=13,
        )
        self.btn_toggle_style = Button(
            pygame.Rect(panel_x + (panel_w - 10) // 2 + 10, y, (panel_w - 10) // 2, 34),
            "🎨 Style: Digimon",
            callback=self._on_toggle_style,
            bg_color=(40, 50, 68),
            font_size=13,
        )

    def _on_scramble_click(self) -> None:
        """Scrambles the puzzle with guaranteed solvability."""
        self.is_auto_playing = False
        self.solution_actions = []
        self.playback_index = 0
        self.state, _ = self.state.scramble(steps=self.scramble_depth)
        self.move_count = 0
        self.status_message = f"Scrambled {self.scramble_depth} steps. Ready to solve!"

    def _on_solver_selected(self, index: int, name: str) -> None:
        self.current_solver_name = name
        self.status_message = f"Selected solver: {name}"

    def _on_solve_click(self) -> None:
        """Solves the board using the selected AI solver."""
        if self.state.is_solved():
            self.status_message = "Puzzle is already solved!"
            return

        solver = self.solvers.get(self.current_solver_name, self.solvers["Hierarchical Solver"])
        self.status_message = f"Solving with {solver.name}..."
        pygame.display.flip()

        res: SolverResult = solver.solve(self.state, time_limit=15.0)
        self.last_solve_duration = res.duration_sec
        self.last_nodes_expanded = res.nodes_expanded

        if res.success:
            self.solution_actions = res.actions
            self.playback_index = 0
            self.is_auto_playing = True
            self.btn_play_pause.text = "⏸ Pause"
            self.status_message = (
                f"Solved in {res.duration_sec:.3f}s ({len(res.actions)} moves, {res.nodes_expanded:,} nodes)!"
            )
        else:
            self.status_message = f"Solver failed: {res.message}"

    def _on_play_pause_click(self) -> None:
        if not self.solution_actions:
            return
        self.is_auto_playing = not self.is_auto_playing
        self.btn_play_pause.text = "⏸ Pause" if self.is_auto_playing else "▶ Play"

    def _on_step_fwd_click(self) -> None:
        if self.playback_index < len(self.solution_actions):
            act = self.solution_actions[self.playback_index]
            self._apply_move_animated(act)
            self.playback_index += 1

    def _on_reset_click(self) -> None:
        self.is_auto_playing = False
        self.solution_actions = []
        self.playback_index = 0
        self.state = PuzzleState.create_goal(self.rows, self.cols)
        self.move_count = 0
        self.status_message = "Reset to solved state."

    def _on_toggle_numbers(self) -> None:
        self.show_numbers = not self.show_numbers
        self.btn_toggle_numbers.text = f"🔢 Numbers: {'ON' if self.show_numbers else 'OFF'}"

    def _on_toggle_style(self) -> None:
        self.use_procedural = not self.use_procedural
        self.btn_toggle_style.text = f"🎨 Style: {'Retro' if self.use_procedural else 'Digimon'}"

    def _apply_move_animated(self, action: Action) -> None:
        """Applies move to game state."""
        if self.state.is_valid_action(action):
            self.state = self.state.apply_action(action)
            self.move_count += 1

    def _handle_board_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handles human mouse clicks to slide adjacent tiles."""
        mx, my = mouse_pos
        bx = mx - self.board_margin_left
        by = my - self.board_margin_top

        if 0 <= bx < self.board_w and 0 <= by < self.board_h:
            clicked_c = bx // self.tile_size
            clicked_r = by // self.tile_size
            br, bc = self.state.blank_pos

            # Find action moving blank to clicked position
            if (clicked_r, clicked_c) == (br - 1, bc):
                self._apply_move_animated(Action.UP)
            elif (clicked_r, clicked_c) == (br + 1, bc):
                self._apply_move_animated(Action.DOWN)
            elif (clicked_r, clicked_c) == (br, bc - 1):
                self._apply_move_animated(Action.LEFT)
            elif (clicked_r, clicked_c) == (br, bc + 1):
                self._apply_move_animated(Action.RIGHT)

    def run(self) -> None:
        """Main application loop."""
        running = True

        while running:
            dt = self.clock.tick(self.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle dropdown popup clicks first
                if self.dropdown_solver.handle_event(event):
                    continue

                # Control events
                self.btn_scramble.handle_event(event)
                self.slider_scramble.handle_event(event)
                self.btn_solve.handle_event(event)
                self.btn_play_pause.handle_event(event)
                self.btn_step_fwd.handle_event(event)
                self.btn_reset.handle_event(event)
                self.slider_speed.handle_event(event)
                self.btn_toggle_numbers.handle_event(event)
                self.btn_toggle_style.handle_event(event)

                # Board mouse click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_board_click(event.pos)

                # Keyboard controls (Arrow keys)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self._apply_move_animated(Action.DOWN)
                    elif event.key == pygame.K_DOWN:
                        self._apply_move_animated(Action.UP)
                    elif event.key == pygame.K_LEFT:
                        self._apply_move_animated(Action.RIGHT)
                    elif event.key == pygame.K_RIGHT:
                        self._apply_move_animated(Action.LEFT)

            # Automated playback execution
            if self.is_auto_playing and self.playback_index < len(self.solution_actions):
                now = time.perf_counter()
                step_interval = 1.0 / max(1.0, self.playback_speed)
                if now - self.last_step_time >= step_interval:
                    act = self.solution_actions[self.playback_index]
                    self._apply_move_animated(act)
                    self.playback_index += 1
                    self.last_step_time = now

                    if self.playback_index >= len(self.solution_actions):
                        self.is_auto_playing = False
                        self.btn_play_pause.text = "▶ Play"

            # Render frame
            self._render()

        pygame.quit()

    def _render(self) -> None:
        """Renders all GUI surfaces and controls."""
        self.screen.fill(self.COLOR_BG)

        # 1. Header Bar
        font_title = pygame.font.SysFont("arial", 22, bold=True)
        title_surf = font_title.render("DIGIMON SLIDING TILE PUZZLE (6x7)", True, (255, 255, 255))
        self.screen.blit(title_surf, (self.board_margin_left, 24))

        # Status text
        font_status = pygame.font.SysFont("arial", 14)
        status_col = self.COLOR_SUCCESS if self.state.is_solved() else (180, 195, 215)
        status_surf = font_status.render(self.status_message, True, status_col)
        self.screen.blit(status_surf, (self.board_margin_left, 52))

        # 2. Plastic Green Outer Frame
        frame_pad = 16
        frame_rect = pygame.Rect(
            self.board_margin_left - frame_pad,
            self.board_margin_top - frame_pad,
            self.board_w + frame_pad * 2,
            self.board_h + frame_pad * 2,
        )
        pygame.draw.rect(self.screen, self.COLOR_FRAME, frame_rect, border_radius=14)
        pygame.draw.rect(self.screen, self.COLOR_FRAME_BORDER, frame_rect, width=3, border_radius=14)

        # 3. Inner Board Background
        board_rect = pygame.Rect(self.board_margin_left, self.board_margin_top, self.board_w, self.board_h)
        pygame.draw.rect(self.screen, self.COLOR_BOARD_BG, board_rect)

        # 4. Render Tiles
        for r in range(self.rows):
            for c in range(self.cols):
                tile_val = int(self.state.board[r, c])
                x = self.board_margin_left + c * self.tile_size
                y = self.board_margin_top + r * self.tile_size

                if tile_val != 0:
                    tile_surf = self.asset_loader.get_tile_surface(
                        tile_num=tile_val,
                        tile_size=self.tile_size,
                        show_numbers=self.show_numbers,
                        use_procedural=self.use_procedural,
                    )
                    self.screen.blit(tile_surf, (x, y))
                else:
                    # Blank tile slot pocket
                    pygame.draw.rect(self.screen, (10, 12, 18), (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(self.screen, (25, 30, 42), (x, y, self.tile_size, self.tile_size), width=1)

        # 5. Right Control Panel Background Card
        panel_x = self.board_margin_left + self.board_w + 40
        panel_rect = pygame.Rect(panel_x - 10, 70, self.WINDOW_WIDTH - panel_x - 20, 630)
        pygame.draw.rect(self.screen, self.COLOR_PANEL_BG, panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (45, 55, 75), panel_rect, width=1, border_radius=12)

        # 6. Telemetry & Stats in Control Panel
        font_stat_title = pygame.font.SysFont("arial", 15, bold=True)
        stat_title = font_stat_title.render("TELEMETRY & CONTROLS", True, (130, 160, 205))
        self.screen.blit(stat_title, (panel_x + 6, 85))

        # Render Controls
        self.btn_scramble.render(self.screen)
        self.slider_scramble.render(self.screen)
        self.dropdown_solver.render(self.screen)
        self.btn_solve.render(self.screen)
        self.btn_play_pause.render(self.screen)
        self.btn_step_fwd.render(self.screen)
        self.btn_reset.render(self.screen)
        self.slider_speed.render(self.screen)
        self.btn_toggle_numbers.render(self.screen)
        self.btn_toggle_style.render(self.screen)

        # Metrics Box
        metrics_y = 560
        pygame.draw.rect(self.screen, (20, 25, 36), (panel_x, metrics_y, panel_rect.width - 20, 120), border_radius=8)
        pygame.draw.rect(self.screen, (40, 50, 70), (panel_x, metrics_y, panel_rect.width - 20, 120), width=1, border_radius=8)

        font_metrics = pygame.font.SysFont("arial", 13)
        m_lines = [
            f"• Moves Made      : {self.move_count}",
            f"• Manhattan Dist  : {self.state.manhattan_distance()}",
            f"• Linear Conflict : {self.state.linear_conflicts()}",
            f"• AI Solve Time   : {self.last_solve_duration:.4f}s",
            f"• Nodes Expanded  : {self.last_nodes_expanded:,}",
        ]
        for idx, line in enumerate(m_lines):
            line_surf = font_metrics.render(line, True, (200, 215, 235))
            self.screen.blit(line_surf, (panel_x + 12, metrics_y + 8 + idx * 22))

        # Overlay dropdown last so popup renders on top
        self.dropdown_solver.render_overlay(self.screen)

        pygame.display.flip()
