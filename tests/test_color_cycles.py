# Copyright (c) 2023 Fabian Stutzki
"""Tests for figure-local color cycles driven by Matplotlib."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib as mpl
import numpy as np
import pytest
from matplotlib.colors import to_rgba_array
from matplotlib.rcsetup import cycler

from fast_fig import FFig

if TYPE_CHECKING:
    from collections.abc import Mapping

    import numpy.typing as npt


def test_cycle_changes_existing_axes_in_color_then_style_order() -> None:
    """Explicit cycle changes apply immediately and retain the existing order."""
    with FFig(show=False) as fig:
        fig.plot([1, 2])
        fig.set_cycle({"a": [255, 0, 0], "b": [0, 0, 255]}, ["a", "b"], ["-", "--"])
        lines = fig.plot([1, 2], [[1, 2], [2, 3], [3, 4], [4, 5]])
        np.testing.assert_allclose(
            to_rgba_array([line.get_color() for line in lines]),
            [(1, 0, 0, 1), (0, 0, 1, 1), (1, 0, 0, 1), (0, 0, 1, 1)],
        )
        assert [line.get_linestyle() for line in lines] == ["-", "-", "--", "--"]


def test_cycle_positions_are_independent_between_subplots() -> None:
    """Switching axes preserves each axis's native cycle position."""
    with FFig(nrows=2, show=False) as fig:
        fig.set_cycle({"a": [1, 0, 0], "b": [0, 0, 1]}, ["a", "b"], ["-"])
        lines = [fig.plot([1, 2])[0]]
        fig.next_axis()
        lines.extend(fig.plot([1, 2]))
        fig.subplot(0)
        lines.extend(fig.plot([1, 2]))
        fig.subplot(1)
        lines.extend(fig.plot([1, 2]))
        np.testing.assert_allclose(
            to_rgba_array([line.get_color() for line in lines]),
            [(1, 0, 0, 1), (1, 0, 0, 1), (0, 0, 1, 1), (0, 0, 1, 1)],
        )


@pytest.mark.parametrize(("method", "args"), [("cla", ()), ("clear", ()), ("subplot", (2, 1))])
def test_configured_cycle_survives_axis_recreation(method: str, args: tuple[int, ...]) -> None:
    """Clearing axes or creating a grid restarts the configured local cycle."""
    with FFig(show=False) as fig:
        fig.set_cycle({"custom": [255, 0, 0]}, ["custom"], ["--"])
        fig.plot([1, 2])
        getattr(fig, method)(*args)
        line = fig.plot([1, 2])[0]
        np.testing.assert_allclose(np.asarray(line.get_color(), dtype=float), [1, 0, 0])
        assert line.get_linestyle() == "--"


def test_colors_do_not_change_global_cycle_defaults() -> None:
    """Constructing or reconfiguring FFig leaves global axes colors alone."""
    with mpl.rc_context({"axes.prop_cycle": cycler(color=["black", "white"])}):
        with FFig(show=False) as fig:
            fig.set_cycle({"custom": [1, 0, 0]}, ["custom"], ["--"])
        assert mpl.rcParams["axes.prop_cycle"].by_key()["color"] == ["black", "white"]


def test_custom_cycles_do_not_leak_to_other_figures() -> None:
    """A custom cycle affects neither existing nor subsequently created figures."""
    with FFig(show=False) as first, FFig(show=False) as second:
        first.set_cycle({"custom": [1, 0, 0]}, ["custom"], ["--"])
        np.testing.assert_allclose(np.asarray(first.get_next_color(), dtype=float), [1, 0, 0])
        np.testing.assert_allclose(
            np.asarray(second.get_next_color(), dtype=float), second.colors["blue"]
        )
        with FFig(show=False) as third:
            np.testing.assert_allclose(
                np.asarray(third.get_next_color(), dtype=float), third.colors["blue"]
            )


def test_next_color_advances_only_the_native_line_cycle() -> None:
    """Advancing line colors does not consume the separate scatter cycle."""
    with FFig(show=False) as fig:
        fig.set_cycle({"a": [1, 0, 0], "b": [0, 0, 1]}, ["a", "b"], ["-"])
        np.testing.assert_allclose(np.asarray(fig.get_next_color(), dtype=float), [1, 0, 0])
        points = fig.scatter([1, 2], [2, 1])
        np.testing.assert_allclose(np.asarray(points.get_facecolor(), dtype=float), [(1, 0, 0, 1)])
        line = fig.plot([1, 2])[0]
        np.testing.assert_allclose(np.asarray(line.get_color(), dtype=float), [0, 0, 1])


def test_advancing_cycle_does_not_replace_last_generated_color() -> None:
    """A cycle lookup does not pretend to generate a plotted color."""
    with FFig(show=False) as fig:
        fig.plot([1, 2], color="red")
        fig.get_next_color()
        assert fig.last_color == "red"


@pytest.mark.parametrize(
    ("colors", "names", "styles"),
    [
        ({"custom": [1, 0, 0]}, [], ["-"]),
        ({"custom": [1, 0, 0]}, ["missing"], ["-"]),
        ({"custom": [1, 0, 0]}, ["custom"], []),
        ({"custom": [1, 0, 0]}, ["custom"], ["not-a-style"]),
        ({"custom": [-1, 0, 0]}, ["custom"], ["-"]),
    ],
)
def test_invalid_cycle_logs_and_preserves_the_previous_cycle(
    colors: Mapping[str, npt.ArrayLike],
    names: list[str],
    styles: list[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Reject invalid configuration before changing active axes."""
    with FFig(show=False) as fig:
        fig.plot([1, 2])
        fig.set_cycle(colors, names, styles)
        assert "set_cycle(): Cannot set cycle for color and linestyle" in caplog.text
        line = fig.plot([1, 2])[0]
        np.testing.assert_allclose(np.asarray(line.get_color(), dtype=float), fig.colors["red"])
