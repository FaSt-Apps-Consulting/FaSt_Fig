"""Tests for axes configuration in FFig."""

from __future__ import annotations

import logging
import numpy as np
import pytest
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


def test_set_xlim_ylim() -> None:
    """Test set_xlim and set_ylim with various inputs."""
    with FFig(show=SHOW) as fig:
        fig.plot([0, 10], [0, 20])

        # Individual values
        fig.set_xlim(1, 9)
        assert fig.current_axis.get_xlim() == (1.0, 9.0)

        # List input
        fig.set_xlim([2, 8])
        assert fig.current_axis.get_xlim() == (2.0, 8.0)

        # Auto-calc
        fig.set_xlim()
        xlim = fig.current_axis.get_xlim()
        assert xlim[0] <= 0
        assert xlim[1] >= 10

        # Y limits
        fig.set_ylim(5, 15)
        assert fig.current_axis.get_ylim() == (5.0, 15.0)

        fig.set_ylim([6, 14])
        assert fig.current_axis.get_ylim() == (6.0, 14.0)

        fig.set_ylim()
        ylim = fig.current_axis.get_ylim()
        assert ylim[0] <= 0
        assert ylim[1] >= 20


def test_set_xlim_errors(caplog: pytest.LogCaptureFixture) -> None:
    """Test error handling in set_xlim."""
    with FFig(show=SHOW) as fig:
        # This should trigger the try-except block in set_xlim
        with caplog.at_level(logging.ERROR):
            fig.set_xlim("invalid", "input")
