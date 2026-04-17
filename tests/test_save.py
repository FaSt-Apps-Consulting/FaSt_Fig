"""Tests for save function of FaSt Fig."""

# %%
import logging
from pathlib import Path

import pytest

from fast_fig import FFig

# %%

SHOW = False  # True requires manual closing of windows


def test_save_png(tmpdir: str) -> None:
    """Save a PNG figure."""
    test_file = Path(tmpdir) / "test_save.png"
    fig = FFig(show=SHOW)
    fig.plot()
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "PNG file not created!"


def test_save_pdf(tmpdir: str) -> None:
    """Save a PDF figure."""
    test_file = Path(tmpdir) / "test_save.pdf"
    fig = FFig(show=SHOW)
    fig.plot()
    fig.save(test_file)
    fig.close()
    assert test_file.is_file(), "PDF file not created!"


def test_save_no_suffix(tmpdir: str) -> None:
    """Save a figure without suffix."""
    test_file = Path(tmpdir) / "test_save"
    if test_file.is_file():
        test_file.unlink()
    fig = FFig(show=SHOW)
    fig.plot()

    # with pytest.warns(UserWarning):
    fig.save(test_file)

    fig.close()
    assert test_file.with_suffix(".png").is_file(), "PNG file not created!"


def test_save_multi(tmpdir: str) -> None:
    """Save multiple figures at once."""
    test_file = Path(tmpdir) / "test_save.pdf"

    fig = FFig(show=SHOW)
    fig.plot()
    fig.save(test_file, ".png", "jpg")
    fig.close()
    assert test_file.is_file(), "PDF file not created!"
    assert test_file.with_suffix(".png").is_file(), "PNG file not created!"
    assert test_file.with_suffix(".jpg").is_file(), "JPG file not created!"


def test_save_nested_dir(tmp_path: Path) -> None:
    """Test save creating nested directories."""
    nested_dir = tmp_path / "a" / "b" / "c"
    filename = nested_dir / "plot.png"

    with FFig(show=SHOW) as fig:
        fig.plot([1, 2, 3])
        saved_paths = fig.save(filename)
        assert filename.exists()
        assert Path(saved_paths[0]).exists()


def test_save_no_suffix_logging(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test save with a filename that has no suffix and check warning."""
    filename = tmp_path / "plot_no_suffix"
    with FFig(show=SHOW) as fig:
        fig.plot([1, 2, 3])
        with caplog.at_level(logging.WARNING):
            fig.save(filename)
            assert "has no suffix, defaulting to .png!" in caplog.text
            assert (tmp_path / "plot_no_suffix.png").exists()
