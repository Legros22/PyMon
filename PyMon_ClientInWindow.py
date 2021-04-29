from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext

import tkinter as tk
from datetime import datetime

import time
from queue import Queue
from threading import Thread
import socket

import logging
import sys

import json

root = Tk()
root.title('PyMon CLient (ZIOT)')
root.geometry('{}x{}'.format(800, 550))

# set default color
WIN_FORGROUNG = "#EEE"
WIN_HIGH_LIGHT ="#CCC"
WIN_BACKGROUND = "#333"
TRACE_BACKGROUNG = "#AAA"
CMD_BACKGROUND = "#EEE"

LABEL_BACKGROUND = WIN_BACKGROUND #"cyan"
LABEL_FOREGROUND = WIN_FORGROUNG
ENTRY_COLOR     = CMD_BACKGROUND #"pink"

BUTTON_DEF_WIDTH = 10
ENTRY_DEF_WIDTH = 15

## Manage software config in json file
## ------------------------------------

def Load_Settings():
    global ADDRESS, MASK, PORT, log_file_name, log_separator

    print(" ========= Load_Settings() not yet working =================")
    try:
        with open("MonZiot.json", "r") as jsonfile:
            ConfData = json.load(jsonfile)
            print("Read configuration successful")
    except:
        ConfData={}


    Update_ConfData = False

    if "Ethernet" in ConfData:
    #-------------------------
        print(" ** Ethernet section")
    else:
        ConfData["Ethernet"]={}
        Update_ConfData = True
        print("create Ethernet section ")

    if "ADDRESS" in ConfData["Ethernet"]:
        ADDRESS = ConfData["Ethernet"]["ADDRESS"]
        print("ADDR = "+ADDRESS)
    else:
        ADDRESS = "192.168.1.11"
        ConfData["Ethernet"]["ADDRESS"]=ADDRESS
        Update_ConfData = True
        print("create ADDR = "+ADDRESS)

    if "MASK" in ConfData["Ethernet"]:
        MASK = ConfData["Ethernet"]["MASK"]
        print("MASK = "+MASK)
    else:
        MASK = "255.255.0.0"
        ConfData["Ethernet"]["MASK"]=MASK
        Update_ConfData = True
        print("create MASK = "+MASK)

    if "PORT" in ConfData["Ethernet"]:
        PORT = int(ConfData["Ethernet"]["PORT"])
        Update_ConfData = True
        print("PORT = "+str(PORT))
    else:
        PORT = 6789
        ConfData["Ethernet"]["PORT"]=str(PORT)
        print("create PORT = "+str(PORT))

    if "Logger" in ConfData:
    #-------------------------
        print(" ** Logger section")
    else:
        ConfData["Logger"]={}
        Update_ConfData = True
        print("create Logger section ")

    if "LogFileName" in ConfData["Logger"]:
        log_file_name = ConfData["Logger"]["LogFileName"]
        print("LogFileName = "+log_file_name)
    else:
        log_file_name = "MyLog.txt"
        ConfData["Logger"]["LogFileName"]=log_file_name
        Update_ConfData = True
        print("create LogFileName = "+log_file_name)

    if "LogDelimiter" in ConfData["Logger"]:
        log_separator = ConfData["Logger"]["LogDelimiter"]
        print("LogDelimiter = "+log_separator)
    else:
        log_separator = ";"
        ConfData["Logger"]["LogDelimiter"]=log_separator
        Update_ConfData = True
        print("create LogDelimiter = "+log_separator)


    if Update_ConfData:
        MyJSON = json.dumps(ConfData, indent=4, sort_keys=True)
        with open("MonZiot.json", "w") as jsonfile:
            jsonfile.write(MyJSON)
            print("ReWrite configuration successful")





