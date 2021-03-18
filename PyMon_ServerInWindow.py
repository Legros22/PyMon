from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext

import tkinter as tk
from datetime import datetime

import time
from queue import Queue
from threading import Thread

import logging
import sys

root = Tk()
root.title('PyMon Server (ZIOT)')
root.geometry('{}x{}'.format(800, 350))

# set default color
LABEL_BCKGROUND ="cyan"
ENTRY_COLOR = "pink"



# Logging features
log_separator=' ; '
log_file_name="MonLog.txt"

def MonLog(TraceLine):
    now = datetime.now()
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


# Output Trace Window
# --------------------
output_area = scrolledtext.ScrolledText(Right_frame,
                                      width = 70,
                                      height = 10,
                                      font = ("Courier",10))

output_area.grid(row=2, pady = 10, padx = 10)
# Making the text read only
#output_area.configure(state ='disabled')

MSG_TYPE_ACTION  = 0
MSG_TYPE_SEND    = 1
MSG_TYPE_RECEIVE = 2

# Output cmd to TRACE
def output_send(msg, msg_type):
    if LogComm.get():
        MonLog(msg)                    #log the cmd received
    if msg_type==MSG_TYPE_ACTION:
        output_area.configure(state ='normal')
        output_area. insert(END,"#"+msg+'\n','ACTION_COLOR')
        output_area.tag_config('ACTION_COLOR', foreground='green')
        output_area.see("end")
        output_area.configure(state ='disabled')
    elif msg_type==MSG_TYPE_SEND:
        output_area.configure(state ='normal')
        output_area. insert(END,"> "+msg+'\n','SEND_COLOR')
        output_area.tag_config('SEND_COLOR', foreground='blue')
        output_area.see("end")
        output_area.configure(state ='disabled')
    elif msg_type==MSG_TYPE_RECEIVE:
        output_area.configure(state ='normal')
        output_area. insert(END,msg+'\n','RECEIVE_COLOR')
        output_area.tag_config('RECEIVE_COLOR', foreground='black')
        output_area.see("end")
        output_area.configure(state ='disabled')
    else:
        output_area.configure(state ='normal')
        output_area. insert(END,msg+'\n','ERROR_COLOR')
        output_area.tag_config('ERROR_COLOR', foreground='grey')
        output_area.see("end")
        output_area.configure(state ='disabled')


# input enter Window
# --------------------

def input_area_enter(event):
    global LogComm
    CmdLine = input_area.get(1.0, END) # input cmd from read
    CmdLine = CmdLine.replace("\n","") # supress \n for start of line
    input_area.delete(1.0,END)         # delete input zone
    # Output cmd to TRACE
    output_send(CmdLine, MSG_TYPE_SEND)



input_area = scrolledtext.ScrolledText(Right_frame,
                                      width = 70,
                                      height = 2,
                                      font = ("Courier",10))

input_area.grid(row=3, pady = 10, padx = 10)
input_area.bind('<Return>',input_area_enter)



# --------------- TCP server thread -------------------

def MyTcpServer(in_q):
    ii=0
    RunRequest = 0
    while 1:
        if in_q.empty()==False:
            RunRequest = in_q.get()
            if RunRequest==1:
                output_send("Server wait for Connect (IP="+IP_StrVar.get()+")",MSG_TYPE_ACTION)
            else:
                output_send("Server pause",MSG_TYPE_ACTION)
            time.sleep(0.5)
        if RunRequest==1:
            ii += 1
            output_send(str(ii),MSG_TYPE_SEND)
            time.sleep(0.1)


q = Queue()
t1 = Thread(target = MyTcpServer, args =(q, ))
t1.start()

# -------------- Connexion widget --------------------


def changeConnStatus():
    global ConnStatus
    if ConnStatus==0:
        ConnStatus_txt.set("Disconnected")
        ConnStatus_label.config(fg="black", font='Helvetica 10')
        q.put(ConnStatus)
        ConnStatus = 1
    elif ConnStatus==1:
        ConnStatus_txt.set("Connected "+Port_StrVar.get())
        ConnStatus_label.config(fg="green", font='Helvetica 11 bold')
        q.put(ConnStatus)
        ConnStatus = 0
    else: #Default state
        ConnStatus_txt.set("----")
        ConnStatus_label.config(fg="black", font='Helvetica 10 bold')
        ConnStatus = 0
        q.put(ConnStatus)
    # Output cmd to TRACE
    # output_send(Port_StrVar.get(), MSG_TYPE_ACTION)




# -------------- IP widget --------------------
IP_StrVar   = StringVar(left_frame, value='10.10.11.254')
IP_label    = Label(left_frame, text='IP address :',background = LABEL_BCKGROUND)
IP_entry    = Entry(left_frame, textvariable = IP_StrVar, background=ENTRY_COLOR);
MASK_StrVar = StringVar(left_frame, value='255.255.255.0')
MASK_label  = Label(left_frame, text='IP mask : ',background = LABEL_BCKGROUND)
MASK_entry  = Entry(left_frame, textvariable = MASK_StrVar, background=ENTRY_COLOR)
Port_StrVar = StringVar(left_frame, value='49491')
Port_label  =  Label(left_frame, text='IP port : ',background = LABEL_BCKGROUND)
Port_entry  =  Entry(left_frame, textvariable = Port_StrVar, background=ENTRY_COLOR);

ConnStatus_txt = StringVar()
ConnStatus_label = Label(left_frame, textvariable=ConnStatus_txt,background = LABEL_BCKGROUND)
ConnStatus_txt.set("----")
ConnStatus_label.config(fg="black", font='Helvetica 10 bold')
ConnStatus = 1
Conn_bouton = Button(left_frame, text="Connect", command=changeConnStatus)
Conn_bouton["fg"] = "black"


##entry_L = Entry(Right_frame, background="orange")

# layout the widgets in the top frame
Conn_bouton.grid(row=0, column=0)
ConnStatus_label.grid(row=0, column=1)
IP_label.grid(row=3, column=0)
IP_entry.grid(row=3, column=1)
MASK_label.grid(row=4, column=0)
MASK_entry.grid(row=4, column=1)
Port_label.grid(row=5, column=0)
Port_entry.grid(row=5, column=1)






# Placing cursor in the text area
output_area.focus()


root.mainloop()
