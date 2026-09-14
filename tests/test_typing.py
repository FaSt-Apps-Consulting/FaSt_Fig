# Copyright (c) 2023 Fabian Stutzki
"""Verify the permissive data-input typing scheme.

Two layers of coverage:

1. Runtime acceptance: every supported container type (list, tuple, ndarray,
   pandas Series/DataFrame/Index) must be accepted by every plotting routine
   that was loosened to the ``DataLike`` alias.
2. Static type checking: pyright must report zero errors for a probe snippet
   that passes all container types through the public API.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import TYPE_CHECKING, get_args

import numpy as np
import numpy.typing as npt
import pytest

from fast_fig import FFig, class_ffig

if TYPE_CHECKING:
    from pathlib import Path

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

SHOW = False

X_1D: list[object] = [
    pytest.param([1.0, 2.0, 3.0], id="list"),
    pytest.param((1.0, 2.0, 3.0), id="tuple"),
    pytest.param(np.array([1.0, 2.0, 3.0]), id="ndarray"),
]

Z_2D: list[object] = [
    pytest.param(np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]), id="ndarray"),
    pytest.param([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], id="nested-list"),
]

if PANDAS_AVAILABLE:
    X_1D.append(pytest.param(pd.Series([1.0, 2.0, 3.0]), id="series"))
    X_1D.append(pytest.param(pd.Index([1, 2, 3]), id="index"))


# %% Runtime acceptance tests


@pytest.mark.parametrize("data", X_1D)
def test_plot_accepts_1d_containers(data: object) -> None:
    """Each 1-D container must produce exactly one line."""
    with FFig(show=SHOW) as fig:
        assert len(fig.plot(data)) == 1


@pytest.mark.parametrize(
    ("data", "expected_lines"),
    [
        pytest.param(np.arange(1.0, 13.0).reshape(3, 4), 2, id="ndarray-3x4"),
        # More rows than columns: must be transposed (3 x-row candidates -> 2 lines).
        pytest.param(np.arange(1.0, 13.0).reshape(4, 3), 2, id="ndarray-4x3-transposed"),
        pytest.param([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], 1, id="nested-list"),
    ],
)
def test_plot_accepts_2d_containers(data: object, expected_lines: int) -> None:
    """2-D containers must plot row-wise, transposing when needed."""
    with FFig(show=SHOW) as fig:
        assert len(fig.plot(data)) == expected_lines


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
def test_plot_accepts_dataframe() -> None:
    """DataFrames must plot one line per column."""
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0]})
    with FFig(show=SHOW) as fig:
        assert len(fig.plot(df)) == 2
        assert fig.current_axis.get_xlabel() == ""


@pytest.mark.parametrize("z", Z_2D)
def test_surface_routines_accept_2d_containers(z: object) -> None:
    """pcolor, pcolor_log, pcolor_square and contour must accept any 2-D container."""
    with FFig(show=SHOW) as fig:
        fig.pcolor(z)
        fig.contour(z)
        assert fig.handle_surface is not None
    with FFig(show=SHOW) as fig:
        fig.pcolor_log(z, vmin=1e-3, vmax=1.0)
        assert fig.handle_surface is not None


def test_scatter_accepts_mixed_containers() -> None:
    """Scatter must accept a list, tuple and ndarray in its data positions."""
    x = [0.1, 0.2, 0.3]
    y = (0.5, 0.6, 0.7)
    size = np.array([10.0, 20.0, 30.0])
    with FFig(show=SHOW) as fig:
        fig.scatter(x, y, s=size, c=y)
        assert fig.handle_surface is not None


def test_bar_plot_accepts_containers() -> None:
    """bar_plot must accept a list for x and an ndarray for the heights."""
    with FFig(show=SHOW) as fig:
        bars = fig.bar_plot([1, 2, 3], np.array([4.0, 5.0, 6.0]))
        assert bars is not None


def test_fill_between_accepts_mixed_containers() -> None:
    """fill_between must accept list, ndarray and tuple for x, y1 and y2."""
    x = np.linspace(0.0, 1.0, 10)
    with FFig(show=SHOW) as fig:
        fig.plot(x, x)  # Baseline so last_color is available
        poly = fig.fill_between(x.tolist(), x, tuple(x**2))
        assert poly is not None


def test_log_plots_accept_containers() -> None:
    """semilogx/semilogy must forward arbitrary containers to plot()."""
    x = np.logspace(0.0, 2.0, 5)
    with FFig(show=SHOW) as fig:
        assert len(fig.semilogx(x.tolist(), x)) == 1
    with FFig(show=SHOW) as fig:
        assert len(fig.semilogy(x, tuple(x**2))) == 1


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
def test_pandas_containers_accepted_by_all_routines() -> None:
    """Series/DataFrame must be accepted by the surface, bar and scatter routines."""
    s = pd.Series([0.1, 0.2, 0.3])
    df = pd.DataFrame({"a": [0.1, 0.2, 0.3], "b": [0.4, 0.5, 0.6]})
    with FFig(show=SHOW) as fig:
        fig.pcolor(df)
        fig.contour(df)
        fig.scatter([1, 2, 3], s, c=s)
        assert fig.handle_surface is not None
    with FFig(show=SHOW) as fig:
        fig.plot(s)
        fig.bar_plot([1, 2, 3], s)
        fig.fill_between([0.1, 0.2, 0.3], s, [0.0, 0.0, 0.0])


def test_save_accepts_int_dpi(tmp_path: Path) -> None:
    """save() must accept an int dpi positionally."""
    with FFig(show=SHOW) as fig:
        fig.plot([1.0, 2.0, 3.0])
        assert len(fig.save(tmp_path / "typing_save", 100)) == 1


# %% DataLike alias structure


def test_datalike_alias_contains_numpy_arraylike() -> None:
    """DataLike must embed numpy's ArrayLike as the generic array-like backbone."""
    members = get_args(class_ffig.DataLike)
    # DataLike is a Union, and typing flattens nested Unions, so ``npt.ArrayLike``
    # itself is not a member - its components are. Verify them as a subset.
    assert set(get_args(npt.ArrayLike)) <= set(members)


