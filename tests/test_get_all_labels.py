"""Tests for get_all_labels method in FFig."""

from __future__ import annotations

from fast_fig import FFig


def test_get_all_labels_single_axis() -> None:
    """Test get_all_labels with a single axis."""
    with FFig(show=False) as fig:
        fig.plot([1, 2, 3], label="A")
        fig.plot([3, 2, 1], label="B")
        labels = fig.get_all_labels()
        # Matplotlib might add other children, but we expect at least "A" and "B"
        # The filter label != "" should catch most things
        assert "A" in labels
        assert "B" in labels
        assert len(labels) == 2


def test_get_all_labels_multiple_axes() -> None:
    """Test get_all_labels with multiple axes."""
    with FFig("m", 1, 2, show=False) as fig:
        fig.plot([1, 2, 3], label="A")
        fig.next_axis()
        fig.plot([3, 2, 1], label="B")
        labels = fig.get_all_labels()
        assert "A" in labels
        assert "B" in labels
        assert len(labels) == 2


def test_get_all_labels_empty() -> None:
    """Test get_all_labels when no labels are present."""
    with FFig(show=False) as fig:
        fig.plot([1, 2, 3])
        labels = fig.get_all_labels()
        # Filtered labels should be empty (assuming we fix get_all_labels to ignore _)
        assert labels == []


def test_get_all_labels_mixed() -> None:
    """Test get_all_labels with mixed labeled and unlabeled plots."""
    with FFig(show=False) as fig:
        fig.plot([1, 2, 3], label="A")
        fig.plot([2, 2, 2])
        fig.plot([3, 2, 1], label="C")
        labels = fig.get_all_labels()
        assert "A" in labels
        assert "C" in labels
        assert len(labels) == 2


def test_get_all_labels_flatten() -> None:
    """Test get_all_labels with 2D grid of axes."""
    with FFig("m", 2, 2, show=False) as fig:
        fig.plot([1, 2, 3], label="1,1")
        fig.next_axis()
        fig.plot([1, 2, 3], label="1,2")
        fig.next_axis()
        fig.plot([1, 2, 3], label="2,1")
        fig.next_axis()
        fig.plot([1, 2, 3], label="2,2")
        labels = fig.get_all_labels()
        assert len(labels) == 4
        assert "1,1" in labels
        assert "1,2" in labels
        assert "2,1" in labels
        assert "2,2" in labels
