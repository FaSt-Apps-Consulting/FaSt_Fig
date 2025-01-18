"""Basic tests for FaSt_Fig."""

# %%

import numpy as np

from fast_fig import FFig

# %%
SHOW = False  # True requires manual closing of windows


# %%
def test_plot() -> None:
    """Test basic plot."""
    fig = FFig(show=SHOW)
    fig.plot()
    assert len(fig.current_axis._children) == 2, "Simple plot should generate two lines!"
    fig.close()


def test_plot_args() -> None:
    """Test basic plot."""
    fig = FFig("l", 2, 1, show=SHOW)
    fig.plot()
    assert len(fig.current_axis._children) == 2, "Simple plot should generate two lines!"
    fig.close()


def test_plot1() -> None:
    """Test plot of vector."""
    fig = FFig(show=SHOW)
    fig.plot(np.random.randn(5))
    assert len(fig.current_axis._children) == 1, "Plot with one vector should generate one line!"
    fig.close()


def test_plot_mat():
    """Test plot of matrix."""
    fig = FFig(show=SHOW)
    mat = np.array(
        [
            [1, 2, 3, 4, 5],
            np.random.randn(5),
            2 * np.random.randn(5),
            1.5 * np.random.randn(5),
        ],
    )
    fig.plot(mat)
    assert (
        len(fig.current_axis._children) == 3
    ), "Plot with matrix shape (4, 8) should generate three lines!"
    fig.close()


def test_label() -> None:
    """Test xlabel and ylabel."""
    fig = FFig(show=SHOW)
    fig.plot()
    fig.set_xlabel("xlab")
    fig.set_ylabel("ylab")
    fig.set_title("Title")
    assert fig.current_axis.get_xlabel() == "xlab", "xlabel should be set to xlab!"
    assert fig.current_axis.get_ylabel() == "ylab", "ylabel should be set to ylab!"
    assert fig.current_axis.get_title() == "Title", "title should be set to Title!"
    fig.close()
    fig.close()


# %%
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
    # print(fig.handle_axis)
    fig.plot()
    assert fig.handle_axis.shape == (
        4,
        3,
    ), "Subplot(nrows=4, ncols=3) should give 4x3 plots."
    assert fig.subplot_index == 4, "subplot(index=4) should set current axe number to 4"
    fig.close()
