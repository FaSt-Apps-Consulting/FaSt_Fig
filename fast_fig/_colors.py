# Copyright (c) 2023 Fabian Stutzki
"""Own palette validation, axis cycles, and plotted color tracking."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Final, Protocol, assert_never
from weakref import WeakSet, ref

import numpy as np
from matplotlib.collections import Collection
from matplotlib.colors import to_rgba
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.rcsetup import cycler

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Mapping, MutableMapping, Sequence
    from weakref import ReferenceType

    import numpy.typing as npt
    from matplotlib.axes import Axes

type ColorArtist = Line2D | Collection | Patch | AxesImage

_BYTE_MAX: Final = 255
_RGBA_CHANNELS: Final = 4

# Only native drawing entry points belong here; ordinary axes methods stay unwrapped.
AXES_PLOT_METHODS: Final[frozenset[str]] = frozenset(
    [
        "add_artist",
        "add_collection",
        "add_image",
        "add_line",
        "add_patch",
        "arrow",
        "axhline",
        "axhspan",
        "axline",
        "axvline",
        "axvspan",
        "bar",
        "barh",
        "broken_barh",
        "grouped_bar",
        "errorbar",
        "eventplot",
        "fill",
        "fill_between",
        "fill_betweenx",
        "loglog",
        "plot",
        "plot_date",
        "scatter",
        "semilogx",
        "semilogy",
        "stackplot",
        "stairs",
        "stem",
        "step",
        "hlines",
        "vlines",
        "boxplot",
        "bxp",
        "ecdf",
        "hexbin",
        "hist",
        "hist2d",
        "pie",
        "violin",
        "violinplot",
        "contour",
        "contourf",
        "imshow",
        "matshow",
        "pcolor",
        "pcolorfast",
        "pcolormesh",
        "spy",
        "tricontour",
        "tricontourf",
        "tripcolor",
        "triplot",
        "barbs",
        "quiver",
        "streamplot",
        "acorr",
        "angle_spectrum",
        "cohere",
        "csd",
        "magnitude_spectrum",
        "phase_spectrum",
        "psd",
        "specgram",
        "xcorr",
    ]
)


class _LineColorCycle(Protocol):
    """Describe the native line-cycle interface omitted from Matplotlib's Axes stubs."""

    def get_next_color(self) -> npt.ArrayLike:
        """Advance the native cycle."""
        ...


class ColorValidationError(ValueError):
    """A palette or cycle configuration cannot produce valid colors."""


