"""Gymnasium environment for 43-slot (and NxM) sliding tile puzzles."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Union
import gymnasium as gym
from gymnasium import spaces
import numpy as np

from src.environment.puzzle_state import Action, PuzzleState


class PuzzleEnv(gym.Env):
    """Standard Gymnasium environment for sliding tile puzzles."""

    metadata = {"render_modes": ["ansi", "rgb_array"], "render_fps": 30}

    def __init__(
        self,
        rows: int = 7,
        cols: int = 6,
        has_pocket: bool = True,
        max_steps: int = 300,
        default_scramble_steps: int = 30,
        render_mode: Optional[str] = None,
        use_reward_shaping: bool = False,
    ) -> None:
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.has_pocket = has_pocket and (rows == 7 and cols == 6)
        self.max_steps = max_steps
        self.default_scramble_steps = default_scramble_steps
        self.render_mode = render_mode
        self.use_reward_shaping = use_reward_shaping

        # Action Space: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT
        self.action_space = spaces.Discrete(4)

        # Observation Space
        if self.has_pocket:
            self.observation_space = spaces.Box(
                low=-1,
                high=42,
                shape=(8, 6),
                dtype=np.int32,
            )
        else:
            self.observation_space = spaces.Box(
                low=0,
                high=rows * cols - 1,
                shape=(self.rows, self.cols),
                dtype=np.int32,
            )

        self._state: PuzzleState = PuzzleState.create_goal(self.rows, self.cols, has_pocket=self.has_pocket)
        self._steps_taken: int = 0
        self._prev_potential: float = 0.0

    @property
    def current_state(self) -> PuzzleState:
        return self._state

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        opts = options or {}
        self._steps_taken = 0

        if "custom_state" in opts:
            self._state = opts["custom_state"]
            scramble_count = 0
        else:
            scramble_count = opts.get("scramble_steps", self.default_scramble_steps)
            goal = PuzzleState.create_goal(self.rows, self.cols, has_pocket=self.has_pocket)
            if scramble_count > 0:
                self._state, _ = goal.scramble(steps=scramble_count, seed=seed)
            else:
                self._state = goal

        self._prev_potential = -float(self._state.manhattan_distance())

        info = {
            "is_solved": self._state.is_solved(),
            "manhattan_distance": self._state.manhattan_distance(),
            "scramble_steps": scramble_count,
        }
        return self._state.board.copy(), info

    def step(self, action_idx: Union[int, Action]) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        action = Action(action_idx)
        self._steps_taken += 1

        is_valid = self._state.is_valid_action(action)
        if is_valid:
            self._state = self._state.apply_action(action)

        is_solved = self._state.is_solved()
        terminated = is_solved
        truncated = self._steps_taken >= self.max_steps and not terminated

        if is_solved:
            reward = 100.0
        else:
            reward = -1.0
            if not is_valid:
                reward -= 2.0
            if self.use_reward_shaping:
                current_potential = -float(self._state.manhattan_distance())
                reward += current_potential - self._prev_potential
                self._prev_potential = current_potential

        info = {
            "is_solved": is_solved,
            "is_valid_move": is_valid,
            "manhattan_distance": self._state.manhattan_distance(),
            "steps_taken": self._steps_taken,
        }

        return self._state.board.copy(), reward, terminated, truncated, info

    def render(self) -> Optional[Union[str, np.ndarray]]:
        if self.render_mode == "ansi" or self.render_mode is None:
            lines = []
            for r in range(self._state.board.shape[0]):
                row_vals = [f"{val:2d}" if val >= 0 else "  " for val in self._state.board[r]]
                lines.append(" ".join(row_vals))
            return "\n".join(lines)
        return None
