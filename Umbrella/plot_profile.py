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

systems = ['B', 'C', 'neutral']
molarities = ['0025', 1]


plt.style.use('seaborn')
plt.title(f'Umbrella Sampling')
plt.ylabel('Potential of Mean Force ($kJ/mol$)',fontsize=18)
plt.xlabel('z ($\AA$)',fontsize=18)
for system in systems:
    #plt.figure()
    
    for molarity in molarities:
       fname = os.path.join('profiles',f'profile_{system}_{molarity}M.xvg')
       t, z = extract_xy(fname)
       z_min_index = np.argmin( z[ int((-.3-t[0])/(t[1]-t[0])) : int((.3-t[0])/(t[1]-t[0])) ] ) + int((-.3-t[0])/(t[1]-t[0]))
       plt.plot(75-t*10,(z-z[z_min_index])*4.18, label = f'{system} {molarity}M')
    plt.legend()

y_min , y_max = plt.ylim()
z_aimed_array = np.arange(-0.4, 2.05, 0.1)
plt.vlines(75-z_aimed_array*10,y_min,y_max, linestyles='dashed', linewidth = .5)
plt.ylim(y_min,y_max)
plt.savefig(f'pmf_barriers_umbrella.png', bbox_inches = 'tight', dpi=400)
plt.close()