def save_Settings():
    global IP_StrVar, MASK_StrVar, Port_StrVar, log_file_name, log_separator
    global ConfData

    print(" ========= save_Settings() not yet working =================")

    try:
        with open("MonZiot.json", "r") as jsonfile:
            ConfData = json.load(jsonfile)
            print("Read successful")
    except:
        ConfData={}


    if "Ethernet" in ConfData:
    #-------------------------
        print(" ** Ethernet y est")
    else:
        ConfData["Ethernet"]={}
        print("create Ethernet section ")

    ConfData["Ethernet"]["ADDRESS"] = IP_StrVar.get()
    print("ADDR = "+IP_StrVar.get())

    ConfData["Ethernet"]["MASK"]=MASK_StrVar.get()
    print("MASK = "+MASK_StrVar.get())

    ConfData["Ethernet"]["PORT"]=str(Port_StrVar.get())
    print("PORT = "+str(Port_StrVar.get()))

    if "Logger" in ConfData:
    #-------------------------
        print(" ** Logger y est")
    else:
        ConfData["Logger"]={}
        print("Logger section ")

    ConfData["Logger"]["LogFileName"]=log_file_name
    print("LogFileName = "+log_file_name)

    ConfData["Logger"]["LogDelimiter"]=log_separator
    print("LogDelimiter = "+log_separator)


    MyJSON = json.dumps(ConfData, indent=4, sort_keys=True)
    with open("MonZiot.json", "w") as jsonfile:
        jsonfile.write(MyJSON)
        print("ReWrite successful")





def MonLog(TraceLine):
    now = datetime.now()
    timeStamp = now.strftime("%d/%m/%Y"+log_separator+"%H:%M:%S")
    with open(log_file_name, 'a') as LogFile:  # Use file to refer to the file object
        LogFile.write(timeStamp+log_separator+TraceLine+'\n')



left_frame = Frame(root,highlightbackground=WIN_HIGH_LIGHT, highlightthickness=1,
                    bg=LABEL_BACKGROUND, width=160, height=50, pady=3)
left_frame.grid(row=0, column=0, sticky="nw")

# create all of the main containers
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

Right_frame = Frame(root, bg=WIN_BACKGROUND,
                    highlightbackground=WIN_HIGH_LIGHT, highlightthickness=1,
                    width=300, height=50, pady=3)
Right_frame.grid(row=0, column=1,sticky="nsew")
Right_frame.grid_columnconfigure(0, weight=1)
Right_frame.grid_rowconfigure(1, weight=1)

# create the widgets for right frame
# =====================================



# Logger selection
# --------------------
def ToggleLogFile ():
    if LogComm.get():
        LogCommTxt.set("Log file (ON:\""+log_file_name+"\")")
    else:
        LogCommTxt.set('Log file (OFF)')

LogComm = IntVar()
LogCommTxt = StringVar()
LogCommTxt.set('Log file (OFF)')
LogSel = Checkbutton(Right_frame,
                    fg = CMD_BACKGROUND, bg = WIN_BACKGROUND,
                    activebackground=WIN_BACKGROUND, activeforeground=CMD_BACKGROUND,
                    selectcolor = WIN_BACKGROUND,
                    #selectcolor = TRACE_BACKGROUNG,
                    textvariable=LogCommTxt,variable=LogComm, onvalue=1, offvalue=0,
                    command=ToggleLogFile)
LogSel.grid(row=0,column=0,padx = 10, columnspan=2, sticky="w")


# Output Trace Window
# --------------------
output_area = scrolledtext.ScrolledText(Right_frame,
                                      width = 70,
                                      height = 10,
                                      bg = TRACE_BACKGROUNG,
                                      font = ("Courier",10))

output_area.grid(row=1, column=0, columnspan =2, pady = 15, padx = 10, sticky="nsew")
output_area.grid_columnconfigure(0, weight=1)
output_area.grid_rowconfigure(0, weight=1)


# input enter Window
# --------------------

