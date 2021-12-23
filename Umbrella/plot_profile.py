import sys
import numpy as np
import matplotlib.pyplot as plt

def extract_xy(filename):
    x_array = []
    y_array = []
    with open(filename) as f:
        line = f.readline()
        while '@TYPE xy' not in line:   # Skip to data
            line = f.readline()
            if not line:
                print('Error: line with "@TYPE" xy was not found')
                sys.exit(1)
        line = f.readline()

        while line:
            x,y = line.split('\t')
            x = float(x)
            y = float(y)
            x_array.append(float(x))
            y_array.append(float(y))

            line = f.readline()
    x_array = np.array(x_array)
    y_array = np.array(y_array)
    
    return x_array, y_array

fname = 'profile.xvg'

t, z = extract_xy(fname)
print(t,z)

plt.plot(t,z*4.18)
plt.show()

