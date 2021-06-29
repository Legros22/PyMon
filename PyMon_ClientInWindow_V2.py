#-------------------------------------------------------------------------------
# Name:        PyMon_ClientInWindow
# Purpose:     Program to have an easy interface with the embedded monitor
#
# Author:      Legros
#
# Created:     21/03/2021
# Copyright:   (c) Legros 2021
# License:     Private Property
#-------------------------------------------------------------------------------

# graphic interface library
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import tkinter as tk

#For Time stamping of log ========================> Should be deleted or kept to timestamp measurements
from datetime import datetime

#used for delay (in main only)
import time


#used to display a popup telling the file is cleared
import pymsgbox

#queue are used to give access to the message received from network
# (more than only printing on the monitor
from multiprocessing import Queue
queue_in = Queue()

#used for network interface
from threading import Thread
import socket

# ================ > should be deleted
import logging

# ================ > should be deleted
import sys

# ================ > should be deleted
import json

#import regular expression tool to analyse ZIOT response
import re

#import logger object
from PyMon_Logger import Logger

#import result window to show measurements
from PyMon_ResultWindow_V4 import ResultWindow

#import Configuration tools (graphic and saved configuration
from PyMon_ConfigFile import *
# create object to share graph configuration
cg = ConfigGraph()
cf = ConfigFile()
CF_ETHERNET_SECTION="Ethernet"


root = Tk()
root.title('PyMon CLient (ZIOT)')
root.geometry('{}x{}'.format(1300, 550))




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

# create the widgets for right frame
# =====================================

#create and place logger object
Log_frame = Frame(Right_frame,highlightbackground=cg.WIN_HIGH_LIGHT, highlightthickness=1,
                            bg=cg.LABEL_BACKGROUND, height=50, pady=3)
Log_frame.grid(row=0,column=0,padx = 10, columnspan=2, sticky="w")
logger = Logger(Log_frame, "Monitor")




# Output Trace Window
# --------------------
output_area = scrolledtext.ScrolledText(Right_frame,
                                      width = 70,
                                      height = 10,
                                      bg = cg.TRACE_BACKGROUND,
                                      font = ("Courier",10))

output_area.grid(row=1, column=0, columnspan =2, pady = 15, padx = 10, sticky="nsew")
output_area.grid_columnconfigure(0, weight=1)
output_area.grid_rowconfigure(0, weight=1)


# input enter Window
# --------------------
IP_label = Label(Right_frame, fg = cg.WIN_FOREGROUND, bg = cg.WIN_BACKGROUND, text='Manual command :')
IP_label.grid(row=3, column=0,pady = 0, padx = 10, sticky="nw")



def input_area_enter(event):
#    global LogComm
    CmdLine = input_area.get(1.0, END) # input cmd from read
    CmdLine = CmdLine.replace("\n","") # supress \n for start of line
    input_area.delete(1.0,END)         # delete input zone
    # Output cmd to TRACE
##    output_send("{"+CmdLine+"}", MSG_TYPE_SEND)
    output_queue.put_nowait(("{"+CmdLine+"}", MSG_TYPE_SEND))

    MyTCP_SendToServer(CmdLine)

input_area = scrolledtext.ScrolledText(Right_frame,
                                      width = 50,
                                      height = 2,
                                      bg = cg.CMD_BACKGROUND,
                                      foreground='blue',
                                      font = ("Courier",10))

input_area.grid(row=4, column=0, pady = 10, padx = 10, sticky="ew",)
input_area.grid_columnconfigure(0, weight=1)
input_area.bind('<Return>',input_area_enter)



MSG_TYPE_ACTION  = 0
MSG_TYPE_SEND    = 1
MSG_TYPE_RECEIVE = 2

# Output cmd to TRACE
def output_send(msg, msg_type):
    logger.save(msg)               #log the cmd received
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

## =============================================================
## =============================================================
## =============================================================

output_queue = Queue()

def output_pull_queue():
    while (1):
        msg, msg_type =output_queue.get(block=True, timeout=None)
        output_send(msg,msg_type)


Thread_output = Thread(target = output_pull_queue, args =())
Thread_output.start()

output_queue.put_nowait(("Mon message de sortie",MSG_TYPE_ACTION))

## =============================================================
## =============================================================
## =============================================================


# --------------- TCP client mamagement -------------------

ClientState = 0
#client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def ProcessReveivedMsg(client):
    try:
