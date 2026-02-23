"""Tests for color management in FFig."""

from __future__ import annotations

import numpy as np
import pytest
from fast_fig import FFig

SHOW = False


def test_next_color() -> None:
    """Test method next_color."""
    fig = FFig(show=SHOW)
    fig.plot()
    assert np.isclose(fig.next_color, fig.colors["green"]).all()
    fig.close()


def test_last_color() -> None:
    """Test method last_color."""
    fig = FFig(show=SHOW)
    fig.plot()
    assert np.isclose(fig.last_color, fig.colors["blue"]).all()
    fig.close()


def test_last_color_error() -> None:
    """Test last_color raises error when no plot exists."""
    with FFig(show=SHOW) as fig:
        with pytest.raises(ValueError, match="No plot exists yet"):
            _ = fig.last_color


def test_next_color_no_plot() -> None:
    """Test next_color works even without plot (returns first color)."""
    with FFig(show=SHOW) as fig:
        c = fig.next_color
        assert c is not None
