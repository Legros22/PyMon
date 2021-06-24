#-------------------------------------------------------------------------------
# Name:        My_Logger
# Purpose:
#
# Author:      Philippe
#
# Created:     20/06/2021
# Copyright:   (c) Philippe 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from tkinter import *
import tkinter as tk

#used to time stamp each line of log file.
from datetime import datetime

#used for file access
import sys

import json

# Used to select log file
from tkinter.filedialog import askopenfilename

#used to display a popup telling the file is cleared
import pymsgbox

#import Configuration tools (graphic and saved configuration
from PyMon_ConfigFile import *

# set default color
##WIN_FORGROUNG = "#EEE"
##WIN_HIGH_LIGHT ="#CCC"
##WIN_BACKGROUND = "#333"
##TRACE_BACKGROUNG = "#AAA"
##CMD_BACKGROUND = "#EEE"
##
##LABEL_BACKGROUND = WIN_BACKGROUND
##LABEL_FOREGROUND = WIN_FORGROUNG
##ENTRY_COLOR     = CMD_BACKGROUND
##
##BUTTON_DEF_WIDTH = 10
##ENTRY_DEF_WIDTH = 15

cg = ConfigGraph()

class Logger():

    def __init__(self,FatherFrame,section_name="MyLog"):
        #manage configuration file
        cf=ConfigFile()
        self.cf = ConfigFile()
        self.conf_section = section_name

        # Save frame where button and text shall be displayed
        self.FatherFrame = FatherFrame
        self.log_file_name = self.cf.take(self.conf_section,"FileName",section_name+".txt")
        self.log_separator = self.cf.take(self.conf_section,"Separator",";")

        #Create var, label, check button
        self.LogComm = IntVar()
        self.LogCommTxt = StringVar()
        self.LogCommTxt.set('Log file (OFF)')
        self.LogSel = Checkbutton(FatherFrame,
                            fg = cg.CMD_BACKGROUND, bg = cg.WIN_BACKGROUND,
                            activebackground=cg.WIN_BACKGROUND, activeforeground=cg.CMD_BACKGROUND,
                            selectcolor = cg.WIN_BACKGROUND,
                            textvariable=self.LogCommTxt,variable=self.LogComm, onvalue=1, offvalue=0,
                            command=self.ToggleLogFile)
        self.LogSel.grid(row=0,column=0,padx = 10, columnspan=1, sticky="w")

        #button to change file name
        self.File_bouton = Button(FatherFrame, text="File...", width = cg.BUTTON_DEF_WIDTH, command=self.select_file)
        self.File_bouton.grid(row=0,column=1,padx = 10, sticky="e")
        self.File_bouton["fg"]  = "black"

        #button to clear file
        self.clear_bouton = Button(FatherFrame, text="Clear file", width = cg.BUTTON_DEF_WIDTH, command=self.clear_file)
        self.clear_bouton.grid(row=0,column=2,padx = 10, sticky="e")
        self.clear_bouton["fg"]  = "black"



    # Logger selection
    # --------------------
    def ToggleLogFile(self):
        if self.LogComm.get():
            self.LogCommTxt.set("Log file (ON:\""+self.log_file_name+"\")")
        else:
            self.LogCommTxt.set('Log file (OFF)')


    # Logger file selection
    def select_file(self):
        #filename = askopenfilename(title='Select File for Logging')
        filename = askopenfilename(title='Select File for Logging', filetypes=(
                    ("text format", ".txt"),
                    ("text format", ".log"),
                    ("text format", ".csv"),
                ))
        if filename:
            self.log_file_name = filename
            self.cf.put(self.conf_section,"FileName",self.log_file_name)
            if self.LogComm.get():
                self.LogCommTxt.set("Log file (ON:\""+self.log_file_name+"\")")

    def clear_file(self):
        with open(self.log_file_name, 'w') as LogFile:  # Use file to refer to the file object
            LogFile.close()
        pymsgbox.alert("File is now empty !", "info")


    def save(self,TraceLine):
        if self.LogSel:
            now = datetime.now()
            timeStamp = now.strftime("%d/%m/%Y"+self.log_separator+"%H:%M:%S")
            with open(self.log_file_name, 'a') as LogFile:  # Use file to refer to the file object
                LogFile.write(timeStamp+self.log_separator+TraceLine+'\n')
                LogFile.close()



def main():
    root = Tk()
    root.title('Unitary test for MyLogger')
    root.geometry('{}x{}'.format(800, 550))

    left_frame = Frame(root,highlightbackground=cg.WIN_HIGH_LIGHT, highlightthickness=1,
                    bg=cg.LABEL_BACKGROUND, width=160, height=50, pady=3)
    left_frame.grid(row=0, column=0, sticky="nw")

    # create all of the main containers
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    Right_frame = Frame(root, bg=cg.WIN_BACKGROUND,
                        highlightbackground=cg.WIN_HIGH_LIGHT, highlightthickness=1,
                        width=300, height=50, pady=3)
    Right_frame.grid(row=0, column=1,sticky="nsew")
    Right_frame.grid_columnconfigure(0, weight=1)
    Right_frame.grid_rowconfigure(1, weight=1)

    MyLog = Logger(Right_frame,"toto")
    MyLog.save("Toto est parti a la plage")




    root.mainloop()


if __name__ == '__main__':
    main()