##        output_send('in ProcessReveivedMsg()',MSG_TYPE_ACTION)
        output_queue.put_nowait(('in ProcessReveivedMsg()',MSG_TYPE_ACTION))

        while 1:
            MyFrame = client.recv(1024)
            if not MyFrame:
##                output_send('Client quit',MSG_TYPE_ACTION)
                output_queue.put_nowait(('Client quit',MSG_TYPE_ACTION))
                break #quit while
            else:
                #convert the "byte" received to a string
                FrameStr = MyFrame.decode('UTF-8')
                rameStr = FrameStr.replace("\n","") # supress \n for start of line
                #FrameStr = FrameStr.replace("\r","") # supress \r for start of line

                #filter received string with just empty string
                #(an empty string always follow a string...)
                if (len(FrameStr)!=0):
                    #display the received msg
##                    output_send(FrameStr,MSG_TYPE_RECEIVE)
                    output_queue.put_nowait((FrameStr,MSG_TYPE_RECEIVE))
                    #push reception to the queue_in
                    queue_in.put_nowait(FrameStr)

    except:
        MyEnd = 0
        # except is used to catch the error when client.rev is waiting a message
        # and client is closed by client.close()


def MyTcpClient(in_q):
    ii=0
    ClientState = 0
    ServerRequest = 0
    while 1:
        #Check if a command is received from main task
        if in_q.empty()==False:
            ServerRequest = in_q.get()

        #if server is disabled, check if it has to be launched
        if ClientState==0:
            if (ServerRequest==1):  # Request server connexion
                # bind socket to server IP and Port
                Port = int(Port_StrVar.get())
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((IP_StrVar.get(),int(Port_StrVar.get())))
                txt='Connection to '+IP_StrVar.get()+', port='+Port_StrVar.get()
##                output_send(txt,MSG_TYPE_ACTION)
                output_queue.put_nowait((txt,MSG_TYPE_ACTION))
                ClientState = 1

        #if server is enabled, check if it has to be stoped
        if ClientState==1:
            if (ServerRequest==0):  # Request server connexion
##                output_send('Disconnect',MSG_TYPE_ACTION)
                output_queue.put_nowait(('Disconnect',MSG_TYPE_ACTION))
                client.close()
                #note : This will cause "ProcessReveivedMsg" exception
##                Thread_ProcessReveivedMsg.join()
                ClientState = 0

        time.sleep(1)
        ii += 1
##        output_send(str(ii),MSG_TYPE_SEND)
        output_queue.put_nowait((str(ii),MSG_TYPE_SEND))

##        if(ClientState==1):
##            client.send(('hello +'+str(ii)).encode())



##Thread_MyTcpClient = Thread(target = MyTcpClient, args =(q, ))
##Thread_MyTcpClient.start()



def MyTCP_ConnectToServer():
    global ClientState
    global client
    #manage client connection to the server
    Port = int(Port_StrVar.get())
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #client connection to server
        client.connect((IP_StrVar.get(),int(Port_StrVar.get())))
        txt='Connection to '+IP_StrVar.get()+', port='+Port_StrVar.get()
        output_queue.put_nowait((txt,MSG_TYPE_ACTION))
        ClientState = 1
        #Launch thread to receive data
        Thread_ProcessReveivedMsg = Thread(target = ProcessReveivedMsg, args =(client, ))
        Thread_ProcessReveivedMsg.start()
        output_queue.put_nowait(('Receiving thread is started',MSG_TYPE_ACTION))

        #widget management
        ConnStatus_txt.set("Connected")
        ConnStatus_label.config(fg="green", font='Helvetica 11 bold')

    except:
        output_queue.put_nowait(("Server refuse connection",MSG_TYPE_ACTION))
        ClientState = 0
        #widget management
        ConnStatus_txt.set("Disconnected")
        ConnStatus_label.config(fg="black", font='Helvetica 10')

def MyTCP_DisConnectToServer():
    global ClientState
    global client
    try:
        #manage client connection to the server
        output_queue.put_nowait(('Disconnect',MSG_TYPE_ACTION))
        client.close()
        #note : This will cause "ProcessReveivedMsg" exception
        Thread_ProcessReveivedMsg.join()
        ClientState = 0
    except:
        ClientState = 0
    #manage widget
    ConnStatus==0
    ConnStatus_txt.set("Disconnected")
    ConnStatus_label.config(fg="black", font='Helvetica 10')