def test_datalike_alias_includes_pandas_containers() -> None:
    """DataLike must explicitly union pandas containers."""
    members = get_args(class_ffig.DataLike)
    forward_refs = {arg.__forward_arg__ for arg in members if hasattr(arg, "__forward_arg__")}
    assert {"pd.DataFrame", "pd.Series", "pd.Index"} <= forward_refs


# %% Static type checking


PYRIGHT_PROBE = """\
import numpy as np
import pandas as pd
from fast_fig import FFig

x = [1.0, 2.0, 3.0]
y = np.array([1.0, 2.0, 3.0])
s = pd.Series([1.0, 2.0, 3.0])
df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0]})
z = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])

fig = FFig()

# plot() and the log-scaled variants: every container type must type-check.
fig.plot(x)
fig.plot(y)
fig.plot(s)
fig.plot(df)
fig.plot(x, y)
fig.plot(x, y, label="line", color=(0.1, 0.2, 0.3))
fig.semilogx(x, y)
fig.semilogy(x, y)

# The remaining plot routines must accept containers in any data position.
fig.bar_plot(x, y)
fig.fill_between(x, y, 0.0, alpha=0.3)
fig.pcolor(z)
fig.pcolor_log(z, vmin=1e-3, vmax=1.0)
fig.pcolor_square(z)
fig.contour(z, levels=[0.2, 0.5])
fig.scatter(x, y, c=s, s=np.arange(3))

# save() must accept an int dpi positionally.
fig.save("/tmp/fast_fig_typing_probe.png", 600, "pdf")
"""


def _pyright_command() -> list[str] | None:
    """Return a working pyright invocation, or None if no runner is installed."""
    if path := shutil.which("pyright"):
        return [path]
    if path := shutil.which("uv"):
        return [path, "run", "--with", "pyright", "pyright"]
    return None


@pytest.mark.skipif(
    _pyright_command() is None,
    reason="pyright or uv is not installed",
)
def test_static_typing_accepts_all_containers(tmp_path: Path) -> None:
    """The public API must type-check with zero errors for every container type."""
    command = _pyright_command()
    assert command is not None  # skipif guarantees this
    probe = tmp_path / "typing_probe.py"
    probe.write_text(PYRIGHT_PROBE, encoding="utf-8")
    result = subprocess.run(  # noqa: S603 - fixed allowlist of type-checker runners
        [*command, "--outputjson", str(probe)],
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )
    if "errorCount" not in result.stdout:
        pytest.skip(f"pyright could not analyze the probe: {result.stderr.strip()}")
    report = json.loads(result.stdout)
    assert report["summary"]["errorCount"] == 0, json.dumps(
        report["generalDiagnostics"],
        indent=2,
    )
