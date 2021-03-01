from tkinter import *

root = Tk()
root.title('PyMon for ZIOT')
root.geometry('{}x{}'.format(460, 350))

# create all of the main containers
top_frame = Frame(root, bg='cyan', width=450, height=50, pady=3)
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
IP_label = Label(left_frame, text='IP address')
MASK_label = Label(left_frame, text='IP mask')

AutoSend = Label(left_frame, text='Auto Send')
entry_cmd = Entry(left_frame, background="pink")
##entry_L = Entry(Right_frame, background="orange")

# layout the widgets in the top frame
##IP_label.grid(row=0, columnspan=3)
IP_label.grid(row=0, column=0)
MASK_label.grid(row=1, column=0)
AutoSend.grid(row=2, column=0)
entry_cmd.grid(row=3, column=0)
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
