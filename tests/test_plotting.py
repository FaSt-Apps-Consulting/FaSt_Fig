"""Tests for basic plotting functionality in FFig."""

from __future__ import annotations

import numpy as np
import pytest
from fast_fig import FFig

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
