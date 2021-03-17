from tkinter import *
gui = Tk()
scrollbar = Scrollbar(gui)
scrollbar.pack( side = RIGHT, fill = Y )
liste = Listbox(gui, yscrollcommand = scrollbar.set )
for i in range(200):
   liste.insert(END, str(i) + " - Hello World!")
liste.pack(side = LEFT, fill = BOTH )
scrollbar.config(command = liste.yview )
gui.mainloop()


from tkinter import *
gui = Tk()
frame1 = Frame(gui)
frame1.pack()
frame2 = Frame(gui)
frame2.pack(side = RIGHT)
btn1 = Button(frame1, text="Valider", bg="green")
btn1.pack(side = LEFT)
btn2 = Button(frame1, text="Anuller", bg="red")
btn2.pack(side = LEFT)
label = Label(frame2, text="Welcome To WayToLearnX!")
label.pack(side = BOTTOM)
##label.pack(side = RIGHT)
gui.mainloop()
