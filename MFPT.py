import os, re, sys
from typing import NoReturn
import numpy as np
from scipy.optimize import curve_fit
from argparse import ArgumentParser
from configparser import ConfigParser
from timeit import default_timer as timer

# Importing custom modules
if not os.path.exists('Libraries'):
    print("Error: Can't find directory 'Libraries'.")
    sys.exit(1)
if not os.path.isdir('Libraries'):
    print("Error: 'Libraries' is not a directory.")
    sys.exit(1)
if not os.path.exists(os.path.join('Libraries','custom_plot.py')):
    print("Error: Can't find 'custom_plot' in the directory 'Libraries'.")
    sys.exit(1)
if not os.path.exists(os.path.join('Libraries','custom_errors.py')):
    print("Error: Can't find 'custom_errors.py' in the directory 'Libraries'.")
    sys.exit(1)
if not os.path.exists(os.path.join('Libraries','custom_class.py')):
    print("Error: Can't find 'custom_class.py' in the directory 'Libraries'.")
    sys.exit(1)

import Libraries.custom_plot as custom_plt    # Library with custom plotting functions (one for each graph)
from Libraries.custom_errors import *          # Library with custom exceptions
import Libraries.custom_class as custom_class    # Library with custom data class


program_description = '''
NaR Mean First Passage Time Data analysis. Takes input parameters and files from the parsed INI file and produces an output file with the result of the analysis.\
Optional: production of graphs for Free Energy, Trajectory, Histogram of z counts and MFPT distribution.'''


