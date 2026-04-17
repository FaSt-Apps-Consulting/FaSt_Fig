"""Tests for color management in FFig."""

from __future__ import annotations

import logging
from unittest.mock import patch

import numpy as np
import pytest

from fast_fig import FFig

SHOW = False


def test_get_next_color() -> None:
    """Test method get_next_color."""
    fig = FFig(show=SHOW)
    fig.plot()
    assert np.isclose(fig.get_next_color(), fig.colors["green"]).all()
    fig.close()


def test_last_color() -> None:
    """Test method last_color."""
    fig = FFig(show=SHOW)
    fig.plot()
    assert np.isclose(fig.last_color, fig.colors["blue"]).all()
    fig.close()


def test_last_color_error() -> None:
    """Test last_color raises error when no plot exists."""
    with FFig(show=SHOW) as fig, pytest.raises(ValueError, match="No plot exists yet"):
        _ = fig.last_color


def test_get_next_color_no_plot() -> None:
    """Test get_next_color works even without plot (returns first color)."""
    with FFig(show=SHOW) as fig:
        c = fig.get_next_color()
        assert c is not None


def test_set_cycle_error(caplog: pytest.LogCaptureFixture) -> None:
    """Test set_cycle error logging."""
    # Let's try to mock cycler to fail
    with FFig(show=SHOW) as fig, \
         patch("fast_fig.class_ffig.cycler", side_effect=TypeError("Mock Failure")), \
         caplog.at_level(logging.ERROR):
        fig.set_cycle({"c": [1, 2, 3]}, ["c"], ["-"])
        assert "set_cycle(): Cannot set cycle for color and linestyle" in caplog.text
