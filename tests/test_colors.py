"""Tests for color management in FFig."""

from __future__ import annotations

import numpy as np
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