#IP_label = Label(Right_frame, text='Manual command :',background = LABEL_BACKGROUND)
IP_label = Label(Right_frame, fg = WIN_FORGROUNG, bg = WIN_BACKGROUND, text='Manual command :')
IP_label.grid(row=3, column=0,pady = 0, padx = 10, sticky="nw")



def input_area_enter(event):
    global LogComm
    CmdLine = input_area.get(1.0, END) # input cmd from read
    CmdLine = CmdLine.replace("\n","") # supress \n for start of line
    input_area.delete(1.0,END)         # delete input zone
    # Output cmd to TRACE
    output_send(CmdLine, MSG_TYPE_SEND)
    MyTCP_SendToServer(CmdLine)

input_area = scrolledtext.ScrolledText(Right_frame,
                                      width = 50,
                                      height = 2,
                                      bg = CMD_BACKGROUND,
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







# --------------- TCP client mamagement -------------------

ClientState = 0
#client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def ProcessReveivedMsg(client):
    try:
        output_send('in ProcessReveivedMsg()',MSG_TYPE_ACTION)
        while 1:
            MyFrame = client.recv(1024)
            if not MyFrame:
                output_send('Client quit',MSG_TYPE_ACTION)
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
                    output_send(FrameStr,MSG_TYPE_RECEIVE)
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
                output_send(txt,MSG_TYPE_ACTION)
                ClientState = 1
##                #Thread_ProcessReveivedMsg = Thread(target = ProcessReveivedMsg, args =(client, ))
##                #Thread_ProcessReveivedMsg.start()
##                #output_send('Receiving thread is started',MSG_TYPE_ACTION)

        #if server is enabled, check if it has to be stoped
        if ClientState==1:
            if (ServerRequest==0):  # Request server connexion
                output_send('Disconnect',MSG_TYPE_ACTION)
                client.close()
                #note : This will cause "ProcessReveivedMsg" exception
##                Thread_ProcessReveivedMsg.join()
                ClientState = 0

##        #if server is supposed to be launched, check if client manager is still alive
##        if ClientState==1:
##            if (Thread_ProcessReveivedMsg.is_alive()==False):
##                output_send('thread managing Client is dead',MSG_TYPE_ACTION)
##                client.close()
##                server.close()
##                ClientState = 0
##                ServerRequest = 1
        time.sleep(1)
        ii += 1
        output_send(str(ii),MSG_TYPE_SEND)
        if(ClientState==1):
            client.send(('hello +'+str(ii)).encode())


##q = Queue()
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
        output_send(txt,MSG_TYPE_ACTION)
        ClientState = 1
        #Launch thread to receive data
        Thread_ProcessReveivedMsg = Thread(target = ProcessReveivedMsg, args =(client, ))
        Thread_ProcessReveivedMsg.start()
        output_send('Receiving thread is started',MSG_TYPE_ACTION)

        #widget management
        ConnStatus_txt.set("Connected")
        ConnStatus_label.config(fg="green", font='Helvetica 11 bold')

    except:
        output_send("Server refuse connection",MSG_TYPE_ACTION)
        ClientState = 0
        #widget management
        ConnStatus_txt.set("Disconnected")
        ConnStatus_label.config(fg="black", font='Helvetica 10')

def MyTCP_DisConnectToServer():
    global ClientState
    global client
    try:
        #manage client connection to the server
        output_send('Disconnect',MSG_TYPE_ACTION)
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
            output_send("Can't send to Server",MSG_TYPE_ACTION)
            MyTCP_DisConnectToServer()
    else:
        output_send("Connect to Server before to send message.",MSG_TYPE_ACTION)

# -------------- Connexion widget --------------------


def changeConnStatus():
    global ClientState
    if ClientState==0:
        MyTCP_ConnectToServer()
         #q.put(ConnStatus)
        #ConnStatus = 1
    elif ClientState==1:

        #ConnStatus_txt.set("Disconnected")
        #ConnStatus_label.config(fg="black", font='Helvetica 10')
        #q.put(ConnStatus)
        MyTCP_DisConnectToServer()
        #ConnStatus = 0
    else: #Default state
        ConnStatus_txt.set("----")
        ConnStatus_label.config(fg="black", font='Helvetica 10 bold')
        ClientState==0
        #ConnStatus = 0
        #ClientState = 0
        #q.put(ConnStatus)



# ---------- Popup Window for Rf Measurement -------------

def Rf_create():
    win = Toplevel(root)


# ---------- Load setting at init -------------

Load_Settings()

# -------------- IP widget --------------------
#ADDRESS = '192.168.1.52'
#PORT = 6789
NetworkTitle_label = Label(left_frame, text='Network',background = LABEL_BACKGROUND, fg = LABEL_FOREGROUND)
IP_StrVar   = StringVar(left_frame, value=ADDRESS)
IP_label    = Label(left_frame, text='IP address :',background = LABEL_BACKGROUND, fg = LABEL_FOREGROUND)
IP_entry    = Entry(left_frame, textvariable = IP_StrVar, width = ENTRY_DEF_WIDTH, background=ENTRY_COLOR);
MASK_StrVar = StringVar(left_frame, value=MASK)
MASK_label  = Label(left_frame, text='IP mask : ',background = LABEL_BACKGROUND, fg = LABEL_FOREGROUND)
MASK_entry  = Entry(left_frame, textvariable = MASK_StrVar, width = ENTRY_DEF_WIDTH, background=ENTRY_COLOR)
Port_StrVar = StringVar(left_frame, value=str(PORT))
Port_label  =  Label(left_frame, text='IP port : ',background = LABEL_BACKGROUND, fg = LABEL_FOREGROUND)
Port_entry  =  Entry(left_frame, textvariable = Port_StrVar, width = ENTRY_DEF_WIDTH, background=ENTRY_COLOR);

NetworkTitle_label.config(font='Helvetica 10 bold')
ConnStatus_txt = StringVar()
ConnStatus_label = Label(left_frame, textvariable=ConnStatus_txt,background = LABEL_BACKGROUND, fg = LABEL_FOREGROUND)
ConnStatus_txt.set("----")
ConnStatus_label.config(fg="black", font='Helvetica 10 bold')
ConnStatus = 1
Conn_bouton = Button(left_frame, text="Connect", width = BUTTON_DEF_WIDTH, command=changeConnStatus)
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
ConfTitle_label    = Label(left_frame, text='Configuration',background = LABEL_BACKGROUND, fg = LABEL_FOREGROUND)
Load_bouton        = Button(left_frame, text="Load JSON", width = BUTTON_DEF_WIDTH, command=Load_Settings)
Load_bouton["fg"]  = "black"
Save_bouton        = Button(left_frame, text="Save JSON", width = BUTTON_DEF_WIDTH, command=save_Settings)
Load_bouton["fg"]  = "black"

ConfTitle_label.config(font='Helvetica 10 bold')

ConfTitle_label.grid(row=7, column=0, columnspan =2, pady=10)
Load_bouton.grid(row=8, column=0, padx=10)
Save_bouton.grid(row=8, column=1, padx=10)

# -------------- Measure Rf --------------------
MeasRfTitle_label    = Label(left_frame, text='Measure Rf',background = LABEL_BACKGROUND, fg = LABEL_FOREGROUND)
MeasRf_bouton        = Button(left_frame, text="Start", width = BUTTON_DEF_WIDTH, command=Rf_create)
MeasRf_bouton["fg"]  = "black"

MeasRfTitle_label.config(font='Helvetica 10 bold')

MeasRfTitle_label.grid(row=9, column=0, columnspan =2, pady=10)
MeasRf_bouton.grid(row=10, column=0, padx=10)



# Placing cursor in the text area
output_area.focus()


root.mainloop()
