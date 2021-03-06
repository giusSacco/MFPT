import sys
from typing import NoReturn, Sequence
from os.path import join
from scipy.constants import k, Avogadro
import numpy as np
import matplotlib.pyplot as plt


boxes_color = 'orange'
boxes_linewidth = 1.5
dashes_imp = (8,6)
plt.style.use('seaborn')


# Plot tajectory of NaR
def plot_trajectory(coord : Sequence[float], /, *, z_start : float, z_end : float, delta_z : float, filename : str, savefig_directory : str,
        add_savefig_name : str = '', savefigures : bool = True, **kwargs) -> NoReturn:  # coord must be positional
    plt.figure(figsize = (10,5))   
    plt.title('NaR trajectory, '+filename, fontsize=20)
    plt.tick_params(labelsize=15)
    plt.ylabel('Time ($n^o$ frame)',fontsize=18)
    plt.xlabel('z ($\AA$)',fontsize=18)
    plt.plot(coord % 90., range(len(coord)), linestyle=' ', markersize=2, marker = 'o') # %90. enforces BC for values >90 or < 0
    plt.axvline(x=z_start + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_start - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    if savefigures:
        savefig_name = 'Trajectory_' + filename + add_savefig_name + '.png'
        plt.savefig(join(savefig_directory, savefig_name), bbox_inches = 'tight', dpi=400) 
    plt.close()


# Plot histogram of z bin counts
def plot_hist_zcounts(coord : Sequence[float], /, *,z_start: float, z_end : float, delta_z : float, n_bins : int, filename : str,
        savefig_directory : str, savefigures : bool = True, add_savefig_name : str = '', **kwargs) -> NoReturn:
    plt.figure(figsize = (10,5))
    plt.title('Z count histrogram, '+filename, fontsize=18)
    plt.hist(coord % 90., bins = n_bins)    # %90. enforces BC for values >90 or < 0
    plt.axvline(x=z_start + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_start - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.tick_params(labelsize=15)
    plt.ylabel('Frame count',fontsize=18)
    plt.xlabel('z ($\AA$)',fontsize=18)
    if savefigures:
        savefig_name = 'Hist_zcounts_' + filename + add_savefig_name + '.png'
        plt.savefig(join(savefig_directory, savefig_name), bbox_inches = 'tight', dpi=400)
    plt.close()

# Plot free energy
def plot_free_energy(coord : Sequence[float], /, *, z_start : float, z_end : float, delta_z : float, filename : str, n_bins : int, 
        savefig_directory : str, add_savefig_name : str = '', savefigures : bool = True, **kwargs) -> NoReturn:

    plt.figure(figsize = (10,5))
    plt.title('Free energy profile, '+filename, fontsize=18)

    def free_energy(count : int, tot_frame : int, bin_lenght : float, T : float = 300) -> float :   # Constants are in Standard SI units, free energy is returned in kJ/mol
        F = -k*T*Avogadro*np.log( (count/tot_frame)/bin_lenght )
        return F/1000       # /1000 -> kJ/mol

    counts, bins = np.histogram(coord % 90., bins=n_bins) # %90. enforces BC for values >90 or < 0
    tot_frame = len(coord)      # == sum(counts)
    bin_lenght = bins[1]-bins[0]
    energy = [free_energy(count, tot_frame, bin_lenght) for count in counts]

    index_z_start = np.argmax( counts[ int(70/bin_lenght) :  int(80/bin_lenght)] )  + int(70/bin_lenght) # finds where the max of counts is for 70<z<80

    plt.plot( bins[1:] - bin_lenght/2, energy - energy[index_z_start], linestyle = '-')
    plt.axvline(x=z_start + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_start - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.tick_params(labelsize=15)
    plt.ylabel('Potential of Mean Force ($kJ/mol$)',fontsize=18)
    plt.xlabel('z ($\AA$)',fontsize=18)
    if savefigures:
        savefig_name = 'Free_energy_' + filename + add_savefig_name + '.png'
        plt.savefig(join(savefig_directory, savefig_name), bbox_inches = 'tight', dpi=400)
    plt.close()
    

# Plot histogram of mfpt distribution vs time   
def plt_hist_mfpt(*, t_bins : Sequence[float], f_bins : Sequence[float], transition_times : Sequence[float], filename : str, 
        savefig_directory : str, add_savefig_name : str = '', savefigures : bool = True, **kwargs) -> NoReturn:
    plt.figure(figsize = (10,5))
    plt.hist(transition_times, t_bins)
    plt.plot(t_bins[1:], f_bins[1:], linestyle = '-')   # Fit curve
    plt.tick_params(labelsize=15)

    plt.ylabel('Number of transition events',fontsize=18)
    plt.xlabel('Transition time (ps)',fontsize=18)
    plt.title('MFPT distrubution, '+filename, fontsize=18)
    if savefigures:
        savefig_name = 'Hist_mfpt_' + filename + add_savefig_name + '.png'
        plt.savefig(join(savefig_directory, savefig_name), bbox_inches = 'tight', dpi=400)
    plt.close()


def free_energy_comparison(coord : Sequence[float],coord2 : Sequence[float], /, *,z_start : float, z_end : float, delta_z : float, filename : str, n_bins : int, 
       molarity1 : str,molarity2 : str, savefig_directory : str, add_savefig_name : str = '', savefigures : bool = True, **kwargs) -> NoReturn:

    plt.figure(figsize = (10,5))
    plt.title('Free energy profile, System '+filename[0], fontsize=18)

    colors = {'1': 'blue', '0025':'red'}

    def free_energy(count : int, tot_frame : int, bin_lenght : float, T : float = 300) -> float :   # Constants are in Standard SI units, free energy is returned in kJ/mol
        F = -k*T*Avogadro*np.log( (count/tot_frame)/bin_lenght )
        return F/1000       # /1000 -> kJ/mol

    counts, bins = np.histogram(coord % 90., bins=n_bins) # %90. enforces BC for values >90 or < 0
    counts2, bins2 = np.histogram(coord2 % 90., bins=n_bins)
    tot_frame = len(coord)      # == sum(counts)
    bin_lenght = bins[1]-bins[0]
    bin_lenght2 = bins2[1]-bins2[0]
    energy = [free_energy(count, tot_frame, bin_lenght) for count in counts]
    energy2 = [free_energy(count2, tot_frame, bin_lenght2) for count2 in counts2]

    index_z_start = np.argmax( counts[ int(70/bin_lenght) :  int(80/bin_lenght)] )  + int(70/bin_lenght) # finds where the max of counts is for 70<z<80
    index_z_start2 = np.argmax( counts2[ int(70/bin_lenght2) :  int(80/bin_lenght2)] )  + int(70/bin_lenght2) # finds where the max of counts is for 70<z<80

    plt.plot( bins[1:] - bin_lenght/2, energy - energy[index_z_start], linestyle = '-', label = f'{molarity1}M', color = colors[molarity1])
    plt.plot( bins2[1:] - bin_lenght2/2, energy2 - energy2[index_z_start2], linestyle = '-', label = f'{molarity2}M', color = colors[molarity2])
    plt.axvline(x=z_start + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_start - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.tick_params(labelsize=15)
    plt.ylabel('Potential of Mean Force ($kJ/mol$)',fontsize=18)
    plt.xlabel('z ($\AA$)',fontsize=18)
    plt.legend()
    if savefigures:
        savefig_name = 'free_energy_comparison_' + filename[0] + add_savefig_name + '.png'
        plt.savefig(join(savefig_directory, savefig_name), bbox_inches = 'tight', dpi=400)
    plt.close()

def free_energy_comparison_with_umbrella(coord : Sequence[float],coord2 : Sequence[float], /, *,z_start : float, z_end : float, delta_z : float, filename : str, n_bins : int, 
       molarity1 : str,molarity2 : str, savefig_directory : str, add_savefig_name : str = '', savefigures : bool = True, **kwargs) -> NoReturn:

    plt.figure(figsize = (10,5))
    plt.title('Free energy profile, System '+filename[0], fontsize=18)

    colors = {'1': 'blue', '0025':'red'}

    def free_energy(count : int, tot_frame : int, bin_lenght : float, T : float = 300) -> float :   # Constants are in Standard SI units, free energy is returned in kJ/mol
        F = -k*T*Avogadro*np.log( (count/tot_frame)/bin_lenght )
        return F/1000       # /1000 -> kJ/mol

    counts, bins = np.histogram(coord % 90., bins=n_bins) # %90. enforces BC for values >90 or < 0
    counts2, bins2 = np.histogram(coord2 % 90., bins=n_bins)
    tot_frame = len(coord)      # == sum(counts)
    bin_lenght = bins[1]-bins[0]
    bin_lenght2 = bins2[1]-bins2[0]
    energy = [free_energy(count, tot_frame, bin_lenght) for count in counts]
    energy2 = [free_energy(count2, tot_frame, bin_lenght2) for count2 in counts2]

    index_z_start = np.argmax( counts[ int(70/bin_lenght) :  int(80/bin_lenght)] )  + int(70/bin_lenght) # finds where the max of counts is for 70<z<80
    index_z_start2 = np.argmax( counts2[ int(70/bin_lenght2) :  int(80/bin_lenght2)] )  + int(70/bin_lenght2) # finds where the max of counts is for 70<z<80

    plt.plot( bins[1:] - bin_lenght/2, energy - energy[index_z_start], linestyle = '-', label = f'{molarity1}M', color = colors[molarity1])
    plt.plot( bins2[1:] - bin_lenght2/2, energy2 - energy2[index_z_start2], linestyle = '-', label = f'{molarity2}M', color = colors[molarity2])
    plt.axvline(x=z_start + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_start - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end + delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.axvline(x=z_end - delta_z, color = boxes_color, dashes = dashes_imp, linewidth = boxes_linewidth)
    plt.tick_params(labelsize=15)
    plt.ylabel('Potential of Mean Force ($kJ/mol$)',fontsize=18)
    plt.xlabel('z ($\AA$)',fontsize=18)

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
    molarities = ['0025', 1]
    systems_labels = {filename[0]: '','neutral': 'neutral'}
    for system in systems_labels.keys():
        for molarity in molarities:
           fname = join('Umbrella','profiles',f'profile_{system}_{molarity}M.xvg')
           t, z = extract_xy(fname)
           z_min_index = np.argmin( z[ int((-.3-t[0])/(t[1]-t[0])) : int((.3-t[0])/(t[1]-t[0])) ] ) + int((-.3-t[0])/(t[1]-t[0]))
           plt.plot(75-(t*10),(z-z[z_min_index])*4.184, label = f'Umbrella {systems_labels[system]} {molarity}M')
    plt.legend()
    plt.xlim(50,83)
    plt.ylim(-1,30)
    if savefigures: plt.savefig(join(savefig_directory,f'pmf_barrier_{filename[0]}.png'), bbox_inches = 'tight', dpi=400)
    plt.close()