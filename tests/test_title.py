# Copyright (c) 2023 Fabian Stutzki
"""Tests for the title argument of FFig."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from fast_fig import FFig

if TYPE_CHECKING:
    from pathlib import Path

SHOW = False


def test_title_default_none(tmp_path: Path) -> None:
    """Without a title argument, no title is applied and save still works."""
    test_file = tmp_path / "test_no_title.png"
    with FFig(show=SHOW) as fig:
        assert fig.title is None
        fig.plot([1, 2, 3])
        fig.save(test_file)
        assert test_file.is_file(), "PNG file not created!"
        assert fig.current_axis.get_title() == "", "No title should be set!"


def test_title_applied_on_save(tmp_path: Path) -> None:
    """Title passed to __init__ must be set on the current axis by save()."""
    test_file = tmp_path / "test_title.png"
    with FFig(show=SHOW, title="Figure Title") as fig:
        fig.plot([1, 2, 3])
        fig.save(test_file)
        assert test_file.is_file(), "PNG file not created!"
        assert fig.current_axis.get_title() == "Figure Title", "Title should be set!"
        assert fig.handle_fig._suptitle is None, "No suptitle for single axis!"  # noqa: SLF001


def test_title_applied_on_show() -> None:
    """Title passed to __init__ must be set on the current axis by show()."""
    with patch("matplotlib.pyplot.show") as mock_show:
        fig = FFig(show=SHOW, title="Figure Title")
        fig.plot([1, 2, 3])
        fig.show()
        mock_show.assert_called_once()
        assert fig.current_axis.get_title() == "Figure Title", "Title should be set!"
        fig.close()


def test_title_with_subplots(tmp_path: Path) -> None:
    """Title must escalate to a suptitle for multi-axis figures."""
    test_file = tmp_path / "test_title_subplots.png"
    with FFig(show=SHOW, title="Grid Title", nrows=2) as fig:
        fig.plot([1, 2, 3])
        fig.next_axis()
        fig.plot([4, 5, 6])
        fig.save(test_file)
        assert test_file.is_file(), "PNG file not created!"
        assert fig.handle_fig._suptitle.get_text() == "Grid Title"  # noqa: SLF001
        assert fig.handle_axis[0].get_title() == "", "Axis titles must stay empty!"


def test_title_with_subplots_preserved_across_axes(tmp_path: Path) -> None:
    """Multi-axis title must remain a suptitle regardless of active axis."""
    test_file = tmp_path / "test_title_subplots_2axis.png"
    with FFig(show=SHOW, title="Grid Title", ncols=2) as fig:
        fig.plot([1, 2, 3])
        fig.next_axis()
        fig.plot([4, 5, 6])
        fig.save(test_file)
        assert test_file.is_file(), "PNG file not created!"
        assert fig.handle_fig._suptitle.get_text() == "Grid Title"  # noqa: SLF001
        assert fig.handle_axis[1].get_title() == "", "Axis titles must stay empty!"
