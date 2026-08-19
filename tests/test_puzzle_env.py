"""Unit tests for 43-slot Gymnasium puzzle environment."""

import gymnasium as gym
import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from src.environment.puzzle_env import PuzzleEnv
from src.environment.puzzle_state import Action, PuzzleState


def test_gym_environment_conformance():
    """Verifies Gymnasium standard API conformance for 43-slot environment."""
    env = PuzzleEnv(rows=7, cols=6, has_pocket=True, max_steps=100)
    check_env(env.unwrapped)
    env.close()


def test_env_reset_and_step_43_slot():
    """Verifies environment reset and step dynamics."""
    env = PuzzleEnv(rows=7, cols=6, has_pocket=True, max_steps=50)
    obs, info = env.reset(seed=42, options={"scramble_steps": 5})

    assert isinstance(obs, np.ndarray)
    assert obs.shape == (8, 6)
    assert "scramble_steps" in info

    # Take step
    obs, reward, terminated, truncated, info = env.step(Action.RIGHT.value)
    assert isinstance(reward, (int, float))
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert "steps_taken" in info
    env.close()


def test_env_solve_reward_termination():
    """Verifies solve reward and termination when puzzle is solved into left side pocket."""
    env = PuzzleEnv(rows=7, cols=6, has_pocket=True)
    # Start 1 move away from solved (blank at 6, 0)
    goal = PuzzleState.create_goal(rows=7, cols=6, has_pocket=True)
    near_goal = goal.apply_action(Action.RIGHT)
    env.reset(options={"custom_state": near_goal})

    # Action LEFT moves blank back into side pocket (7, 0) and solves puzzle!
    obs, reward, terminated, truncated, info = env.step(Action.LEFT.value)
    assert terminated is True
    assert reward >= 100.0
    assert info.get("is_solved") is True
    env.close()
