# Copyright (c) 2023 Fabian Stutzki
"""Tests for palette normalization and validation through FFig."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

from fast_fig import FFig

if TYPE_CHECKING:
    import numpy.typing as npt


@pytest.mark.parametrize(
    ("color", "expected"),
    [
        ([1, 0.5, 0], [1, 0.5, 0]),
        ([0, 0, 0], [0, 0, 0]),
        ([1, 1, 1], [1, 1, 1]),
        ([255, 128, 0], [1, 128 / 255, 0]),
        ([1, 0, 0.5, 0.25], [1, 0, 0.5, 0.25]),
        ([255, 0, 128, 128], [1, 0, 128 / 255, 128 / 255]),
        ([255, 0, 128, 0.5], [1, 0, 128 / 255, 0.5]),
        ("red", [1, 0, 0, 1]),
        ("#ff008080", [1, 0, 128 / 255, 128 / 255]),
        ("none", [0, 0, 0, 0]),
    ],
)
def test_palette_colors_are_normalized(color: npt.ArrayLike, expected: list[float]) -> None:
    """Normalized, byte, and string colors remain usable in actual plots."""
    with FFig(show=False, presets={"colors": {"custom": color}, "color_seq": ["custom"]}) as fig:
        np.testing.assert_allclose(fig.colors["custom"], expected)
        lines = fig.plot([1, 2])
        np.testing.assert_allclose(np.asarray(lines[0].get_color(), dtype=float), expected)


@pytest.mark.parametrize(
    "color",
    [
        [],
        [1, 0],
        [1, 0, 0, 1, 1],
        [[1, 0, 0]],
        [-1, 0, 0],
        [256, 0, 0],
        [0, 0, 0, 256],
        [np.nan, 0, 0],
        [np.inf, 0, 0],
        "not-a-color",
    ],
)
def test_invalid_palette_colors_identify_the_entry(color: npt.ArrayLike) -> None:
    """Reject malformed palette entries with their names in the error."""
    with (
        pytest.raises(ValueError, match="custom"),
        FFig(show=False, presets={"colors": {"custom": color}, "color_seq": ["custom"]}),
    ):
        pass


def test_palette_does_not_mutate_or_alias_input() -> None:
    """Palette normalization owns its arrays without changing caller data."""
    color = np.array([255.0, 128.0, 0.0])
    with FFig(show=False, presets={"colors": {"custom": color}, "color_seq": ["custom"]}) as fig:
        np.testing.assert_allclose(color, [255, 128, 0])
        color[:] = 0
        np.testing.assert_allclose(fig.colors["custom"], [1, 128 / 255, 0])


def test_assigning_colors_validates_and_normalizes_the_palette() -> None:
    """The existing writable colors attribute exposes the manager's palette."""
    with FFig(show=False) as fig:
        fig.colors = {"custom": [255, 0, 0]}
        np.testing.assert_allclose(fig.colors["custom"], [1, 0, 0])
        fig.colors["custom"] = np.array([0, 1, 0])
        fig.set_cycle(fig.colors, ["custom"], ["-"])
        lines = fig.plot([1, 2])
        np.testing.assert_allclose(np.asarray(lines[0].get_color(), dtype=float), [0, 1, 0])


def test_invalid_palette_assignment_preserves_existing_colors() -> None:
    """A failed palette replacement leaves the existing mapping intact."""
    with FFig(show=False) as fig:
        original = fig.colors
        with pytest.raises(ValueError, match="broken"):
            fig.colors = {"broken": [-1, 0, 0]}
        assert fig.colors is original


def test_unknown_cycle_names_warn_and_keep_valid_colors(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Keep accepted preset behavior while reporting unknown color names."""
    with FFig(show=False, presets={"color_seq": ["missing", "blue"]}) as fig:
        assert "missing" in caplog.text
        np.testing.assert_allclose(
            np.asarray(fig.get_next_color(), dtype=float), fig.colors["blue"]
        )
