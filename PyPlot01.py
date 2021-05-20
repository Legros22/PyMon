#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Philippe
#
# Created:     29/04/2021
# Copyright:   (c) Philippe 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt2

print ("pi = ",np.pi)

#defini un [ 3  5  7  9 11 13], de type numpy.ndarray
m = np.arange(3, 15, 2)


##x = np.array([1, 3, 4, 6])
##y = np.array([2, 3, 5, 1])
##plt.plot(x, y)
##plt.show() # affiche la figure a l'ecran
##
##x2 = np.linspace(0, 2*np.pi, 30)
##y2 = np.cos(x2)
##plt2.plot(x2, y2)
##plt2.title("Fonction cosinus")
##plt2.show() # affiche la figure a l'ecran



x = np.linspace(0, 3, 100)
k = 2*np.pi
w = 2*np.pi
dt = 0.01

y = np.cos(k*x)
line, = plt.plot(x, y)
t = 0
for i in range(20):
    y = np.cos(k*x - w*t)
    line.set_ydata(y)
    plt.pause(0.1) # pause avec duree en secondes
    t = t + dt

##    y = np.cos(k*x - w*t)
##    plt.plot(x, y)
##    plt.pause(0.01) # pause avec duree en secondes
##    t = t + dt


plt.show()