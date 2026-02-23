"""Tests for FFig lifecycle (context manager, clear, close)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pytest
from fast_fig import FFig

SHOW = False


def test_context_manager() -> None:
    """Test using FFig as a context manager."""
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2, 3])
        assert len(fig.current_axis._children) == 1, "Plot should generate one line"  # noqa: SLF001

    # After context exit, figure should be closed
    assert plt.fignum_exists(fig.handle_fig.number) is False, (
        "Figure should be closed after context exit"
    )


def test_clear() -> None:
    """Test clearing figure content."""
    fig = FFig(show=SHOW)
    fig.plot([1, 2, 3])
    assert len(fig.current_axis._children) == 1, "Plot should generate one line"  # noqa: SLF001

    # Test successful clear
    success = fig.clear()
    assert success is True, "Clear should return True on success"
    assert len(fig.current_axis._children) == 0, "Clear should remove all plot elements"  # noqa: SLF001

    # Test reuse after clear
    fig.plot([4, 5, 6])
    assert len(fig.current_axis._children) == 1, "Should be able to plot after clear"  # noqa: SLF001
    fig.close()


def test_close() -> None:
    """Test closing figure."""
    fig = FFig(show=SHOW)
    fig.plot([1, 2, 3])

    # Test successful close
    success = fig.close()
    assert success is True, "Close should return True on success"
    assert plt.fignum_exists(fig.handle_fig.number) is False, "Figure should be closed"

    # Test double close
    success = fig.close()
    assert success is True, "Close should return True when figure already closed"


def test_clear_after_close() -> None:
    """Test clearing after closing."""
    fig = FFig(show=SHOW)
    fig.plot([1, 2, 3])
    fig.close()

    # Try to clear after close
    success = fig.clear()
    assert success is True, "Clear should return True after figure is closed"


def test_repr_str() -> None:
    """Test __repr__ and __str__ methods."""
    with FFig(template="s", nrows=2, ncols=3, show=SHOW) as fig:
        r = repr(fig)
        s = str(fig)
        assert "FFig" in r
        assert "template='s'" in r
        assert "nrows=2" in r
        assert "ncols=3" in r
        assert "2x3 subplots" in s


def test_getattr_delegation() -> None:
    """Test __getattr__ delegation to internal handles."""
    with FFig(show=SHOW) as fig:
        # Should delegate to current_axis (Axes object)
        assert hasattr(fig, "get_title")
        assert callable(fig.get_title)

        # Should delegate to handle_fig (Figure object)
        assert hasattr(fig, "get_size_inches")

        # Non-existent attribute should raise AttributeError
        with pytest.raises(AttributeError, match="cannot be processed"):
            _ = fig.non_existent_attribute
