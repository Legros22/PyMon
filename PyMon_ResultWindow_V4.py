#-------------------------------------------------------------------------------
# Name:        PyMon_ResultWindow V4
# Purpose:     Object ResultWindow to create a GUI for meaurement display :
#              Array of value, graphical display, log of measurements.
#
# Author:      Legros
#
# Created:     20/06/2021
# Copyright:   (c) Legros 2021
# License:     Private Property
#-------------------------------------------------------------------------------

# graphic interface library
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import tkinter as tk
import tkinter
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Simplifier les imports de tkinter

# import for displaying a plot (from matplotlib) in tkinter
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#used for delay (in main only)
import time

#used for math vector generation (in main only)
import numpy as np

#import scope object
from MyScope_V2 import Scope

#import logger object
from PyMon_Logger import Logger

#import Configuration tools (graphic and saved configuration
from PyMon_ConfigFile import *
# create object to share graph configuration
cg = ConfigGraph()


# Class to create a GUI for meaurement display :
# Array of value, graphical display, log of measurements.
class ResultWindow:

    def __init__(self,rootWindow):
        win = Toplevel(rootWindow)
        win.title('PyMon Display Result')
        win.geometry('{}x{}'.format(700, 700))


        left_frame = Frame(win,highlightbackground=cg.WIN_HIGH_LIGHT, highlightthickness=1,
                            bg=cg.LABEL_BACKGROUND, width=160, height=50, pady=3)
        left_frame.grid(row=0, column=0, sticky="nw")

        # create all of the main containers
        win.grid_columnconfigure(1, weight=1)
        win.grid_rowconfigure(0, weight=1)

        Right_frame = Frame(win, bg=cg.WIN_BACKGROUND,
                            highlightbackground=cg.WIN_HIGH_LIGHT, highlightthickness=1,
                            width=300, height=50, pady=3)
        Right_frame.grid(row=0, column=1,sticky="nsew")
        Right_frame.grid_columnconfigure(0, weight=1)
        Right_frame.grid_rowconfigure(1, weight=1)

        # Output value scroll window
        # --------------------------
        self.output_area = scrolledtext.ScrolledText(left_frame,
                                              width = 15,
                                              height = 20,
                                              bg = cg.TRACE_BACKGROUND,
                                              font = ("Courier",10))

        self.output_area.grid(row=0, column=0, columnspan =2, pady = 15, padx = 10, sticky="nsew")
        self.output_area.grid_columnconfigure(0, weight=1)
        self.output_area.grid_rowconfigure(0, weight=1)

        # Output value graphical window
        # ------------------------------

        #create the plot
        self.fig, self.ax = plt.subplots()

        #create the Scope object to diplay measurement in plot
        self.scope = Scope(self.fig, self.ax, max_points = 100)

        # Set self.fig in the Right_frame
        canvas = FigureCanvasTkAgg(self.fig, master=Right_frame)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # Add tool bar to the Right_frame
        toolbar = NavigationToolbar2Tk(canvas, Right_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        plt.pause(0.1)


        def on_key_press(event):
            print("you pressed {}".format(event.key))
            key_press_handler(event, canvas, toolbar)


        canvas.mpl_connect("key_press_event", on_key_press)


        def _quit():
            win.quit()     # stops mainloop
            win.destroy()  # this is necessary on Windows to prevent
                            # Fatal Python Error: PyEval_RestoreThread: NULL tstate


        # Add logger object below the scope.
        self.Log_frame = Frame(Right_frame,highlightbackground=cg.WIN_HIGH_LIGHT, highlightthickness=1,
                            bg=cg.LABEL_BACKGROUND, height=50, pady=3)
        self.Log_frame.pack(side=tkinter.BOTTOM)

        self.logger = Logger(self.Log_frame)
        (grid_x, grid_y) =self.Log_frame.grid_size() #grid_size return tuple (1,3), when grid is set in row 0
        # button Quit
        #self.button = tkinter.Button(master=Right_frame, text="Quit", command=_quit)
        self.button = tkinter.Button(master=self.Log_frame, text="Quit", command=_quit)
        #use grid inside the log_frame layout, addit 'Quit' button to the right
        self.button.grid(row=grid_y-1,column=grid_x+1,padx = 10, sticky="e")
        # pack theLog_frame layout to use all the width (X)
        self.Log_frame.pack(fill = tkinter.X, side=tkinter.BOTTOM)



    #method to add a value to the result window. value is float, unit is text.
    def AddResult(self, value,unit):
        self.output_area.configure(state ='normal')
        self.output_area.insert(END,"{:.2f}".format(value)+" "+unit+'\n','cg.WIN_FORGROUNG')

        self.output_area.tag_config('ACTION_COLOR', foreground='green')
        self.output_area.see("end")
        self.output_area.configure(state ='disabled')

        #received value is ploted in scope
        self.scope.add_point_xy(None, value)

        #log value if logger is enabled
        self.logger.save(str(value));

    def __del__(self):
        del self.scope
        print("destruct ResultWindow")



# main is a unitary test (+ demonstration) features
def main():
    print("Create Root Window")
    root = Tk()
    root.title('Root Window')
    root.geometry('{}x{}'.format(800, 550))

    print("Create Result Window")
    rWin = ResultWindow(root)

    if 1:
        rWin.AddResult(0.22,"Ohm")
        rWin.AddResult(0.5,"Ω")
        t = np.arange(0, 5, .01)
        y = 1*np.sin(2 * np.pi * t)


        for tt in np.arange(0, 5, .05):
            y = 1*np.sin(2 * np.pi * tt)
            rWin.AddResult(y,"Ω")
            time.sleep(0.1)

    root.mainloop()

if __name__ == '__main__':
    main()
