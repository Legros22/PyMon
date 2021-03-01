#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      Philippe
#
# Created:     27/12/2020
# Copyright:   (c) Philippe 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import tkinter as tk



def auto():
   nb_mod  = int(ligne_Nb.get())
   tva = float(ligne_tva.get())
   racine.destroy()
   garage(nb_mod,tva)






def garage (Nbr_modele,TVA):

    Fen_garage3 = tk.Tk()
    Fen_garage3.title("Tableau final")
#fen 3
    tk.Label(Fen_garage3, text = "Modèle", font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=0, column=0)
    tk.Label(Fen_garage3, text = "Quantité", font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=0, column=1)
    tk.Label(Fen_garage3, text = "HT Achat", font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=0, column=2)
    tk.Label(Fen_garage3, text = "HT Vente", font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=0, column=3)
    tk.Label(Fen_garage3, text = "TTC Vente", font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=0, column=4)
    tk.Label(Fen_garage3, text = "Bénéfice unité", font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=0, column=5)
    tk.Label(Fen_garage3, text = "Bénéfice total", font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=0, column=6)

    for i in range (Nbr_modele):
        tk.Label(Fen_garage3, text = "Modèle"+str(i), font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=i+1, column=0)
        tk.Label(Fen_garage3, text = str(i),          font=("Courrier", 20), bg='#DDB580', fg='white', borderwidth=1).grid(row=i+1, column=1)

    Fen_garage3.mainloop()





racine = tk.Tk()
canv = tk.Canvas(racine, bg="white", height=200, width=200)
##canv.pack()

##canv.create_oval(0+20, 0+20, 200-20, 200-20, outline="red", width=10)
##canv.create_line(0, 0, 200, 200, fill="black", width=10)
##canv.create_line(0, 200, 200, 0, fill="black", width=10)

label = tk.Label(canv, text="Nombre modèle :")
label.grid(row=0, column=0)

var_Nb = tk.StringVar(value='2')
ligne_Nb = tk.Entry(canv, textvariable = var_Nb, width=30)
ligne_Nb.grid(row = 0, column = 1)

label = tk.Label(canv, text="TVA :")
label.grid(row=0, column=0)

var_tva = tk.StringVar(value='19.6')
ligne_tva = tk.Entry(canv, textvariable = var_tva, width=30)
ligne_tva.grid(row = 1, column = 1)


bouton = tk.Button(canv, text="Quitter", command=auto)
bouton["fg"] = "red"
bouton.grid(row=2, column=3)



##label.pack()
##bouton.pack()
canv.pack()
racine.mainloop()
print("C'est fini !")