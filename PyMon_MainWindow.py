from tkinter import *

root = Tk()
root.title('PyMon for ZIOT')
root.geometry('{}x{}'.format(460, 350))

# set default color
LABEL_BCKGROUND ="cyan"
ENTRY_COLOR = "pink";





# create all of the main containers
top_frame = Frame(root, bg=LABEL_BCKGROUND, width=450, height=50, pady=3)
btm_frame = Frame(root, bg='white', width=450, height=45, pady=3)

left_frame = Frame(top_frame, bg='gray', width=150, height=50, pady=3)
left_frame = top_frame
##Right_frame = Frame(top_frame, bg='blue', width=300, height=50, pady=3)

# layout all of the main containers
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="nsew")
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

AutoSend = Label(left_frame, text='Auto Send')
entry_cmd = Entry(left_frame, background="pink")
##entry_L = Entry(Right_frame, background="orange")

# layout the widgets in the top frame
##IP_label.grid(row=0, columnspan=3)
Conn_bouton.grid(row=0, column=0)
ConnStatus_label.grid(row=0, column=1)
IP_label.grid(row=3, column=0)
IP_entry.grid(row=3, column=1)
MASK_label.grid(row=4, column=0)
MASK_entry.grid(row=4, column=1)
AutoSend.grid(row=5, column=0)
entry_cmd.grid(row=6, column=0)
##entry_L.grid(row=3, column=1)

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

root.mainloop()
