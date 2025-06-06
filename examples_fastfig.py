"""Script gives some examples for the use of FaSt_Fig."""

# %%
import numpy as np
import pandas as pd

from fast_fig import FFig

# %% Very simple example
fig = FFig()
fig.plot([1, 1, 4, 1])
fig.plot([2, 3, 4, 1])
fig.legend()
fig.show()
# fig.save("fig_example1.png")  # noqa: ERA001

# %% More complex example
fig = FFig("l", nrows=2, sharex=True)  # create figure with template l=large
fig.plot([1, 2, 3, 1, 2, 3, 4, 1, 1])  # plot first data set
fig.set_title("First data set")  # set title for subplot
fig.subplot()  # set focus to next subplot/axis
fig.plot([0, 1, 2, 3, 4], [0, 1, 1, 2, 3], label="rand1")  # plot data to second subplot
fig.plot([2, 3, 4, 5], [1, 3, 1, 1], label="rand2")  # plot data to second subplot
fig.legend()  # generate legend
fig.grid()  # show translucent grid to highlight major ticks
fig.set_xlabel("Data")  # create xlabel for second axis
fig.show()
# fig.save("fig_example2.png", "pdf")  # save figure to png and pdf  # noqa: ERA001


# %% Check color sequence
fig = FFig()
fig.plot([1, 1, 4, 1], label="1")
fig.plot([2, 3, 4, 1], label="2")
fig.plot([3, 2, 1, 1], label="3")
fig.plot([4, 2, 4, 1], label="4")
fig.plot([5, 2, 1, 1], label="5")
fig.plot([6, 2, 1, 1], label="6")
fig.plot([6, 1, 2, 1], label="7")
fig.plot([8, 1, 2, 3], label="8")
fig.legend()
fig.show()

# %% Plot several lines with one matrix
mat = np.array(
    [
        [1, 2, 3, 4, 5, 6, 7, 8],
        np.random.randn(8),
        2 * np.random.randn(8),
        1.5 * np.random.randn(8),
    ],
)
fig = FFig()
fig.plot(mat)
fig.show()

# %% Read custom preset JSON
fig = FFig(presets="fast_fig_presets.json")
fig.plot([1, 1, 4, 1], label="1")
fig.plot([2, 3, 4, 1], label="2")
fig.plot([3, 2, 1, 1], label="3")
fig.plot([4, 2, 4, 1], label="4")
fig.plot([5, 2, 1, 1], label="5")
fig.plot([6, 2, 1, 1], label="6")
fig.show()

# %% Example for webpage
xvec = np.arange(-50, 50, 0.1)
xmesh, ymesh = np.meshgrid(xvec, xvec)
r_gauss = 30 / 2
e_gauss = 2 * np.exp(-(xmesh**2 + ymesh**2) / r_gauss**2) + np.exp(
    -((xmesh - 10) ** 2 + (ymesh + 20) ** 2) / (r_gauss / 2) ** 2
)

fig = FFig("l", nrows=2, ncols=2)  # create figure with template l=large
fig.plot([1, 2, 3, 1, 2, 3, 4, 1, 1])  # plot first data set
fig.set_xlabel("Number of values")
fig.set_ylabel("Count")

fig.subplot()
fig.pcolor(e_gauss)
fig.set_title("Profile")
fig.set_ylabel("Y-Axis")

fig.subplot()  # set focus to next subplot/axis
fig.plot([0, 1, 2, 3, 4], [0, 1, 1, 2, 3], label="A")  # plot data to second subplot
fig.plot([2, 3, 4, 5], [1, 3, 1, 1], label="B")  # plot data to second subplot
fig.legend()  # generate legend
fig.grid()  # show translucent grid to highlight major ticks

fig.subplot()
fig.pcolor(e_gauss)
fig.contour(e_gauss, [0.2], colors="white", alpha=0.8, linestyles="dashed")
fig.set_title("20% contour")
fig.set_ylabel("Y-Axis")
fig.set_xlabel("X-Axis")  # create xlabel for second axis
fig.suptitle("Simulation result")  # set title for subplot
fig.show()
# fig.save("example_pcolor.png")  # save figure to png and pdf  # noqa: ERA001

# %% Create thumbnail

fig = FFig()
fig.pcolor(e_gauss)
fig.set_title("Profile")
fig.set_ylabel("Y-Axis")
fig.save("fastfig_thumbnail.png")

# %% DataFrame example
# Create sample DataFrame
dates = pd.date_range("2024-01-01", periods=10)
df = pd.DataFrame(
    {"A": np.random.randn(10), "B": np.random.randn(10) + 2, "C": np.random.randn(10) - 2},
    index=dates,
)

# Plot DataFrame columns
fig = FFig("l")
fig.plot(df)
fig.legend()
fig.set_xlabel("Date")
fig.set_ylabel("Value")
fig.set_title("DataFrame Column Values Over Time")
fig.show()

# %% Example for custom preset with YAML file
# Create a custom preset configuration
import fast_fig

fast_fig.presets.generate_file(filepath="example_preset.yaml")

# Use the custom preset
fig = FFig(presets="example_preset.yaml")
x = np.linspace(0, 10, 100)
fig.plot(x, np.sin(x), label="sin(x)")
fig.plot(x, np.cos(x), label="cos(x)")
fig.set_xlabel("x")
fig.set_ylabel("y")
fig.set_title("Publication-Ready Plot")
fig.legend()
fig.grid()
fig.show()
# fig.save('publication_plot.png')  # Will save with high DPI and tight layout

# %% Beautiful visualization example

# Create a complex 2D function (a combination of Gaussian peaks)
x = np.linspace(-4, 4, 200)
y = np.linspace(-4, 4, 200)
X, Y = np.meshgrid(x, y)
Z = (
    2 * np.exp(-((X - 1) ** 2 + (Y - 1) ** 2) / 2.0)
    + 1.5 * np.exp(-((X + 1) ** 2 + (Y + 1) ** 2) / 0.8)
    + np.exp(-((X - 2) ** 2 + (Y + 2) ** 2) / 0.3)
)

# Create visualization
fig = FFig("square")  # Use square template
# Create heatmap with custom colormap
fig.pcolor(X, Y, Z, cmap="magma", vmin=0)
# Add contour lines with custom styling
fig.contour(X, Y, Z, levels=8, colors="white", alpha=0.3, linewidths=0.8)
# Add specific contours with different style
fig.contour(X, Y, Z, levels=[0.7], colors="cyan", alpha=0.8, linewidths=2, linestyles="--")

# Customize the plot
fig.set_title("Gaussian Peaks Landscape")
fig.set_xlabel("X Position in mm")
fig.set_ylabel("Y Position in mm")

# Show the result
fig.show()
# fig.save('gaussian_landscape.png', dpi=300)  # Save in high resolution
