import sys
import numpy as np

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
            if x%1 == 0:
                x_array.append(int(x))
                y_array.append(float(y))
            else:
                x_array.append(-1)
                y_array.append(-100.)
            line = f.readline()
    x_array = np.array(x_array)
    y_array = np.array(y_array)
    
    return x_array, y_array        


fname = 'B1M_pullx.xvg'
out_fname = 'start_umbrella_pos_1M.txt'

t, z = extract_xy(fname)
#z_aimed_array = np.linspace(-0.4, 2.05, 10, endpoint=True)
z_aimed_array = np.arange(-0.4, 2.05, 0.1)
with open(out_fname,'w') as outf:
    #outf.write(f"{'index':>10},{'t':>10},{'z':>10},{'z_aimed':>10}\n")
    for z_aimed in z_aimed_array:
        index = np.argmin(np.abs(z - z_aimed))
        #outf.write(f"{index:10},{t[index]:10},{z[index]:10.4f},{z_aimed:10.4f}\n")
        outf.write(f"{t[index]}\n")

