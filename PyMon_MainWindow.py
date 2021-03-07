from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext

import tkinter as tk
from datetime import datetime

import logging
import sys

root = Tk()
root.title('PyMon for ZIOT')
root.geometry('{}x{}'.format(460, 350))

# set default color
LABEL_BCKGROUND ="cyan"
ENTRY_COLOR = "pink"



# Logging features
now = datetime.now()
log_separator=' ; '
log_file_name="MonLog.txt"

def MonLog(TraceLine):
    timeStamp = now.strftime("%d/%m/%Y"+log_separator+"%H:%M:%S")
    with open(log_file_name, 'a') as LogFile:  # Use file to refer to the file object
        LogFile.write(timeStamp+log_separator+TraceLine+'\n')


# create all of the main containers
top_frame = Frame(root, bg=LABEL_BCKGROUND, width=450, height=50, pady=3)
btm_frame = Frame(root, bg='white', width=450, height=45, pady=3)

left_frame = Frame(top_frame, bg=LABEL_BCKGROUND, width=150, height=50, pady=3)
##left_frame = top_frame
Right_frame = Frame(top_frame, bg='green', width=300, height=50, pady=3)

# layout all of the main containers
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="nsew")
left_frame.grid(row=0, column=0)
Right_frame.grid(row=0, column=1)
btm_frame.grid(row=1, sticky="ew")


# create the widgets for the top frame
# =====================================

# -------------- Connexion widget --------------------


def changeConnStatus():
    global ConnStatus
    if ConnStatus==0:
        ConnStatus_txt.set("Disconnected")
        ConnStatus_label.config(fg="black", font='Helvetica 10')
        ConnStatus = 1
    elif ConnStatus==1:
        ConnStatus_txt.set("Connected")
        ConnStatus_label.config(fg="green", font='Helvetica 11 bold')
        ConnStatus = 0
    else: #Default state
        ConnStatus_txt.set("----")
        ConnStatus_label.config(fg="black", font='Helvetica 10 bold')
        ConnStatus = 0


ConnStatus_txt = StringVar()
ConnStatus_label = Label(left_frame, textvariable=ConnStatus_txt,background = LABEL_BCKGROUND)
ConnStatus = -1;
changeConnStatus()

Conn_bouton = Button(left_frame, text="Connect", command=changeConnStatus)
Conn_bouton["fg"] = "black"



# -------------- IP widget --------------------
IP_label = Label(left_frame, text='IP address :',background = LABEL_BCKGROUND)
IP_entry = Entry(left_frame, background=ENTRY_COLOR);
MASK_label = Label(left_frame, text='IP mask : ',background = LABEL_BCKGROUND)
MASK_entry = Entry(left_frame, background=ENTRY_COLOR);


##entry_L = Entry(Right_frame, background="orange")

# layout the widgets in the top frame
Conn_bouton.grid(row=0, column=0)
ConnStatus_label.grid(row=0, column=1)
IP_label.grid(row=3, column=0)
IP_entry.grid(row=3, column=1)
MASK_label.grid(row=4, column=0)
MASK_entry.grid(row=4, column=1)

# create the center widgets
top_frame.grid_rowconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=1)

##ctr_left = Frame(center, bg='blue', width=100, height=190)
##ctr_mid = Frame(center, bg='yellow', width=250, height=190, padx=3, pady=3)
##ctr_right = Frame(center, bg='green', width=100, height=190, padx=3, pady=3)
##
##ctr_left.grid(row=0, column=0, sticky="ns")
##ctr_mid.grid(row=0, column=1, sticky="nsew")
##ctr_right.grid(row=0, column=2, sticky="ns")

# Logger selection
# --------------------
def ToggleLogFile ():
    if LogComm.get():
        LogCommTxt.set("Log ON (\""+log_file_name+"\")")
    else:
        LogCommTxt.set('Log OFF')

LogComm = IntVar()
LogCommTxt = StringVar()
LogCommTxt.set('Log OFF')
LogSel = Checkbutton(Right_frame, textvariable=LogCommTxt,variable=LogComm, onvalue=1, offvalue=0, command=ToggleLogFile)
LogSel.grid(row=1,column=0)


#COMMENT_label = Label(Right_frame, text='TRACES',background = LABEL_BCKGROUND)
#COMMENT_label.grid(row=1, column=1)


##output_area = scrolledtext.ScrolledText(Right_frame,
##                                      wrap = root.WORD,
##                                      width = 40,
##                                      height = 10,
##                                      font = ("Times New Roman",15))
output_area = scrolledtext.ScrolledText(Right_frame,
                                      width = 40,
                                      height = 10,
                                      font = ("Courier",12))

output_area.grid(row=2, pady = 10, padx = 10)
# Making the text read only
#output_area.configure(state ='disabled')


def input_area_enter(event):
    global LogComm
    CmdLine = input_area.get(1.0, END) # input cmd from read
    CmdLine = CmdLine.replace("\n","") # supress \n for start of line
    input_area.delete(1.0,END)         # delete input zone
    if LogComm.get():
        MonLog(CmdLine)                    #log the cmd received

    # Output cmd to TRACE
    output_area.configure(state ='normal')
    output_area. insert(END,"> "+CmdLine+'\n','CmdColor')
    output_area.tag_config('CmdColor', foreground='blue')
    output_area.see("end")
    output_area.configure(state ='disabled')



input_area = scrolledtext.ScrolledText(Right_frame,
                                      width = 40,
                                      height = 2,
                                      font = ("Courier",12))

input_area.grid(row=3, pady = 10, padx = 10)
input_area.bind('<Return>',input_area_enter)


# Placing cursor in the text area
output_area.focus()
##stext = init.ScrolledText(Right_frame, bg='white', height=10)
####stext.insert(END, __doc__)
##stext.insert(END, "toto est a la plage")
##stext.pack(fill=BOTH, side=LEFT, expand=True)
##stext.focus_set()
##stext.mainloop()



root.mainloop()
