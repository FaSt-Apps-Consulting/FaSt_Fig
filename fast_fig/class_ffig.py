"""fast_fig simplifies figure handling with mpl.

Key functions:
- predefinied templates
- figure instantiation in a class object
- simplified handling (e.g. plot with vectors)

from fast_fig import FFig
# very simple example
fig = FFig()
fig.plot()
fig.show()

More complex example
fig = FFig("l", nrows=2, sharex=True)  # create figure with template l=large
fig.plot([1, 2, 3, 1, 2, 3, 4, 1, 1])  # plot first data set
fig.title("First data set")  # set title for subplot
fig.subplot()  # set focus to next subplot/axis
fig.plot([0, 1, 2, 3, 4], [0, 1, 1, 2, 3], label="random")  # plot second data set
fig.legend()  # generate legend
fig.grid()  # show translucent grid to highlight major ticks
fig.xlabel("Data")  # create xlabel for second axis
fig.save("fig1.png", "pdf")  # save figure to png and pdf

The following handlers can be used to access all matplotlib functionality:
- fig.current_axis
- fig.handle_plot
- fig.handle_axis
- fig.handle_fig

"""

from __future__ import annotations

# %%
__author__ = "Fabian Stutzki"
__email__ = "fast@fast-apps.de"
__version__ = "0.5.3"


import logging
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from packaging import version

from . import presets

MAT_EXAMPLE = np.array([[1, 2, 3, 4, 5, 6, 7], np.random.randn(7), 2 * np.random.randn(7)])  # noqa: NPY002


