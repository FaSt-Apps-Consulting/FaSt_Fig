# Copyright (c) 2023 Fabian Stutzki
"""Tests for legends across plot types."""

from __future__ import annotations

import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg

from fast_fig import FFig


@pytest.mark.parametrize(
    "plot_methods",
    [
        ("plot",),
        ("scatter",),
        ("bar_plot",),
        ("plot", "scatter", "bar_plot"),
    ],
    ids=["line", "scatter", "bar", "mixed"],
)
@pytest.mark.parametrize("labeled", [True, False], ids=["labeled", "unlabeled"])
def test_legend_displays_plot_labels(plot_methods: tuple[str, ...], *, labeled: bool) -> None:
    """Render all labeled entries and omit legends for unlabeled plots."""
    with FFig(show=False) as fig:
        expected_labels = []
        for method_name in plot_methods:
            plot = getattr(fig, method_name)
            for label, x, y in [
                ("C1", [1, 2, 3, 1], [4, 2, 1, 2]),
                ("C2", [2, 1, 3, 1], [3, 2, 1, 1]),
            ]:
                entry_label = f"{method_name} {label}" if labeled else ""
                plot(x, y, label=entry_label)
                if labeled:
                    expected_labels.append(entry_label)

        fig.legend()

        axis = fig.current_axis
        assert axis is not None
        legend = axis.get_legend()
        FigureCanvasAgg(fig.handle_fig).draw()
        if labeled:
            assert legend is not None
            assert legend.get_visible()
            assert [text.get_text() for text in legend.get_texts()] == expected_labels
        else:
            assert legend is None
