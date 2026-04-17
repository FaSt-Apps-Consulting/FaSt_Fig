"""Tests for basic plotting functionality in FFig."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib as mpl
import numpy as np
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg

from fast_fig import FFig

if TYPE_CHECKING:
    from pathlib import Path

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

SHOW = False  # Set to False for automated tests
RNG = np.random.default_rng(42)


def test_ffig() -> None:
    """Test basic plot."""
    fig = FFig(show=SHOW)
    fig.plot()
    assert len(fig.current_axis._children) == 2, "Simple plot should generate two lines!"  # noqa: SLF001
    fig.close()


def test_ffig_args() -> None:
    """Test basic plot."""
    fig = FFig("l", 2, 1, show=SHOW)
    fig.plot()
    assert len(fig.current_axis._children) == 2, "Simple plot should generate two lines!"  # noqa: SLF001
    fig.close()


def test_plot_1d() -> None:
    """Test plot of vector."""
    fig = FFig(show=SHOW)
    fig.plot(RNG.standard_normal(5))
    assert len(fig.current_axis._children) == 1, "Plot with one vector should generate one line!"  # noqa: SLF001
    fig.close()


def test_plot_mat() -> None:
    """Test plot of matrix."""
    mat = np.array(
        [
            [1, 2, 3, 4, 5],
            RNG.standard_normal(5),
            2 * RNG.standard_normal(5),
            1.5 * RNG.standard_normal(5),
        ],
    )
    with FFig(show=SHOW) as fig:
        fig.plot(mat)
        assert len(fig.current_axis._children) == 3, (  # noqa: SLF001
            "Plot with matrix shape (4, 8) should generate three lines!"
        )


def test_plot_list() -> None:
    """Test plot of a list."""
    with FFig("l", 2, 1, show=SHOW) as fig:
        fig.plot([1, 2, 3], [1, 1, 3])
        assert len(fig.current_axis._children) == 1, (  # noqa: SLF001
            "Simple plot with list should generate one line!"
        )


def test_plot_lol() -> None:
    """Test plot of a list of lists."""
    with FFig("l", 2, 1, show=SHOW) as fig:
        fig.plot([1, 2, 3], [[1, 1, 3], [1, 2, 1]])
        assert len(fig.current_axis._children) == 2, (  # noqa: SLF001
            "Simple plot with list should generate two lines!"
        )


def test_plot_lol_arg() -> None:
    """Test plot of a list of lists with additional argument."""
    with FFig("l", 2, 1, show=SHOW) as fig:
        fig.plot([1, 2, 3], [[1, 1, 3], [1, 2, 1]], "--")
        assert len(fig.current_axis._children) == 2, (  # noqa: SLF001
            "Simple plot with list should generate two lines!"
        )


def test_semilogx() -> None:
    """Test plot with logarithmic x-axis."""
    with FFig(show=SHOW) as fig:
        fig.semilogx(RNG.standard_normal(5))
        assert len(fig.current_axis._children) == 1, (  # noqa: SLF001
            "Plot with one vector should generate one line!"
        )


def test_semilogy() -> None:
    """Test plot with logarithmic y-axis."""
    with FFig(show=SHOW) as fig:
        fig.semilogy(RNG.standard_normal(5))
        assert len(fig.current_axis._children) == 1, (  # noqa: SLF001
            "Plot with one vector should generate one line!"
        )


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
def test_plot_dataframe() -> None:
    """Test plot of pandas DataFrame with two columns and index."""
    fig = FFig(show=SHOW)

    # Create a test DataFrame
    index = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame(
        {
            "A": [1, 2, 3, 4, 5],
            "B": [2, 4, 6, 8, 10],
        },
        index=index,
    )

    fig.plot(df)
    assert len(fig.current_axis._children) == 2, (  # noqa: SLF001
        "Plot with DataFrame of two columns should generate two lines!"
    )
    assert fig.current_axis.get_xlabel() == "Date", (
        "xlabel should default to index name for DataFrame!"
    )
    fig.close()


def test_bar_plot() -> None:
    """Test bar_plot method."""
    with FFig(show=SHOW) as fig:
        fig.bar_plot([1, 2, 3], [4, 5, 6])
        assert len(fig.current_axis.patches) == 3


def test_pcolor_square() -> None:
    """Test pcolor_square method."""
    with FFig(show=SHOW) as fig:
        data = RNG.random((10, 10))
        fig.pcolor_square(data)
        assert fig.handle_surface is not None


def test_fill_between() -> None:
    """Test fill_between method."""
    with FFig(show=SHOW) as fig:
        x = np.linspace(0, 1, 10)
        y1 = x
        y2 = x**2
        fig.plot(x, y1)  # Create a plot first so last_color works
        poly = fig.fill_between(x, y1, y2)
        assert isinstance(poly, mpl.collections.PolyCollection)


def test_plot_matrix_transpose() -> None:
    """Test plot with matrix that needs transpose (more rows than columns)."""
    with FFig(show=SHOW) as fig:
        # 5 rows, 3 columns. Should transpose to 3 rows (1st is x, 2nd and 3rd are y).
        data = RNG.standard_normal((5, 3))
        lines = fig.plot(data)
        # 3 rows means 1 x-row and 2 y-rows -> 2 lines
        assert len(lines) == 2
        assert len(fig.handle_plot) == 2


def test_plot_dataframe_index_name() -> None:
    """Test plot with DataFrame that has a named index."""
    if not PANDAS_AVAILABLE:
        pytest.skip("pandas not available")
    import pandas as pd  # noqa: PLC0415
    df = pd.DataFrame({"A": [1, 2, 3]}, index=[10, 20, 30])
    df.index.name = "MyIndex"
    with FFig(show=SHOW) as fig:
        fig.plot(df)
        assert fig.current_axis.get_xlabel() == "MyIndex"


def test_colorbar() -> None:
    """Test colorbar method."""
    with FFig(show=SHOW) as fig:
        data = RNG.standard_normal((10, 10))
        fig.pcolor(data)
        cb = fig.colorbar(label="Test Label")
        assert cb is not None
        assert cb.ax.get_ylabel() == "Test Label"


def test_watermark(tmp_path: Path) -> None:
    """Test watermark method."""
    # Create a dummy image
    img_path = tmp_path / "watermark.png"
    fig_temp = mpl.figure.Figure()
    _ = FigureCanvasAgg(fig_temp)
    fig_temp.savefig(img_path)

    with FFig(show=SHOW) as fig:
        fig.watermark(img_path)
        # Check if figimage was called (it adds to images list)
        assert len(fig.handle_fig.images) > 0

    with FFig(show=SHOW) as fig, pytest.raises(FileNotFoundError):
        fig.watermark("non_existent.png")


def test_legend_empty_plot() -> None:
    """Test legend with no plot objects."""
    with FFig(show=SHOW) as fig:
        # Should not raise error and not create legend
        fig.legend()
        assert fig.current_axis.get_legend() is None


def test_legend_with_labels() -> None:
    """Test legend with explicit labels."""
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2], [3, 4])
        fig.legend(labels=["New Label"])
        _, labels = fig.current_axis.get_legend_handles_labels()
        assert "New Label" in labels


def test_legend_entries_check() -> None:
    """Test legend_entries and legend_count."""
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2], [3, 4], label="Test")
        handles, labels = fig.legend_entries()
        assert len(handles) == 1
        assert labels[0] == "Test"
        assert fig.legend_count() == 1

