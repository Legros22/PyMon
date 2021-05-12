#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Philippe
#
# Created:     11/05/2021
# Copyright:   (c) Philippe 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext

import tkinter as tk

import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


import numpy as np


# set default color
WIN_FORGROUNG = "#EEE"
WIN_HIGH_LIGHT ="#CCC"
WIN_BACKGROUND = "#333"
TRACE_BACKGROUNG = "#AAA"
CMD_BACKGROUND = "#EEE"

LABEL_BACKGROUND = WIN_BACKGROUND
LABEL_FOREGROUND = WIN_FORGROUNG
ENTRY_COLOR     = CMD_BACKGROUND

BUTTON_DEF_WIDTH = 10
ENTRY_DEF_WIDTH = 15



class ResultWindow:

    def __init__(self,rootWindow):
        win = Toplevel(rootWindow)
        win.title('PyMon Display Result')
        win.geometry('{}x{}'.format(500, 500))


        left_frame = Frame(win,highlightbackground=WIN_HIGH_LIGHT, highlightthickness=1,
                            bg=LABEL_BACKGROUND, width=160, height=50, pady=3)
        left_frame.grid(row=0, column=0, sticky="nw")

        # create all of the main containers
        win.grid_columnconfigure(1, weight=1)
        win.grid_rowconfigure(0, weight=1)

        Right_frame = Frame(win, bg=WIN_BACKGROUND,
                            highlightbackground=WIN_HIGH_LIGHT, highlightthickness=1,
                            width=300, height=50, pady=3)
        Right_frame.grid(row=0, column=1,sticky="nsew")
        Right_frame.grid_columnconfigure(0, weight=1)
        Right_frame.grid_rowconfigure(1, weight=1)

        # Output value scroll window
        # --------------------------
        self.output_area = scrolledtext.ScrolledText(left_frame,
                                              width = 15,
                                              height = 20,
                                              bg = TRACE_BACKGROUNG,
                                              font = ("Courier",10))

        self.output_area.grid(row=0, column=0, columnspan =2, pady = 15, padx = 10, sticky="nsew")
        self.output_area.grid_columnconfigure(0, weight=1)
        self.output_area.grid_rowconfigure(0, weight=1)

        # Output value graphical window
        # --------------------------

        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

        canvas = FigureCanvasTkAgg(fig, master=Right_frame)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, Right_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


        def on_key_press(event):
            print("you pressed {}".format(event.key))
            key_press_handler(event, canvas, toolbar)


        canvas.mpl_connect("key_press_event", on_key_press)


        def _quit():
            win.quit()     # stops mainloop
            win.destroy()  # this is necessary on Windows to prevent
                            # Fatal Python Error: PyEval_RestoreThread: NULL tstate


        button = tkinter.Button(master=Right_frame, text="Quit", command=_quit)
        button.pack(side=tkinter.BOTTOM)




    def AddResult(self, value,unit):
        self.output_area.configure(state ='normal')
        # self.output_area. insert(END,str(value)+" "+unit+'\n','WIN_FORGROUNG')
        self.output_area. insert(END,"{:.2f}".format(value)+" "+unit+'\n','WIN_FORGROUNG')

        self.output_area.tag_config('ACTION_COLOR', foreground='green')
        self.output_area.see("end")
        self.output_area.configure(state ='disabled')


def main():
    root = Tk()
    root.title('Root Window')
    root.geometry('{}x{}'.format(800, 550))

    rWin = ResultWindow(root)
    rWin.AddResult(12.0,"Ohm")
    rWin.AddResult(50,"Ω")
    t = np.arange(0, 3, .1)
    y = 100*np.sin(2 * np.pi * t)

    for val in y:
        rWin.AddResult(val,"Ω")


    root.mainloop()


if __name__ == '__main__':
    main()
