"""Tests for compatibility and optional dependencies."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib as mpl
import pytest

from fast_fig import FFig, class_ffig

if TYPE_CHECKING:
    import pytest
    from packaging.version import Version


SHOW = False


def test_mpl_legacy_version_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test legacy Matplotlib version paths."""
    from packaging import version as pkg_version  # noqa: PLC0415

    class MockVersion:
        def parse(self, v: str) -> Version:
            if v == mpl.__version__:
                return pkg_version.parse("2.9.9")
            return pkg_version.parse(v)

    monkeypatch.setattr(class_ffig, "version", MockVersion())

    with FFig(show=SHOW) as fig:
        fig.plot([1, 2], [3, 4])
        fig.set_xlim(0, 1)
        fig.set_ylim(0, 1)


def test_pandas_not_available(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test behavior when pandas is not available."""
    monkeypatch.setattr(class_ffig, "PANDAS_AVAILABLE", False)

    with FFig(show=SHOW) as fig:
        # This hits fallback plotting logic when pandas is "missing"
        fig.plot([1, 2, 3])
