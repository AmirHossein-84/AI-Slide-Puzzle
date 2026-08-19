"""Unit and integration tests for PyTorch Neural Network and Neural A* Solver."""

import numpy as np
import pytest
import torch

from src.environment.puzzle_state import PuzzleState
from src.models.heuristic_net import PuzzleHeuristicNet
from src.solvers.neural_solver import NeuralAStarSolver


def test_heuristic_net_forward_shape():
    """Verifies neural model produces correct output shape and non-negative costs."""
    model = PuzzleHeuristicNet(rows=3, cols=3)
    dummy_input = torch.randn(4, 9, 3, 3)  # Batch of 4 states
    output = model(dummy_input)

    assert output.shape == (4, 1)
    assert (output >= 0).all()


def test_heuristic_net_predict_states():
    """Verifies predict_states correctly handles list of PuzzleState instances."""
    model = PuzzleHeuristicNet(rows=3, cols=3)
    goal = PuzzleState.create_goal(rows=3, cols=3)
    s1, _ = goal.scramble(steps=5, seed=1)
    s2, _ = goal.scramble(steps=10, seed=2)

    preds = model.predict_states([goal, s1, s2])
    assert isinstance(preds, np.ndarray)
    assert preds.shape == (3,)
    assert (preds >= 0).all()


def test_neural_training_step_reduces_loss():
    """Verifies that gradient descent step strictly reduces training loss."""
    model = PuzzleHeuristicNet(rows=3, cols=3)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    loss_fn = torch.nn.MSELoss()

    goal = PuzzleState.create_goal(rows=3, cols=3)
    states = [goal.scramble(steps=i + 1, seed=i)[0] for i in range(8)]
    inputs = torch.stack([torch.from_numpy(s.to_one_hot()).float() for s in states])
    targets = torch.tensor([[float(s.heuristic_cost())] for s in states])

    # Initial loss
    initial_loss = loss_fn(model(inputs), targets).item()

    # Run 15 optimization steps
    for _ in range(15):
        optimizer.zero_grad()
        loss = loss_fn(model(inputs), targets)
        loss.backward()
        optimizer.step()

    final_loss = loss_fn(model(inputs), targets).item()
    assert final_loss <= initial_loss


def test_neural_astar_solver_shallow():
    """Verifies Neural A* solver finds a solution on a shallow puzzle."""
    model = PuzzleHeuristicNet(rows=3, cols=3)
    solver = NeuralAStarSolver(model=model, rows=3, cols=3)

    goal = PuzzleState.create_goal(rows=3, cols=3)
    scrambled, _ = goal.scramble(steps=6, seed=42)

    result = solver.solve(scrambled, time_limit=5.0)
    assert result.success is True
    assert result.states[-1].is_solved()
