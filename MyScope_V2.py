
#-------------------------------------------------------------------------------
# Name:        Scope
# Purpose:     Object display measurement points as long as they are measured
#
# Author:      Legros
#
# Created:     20/06/2021
# Copyright:   (c) Legros 2021
# License:     Private Property
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Inspiration : https://stackoverflow.com/questions/10944621/dynamically-updating-plot-in-matplotlib
#-------------------------------------------------------------------------------
#used to plot graphs
import matplotlib.pyplot as plt

#used for math vector generation (in main only)
import numpy as np
#used for delay (in main only)
import time

#enable interractive mode for plot
plt.ion()

class Scope():

    def __init__(self, fig, ax, max_points = 50, dt=1.0):
         #Suppose we know the x range
        self.min_x = 0
        self.max_x = 10
        self.dt = dt    # default Delay between 2 points
        self.max_points = max_points  #max number of points to display.
        #Set up plot
        self.figure = fig
        self.ax = ax
        self.lines, = self.ax.plot([],[], 'o-')
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()
        #list of points
        self.xdata = []
        self.ydata = []


    def on_running(self):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(self.xdata)
        self.lines.set_ydata(self.ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        max10 = max(max(self.xdata),10)
        self.ax.set_xlim(min(self.xdata), max10)
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


    def add_point_xy(self, x, y):
        #set x, pass None if not used
        if x==None: #x not used, step is self.dt
            if self.xdata: #not empty list
                self.xdata.append(self.xdata[-1]+self.dt)
            else:
                self.xdata.append(0)
        else:       #x is defined
            self.xdata.append(x)
        #set y, pass None if not used
        self.ydata.append(y)
        #delete first point if the max number of points to plot is reached.
        if (len(self.xdata) > self.max_points):
            self.xdata.pop(0)
            self.ydata.pop(0)
        self.on_running()



# main is a unitary test (+ demonstration) features

def main():
    fig, ax = plt.subplots()
    scope = Scope(fig, ax)
    for x in np.arange(0,20,0.5):
        y = np.exp(-x**2)+10*np.exp(-(x-7)**2)
        scope.add_point_xy(None, y)
        time.sleep(0.25)


if __name__ == '__main__':
    main()
