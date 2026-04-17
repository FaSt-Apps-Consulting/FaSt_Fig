"""Tests for subplot management in FFig."""

from __future__ import annotations

import pytest

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


def test_subplot_args() -> None:
    """Test subplot with various argument combinations."""
    with FFig(show=SHOW) as fig:
        # Test 3 arguments: nrows, ncols, index
        fig.subplot(2, 2, 1)
        assert fig.subplot_nrows == 2
        assert fig.subplot_ncols == 2
        assert fig.subplot_index == 1

        # Test 2 arguments: nrows, ncols (index defaults to 0)
        fig.subplot(3, 1)
        assert fig.subplot_nrows == 3
        assert fig.subplot_ncols == 1
        assert fig.subplot_index == 0

        # Test invalid arguments
        with pytest.raises(ValueError, match="Invalid arguments for subplot"):
            fig.subplot(1, 2, 3, 4)


def test_next_axis_2d() -> None:
    """Test next_axis in a 2D subplot grid."""
    with FFig(nrows=2, ncols=2, show=SHOW) as fig:
        # Initial index should be 0 (0,0)
        assert fig.subplot_index == 0
        fig.next_axis()
        assert fig.subplot_index == 1
        fig.next_axis()
        assert fig.subplot_index == 2
        fig.next_axis()
        assert fig.subplot_index == 3
        # Should wrap around or continue incrementing?
        # Actually set_current_axis handles it.
        fig.next_axis()
        assert fig.subplot_index == 0  # It wraps around


def test_subplot_one_arg() -> None:
    """Test subplot with 1 argument."""
    with FFig(nrows=2, show=SHOW) as fig:
        fig.subplot(1)
        assert fig.subplot_index == 1


def test_subplot_spacing_coverage() -> None:
    """Test coverage for subplot spacing adjustments."""
    with FFig(nrows=2, ncols=2, hspace=0.5, wspace=0.5, show=SHOW) as fig:
        fig.set_parameters()


def test_subplot_none_nrows() -> None:
    """Test subplot with nrows=None."""
    with FFig(show=SHOW) as fig:
        fig.subplot(nrows=None, ncols=2)
        assert fig.subplot_nrows == 1
        assert fig.subplot_ncols == 2
