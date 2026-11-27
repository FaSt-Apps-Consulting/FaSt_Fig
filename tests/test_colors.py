# Copyright (c) 2023 Fabian Stutzki
"""Tests for color management in FFig."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
import pytest
from matplotlib.colors import to_rgba, to_rgba_array

from fast_fig import FFig

if TYPE_CHECKING:
    from collections.abc import Mapping

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
    fig.plot([0, 1], [0, 1])
    assert np.isclose(fig.last_color, fig.colors["blue"]).all()
    fig.close()


def test_last_color_error() -> None:
    """Test last_color raises error when no plot exists."""
    with FFig(show=SHOW) as fig, pytest.raises(ValueError, match="No plot exists yet"):
        _ = fig.last_color


@pytest.mark.parametrize("prior_line", [False, True])
@pytest.mark.parametrize("colors", ["green", ["red", "green"]])
def test_last_color_scatter(colors: str | list[str], *, prior_line: bool) -> None:
    """Return the last scatter color even when a line was plotted earlier."""
    with FFig(show=SHOW) as fig:
        if prior_line:
            fig.plot([0, 1], [0, 1], color="blue")
        fig.scatter([0, 1], [1, 0], c=colors)
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), to_rgba("green"))


@pytest.mark.parametrize("marker", ["o", "x"])
def test_last_color_scatter_colormap(marker: str) -> None:
    """Resolve the last mapped scatter color before the figure is drawn."""
    with FFig(show=SHOW) as fig:
        fig.scatter([0, 1], [1, 0], c=[0, 1], cmap="gray", marker=marker)
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), to_rgba("white"))


@pytest.mark.parametrize("plot_method", ["plot", "semilogx", "semilogy", "scatter"])
def test_last_color_common_plots_after_scatter(plot_method: str) -> None:
    """Common plotting methods replace the previous scatter color."""
    with FFig(show=SHOW) as fig:
        fig.scatter([1, 2], [2, 1], color="green")
        getattr(fig, plot_method)([1, 2], [3, 4], color=(1, 0, 0, 1))
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), (1, 0, 0, 1))


def test_last_color_multiple_lines() -> None:
    """Return the final line color when one call generates several lines."""
    with FFig(show=SHOW) as fig:
        fig.plot([0, 1], [[0, 1], [1, 0]])
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), fig.colors["red"])


@pytest.mark.parametrize(
    ("plot_method", "plot_args", "plot_kwargs"),
    [
        ("plot", ([1, 2], [3, 4]), {"color": (1, 0, 0, 1)}),
        ("semilogx", ([1, 2], [3, 4]), {"color": (1, 0, 0, 1)}),
        ("semilogy", ([1, 2], [3, 4]), {"color": (1, 0, 0, 1)}),
        ("loglog", ([1, 2], [3, 4]), {"color": (1, 0, 0, 1)}),
        ("step", ([1, 2], [3, 4]), {"color": (1, 0, 0, 1)}),
        ("scatter", ([1, 2], [3, 4]), {"c": ["green", "red"]}),
        ("bar", ([1, 2], [3, 4]), {"color": ["green", "red"]}),
        ("barh", ([1, 2], [3, 4]), {"color": ["green", "red"]}),
        ("bar_plot", ([1, 2], [3, 4]), {"color": ["green", "red"]}),
        ("hist", ([1, 1, 2, 3],), {"bins": 2, "color": "red"}),
        ("hist", ([1, 1, 2, 3],), {"bins": 2, "color": "red", "histtype": "step"}),
        ("stairs", ([1, 2], [0, 1, 2]), {"color": "red"}),
        ("eventplot", ([1, 2, 3],), {"colors": "red"}),
        ("fill", ([1, 2, 3], [1, 3, 1]), {"color": "red"}),
        ("fill_between", ([1, 2], [3, 4]), {"color": "red", "alpha": 1}),
        ("fill_betweenx", ([1, 2], [3, 4]), {"color": "red"}),
        ("hlines", ([1, 2], 0, 3), {"colors": ["green", "red"]}),
        ("vlines", ([1, 2], 0, 3), {"colors": ["green", "red"]}),
        ("errorbar", ([1, 2], [3, 4]), {"yerr": 0.5, "color": "red"}),
        ("stem", ([1, 2], [3, 4]), {"linefmt": "r-", "markerfmt": "ro", "basefmt": "r-"}),
        ("quiver", ([1, 2], [3, 4]), {"color": "red"}),
        ("barbs", ([10, 20], [1, 2]), {"barbcolor": "red", "flagcolor": "red"}),
        ("angle_spectrum", ([1, 0, -1, 0],), {"color": (1, 0, 0, 1)}),
        ("triplot", ([0, 1, 0], [0, 0, 1]), {"color": (1, 0, 0, 1)}),
        (
            "tricontour",
            ([0, 1, 0], [0, 0, 1], [0, 1, 2]),
            {"levels": [0.5, 1.5], "colors": ["green", "red"]},
        ),
        (
            "tricontourf",
            ([0, 1, 0], [0, 0, 1], [0, 1, 2]),
            {"levels": [0, 1, 2], "colors": ["green", "red"]},
        ),
        ("axhline", (1,), {"color": (1, 0, 0, 1)}),
        ("axvline", (1,), {"color": (1, 0, 0, 1)}),
        ("axhspan", (1, 2), {"color": "red"}),
        ("axvspan", (1, 2), {"color": "red"}),
        ("stackplot", ([1, 2], [1, 2], [2, 3]), {"colors": ["green", "red"]}),
        ("pie", ([1, 2],), {"colors": ["green", "red"]}),
        ("contour", ([[0, 1], [2, 3]],), {"levels": [1, 2], "colors": ["green", "red"]}),
        ("contourf", ([[0, 1], [2, 3]],), {"levels": [0, 1, 3], "colors": ["green", "red"]}),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_last_color_plotting_routines(
    plot_method: str,
    plot_args: tuple[npt.ArrayLike, ...],
    plot_kwargs: Mapping[str, npt.ArrayLike],
) -> None:
    """Read the final generated color across wrapped and delegated plot types."""
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2], [2, 1], color=(0, 1, 0, 1))
        getattr(fig, plot_method)(*plot_args, **plot_kwargs)
        np.testing.assert_allclose(to_rgba_array(np.atleast_1d(fig.last_color)), [(1, 0, 0, 1)])


@pytest.mark.parametrize(
    "plot_method", ["pcolor", "pcolor_log", "pcolor_square", "pcolormesh", "imshow", "matshow"]
)
def test_last_color_mapped_routines(plot_method: str) -> None:
    """Resolve the final cell color before drawing a colormapped plot."""
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2], [2, 1], color=(1, 0, 0, 1))
        getattr(fig, plot_method)([[1, 2], [3, 4]], cmap="gray")
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), (1, 1, 1, 1))


@pytest.mark.parametrize("channels", [3, 4])
def test_last_color_image_pixels(channels: int) -> None:
    """RGB and RGBA images return their last pixel color."""
    pixels = np.array([[[0, 1, 0, 1], [1, 0, 0, 0.5]]])
    with FFig(show=SHOW) as fig:
        fig.imshow(pixels[:, :, :channels])
        expected = (1, 0, 0, 0.5 if channels == 4 else 1)
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), expected)


@pytest.mark.parametrize("plot_method", ["bar", "barh", "bar_plot", "scatter"])
def test_last_color_hollow_artists(plot_method: str) -> None:
    """Use edge colors when markers or patches have no face color."""
    with FFig(show=SHOW) as fig:
        getattr(fig, plot_method)([1, 2], [3, 4], facecolor="none", edgecolor="red")
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), (1, 0, 0, 1))


def test_last_color_across_subplots() -> None:
    """Selecting an older subplot does not replace the latest generated color."""
    with FFig(nrows=2, show=SHOW) as fig:
        fig.bar_plot([1, 2], [3, 4], color="red")
        fig.next_axis()
        fig.hist([1, 2, 3], color="green")
        fig.subplot(0)
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), to_rgba("green"))


def test_last_color_ignores_formatting() -> None:
    """Labels, legends, and grids do not replace a plot's color."""
    with FFig(show=SHOW) as fig:
        fig.bar([1, 2], [3, 4], color="red", label="Bars")
        fig.set_title("Title", color="blue")
        fig.text(1, 1, "Text", color="blue")
        fig.grid(color="blue")
        fig.legend()
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), to_rgba("red"))