def NPY_data_analysis(NPY : str) -> NoReturn:

    # Getting file infos from filename: it must be of the format A_0M.npy (one or more digits before M, any letter at the beginning)
    # letter identify the system, number before 'M' identify molarity.
    pattern = re.compile( r'''
    (^             # Beginning of group: system_name.   ^ ->beginning of string
    [a-zA-Z])_            # Letter identifying the system
    (\d+)                     # At least one digit --> Molarity
    M\.npy$                  # rest of filename + end of line
    ''', re.VERBOSE )       # VERBOSE -> whitespace ignored and enables comments

    file_infos = pattern.fullmatch(NPY) 
    if file_infos is None:  # Raises an error if filename does not match the pattern
        raise FileNotValidError(NPY, msg = f"File name '{NPY}' does not match the required format")
    system_name, molarity = file_infos.group(1), file_infos.group(2)


    # Load trajectory array from .npy file
    z_coordinate_NAR = np.load(os.path.join(params.npy_directory, NPY))     # z_coordinate_NAR is np.ndarray


    # Find z_start, z_min from z counts histogram    
    hist, bins = np.histogram(z_coordinate_NAR, bins = params.n_bins)
    dz = bins[1]-bins[0] # Angstrom
    index_z_start = np.argmax( hist[ int(70/dz) :  int(80/dz)] )  + int(70/dz) # finds where the max of counts is for 70<z<80
    z_start = index_z_start * dz 
    z_end = ( np.argmax( hist[ int(40/dz) : int(70/dz) ] ) + int(40/dz) )* dz  # finds where the max of counts is for 40<z<70
    
    #Plot trajectory, z counts histogram and free energy
    if params.plot_graphs:
        plotting_params['filename'] = NPY.removesuffix('.npy')  
        plotting_params['index_z_start'] = index_z_start      
        plotting_params['z_start'] = z_start
        plotting_params['z_end'] = z_end
        custom_plt.plot_trajectory(z_coordinate_NAR, **plotting_params)
        custom_plt.plot_hist_zcounts(z_coordinate_NAR, **plotting_params)        
        custom_plt.plot_free_energy(z_coordinate_NAR, **plotting_params)

        # Plot of comparison of free energy for the same system at different molarity
        if system_name not in sys_analysed: # Indicates if this couple of files has been already plotted in a previous cycle
            for f in NPYs:   # Searches for the other file referring to the same system
                if pattern.fullmatch(f) is None:
                    # If the name of a file is wrong a warning will be printed later when it is analysed by the function NPY_data_analysis
                    continue
                if pattern.fullmatch(f).group(1) == system_name and pattern.fullmatch(f).group(2) != molarity: # Same system but different molarity
                    custom_plt.free_energy_comparison(z_coordinate_NAR, np.load(os.path.join(params.npy_directory, f)), \
                        molarity1 = molarity, molarity2 = pattern.fullmatch(f).group(2), **plotting_params)
                    sys_analysed.append(system_name)
                    break
            else:   # If the other file has not been found
                print("Warning: The counterpart of '{NPY}' with different molarity has not been found in '{params.npy_directory}'")

    #Compute total residence time and transition times from z_start to z_end
    transition_times  = list()
    n_frame_lag = int(params.lag_time/delta_t)  # Number of frames analysed to choose if the transition valid
    passage_time = 0      # Residence time between transitions
    res = 0       # Total residence time
    for i in range(len(z_coordinate_NAR)):
        if z_start-params.delta_z < z_coordinate_NAR[i] < z_start+params.delta_z:     # Update residence time if in strarting box
            passage_time += 1
        elif (z_end-params.delta_z < z_coordinate_NAR[i] < z_end+params.delta_z) and (passage_time != 0):   # If the ion is in second box and has returned at least once in the first box
            mask = [ z_end-params.delta_z < z < z_end+params.delta_z for z in z_coordinate_NAR[i: i+n_frame_lag] ]   # List of bool: True if the ion stayed in the box
            if sum(mask)/len(mask) >= params.acceptance_rate:     # Executed if particle stayed in the box for at least the number of frames required by the acceptance rate
                res += passage_time
                transition_times.append(passage_time)                                   
                passage_time = 0
        if i == len(z_coordinate_NAR) - 1:     # Update res anyway when arrived at the last frame
            res += passage_time

    n_transitions = len(transition_times)
    if n_transitions == 0:      #  No transition found
        out_file.write('{:<15} {:<10} {:>15} {:>20.0f} \n'.format(system_name, molarity, 'NO TRANSITIONS', res ))
        
        hist_figname = 'Hist_mfpt_' + NPY.removesuffix('.npy') + params.add_savefig_name + '.png'
        hist_figpath = os.path.join(params.savefig_directory, hist_figname)
        if os.path.exists(hist_figpath):    # Deletes previous MFPT hist (if it exists)
            os.remove(hist_figpath)
        
        raise NoTransitionFoundError(NPY)

    transition_times = [n_frames * delta_t for n_frames in transition_times]    # conversion n of frame -> time
    res*=delta_t

    # Fit of tau
    def fitfunction(t, tau, A):    # tau is in ps only if t is
        return A * np.exp(-t / tau)

    t_bins = np.linspace(0.1, np.amax(transition_times), params.nbins_t)
    hist, _ = np.histogram(transition_times, bins=t_bins)
    t_bin_len = t_bins[1]-t_bins[0]
    best_vals, covar = curve_fit(fitfunction, t_bins[:-1] + t_bin_len, hist, p0=[500.0, hist[0]] )
    f_bins = fitfunction(t_bins, *best_vals)    # y values of fit curve

    tau = best_vals[0]
    d_tau = np.sqrt(covar[0,0])     # Std. Dev.

    # Plot histogram of mfpt distribution
    if params.plot_graphs:
        hist_params = {'t_bins': t_bins, 'f_bins': f_bins, 'transition_times': transition_times, 'filename': NPY.removesuffix('.npy'), \
            'savefigures': params.save_figures, 'add_savefig_name': params.add_savefig_name, 'savefig_directory': params.savefig_directory}
        custom_plt.plt_hist_mfpt(**hist_params)


    # Printing results in the output file
    out_file.write('{:<15} {:<10} {:>15d} {:>20.0f} {:>20.0f} {:>20.0f} {:>15.0f} {:>15.0f} {:>10.0f} {:>10.0f}\n'.format( \
        system_name, molarity, n_transitions, res, res/n_transitions, np.mean(transition_times), tau, d_tau, np.max(transition_times), np.min(transition_times) ))

    # Progress and time elapsed
    print(f'{NPYs.index(NPY) + 1}/{len(NPYs):<25} {timer()-timer_start:<20.1f}' )   



