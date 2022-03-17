from cProfile import label
import sys, os
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

systems = ['B', 'C']
molarities = ['0025', 1]
for system in systems:
    plt.figure()
    plt.title(f'System {system}')
    for molarity in molarities:
       fname = os.path.join('profiles',f'profile_{system}_{molarity}M.xvg')
       t, z = extract_xy(fname)
       plt.plot(t,z*4.18, label = f'{system} {molarity}M')
    plt.legend()
    plt.savefig(f'pmf_barrier_{system}.png', bbox_inches = 'tight', dpi=400)

plt.show()