def MyTCP_SendToServer(strMessage):
    global ClientState
    global client
    if(ClientState==1):
        try:
            client.send(strMessage.encode())
        except:
            output_queue.put_nowait(("Can't send to Server",MSG_TYPE_ACTION))
            MyTCP_DisConnectToServer()
    else:
        output_queue.put_nowait(("Connect to Server before to send message.",MSG_TYPE_ACTION))

# -------------- Connexion widget --------------------


def changeConnStatus():
    global ClientState
    if ClientState==0:
        MyTCP_ConnectToServer()
    elif ClientState==1:

        MyTCP_DisConnectToServer()
    else: #Default state
        ConnStatus_txt.set("----")
        ConnStatus_label.config(fg="black", font='Helvetica 10 bold')
        ClientState==0



# ---------- Popup Window for Rf Measurement -------------

def ZIOT_SendReceive(msg, MaxDelay_ms):
    # if a message has to be sent.
    if msg!=None:
        output_queue.put_nowait((msg, MSG_TYPE_SEND))
        MyTCP_SendToServer(msg)
    # wait reception of a message with a max delay.
    # return None if no message is received before delay.
    try:
        response = queue_in.get(block=True, timeout=MaxDelay_ms/1000)
    except:
        response = None
    return response

def Rf_create(save):

    #analyse response with regular expression
    ##   /RF\s*:\s*([0-9]*\.[0-9]*)/gm
    # First regular expression to identify line "RF    : 3135.10742 Ohm"
    p_line = re.compile('RF\s*:\s*([0-9]*\.[0-9]*)')
    # second regular expression to identify line "3135.10742"
    p_val  = re.compile('[0-9]*\.[0-9]*')

    #create result window
    rWin = ResultWindow(root)

    #empty reception queue
    while queue_in.empty()==False:
        queue_in.get_nowait()

    #repeat 10 Rf estimation
    for i in range(1,100):
        print("=========== "+str(i)+" ===========")
        #send command 'S2' to request Rf measurement.
        response = ZIOT_SendReceive('S2', 2000)
        if response==None:
            output_queue.put_nowait(("Response expected, not received", MSG_TYPE_SEND))
            return
        if (save):
            response = ZIOT_SendReceive('1', 3000)
        else:
            response = ZIOT_SendReceive('0', 3000)

        while response!=None:
            m = p_line.search(response)
            if m!=None:
                #print(m)
                #print(m.group())
                m = p_val.search(response)
                if m!=None:
                    #print(m)
                    print(m.group())
                    rWin.AddResult(float(m.group()),"Ω")

            #ask for next answer.
            response = ZIOT_SendReceive(None, 1000)




## pour récuperer la valeur de resistance dans : T1[Z,|Z|,RF,Lm], T2[|U|,U_RMS]  : 23.65427  + 270.62933 j : 271.66110 : 3119.93384 Ohm : 0.02370 H : 0.15680 V : 0.45808 V
#  /T1\[Z,\|Z\|,RF,Lm\], T2\[\|U\|,U_RMS\] (\d|\s|\.|\+|j)*:(\d|\s|\.|\+|j)*:(\d|\s|\.|\+|j)*: ([0-9]*\.[0-9]*)/gm

def Rf_createSave():
    Rf_create(True)

def Rf_createNotSave():
    Rf_create(False)

# ---------- Manage IP settings -------------

#Load settings in configuration file
ADDRESS = cf.take(CF_ETHERNET_SECTION,"addrIPv4","192.168.1.11")
MASK    = cf.take(CF_ETHERNET_SECTION,"maskIPv4","255.25.0.0")
PORT    = cf.take(CF_ETHERNET_SECTION,"portIPv4",4101)

#callback to save settings in configuration file when Entry is modified
def IP_StrVar_modified(*args):
    cf.put(CF_ETHERNET_SECTION,"addrIPv4",IP_StrVar.get())
def MASK_StrVar_modified(*args):
    cf.put(CF_ETHERNET_SECTION,"maskIPv4",MASK_StrVar.get())
def Port_StrVar_modified(*args):
    try:
        cf.put(CF_ETHERNET_SECTION,"portIPv4",int(Port_StrVar.get()))
    except:
        cf.put(CF_ETHERNET_SECTION,"portIPv4",4101)
# -------------- IP widget --------------------

