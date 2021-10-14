import os, re, sys, pickle
from typing import NoReturn
import numpy as np
from scipy.optimize import curve_fit
from argparse import ArgumentParser
from configparser import ConfigParser
from timeit import default_timer as timer

# TO DO:
# Insert creation of pickle file

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


def PICKLE_data_analysis(PICKLE : str) -> NoReturn:

    # Getting file infos from filename: it must be of the format 00-00-00-00_0M_NAR.pickle (one or more digits before M)
    # beginning numbers identify the sistem, number before 'M' identify molarity.
    pattern = re.compile( r'''
    (^             # Beginning of group: system_name.   ^ ->beginning of string
    (?:\d{2}-){3}      # 2 digits followed by '-', threefold. Non capturing group
    \d{2})_            # 2 digits followed by '_'     End of system_name group
    (\d+)                     # At least one digit --> Molarity
    M_NAR\.pickle$                  # rest of filename + end of line
    ''', re.VERBOSE )       # VERBOSE -> whitespace ignored and enables comments

    file_infos = pattern.fullmatch(PICKLE) 
    if file_infos is None:  # Raises an error if filename does not match the pattern
        raise FileNotValidError(PICKLE, msg = f"File name '{PICKLE}' does not match the required format 00-00-00-00_0M_NAR.pickle")
    system_name, molarity = file_infos.group(1), file_infos.group(2)


    # load trajectory array from .pickle file
    with open(os.path.join(params.pickle_directory, PICKLE), 'rb') as fp:
        z_coordinate_NAR = pickle.load(fp)     # z_coordinate_NAR is np.ndarray


    # Find z_start, z_min from z counts histogram    
    hist, bins = np.histogram(z_coordinate_NAR, bins = params.n_bins)
    dz = bins[1]-bins[0] # Angstrom
    z_start = ( np.argmax( hist[ int(70/dz) : ] )  + int(70/dz) )* dz     # finds where the max of counts is for z>70
    z_end = ( np.argmax( hist[ int(40/dz) : int(70/dz) ] ) + int(40/dz) )* dz  # finds where the max of counts is for 40<z<70
    
    #Plot trajectory, z counts histogram and free energy
    if params.plot_graphs:
        plotting_params['filename'] = PICKLE.removesuffix('.pickle')        
        plotting_params['z_start'] = z_start
        plotting_params['z_end'] = z_end
        custom_plt.plot_trajectory(z_coordinate_NAR, **plotting_params)
        custom_plt.plot_hist_zcounts(z_coordinate_NAR, **plotting_params)        
        custom_plt.plot_free_energy(z_coordinate_NAR, **plotting_params)


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
        
        hist_figname = 'Hist_mfpt_' + PICKLE.removesuffix('.pickle') + params.add_savefig_name + '.png'
        hist_figpath = os.path.join(params.savefig_directory, hist_figname)
        if os.path.exists(hist_figpath):    # Deletes previous MFPT hist (if it exists)
            os.remove(hist_figpath)
        
        raise NoTransitionFoundError(PICKLE)

    transition_times = [n_frames * delta_t for n_frames in transition_times]    # conversion n of frame -> time
    res*=delta_t

    # Fit of tau
    def fitfunction(t, tau, A):    # tau is in ps only if t is
        return A * np.exp(-t / tau)

    t_bins = np.linspace(0.1, np.amax(transition_times), params.nbins_t)
    hist, _ = np.histogram(transition_times, bins=t_bins)
    t_bin_len = t_bins[1]-t_bins[0]
    best_vals, covar = curve_fit(fitfunction, t_bins[:-1]+(t_bin_len/2), hist, p0=[500.0, hist[0]] )
    f_bins = fitfunction(t_bins, *best_vals)    # y values of fit curve

    tau = best_vals[0]
    d_tau = np.sqrt(covar[0,0])     # Std. Dev.

    # Plot histogram of mfpt distribution
    if params.plot_graphs:
        hist_params = {'t_bins': t_bins, 'f_bins': f_bins, 'transition_times': transition_times, 'filename': PICKLE.removesuffix('.pickle'), \
            'savefigures': params.save_figures, 'add_savefig_name': params.add_savefig_name, 'savefig_directory': params.savefig_directory}
        custom_plt.plt_hist_mfpt(**hist_params)


    # Printing results in the output file
    out_file.write('{:<15} {:<10} {:>15d} {:>20.0f} {:>20.0f} {:>20.0f} {:>15.0f} {:>15.0f} {:>10.0f} {:>10.0f}\n'.format( \
        system_name, molarity, n_transitions, res, res/n_transitions, np.mean(transition_times), tau, d_tau, np.max(transition_times), np.min(transition_times) ))

    # Progress and time elapsed
    print(f'{PICKLEs.index(PICKLE) + 1}/{len(PICKLEs):<25} {timer()-timer_start:<20.1f}' )   



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
#delta_t = 2.0
delta_t = 0.04

# Creation of savefig_directory if it is needed and does not exist.
if params.plot_graphs:
    plotting_params = {
        'plot_graphs': params.plot_graphs, 'delta_z': params.delta_z, 'savefigures': params.save_figures, \
        'n_bins': params.n_bins, 'add_savefig_name': params.add_savefig_name, 'savefig_directory': params.savefig_directory}
    if (not os.path.exists(params.savefig_directory)) and params.save_figures:
        os.mkdir(params.savefig_directory)

# Creation list of files .pickle found in pickle_directory
if not os.path.exists(params.pickle_directory):
    print(f'Error: Directory {params.pickle_directory} does not exist.')
    sys.exit(1)
if not os.path.isdir(params.pickle_directory):
    print(f"Error: '{params.pickle_directory}' is not a directory.")
    sys.exit(1)
PICKLEs = tuple([ file_ for file_ in os.listdir(params.pickle_directory) if file_.endswith('.pickle') ])
#print(PICKLEs)
if len(PICKLEs) == 0:
    print(f'Error: No valid file has been found in the directory {params.pickle_directory}')
    sys.exit(1)

# Creation of output file with the results of the data analysis
with open(params.output_file, 'w') as out_file:
    out_file.write('\tRESULTS NAR DATA ANALYSIS\n')
    out_file.write(f'\t PARAMETERS USED: \t delta_z = {params.delta_z} A \t Lag time = {params.lag_time} ps \t Accaptance rate = {params.acceptance_rate} \t Time is in ps\n')
    out_file.write('{:<15} {:<10} {:>15} {:>20} {:>20} {:>20} {:>15} {:>15} {:>10} {:>10}\n'.format( \
        'SYSTEM', 'MOLARITY','TRANSITION EV.','RESIDENCE TIME','MFPT as ratio','MFPT as mean','TAU FITTED', 'TAU DEV. STD.', 'MAX', 'MIN'))
    
    # Print execution progress
    print('{:<25} {:<20}'.format('N. of analysed files:','Time elapsed (s):'))


    # PICKLE data analysis
    for PICKLE in PICKLEs:        
        try:
            PICKLE_data_analysis(PICKLE)            
        except (FileNotValidError, NoTransitionFoundError) as err:
            print('Warning: ', err, ', proceeding to next file.', sep='')
            continue
        #break          # Useful for testing on just one file

    print(f"Results correctly printed in '{params.output_file}'")
    if params.plot_graphs and params.save_figures:
        print(f"Graphs correctly saved in the directory '{params.savefig_directory}'")