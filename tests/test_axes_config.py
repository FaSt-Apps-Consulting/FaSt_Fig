"""Tests for axes configuration in FFig."""

from __future__ import annotations

from fast_fig import FFig

SHOW = False


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
