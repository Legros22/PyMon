

from tkinter import *
gui = Tk()
frame1 = Frame(gui)
##frame1.pack()
##frame2 = Frame(gui)
##frame2.pack(side = RIGHT)
##frame3 = Frame(gui)
##frame3.pack(side = RIGHT)

btn1 = Button(frame1, text="Valider", bg="green")
##btn1.pack(side = LEFT)
btn1.grid(row=0, column=1)
btn2 = Button(frame1, text="Anuller", bg="red")
btn2.grid(row=0, column=2)
##btn2.pack(side = LEFT)
##label = Label(frame2, text="Welcome To WayToLearnX!")
##label.pack(side = BOTTOM)

##scrollbar = Scrollbar(frame3)
##scrollbar.pack( side = RIGHT, fill = Y )
##liste = Listbox(frame3, yscrollcommand = scrollbar.set )
##for i in range(200):
##   liste.insert(END, str(i) + " - Hello World!")
##liste.pack(side = LEFT, fill = BOTH )
##scrollbar.config(command = liste.yview )
##frame3.grid(row=0,column=2)

frame1.mainloop()


gui.mainloop()
