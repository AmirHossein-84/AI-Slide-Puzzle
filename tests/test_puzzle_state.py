"""Unit tests for 43-slot and NxM puzzle state logic, left side pocket, and heuristics."""

import numpy as np
import pytest

from src.environment.puzzle_state import Action, PuzzleState


def test_goal_state_creation_43_slot():
    """Verifies 43-slot Digimon goal state: 42 tiles (1..42) on grid + blank 0 at (7, 0)."""
    state = PuzzleState.create_goal(rows=7, cols=6, has_pocket=True)
    assert state.rows == 7
    assert state.cols == 6
    assert state.has_pocket is True
    assert state.is_solved()
    assert state.blank_pos == (7, 0)
    assert state.board[7, 0] == 0
    assert state.board[0, 0] == 1
    assert state.board[6, 5] == 42
    assert state.board[7, 1] == -1


def test_left_pocket_movement_rules():
    """Verifies blank enters side pocket from (6, 0) via LEFT, and exits via RIGHT."""
    goal = PuzzleState.create_goal(rows=7, cols=6, has_pocket=True)
    # Blank in pocket (7, 0) on the LEFT of (6, 0): can ONLY move RIGHT to (6, 0)
    valid_actions = goal.get_valid_actions()
    assert valid_actions == [Action.RIGHT]

    # Move RIGHT -> blank is now at (6, 0), tile 37 is in side pocket (7, 0)
    moved_right = goal.apply_action(Action.RIGHT)
    assert moved_right.blank_pos == (6, 0)
    assert moved_right.board[7, 0] == 37
    assert moved_right.board[6, 0] == 0

    # From (6, 0), blank can move UP, RIGHT, or LEFT (back into pocket)
    assert Action.UP in moved_right.get_valid_actions()
    assert Action.RIGHT in moved_right.get_valid_actions()
    assert Action.LEFT in moved_right.get_valid_actions()
    assert Action.DOWN not in moved_right.get_valid_actions()

    # Move LEFT -> restores goal state in side pocket
    restored = moved_right.apply_action(Action.LEFT)
    assert restored.is_solved()
    assert restored.blank_pos == (7, 0)


def test_solvability_parity_43_slot():
    """Verifies solvability invariant on 43-slot board."""
    goal = PuzzleState.create_goal(rows=7, cols=6, has_pocket=True)
    assert goal.is_solvable()

    # Unsolvable: swap tile 1 and tile 2
    unsolvable_board = goal.board.copy()
    unsolvable_board[0, 0], unsolvable_board[0, 1] = 2, 1
    unsolvable_state = PuzzleState(unsolvable_board, rows=7, cols=6, has_pocket=True)
    assert not unsolvable_state.is_solvable()


def test_scramble_guarantees_solvability_43_slot():
    """Verifies that random scrambles on 43-slot board are 100% solvable."""
    goal = PuzzleState.create_goal(rows=7, cols=6, has_pocket=True)
    for seed in range(10):
        scrambled, actions = goal.scramble(steps=30, seed=seed)
        assert scrambled.is_solvable()
        assert len(actions) == 30
