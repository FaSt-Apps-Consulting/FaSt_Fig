# Copyright (c) 2023 Fabian Stutzki
"""Tests for FFig lifecycle (context manager, clear, close)."""

from __future__ import annotations

import logging
import subprocess
import sys

import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_rgba

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


@pytest.mark.parametrize(("nrows", "ncols", "index"), [(1, 1, 0), (2, 2, 3)])
def test_clear(nrows: int, ncols: int, index: int) -> None:
    """Clearing restores attached axes and preserves the selected subplot."""
    fig = FFig(nrows=nrows, ncols=ncols, show=SHOW)
    fig.subplot(index)
    fig.plot([1, 2, 3])
    assert len(fig.current_axis._children) == 1, "Plot should generate one line"  # noqa: SLF001

    # Test successful clear
    success = fig.clear()
    assert success is True, "Clear should return True on success"
    assert len(fig.handle_fig.axes) == nrows * ncols
    assert fig.current_axis in fig.handle_fig.axes
    assert fig.subplot_index == index
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


@pytest.mark.parametrize(
    "method",
    [
        "get_title",
        "set_title",
        "get_xlabel",
        "set_xlabel",
        "get_xlim",
        "get_ylim",
        "set_xscale",
        "set_yscale",
        "set_prop_cycle",
        "set_facecolor",
        "tick_params",
        "format_coord",
        "twinx",
    ],
)
def test_non_plot_delegation_preserves_bound_methods(method: str) -> None:
    """Forward ordinary axes methods with their original binding and metadata."""
    with FFig(show=SHOW) as fig:
        native = getattr(fig.current_axis, method)
        forwarded = getattr(fig, method)
        assert forwarded == native
        assert forwarded.__self__ is fig.current_axis
        assert forwarded.__func__ is native.__func__


@pytest.mark.parametrize(("method", "args"), [("get_title", ()), ("set_title", ("Title",))])
def test_non_plot_calls_do_not_reset_custom_axis_cycles(method: str, args: tuple[str, ...]) -> None:
    """Reading or formatting a custom axis does not install FFig's cycle."""
    with FFig(show=SHOW) as fig:
        axis = fig.current_axis.twinx()
        axis.set_prop_cycle(color=["magenta"])
        fig.current_axis = axis
        getattr(fig, method)(*args)
        line = axis.plot([1, 2])[0]
        assert to_rgba(line.get_color()) == (1, 0, 1, 1)


def test_delegated_setter_returns_the_original_artist() -> None:
    """Forwarding a setter preserves its normal result and visible state."""
    with FFig(show=SHOW) as fig:
        title = fig.set_title("Title")
        assert title is fig.current_axis.title
        assert fig.get_title() == "Title"


def test_getattr_delegation_boost() -> None:
    """Test __getattr__ delegation to various handles."""
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2, 3])
        # Delegate to handle_plot (list of lines)
        assert fig.count(fig.handle_plot[0]) == 1  # list.count()

        # Delegate to handle_axis (numpy array of axes or single axis)
        assert fig.get_xlim() is not None


def test_getattr_delegation_axis() -> None:
    """Test __getattr__ delegation specifically to handle_axis."""
    with FFig(nrows=2, show=SHOW) as fig:
        if hasattr(fig.handle_axis, "reshape"):
            assert fig.reshape((1, 2)) is not None


def test_error_handling_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Test that exceptions in try-except blocks are logged."""
    with FFig(show=SHOW) as fig:
        # Mock tight_layout to fail
        def fail_tight_layout() -> None:
            msg = "Mock failure"
            raise ValueError(msg)

        fig.handle_fig.tight_layout = fail_tight_layout

        with caplog.at_level(logging.ERROR):
            fig.set_parameters()
            assert "set_parameters(): Tight layout cannot be set!" in caplog.text


def test_clear_error_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Test clear method error logging."""
    with FFig(show=SHOW) as fig:

        def fail_clf(*_args: float | str | bool, **_kwargs: float | str | bool) -> None:
            msg = "Mock failure"
            raise AttributeError(msg)

        fig.handle_fig.clf = fail_clf

        with caplog.at_level(logging.ERROR):
            result = fig.clear()
            assert result is False
            assert "Error clearing figure" in caplog.text


def test_init_invalid_template() -> None:
    """Test initializing with an invalid template name."""
    with FFig(template="non_existent", show=SHOW) as fig:
        assert fig.template == "m"


def test_main_block() -> None:
    """Test the if __name__ == '__main__': block."""
    script = """
import matplotlib.pyplot as plt
from unittest.mock import patch
with patch('matplotlib.pyplot.show'):
    import fast_fig.class_ffig
"""
    subprocess.run([sys.executable, "-c", script], check=True, env={"PYTHONPATH": "."}, timeout=30)  # noqa: S603
