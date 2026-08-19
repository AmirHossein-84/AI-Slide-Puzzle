"""Pygame UI widgets: Buttons, Dropdowns, Sliders, and Toggles."""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple
import pygame


class UIElement:
    """Base class for interactive UI elements."""

    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.is_hovered: bool = False
        self.is_active: bool = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def render(self, surface: pygame.Surface) -> None:
        pass


class Button(UIElement):
    """Clickable button with hover and active states."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Optional[Callable[[], None]] = None,
        bg_color: Tuple[int, int, int] = (50, 65, 85),
        hover_color: Tuple[int, int, int] = (70, 95, 125),
        active_color: Tuple[int, int, int] = (35, 130, 80),
        text_color: Tuple[int, int, int] = (240, 245, 255),
        font_size: int = 16,
    ) -> None:
        super().__init__(rect)
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("arial", font_size, bold=True)
        self.is_pressed: bool = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_active:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
        return False

    def render(self, surface: pygame.Surface) -> None:
        color = self.hover_color if self.is_hovered else self.bg_color
        if not self.is_active:
            color = (35, 40, 50)

        # Draw rounded card background
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        border_col = (100, 130, 170) if self.is_hovered and self.is_active else (30, 35, 45)
        pygame.draw.rect(surface, border_col, self.rect, width=1, border_radius=6)

        # Text rendering
        txt_col = self.text_color if self.is_active else (100, 110, 125)
        text_surf = self.font.render(self.text, True, txt_col)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Slider(UIElement):
    """Horizontal value slider."""

    def __init__(
        self,
        rect: pygame.Rect,
        min_val: float,
        max_val: float,
        initial_val: float,
        label: str = "",
        format_str: str = "{:.0f}",
        on_change: Optional[Callable[[float], None]] = None,
    ) -> None:
        super().__init__(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.format_str = format_str
        self.on_change = on_change
        self.is_dragging: bool = False
        self.font = pygame.font.SysFont("arial", 13, bold=True)

    @property
    def handle_x(self) -> int:
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_active:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(10, 16).collidepoint(event.pos):
                self.is_dragging = True
                self._update_value_from_pos(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self._update_value_from_pos(event.pos[0])
            return True
        return False

    def _update_value_from_pos(self, mouse_x: int) -> None:
        clamped_x = max(self.rect.x, min(mouse_x, self.rect.right))
        ratio = (clamped_x - self.rect.x) / self.rect.width
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        if self.on_change:
            self.on_change(self.value)

    def render(self, surface: pygame.Surface) -> None:
        # Label & value display
        val_text = f"{self.label}: {self.format_str.format(self.value)}"
        label_surf = self.font.render(val_text, True, (200, 210, 230))
        surface.blit(label_surf, (self.rect.x, self.rect.y - 18))

        # Track line
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.width, 6)
        pygame.draw.rect(surface, (40, 48, 62), track_rect, border_radius=3)

        # Filled portion
        fill_width = self.handle_x - self.rect.x
        if fill_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, fill_width, 6)
            pygame.draw.rect(surface, (60, 130, 240), filled_rect, border_radius=3)

        # Draggable knob handle
        knob_color = (255, 255, 255) if self.is_dragging else (210, 225, 245)
        pygame.draw.circle(surface, knob_color, (self.handle_x, self.rect.centery), 8)
        pygame.draw.circle(surface, (30, 40, 55), (self.handle_x, self.rect.centery), 8, width=2)


class Dropdown(UIElement):
    """Select dropdown with popup list."""

    def __init__(
        self,
        rect: pygame.Rect,
        options: List[str],
        selected_index: int = 0,
        on_select: Optional[Callable[[int, str], None]] = None,
    ) -> None:
        super().__init__(rect)
        self.options = options
        self.selected_index = selected_index
        self.on_select = on_select
        self.is_open: bool = False
        self.font = pygame.font.SysFont("arial", 14, bold=True)

    @property
    def selected_text(self) -> str:
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return ""

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_active:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click main box
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

            # Click inside open options
            if self.is_open:
                opt_height = self.rect.height
                for i in range(len(self.options)):
                    opt_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.bottom + i * opt_height,
                        self.rect.width,
                        opt_height,
                    )
                    if opt_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.is_open = False
                        if self.on_select:
                            self.on_select(i, self.options[i])
                        return True

                # Clicked outside
                self.is_open = False
                return True
        return False

    def render(self, surface: pygame.Surface) -> None:
        # Main box
        pygame.draw.rect(surface, (45, 55, 75), self.rect, border_radius=6)
        pygame.draw.rect(surface, (80, 100, 130), self.rect, width=1, border_radius=6)

        text_surf = self.font.render(self.selected_text, True, (240, 245, 255))
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

        # Arrow indicator
        arrow = "▲" if self.is_open else "▼"
        arrow_surf = self.font.render(arrow, True, (160, 180, 210))
        surface.blit(arrow_surf, (self.rect.right - 22, self.rect.y + (self.rect.height - arrow_surf.get_height()) // 2))

    def render_overlay(self, surface: pygame.Surface) -> None:
        """Renders popup menu on top of other elements."""
        if not self.is_open:
            return

        opt_height = self.rect.height
        total_h = len(self.options) * opt_height
        menu_rect = pygame.Rect(self.rect.x, self.rect.bottom + 2, self.rect.width, total_h)
        pygame.draw.rect(surface, (35, 45, 60), menu_rect, border_radius=6)
        pygame.draw.rect(surface, (100, 130, 170), menu_rect, width=1, border_radius=6)

        mouse_pos = pygame.mouse.get_pos()
        for i, opt in enumerate(self.options):
            r = pygame.Rect(self.rect.x, self.rect.bottom + 2 + i * opt_height, self.rect.width, opt_height)
            if r.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (55, 75, 105), r)
            if i == self.selected_index:
                pygame.draw.rect(surface, (60, 120, 210), (r.x + 2, r.y + 2, 4, r.height - 4), border_radius=2)

            opt_surf = self.font.render(opt, True, (255, 255, 255))
            surface.blit(opt_surf, (r.x + 12, r.y + (opt_height - opt_surf.get_height()) // 2))