def test_last_color_after_artist_removal() -> None:
    """Removing the latest artist restores the preceding plot's color."""
    with FFig(show=SHOW) as fig:
        fig.bar([1, 2], [3, 4], color="red")
        points = fig.scatter([1, 2], [3, 4], color="green")
        points.remove()
        np.testing.assert_allclose(np.asarray(fig.last_color, dtype=float), to_rgba("red"))


@pytest.mark.parametrize("clear_method", ["clear", "cla", "clf"])
def test_last_color_after_clear(clear_method: str) -> None:
    """Cleared plots no longer supply a color."""
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2], [3, 4])
        getattr(fig, clear_method)()
        with pytest.raises(ValueError, match="No plot exists yet"):
            _ = fig.last_color


def test_get_next_color_no_plot() -> None:
    """Test get_next_color works even without plot (returns first color)."""
    with FFig(show=SHOW) as fig:
        np.testing.assert_allclose(
            np.asarray(fig.get_next_color(), dtype=float), fig.colors["blue"]
        )


def test_set_cycle_error(caplog: pytest.LogCaptureFixture) -> None:
    """Test set_cycle error logging."""
    with (
        FFig(show=SHOW) as fig,
        caplog.at_level(logging.ERROR),
    ):
        fig.set_cycle({"c": [1, 2, 3]}, ["c"], ["not-a-style"])
        assert "set_cycle(): Cannot set cycle for color and linestyle" in caplog.text
