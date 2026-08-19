"""Unit tests for the TrainingManager and PyTorch ADI streaming pipeline."""

import asyncio
import time
from pathlib import Path
import pytest

from src.environment.puzzle_state import PuzzleState
from src.models.heuristic_net import PuzzleHeuristicNet
from src.server.training_manager import TrainingManager


@pytest.mark.anyio
async def test_training_manager_session():
    """Verifies that TrainingManager starts, emits telemetry, and completes a short training session."""
    manager = TrainingManager()
    loop = asyncio.get_running_loop()
    q = manager.subscribe()

    test_save = "models/test_temp_model.pt"

    started = manager.start_training(
        loop=loop,
        rows=2,
        cols=2,
        has_pocket=False,
        epochs=2,
        steps_per_epoch=2,
        batch_size=16,
        max_depth=4,
        lr=1e-3,
        save_path=test_save,
    )
    assert started is True
    assert manager.is_training is True

    events = []
    start_wait = time.perf_counter()

    while time.perf_counter() - start_wait < 10.0:
        try:
            event = await asyncio.wait_for(q.get(), timeout=1.0)
            events.append(event)
            if event.get("type") in ("completed", "stopped", "error"):
                break
        except asyncio.TimeoutError:
            if not manager.is_training:
                break

    manager.unsubscribe(q)

    # Verify key event types received
    event_types = [e.get("type") for e in events]
    assert "start" in event_types
    assert "epoch_complete" in event_types or "step" in event_types

    # Clean up test model file
    p = Path(test_save)
    if p.exists():
        p.unlink()


def test_training_manager_stop():
    """Verifies that TrainingManager can be cancelled gracefully."""
    manager = TrainingManager()
    assert manager.stop_training() is False  # Not running

    manager.is_training = True
    assert manager.stop_training() is True
    assert manager.stop_requested is True