### START ###

timer_start = timer()   # Start the timer

# Verify Python version is at least 3.9
if not (sys.version_info.major == 3 and sys.version_info.minor >= 9):
    print('Error: Python version must be 3.9 or later')
    sys.exit(1)


# Parsing and input file. If not given, default is 'input_file.ini'
PROGNAME = os.path.basename(sys.argv[0])
parser = ArgumentParser(prog = PROGNAME, description = program_description)
parser.add_argument('-i','--input','--input_file', dest= 'input', help='input INI file. default: input_file.ini', default = 'input_file.ini')
args_parser = parser.parse_args()
input_file = args_parser.input

if not os.path.exists(input_file):
    print(f"Error: Input file '{input_file}' has not been found")
    sys.exit(1)
if not input_file.endswith('.ini'):
    print(f"Error in input file: '{input_file}' is not an INI file")
    sys.exit(1)


# Setting input parameters from the input file
cfg = ConfigParser()
cfg.read(input_file)
try:
    params = custom_class.Unmodifiable_Data(cfg) # Reads and sets all the needed input parameters. It also checks their existance and that types are correct.
except (OptionError, ParameterNotPresentError, SectionNotPresentError) as err:
    print(err)
    sys.exit(1)
delta_t = 0.04

# Creation of savefig_directory if it is needed and does not exist.
if params.plot_graphs:
    plotting_params = {
        'plot_graphs': params.plot_graphs, 'delta_z': params.delta_z, 'savefigures': params.save_figures, \
        'n_bins': params.n_bins, 'add_savefig_name': params.add_savefig_name, 'savefig_directory': params.savefig_directory}
    if (not os.path.exists(params.savefig_directory)) and params.save_figures:
        os.mkdir(params.savefig_directory)

# Creation list of files .npy found in npy_directory
if not os.path.exists(params.npy_directory):
    print(f'Error: Directory {params.npy_directory} does not exist.')
    sys.exit(1)
if not os.path.isdir(params.npy_directory):
    print(f"Error: '{params.npy_directory}' is not a directory.")
    sys.exit(1)
NPYs = tuple([ file_ for file_ in os.listdir(params.npy_directory) if file_.endswith('.npy') ])
#print(NPYs)
if len(NPYs) == 0:
    print(f'Error: No valid file has been found in the directory {params.npy_directory}')
    sys.exit(1)

print('MFPT NaR data analysis')
print('The following files will be analysed: \n', ', '.join(NPYs))

# List of already analysed systems
sys_analysed = []

# Creation of output file with the results of the data analysis
with open(params.output_file, 'w') as out_file:
    out_file.write('\tRESULTS NAR DATA ANALYSIS\n')
    out_file.write(f'\t PARAMETERS USED: \t delta_z = {params.delta_z} A \t Lag time = {params.lag_time} ps \t Accaptance rate = {params.acceptance_rate} \t Time is in ps\n')
    out_file.write('{:<15} {:<10} {:>15} {:>20} {:>20} {:>20} {:>15} {:>15} {:>10} {:>10}\n'.format( \
        'SYSTEM', 'MOLARITY','TRANSITION EV.','RESIDENCE TIME','MFPT as ratio','MFPT as mean','TAU FITTED', 'TAU DEV. STD.', 'MAX', 'MIN'))
    
    # Print execution progress
    print('{:<25} {:<20}'.format('N. of analysed files:','Time elapsed (s):'))


    # NPY data analysis
    for NPY in NPYs:        
        try:
            NPY_data_analysis(NPY)            
        except (FileNotValidError, NoTransitionFoundError) as err:
            print('Warning: ', err, ', proceeding to next file.', sep='')
            continue
        #break          # Useful for testing on just one file

    print(f"Results correctly printed in '{params.output_file}'")
    if params.plot_graphs and params.save_figures:
        print(f"Graphs correctly saved in the directory '{params.savefig_directory}'")