NetworkTitle_label = Label(left_frame, text='Network',background = cg.LABEL_BACKGROUND, fg = cg.LABEL_FOREGROUND)
IP_StrVar   = StringVar(left_frame, value=ADDRESS)
IP_StrVar.trace_add("write",IP_StrVar_modified)
IP_label    = Label(left_frame, text='IP address :',background = cg.LABEL_BACKGROUND, fg = cg.LABEL_FOREGROUND)
IP_entry    = Entry(left_frame, textvariable = IP_StrVar, width = cg.ENTRY_DEF_WIDTH, background=cg.ENTRY_COLOR);

MASK_StrVar = StringVar(left_frame, value=MASK)
MASK_StrVar.trace_add("write",MASK_StrVar_modified)
MASK_label  = Label(left_frame, text='IP mask : ',background = cg.LABEL_BACKGROUND, fg = cg.LABEL_FOREGROUND)
MASK_entry  = Entry(left_frame, textvariable = MASK_StrVar, width = cg.ENTRY_DEF_WIDTH, background=cg.ENTRY_COLOR)

Port_StrVar = StringVar(left_frame, value=str(PORT))
Port_StrVar.trace_add("write",Port_StrVar_modified)
Port_label  =  Label(left_frame, text='IP port : ',background = cg.LABEL_BACKGROUND, fg = cg.LABEL_FOREGROUND)
Port_entry  =  Entry(left_frame, textvariable = Port_StrVar, width = cg.ENTRY_DEF_WIDTH, background=cg.ENTRY_COLOR);

NetworkTitle_label.config(font='Helvetica 10 bold')
ConnStatus_txt = StringVar()
ConnStatus_label = Label(left_frame, textvariable=ConnStatus_txt,background = cg.LABEL_BACKGROUND, fg = cg.LABEL_FOREGROUND)
ConnStatus_txt.set("----")
ConnStatus_label.config(fg="black", font='Helvetica 10 bold')
ConnStatus = 1
Conn_bouton = Button(left_frame, text="Connect", width = cg.BUTTON_DEF_WIDTH, command=changeConnStatus)
Conn_bouton["fg"] = "black"


##entry_L = Entry(Right_frame, background="orange")

# layout the widgets in the top frame
NetworkTitle_label.grid(row=0, column=0, columnspan =2, padx=10,pady=10)
Conn_bouton.grid(row=1, column=0)
ConnStatus_label.grid(row=1, column=1)
IP_label.grid(row=4, column=0)
IP_entry.grid(row=4, column=1, padx=5)
MASK_label.grid(row=5, column=0)
MASK_entry.grid(row=5, column=1, padx=5)
Port_label.grid(row=6, column=0)
Port_entry.grid(row=6, column=1, padx=5)


# -------------- Config Widget --------------------

def save_Settings():
    ...

def Load_Settings():
    ...

ConfTitle_label    = Label(left_frame, text='Configuration',background = cg.LABEL_BACKGROUND, fg = cg.LABEL_FOREGROUND)
Load_bouton        = Button(left_frame, text="Load JSON", width = cg.BUTTON_DEF_WIDTH, command=Load_Settings)
Load_bouton["fg"]  = "black"
Save_bouton        = Button(left_frame, text="Save JSON", width = cg.BUTTON_DEF_WIDTH, command=save_Settings)
Load_bouton["fg"]  = "black"

ConfTitle_label.config(font='Helvetica 10 bold')

ConfTitle_label.grid(row=7, column=0, columnspan =2, pady=10)
Load_bouton.grid(row=8, column=0, padx=10)
Save_bouton.grid(row=8, column=1, padx=10)

# -------------- Measure Rf --------------------
MeasRfTitle_label    = Label(left_frame, text='Measure Rf',background = cg.LABEL_BACKGROUND, fg = cg.LABEL_FOREGROUND)
MeasRfTitle_label.config(font='Helvetica 10 bold')
MeasRfTitle_label.grid(row=9, column=0, columnspan =2, pady=10)

MeasRf_bouton        = Button(left_frame, text="Start", width = cg.BUTTON_DEF_WIDTH, command=Rf_createNotSave)
MeasRf_bouton["fg"]  = "black"
MeasRf_bouton.grid(row=10, column=0, padx=10)

SaveRf_bouton        = Button(left_frame, text="Start & Save", width = cg.BUTTON_DEF_WIDTH, command=Rf_createSave)
SaveRf_bouton["fg"]  = "black"
SaveRf_bouton.grid(row=10, column=1, padx=10)



# Placing cursor in the text area
output_area.focus()


root.mainloop()
