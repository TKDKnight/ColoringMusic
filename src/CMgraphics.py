from matplotlib import pyplot as plt
#import matplotlib.pyplot as plt
from matplotlib import animation as animation
#import matplotlib.animation as animation
import numpy as np

class AnimatedScatter(object):
    """An animated scatter plot using matplotlib.animations.FuncAnimation."""
    def __init__(self, numpoints=8192):
        self.numpoints = numpoints
        self.stream = self.data_stream()

        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()
        self.fig.set_facecolor("black")
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=500, 
                                          init_func=self.setup_plot, blit=False)

    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        x, y, s, c = next(self.stream).T
        self.scat = self.ax.scatter(x, y, c=c, s=s, vmin=0, vmax=1,
                                    cmap="jet", edgecolor="k", marker="s")
        self.ax.axis([0, 20, 0, 128])
        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def data_stream(self):
        x = (np.random.random((self.numpoints, 1))-0.5)
        y = (np.random.random((self.numpoints, 1))-0.5)
        for j in range(self.numpoints):
          x[j] = (j*.1*20)
          y[j] = 60
        
        s, c = np.random.random((self.numpoints, 2)).T

        while True:
#            for j in range(self.numpoints-1):
#               x[j] = x[j+1]
#               y[j] = y[j+1]
#               s[j] = s[j+1]
#               c[j] = c[j+1]
             
#            x[self.numpoints-1] = x[self.numpoints-2] + 0.1*20
            y[self.numpoints-1] = 60 # (np.random.random((1, 1))-0.5)*10
#            s += 0.05 * (np.random.random(self.numpoints) - 0.5)
            c += 0.02 * (np.random.random(self.numpoints) - 0.5)
            yield np.c_[x, y, s, c]

    def update(self, i):
        """Update the scatter plot."""
        data = next(self.stream)

#        if i > 100:
#        self.ax.set_xlim(max(0, (i-75-1)*.1 - 10), (i-75)*.1+10)
        left, right = self.ax.get_xlim() 
        self.ax.set_xlim(left + 0.1, right + 0.1 )

        # Set x and y data...
        self.scat.set_offsets(data[:, :2])
        # Set sizes...
        self.scat.set_sizes(100 * abs(data[:, 2])**1)
        # Set colors..
        self.scat.set_array(1*data[:, 3]+-2.21230855e-02)

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,


if __name__ == '__main__':
    a = AnimatedScatter()
    plt.show()

