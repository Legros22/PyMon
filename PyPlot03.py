#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Philippe
#
# Created:     20/05/2021
# Copyright:   (c) Philippe 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import time


x = np.linspace(0, 2*np.pi, 30)
y1 = np.cos(x)
y2 = np.sin(x)
print("1st plot")
plt.plot(x, y1, label="cos(x)")
#time.sleep(1) # Sleep for 3 seconds
plt.show()

print("2nd plot")
plt.plot(x, y2, label="sin(x)")
plt.legend()

plt.show()

def main():
    pass

if __name__ == '__main__':
    main()