# %%
class FFig:
    """FFig simplifies handling of matplotlib figures.

    Use as
    from fast_fig import FFig
    fig = FFig('m')
    fig.plot([0,1,2,3,4],[0,1,1,2,3])
    fig.save('test.png')

    @author: fstutzki

    """

    def __init__(
        self: FFig,
        template: str = "m",
        nrows: int = 1,
        ncols: int = 1,
        **kwargs: int | str,
    ) -> None:
        """Set default values and create figure.

        fig = FFig("OL", nrows=2, ncols=2)
        """
        # Enable logger
        self.logger = logging.getLogger(self.__class__.__name__)

        kwargs.setdefault("isubplot", 0)
        kwargs.setdefault("sharex", False)
        kwargs.setdefault("sharey", False)
        kwargs.setdefault("show", True)
        kwargs.setdefault("vspace", None)
        kwargs.setdefault("hspace", None)
        kwargs.setdefault("presets", None)

        # Initialize dictionary with presets
        self.presets = presets.define_presets(kwargs["presets"])

        # Check if template exists (ignoring case), otherwise set template m (default)
        template = template.lower()
        if template not in self.presets:
            template = "m"

        # Fill undefined kwargs with presets
        for key in ["width", "height", "fontfamily", "fontsize", "linewidth"]:
            kwargs.setdefault(key, self.presets[template][key])

        # Apply parameters to matplotlib
        mpl.rc("font", size=kwargs["fontsize"])
        mpl.rc("font", family=kwargs["fontfamily"])
        mpl.rc("lines", linewidth=kwargs["linewidth"])

        # Convert colors to ndarray and scale to 1 instead of 255
        self.colors = {}
        for iname, icolor in self.presets["colors"].items():
            if np.max(icolor) > 1:
                self.colors[iname] = np.array(icolor) / 255

        # Define cycle with colors, color_seq and linestyle_seq
        self.set_cycle(self.colors, self.presets["color_seq"], self.presets["linestyle_seq"])

        # Store global variables
        self.figure_show = kwargs["show"]  # show figure after saving
        self.subplot_index = 0
        self.handle_bar = None
        self.handle_plot = None
        self.handle_surface = None
        self.linewidth = kwargs["linewidth"]

        # Create figure
        self.handle_fig = plt.figure()
        self.handle_fig.set_size_inches(kwargs["width"] / 2.54, kwargs["height"] / 2.54)
        self.subplot(
            nrows=nrows,
            ncols=ncols,
            index=kwargs["isubplot"],
            sharex=kwargs["sharex"],
            sharey=kwargs["sharey"],
            vspace=kwargs["vspace"],
            hspace=kwargs["hspace"],
        )

    def __getattr__(self: FFig, item: str):  # noqa: ANN204
        """Pass unkown methods to current_axis, handle_plot, handle_axis or handle_fig."""
        # Check attributes of current_axis
        if hasattr(self.current_axis, item):
            return getattr(self.current_axis, item)

        # Check attributes of handle_plt
        if hasattr(self.handle_plot, item):
            return getattr(self.handle_plot, item)

        # Check attributes of handle_axis
        if hasattr(self.handle_axis, item):
            return getattr(self.handle_axis, item)

        # Check attributes of handle_fig
        if hasattr(self.handle_fig, item):
            return getattr(self.handle_fig, item)

        msg = f"'{item}' cannot be processed as axis or figure property.'"
        raise AttributeError(msg)

    def set_current_axis(self: FFig, index: int | None = None) -> None:
        """Set current axis index."""
        # Overwrite subplot_index with named argument
        if index is None:
            self.subplot_index += 1
        else:
            self.subplot_index = index

        # Set current axe handle
        self.subplot_index = self.subplot_index % (self.subplot_nrows * self.subplot_ncols)
        if self.subplot_nrows == 1 and self.subplot_ncols == 1:
            self.current_axis = self.handle_axis
        elif self.subplot_nrows > 1 and self.subplot_ncols > 1:
            isuby = self.subplot_index // self.subplot_ncols
            isubx = self.subplot_index % self.subplot_ncols
            self.current_axis = self.handle_axis[isuby][isubx]
        else:
            self.current_axis = self.handle_axis[self.subplot_index]

    def next_axis(self: FFig) -> None:
        """Iterate current axis to next subplot."""
        self.set_current_axis(index=None)

    def subplot(  # noqa: PLR0913
        self: FFig,
        nrows: [int | None] = None,
        ncols: [int | None] = None,
        index: [int | None] = None,
        *,  # following arguments are keyword only
        vspace: [float | None] = None,
        hspace: [float | None] = None,
        sharex: [bool, str] = False,
        sharey: [bool, str] = False,
    ) -> None:
        """Set current axis/subplot.

        fig.subplot(0) # for first subplot
        fig.subplot() # for next subplot
        """
        if nrows is not None or ncols is not None:
            # Generate new subplot
            if nrows is None:
                nrows = 1
            if ncols is None:
                ncols = 1
            if index is None:
                index = 0
            self.subplot_nrows = nrows
            self.subplot_ncols = ncols
            self.subplot_sharex = sharex
            self.subplot_sharey = sharey
            self.subplot_vspace = vspace
            self.subplot_hspace = hspace

            self.handle_fig.clf()
            self.handle_fig, self.handle_axis = plt.subplots(
                nrows=self.subplot_nrows,
                ncols=self.subplot_ncols,
                num=self.handle_fig.number,  # reference to existing figure
                sharex=self.subplot_sharex,
                sharey=self.subplot_sharey,
                vspace=self.subplot_vspace,
                hspace=self.subplot_hspace,
            )

        self.set_current_axis(index=index)

    def bar_plot(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """Generate bar plot."""
        self.handle_bar = self.current_axis.bar(*args, **kwargs)
        return self.handle_bar

    def plot(
        self: FFig,
        mat: [list, np.ndarray] = MAT_EXAMPLE,
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> None:
        """Generate a line plot."""
        if np.ndim(mat) > 1:
            if np.shape(mat)[0] > np.shape(mat)[1]:
                mat = mat.T
            for imat in mat[1:]:
                self.handle_plot = self.current_axis.plot(mat[0, :], imat, *args, **kwargs)
        else:
            self.handle_plot = self.current_axis.plot(mat, *args, **kwargs)
        return self.handle_plot

    def semilogx(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """Semi-log plot on x axis."""
        self.plot(*args, **kwargs)
        self.xscale("log")

    def semilogy(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """Semi-log plot on y axis."""
        self.plot(*args, **kwargs)
        self.yscale("log")

    def fill_between(
        self: FFig,
        *args: float | str | bool,
        color: list | None = None,
        alpha: float = 0.1,
        linewidth: float = 0,
        **kwargs: float | str | bool,
    ) -> None:
        """Fill area below or between lines."""
        if color is None:
            color = self.last_color()
        self.current_axis.fill_between(
            *args,
            color=color,
            alpha=alpha,
            linewidth=linewidth,
            **kwargs,
        )

    def last_color(self: FFig) -> None:
        """Return last color code used by plot."""
        return self.handle_plot[0].get_color()

    def pcolor(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """2D area plot."""
        kwargs.setdefault("cmap", "nipy_spectral")
        self.handle_surface = self.current_axis.pcolormesh(*args, **kwargs)
        return self.handle_surface

    def pcolor_log(
        self: FFig,
        *args: float | str | bool,
        vmin: float | None = None,
        vmax: float | None = None,
        **kwargs: float | str | bool,
    ) -> None:
        """2D area plot with logarithmic scale."""
        kwargs.setdefault("cmap", "nipy_spectral")
        kwargs_log = {}
        if vmin is not None:
            kwargs_log["vmin"] = vmin
        if vmax is not None:
            kwargs_log["vmax"] = vmax
        kwargs["norm"] = mpl.colors.LogNorm(**kwargs_log)
        self.handle_surface = self.current_axis.pcolormesh(*args, **kwargs)
        return self.handle_surface

    def pcolor_square(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """2D area plot with axis equal and off."""
        kwargs.setdefault("cmap", "nipy_spectral")
        self.handle_surface = self.current_axis.pcolormesh(*args, **kwargs)
        self.current_axis.axis("off")
        self.current_axis.set_aspect("equal")
        self.current_axis.set_xticks([])
        self.current_axis.set_yticks([])
        return self.handle_surface

    def contour(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """2D contour plot."""
        self.handle_surface = self.current_axis.contour(*args, **kwargs)
        return self.handle_surface

    def scatter(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """Plot scattered data."""
        self.handle_surface = self.current_axis.scatter(*args, **kwargs)
        return self.handle_surface

    def colorbar(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """Add colorbar to figure."""
        self.handle_fig.colorbar(*args, self.handle_surface, ax=self.current_axis, **kwargs)

    def grid(
        self: FFig,
        *args: int | str,
        color: str = "grey",
        alpha: float = 0.2,
        **kwargs: int | str | bool,
    ) -> None:
        """Access axis aspect ration."""
        self.current_axis.grid(*args, color=color, alpha=alpha, **kwargs)

    def set_xlim(self: FFig, xmin: float = np.inf, xmax: float = -np.inf) -> None:
        """Set limits for current x-axis.

        xlim(0,1) # limit set to 0 and 1
        xlim() # set limit to min and max
        """
        try:
            if np.size(xmin) == 2:  # noqa: PLR2004
                xmax = xmin[1]
                xmin = xmin[0]
            elif xmin == np.inf and xmax == -np.inf:
                for iline in self.current_axis.lines:
                    xdata = iline.get_xdata()
                    xmin = np.minimum(xmin, np.nanmin(xdata))
                    xmax = np.maximum(xmax, np.nanmax(xdata))
            if version.parse(mpl.__version__) >= version.parse("3"):
                if np.isfinite(xmin):
                    self.current_axis.set_xlim(left=xmin)
                if np.isfinite(xmax):
                    self.current_axis.set_xlim(right=xmax)
            else:
                if np.isfinite(xmin):
                    self.current_axis.set_xlim(xmin=xmin)
                if np.isfinite(xmax):
                    self.current_axis.set_xlim(xmax=xmax)
        except (ValueError, TypeError):
            self.logger.exception()

    def set_ylim(self: FFig, ymin: float = np.inf, ymax: float = -np.inf) -> None:
        """Set limits for current y-axis.

        ylim(0,1) # set limit to 0 and 1
        ylim() # set limit to min and max
        """
        try:
            if np.size(ymin) == 2:  # noqa: PLR2004
                ymax = ymin[1]
                ymin = ymin[0]
            elif ymin == np.inf and ymax == -np.inf:
                for iline in self.current_axis.lines:
                    ydata = iline.get_ydata()
                    ymin = np.minimum(ymin, np.nanmin(ydata))
                    ymax = np.maximum(ymax, np.nanmax(ydata))
            if version.parse(mpl.__version__) >= version.parse("3"):
                if np.isfinite(ymin):
                    self.current_axis.set_ylim(bottom=ymin)
                if np.isfinite(ymax):
                    self.current_axis.set_ylim(top=ymax)
            else:
                if np.isfinite(ymin):
                    self.current_axis.set_ylim(ymin=ymin)
                if np.isfinite(ymax):
                    self.current_axis.set_ylim(ymax=ymax)
        except (ValueError, TypeError):
            self.logger.exception()

    def legend(
        self: FFig,
        *args: float | str | bool,
        labels: str | [str] | None = None,
        **kwargs: float | str | bool,
    ) -> None:
        """Insert legend based on labels given in plot(x,y,label='Test1') etc."""
        if labels is not None:
            for ilabel, iline in enumerate(self.current_axis.lines):
                iline.set_label(labels[ilabel])
        _, labels = self.current_axis.get_legend_handles_labels()
        if np.size(self.current_axis.lines) != 0 and len(labels) != 0:
            self.current_axis.legend(*args, **kwargs)

    def legend_entries(self: FFig) -> None:
        """Return handle and labels of legend."""
        handles, labels = self.current_axis.get_legend_handles_labels()
        return handles, labels

    def legend_count(self: FFig) -> None:
        """Return number of legend entries."""
        handles, _ = self.current_axis.get_legend_handles_labels()
        return np.size(handles)

    def set_cycle(
        self: FFig,
        colors: list,
        color_seq: [str],
        linestyle_seq: [str],
    ) -> None:  # ,linewidth=False):
        """Set cycle for colors and linestyles (will be used in this order)."""
        # generate cycle from color_seq and linestyle_seq
        color_list = [colors[icolor] for icolor in color_seq if icolor in colors]
        cyc_color = np.tile(color_list, (np.size(linestyle_seq), 1))
        cyc_linestyle = np.repeat(linestyle_seq, np.shape(color_list)[0])
        try:
            mpl.rc(
                "axes",
                prop_cycle=(cycler("color", cyc_color) + cycler("linestyle", cyc_linestyle)),
            )
        except (ValueError, TypeError):
            self.logger.exception("set_cycle(): Cannot set cycle for color and linestyle")

    def set_parameters(self: FFig) -> None:
        """Set useful figure parameters, called automatically by save and show function."""
        try:
            self.handle_fig.tight_layout()
        except (ValueError, TypeError):
            self.logger.exception("set_parameters(): Tight layout cannot be set!")

        if self.subplot_hspace is not None and self.subplot_nrows > 1:
            self.handle_fig.subplots_adjust(hspace=self.subplot_hspace)
        if self.subplot_vspace is not None and self.subplot_ncols > 1:
            self.handle_fig.subplots_adjust(vspace=self.subplot_vspace)

    def watermark(  # noqa: PLR0913
        self: FFig,
        img: str | Path,
        xpos: float = 100,
        ypos: float = 100,
        alpha: float = 0.15,
        zorder: float = 1,
        **kwargs: float | str | bool,
    ) -> None:
        """Include watermark image to plot."""
        img = Path(img)
        if img.is_file():
            self.handle_fig.figimage(img, xpos, ypos, alpha=alpha, zorder=zorder, **kwargs)
        else:
            FileNotFoundError("watermark(): File not found")

    def show(self: FFig) -> None:
        """Show figure in interactive console (similar to save)."""
        self.set_parameters()
        plt.show()

    def save(
        self: FFig,
        filename: str | Path,
        *args: float | str | bool,
        **kwargs: float | str | bool,
    ) -> None:
        """Save figure as image (png, pdf...).

        save('test.png',600,'pdf') # save test.png and test.pdf with 600dpi
        """
        kwargs.setdefault("dpi", 300)  # Default to 300 dpi

        filepath = Path(filename)

        format_set = set()
        if filepath.suffix == "":
            msg = f"FFig: Filepath {filepath} has no suffix, defaulting to .png!"
            self.logger.warning(msg)
            format_set.add(".png")
        else:
            format_set.add(filepath.suffix)
        for iarg in args:
            if isinstance(iarg, int):
                kwargs["dpi"] = iarg
            elif isinstance(iarg, str):
                if iarg.startswith("."):
                    format_set.add(iarg)
                else:
                    format_set.add("." + iarg)

        self.set_parameters()

        for iformat in format_set:
            ifilepath = filepath.with_suffix(iformat)
            try:
                ifilepath.parent.mkdir(parents=True, exist_ok=True)
                self.handle_fig.savefig(ifilepath, **kwargs)
            except (FileNotFoundError, PermissionError, OSError):
                except_message = f"save(): Figure cannot be saved to {ifilepath}"
                self.logger.exception(except_message)
        if self.figure_show:
            plt.show()  # block=False)
        else:
            plt.draw()

    def clear(self: FFig, *args: float | str | bool, **kwargs: float | str | bool) -> None:
        """Clear figure content in order to reuse figure."""
        self.handle_fig.clf(*args, **kwargs)

    def close(self: FFig) -> None:
        """Close figure."""
        try:
            plt.close(self.handle_fig)
        except (ValueError, TypeError, AttributeError):
            self.logger.exception("close(): Figure cannot be closed")


# %%
if __name__ == "__main__":
    fig = FFig()
    fig.plot()
    fig.show()
