"""Unit tests for FastAPI REST and WebSocket endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.server.app import app

client = TestClient(app)


def test_get_state_endpoint():
    """Verifies GET /api/state returns 43-slot state."""
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == 7
    assert data["cols"] == 6
    assert data["has_pocket"] is True
    assert len(data["board"]) == 43
    assert data["is_solved"] is True


def test_scramble_and_reset_endpoints():
    """Verifies POST /api/scramble and POST /api/reset."""
    scramble_res = client.post("/api/scramble", json={"steps": 5, "seed": 42})
    assert scramble_res.status_code == 200
    scrambled_data = scramble_res.json()
    assert scrambled_data["is_solvable"] is True

    reset_res = client.post("/api/reset")
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["is_solved"] is True


def test_solve_endpoint():
    """Verifies POST /api/solve solves a scrambled board."""
    client.post("/api/scramble", json={"steps": 6, "seed": 10})
    solve_res = client.post("/api/solve", json={"solver": "Hierarchical Subgoal Solver"})
    assert solve_res.status_code == 200
    solve_data = solve_res.json()
    assert solve_data["success"] is True
    assert len(solve_data["actions"]) > 0
    assert solve_data["duration_ms"] > 0
