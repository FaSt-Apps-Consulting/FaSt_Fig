# FaSt_Fig
FaSt_Fig is a wrapper for matplotlib that provides a simple interface for fast and easy plotting.

Key functions:
- figure instantiation in a class object
- predefinied templates
- simplified handling (e.g. plot with vectors)
- save to multiple file formats

## Usage
After installation by `pip install fast_fig` you can start with a very simple example:

```python
from fast_fig import FFig

data = np.array([[1,2,3,4,5],[2,4,6,8,10]])
fig = FFig()
fig.plot(data)
fig.show()
```

In the following example, the large template `'l'` is initialized and the figure is saved.

```python
data = np.array([[1,2,3,4,5],[2,4,6,8,10],[1,3,6,7,9]])
fig = FFig('l')
fig.plot(data)
fig.save('test_fig1.png') # save figure
```

FaSt_Fig can also be used as a context manager, which automatically handles figure cleanup:

```python
with FFig('m') as fig:
    fig.plot(data)
    fig.save('plot.png')
    # Figure automatically closed when exiting the with block
```

FaSt_Fig allows for more complex behavior with multiple subplots, legend, grid and saving to multiple files at once.

```python
fig = FFig('l',nrows=2) # create figure with two rows and template 'l'
fig.plot([1,2,3,1,2,3,4,1,1]) # plot first data set
fig.title('First data set') # set title for subplot
fig.next_axis() # set focus to next subplot/axis
fig.plot([0,1,2,3,4],[0,1,1,2,3],label="random") # plot second data set
fig.legend() # generate legend
fig.grid() # show translucent grid to highlight major ticks
fig.xlabel('Data') # create xlabel for second axis
fig.save('test_fig2.png','pdf') # save figure to png and pdf
```

## Plot Types

FaSt_Fig supports various plot types beyond basic line plots:

```python
# Bar plots
fig.bar_plot(x, height)

# Logarithmic scales
fig.semilogx(x, y)  # logarithmic x-axis
fig.semilogy(x, y)  # logarithmic y-axis

# 2D plots
x, y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
z = np.exp(-(x**2 + y**2))

fig.pcolor(z)  # pseudocolor plot
fig.pcolor_log(z)  # pseudocolor with logarithmic color scale
fig.contour(z, levels=[0.2, 0.5, 0.8])  # contour plot
fig.colorbar(label='Values')  # add colorbar

# Scatter plots
fig.scatter(x, y, c=colors, s=sizes)  # scatter plot with colors and sizes
```

## DataFrame Support

FaSt_Fig has built-in support for pandas DataFrames (as optional dependency):

```python
import pandas as pd

# Create a DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [2, 4, 6, 8]
}, index=pd.date_range('2024-01-01', periods=4))

# Plot DataFrame
fig = FFig()
fig.plot(df)  # Each column becomes a line, index is x-axis
# Column names are used as labels
# Date index automatically sets x-label to "Date"
```

## Matplotlib Handles

FaSt_Fig provides direct access to the underlying matplotlib objects through these handles:

- `fig.current_axis`: The currently active axes object. Use this for axis-specific operations like setting scales, limits, or adding specialized plots.
```python
fig.current_axis.set_yscale('log')  # Set y-axis to logarithmic scale
```

- `fig.handle_fig`: The main Figure object. Use this for figure-level operations like adjusting layout or adding subfigures.
```python
fig.handle_fig.tight_layout()  # Adjust subplot parameters for better fit
```

- `fig.handle_plot`: List of Line2D objects from the most recent plot. Use this to modify line properties after plotting.
```python
fig.handle_plot[0].set_linewidth(2)  # Change line width of first line
```

- `fig.handle_axis`: Array of all Axes objects. Use this to access any subplot directly.
```python
fig.handle_axis[0].set_title('First subplot')  # Set title of first subplot
```

These handles give you full access to matplotlib's functionality when you need more control than FaSt_Fig's simplified interface provides.

## Presets

FaSt_Fig comes with built-in presets that control figure appearance. Available preset templates:

- `m` (medium): 15x10 cm, sans-serif font, good for general use
- `s` (small): 10x8 cm, sans-serif font, suitable for small plots
- `l` (large): 20x15 cm, sans-serif font, ideal for presentations
- `ol` (Optics Letters): 8x6 cm, serif font, optimized for single line plots
- `oe` (Optics Express): 12x8 cm, serif font, designed for equation plots
- `square`: 10x10 cm, serif font, perfect for square plots

Each preset defines:
- `width`: Figure width in cm
- `height`: Figure height in cm
- `fontfamily`: Font family (serif or sans-serif)
- `fontsize`: Font size in points
- `linewidth`: Line width in points

You can use presets in three ways:

1. Use a built-in preset:
```python
fig = FFig('l')  # Use large preset
```

2. Load custom presets from a file:
```python
fig = FFig('m', presets='my_presets.yaml')  # YAML format
fig = FFig('m', presets='my_presets.json')  # or JSON format
```

3. Override specific preset values:
```python
fig = FFig('m', width=12, fontsize=14)  # Override width and fontsize
```

The preset system also includes color sequences and line styles that cycle automatically when plotting multiple lines:
- Default colors: blue, red, green, orange
- Default line styles: solid (-), dashed (--), dotted (:), dash-dot (-.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Licensed under MIT License. See [LICENSE](LICENSE) for details.

## Author

Written by Fabian Stutzki (fast@fast-apps.de)

For more information, visit [www.fast-apps.de](https://www.fast-apps.de)