class ColorManager:
    """Own mutable palette, cycle configuration, and weak artist history for one figure."""

    def __init__(
        self,
        colors: Mapping[str, npt.ArrayLike],
        color_seq: Sequence[str],
        linestyle_seq: Sequence[str],
    ) -> None:
        """Validate the palette and configure a cycle without changing global defaults."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.palette = self._normalize_palette(colors)
        self._axes: WeakSet[Axes] = WeakSet()
        self._color_history: list[ReferenceType[ColorArtist]] = []
        self.set_cycle(self.palette, color_seq, linestyle_seq)

    @staticmethod
    def _normalize_palette(
        colors: Mapping[str, npt.ArrayLike],
    ) -> MutableMapping[str, npt.NDArray[np.float64]]:
        """Copy and normalize RGB/RGBA components at the palette input boundary."""
        palette: dict[str, npt.NDArray[np.float64]] = {}
        for name, value in colors.items():
            try:
                match value:
                    case str():
                        normalized = np.asarray(to_rgba(value), dtype=float)
                    case _:
                        normalized = np.array(value, dtype=float, copy=True)
                        if (
                            normalized.ndim != 1
                            or normalized.size not in (3, 4)
                            or not np.isfinite(normalized).all()
                        ):
                            msg = "expected finite RGB or RGBA components"
                            raise ColorValidationError(msg)
                        if np.any(normalized < 0) or np.any(normalized > _BYTE_MAX):
                            msg = "components must be between 0 and 255"
                            raise ColorValidationError(msg)
                        scale = np.ones(normalized.size)
                        if np.max(normalized[:3]) > 1:
                            scale[:3] = _BYTE_MAX
                        if normalized.size == _RGBA_CHANNELS and normalized[3] > 1:
                            scale[3] = _BYTE_MAX
                        normalized = normalized / scale
                        to_rgba(normalized)
            except (ValueError, TypeError) as error:
                msg = f"Invalid palette color {name!r}: {error}"
                raise ColorValidationError(msg) from error
            palette[name] = normalized
        return palette

    def set_palette(self, colors: Mapping[str, npt.ArrayLike]) -> None:
        """Replace the exposed palette after validation, leaving the active cycle unchanged."""
        self.palette = self._normalize_palette(colors)

    def set_cycle(
        self,
        colors: Mapping[str, npt.ArrayLike],
        color_seq: Sequence[str],
        linestyle_seq: Sequence[str],
    ) -> None:
        """Validate a cycle before applying it to all managed axes."""
        palette = self._normalize_palette(colors)
        values = [palette[name] for name in color_seq if name in palette]
        if len(values) == 0 or len(linestyle_seq) == 0:
            msg = "A cycle requires at least one known color and one linestyle"
            raise ColorValidationError(msg)
        cycle = cycler(linestyle=list(linestyle_seq)) * cycler(color=values)
        unknown = [name for name in color_seq if name not in palette]
        if unknown:
            self.logger.warning("Ignoring unknown cycle colors: %s", ", ".join(unknown))
        for axis in self._axes:
            axis.set_prop_cycle(cycle)
        self._cycle = cycle

    def apply(self, axes: Iterable[Axes]) -> None:
        """Install the configured cycle on new or cleared axes."""
        for axis in axes:
            axis.set_prop_cycle(self._cycle)
            self._axes.add(axis)

    def reset(self) -> None:
        """Forget cleared plots and restart the configured cycles."""
        self._color_history.clear()
        self.apply(tuple(self._axes))

    def get_next_color(self, axis: Axes) -> npt.ArrayLike:
        """Advance Matplotlib's line cycle without generating a plotted color."""
        if axis not in self._axes:
            self.apply((axis,))
        line_cycle: _LineColorCycle = vars(axis)["_get_lines"]
        return line_cycle.get_next_color()

    @contextmanager
    def track_artists(self, axis: Axes) -> Iterator[None]:
        """Record artists after a plotting block without replacing the axes method."""
        if axis not in self._axes:
            self.apply((axis,))
        previous = set(axis.get_children())
        yield
        self._color_history.extend(
            ref(artist)
            for artist in axis.get_children()
            if artist not in previous and isinstance(artist, (Line2D, Collection, Patch, AxesImage))
        )

    def track_plot[**P, T](self, axis: Axes, method: Callable[P, T]) -> Callable[P, T]:
        """Adapt a delegated plotting method while preserving its result."""
        clears_axis = method in (axis.cla, axis.clear)

        @wraps(method)
        def tracked(*args: P.args, **kwargs: P.kwargs) -> T:
            with self.track_artists(axis):
                result = method(*args, **kwargs)
            if clears_axis:
                self.apply((axis,))
            return result

        return tracked

    @property
    def last_color(self) -> npt.ArrayLike:
        """Return the final color generated by the latest plotting call.

        Supports lines, bars, histograms, fills, scatter, contours, meshes,
        images, and other axes methods that create these data artists.
        Multicolored artists return their last color entry or image pixel.
        Colormap values are resolved without drawing the figure.

        Line colors retain their original specification; other artists return
        RGBA colors. Formatting calls do not replace the last plot color.

        Raises
        ------
        ValueError
            If no remaining plotted artist supplies a color.

        """
        for reference in reversed(self._color_history):
            artist = reference()
            if artist is None or artist.axes is None:
                continue
            match artist:
                case Line2D():
                    return artist.get_color()
                case Collection():
                    artist.update_scalarmappable()
                    colors = np.asarray(artist.get_facecolor(), dtype=float)
                    if len(colors) == 0:
                        colors = np.asarray(artist.get_edgecolor(), dtype=float)
                    if len(colors) > 0:
                        return colors.reshape(-1, 4)[-1]
                case Patch():
                    face = np.asarray(artist.get_facecolor(), dtype=float)
                    return face if artist.get_fill() and face[-1] > 0 else artist.get_edgecolor()
                case AxesImage():
                    data = artist.get_array()
                    if data is not None and data.size > 0:
                        colors = artist.to_rgba(data, alpha=artist.get_alpha())
                        return colors.reshape(-1, 4)[-1]
                case unreachable:
                    assert_never(unreachable)
        msg = "No plot exists yet to get color"
        raise ValueError(msg)
