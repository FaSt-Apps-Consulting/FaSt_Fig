"""Script gives some examples for the use of FaSt_Fig."""

# %%
import numpy as np

from fast_fig import FFig

# %% Very simple example
fig = FFig()
fig.plot([1, 1, 4, 1])
fig.plot([2, 3, 4, 1])
fig.legend()
fig.show()
# fig.save("FaSt_Fig_example.png")  # noqa: ERA001

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
fig.save("fig1.png", "pdf")  # save figure to png and pdf  # noqa: ERA001


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
# fig.save("example_pcolor.png")  # save figure to png and pdf  # noqa: ERA001
fig.show()
