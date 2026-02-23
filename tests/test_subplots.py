"""Tests for subplot management in FFig."""

from __future__ import annotations

import numpy as np
from fast_fig import FFig

SHOW = False


def test_subplot_nrows() -> None:
    """Test subplot with nrows."""
    fig = FFig(show=SHOW)
    fig.subplot(nrows=3)
    fig.plot()
    assert len(fig.handle_axis) == 3, "Subplot(nrows=3) should give 3 axis."
    fig.close()


def test_subplot_ncols() -> None:
    """Test subplot with ncols."""
    fig = FFig(show=SHOW)
    fig.subplot(nrows=4)
    fig.plot()
    assert len(fig.handle_axis) == 4, "Subplot(ncols=4) should give 4 axis."
    fig.close()


def test_subplot_nrows_cols() -> None:
    """Test subplot with nrows, ncols and index."""
    fig = FFig(show=SHOW)
    fig.subplot(nrows=4, ncols=3, index=4)
    fig.plot()
    assert fig.handle_axis.shape == (
        4,
        3,
    ), "Subplot(nrows=4, ncols=3) should give 4x3 plots."
    assert fig.subplot_index == 4, "subplot(index=4) should set current axe number to 4"
    fig.close()


def test_subplot_index() -> None:
    """Test subplot with index."""
    fig = FFig(show=SHOW, nrows=4, ncols=3)
    fig.subplot(index=4)
    fig.plot()
    assert fig.subplot_index == 4, "subplot(index=4) should set current axe number to 4"
    fig.close()


def test_subplot_arg() -> None:
    """Test subplot with index."""
    fig = FFig(show=SHOW, nrows=4, ncols=3)
    fig.subplot(3)
    fig.plot()
    assert fig.subplot_index == 3, "subplot(index=4) should set current axe number to 4"
    fig.close()
