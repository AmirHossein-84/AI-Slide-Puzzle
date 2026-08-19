"""Unit and integration tests for puzzle solvers (A*, IDA*, Hierarchical) on 43-slot and NxM boards."""

import pytest

from src.environment.puzzle_state import Action, PuzzleState
from src.solvers.astar_solver import AStarSolver
from src.solvers.hierarchical_solver import HierarchicalSolver
from src.solvers.idastar_solver import IDAStarSolver


def test_astar_solver_3x3():
    """Verifies A* solves random 3x3 scrambled boards."""
    solver = AStarSolver()
    goal = PuzzleState.create_goal(rows=3, cols=3, has_pocket=False)

    for seed in range(3):
        scrambled, _ = goal.scramble(steps=12, seed=seed)
        result = solver.solve(scrambled, time_limit=5.0)

        assert result.success is True
        assert result.states[-1].is_solved()

        cur = scrambled
        for a in result.actions:
            cur = cur.apply_action(a)
        assert cur.is_solved()


def test_idastar_solver_3x3():
    """Verifies IDA* finds solutions for 3x3 boards."""
    solver = IDAStarSolver()
    goal = PuzzleState.create_goal(rows=3, cols=3, has_pocket=False)
    scrambled, _ = goal.scramble(steps=10, seed=42)

    result = solver.solve(scrambled, time_limit=5.0)
    assert result.success is True
    assert result.states[-1].is_solved()


def test_hierarchical_solver_digimon_43_slot():
    """Verifies Hierarchical solver solves full 43-slot Digimon puzzle."""
    solver = HierarchicalSolver()
    goal = PuzzleState.create_goal(rows=7, cols=6, has_pocket=True)

    # Scramble 43-slot board
    scrambled, _ = goal.scramble(steps=10, seed=99)
    result = solver.solve(scrambled, time_limit=10.0)

    assert result.success is True
    assert result.states[-1].is_solved()
    assert result.duration_sec < 2.0

    # Step through all actions to verify validity
    cur = scrambled
    for a in result.actions:
        cur = cur.apply_action(a)
    assert cur.is_solved()
    assert cur.blank_pos == PuzzleState.POCKET_POS
