# FaSt_Fig
FaSt_Fig is a wrapper for matplotlib that provides a simple interface for fast and easy plotting.

## Usage
After installation by `pip install fast_fig` you can start with a very simple example:

```python
from fast_fig import FFig
fig = FFig()
fig.plot()
fig.show()
```

You can also start with your own data, change to a large templateand save the figure.

```python
data = np.array([[1,2,3,4,5],[2,4,6,8,10]])
fig = FFig('l')
fig.plot(data)
fig.save('test_fig1.png')
```

FaSt_Fig allows for more complex behavior with multiple subplots, legend, grid and saving to multiple files at once.

```python
fig = FFig('l',nrows=2) # create figure with two rows and template 'l'
fig.plot([1,2,3,1,2,3,4,1,1]) # plot first data set
fig.title('First data set') # set title for subplot
fig.subplot() # set focus to next subplot/axis
fig.plot([0,1,2,3,4],[0,1,1,2,3],label="random") # plot second data set
fig.legend() # generate legend
fig.grid() # show translucent grid to highlight major ticks
fig.xlabel('Data') # create xlabel for second axis
fig.save('test_fig2.png','pdf') # save figure to png and pdf
```

Written by Fabian Stutzki, fast@fast-apps.de

Licensed under MIT

