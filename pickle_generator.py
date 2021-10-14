import pickle, os, sys
import numpy as np
from argparse import ArgumentParser
from timeit import default_timer as timer

timer_start = timer()

PROGNAME = os.path.basename(sys.argv[0])
parser = ArgumentParser(prog = PROGNAME)
parser.add_argument('-d',dest= 'dir_', default = 'NewPickles')
args_parser = parser.parse_args()
dir_ = args_parser.dir_

if not os.path.exists(dir_):
    print(f"Error: Directory '{dir_}' has not been found")
    sys.exit(1)
if not os.path.isdir(dir_):
    print(f"Error: '{dir_}' is not a directory.")
    sys.exit(1)
TXTs = tuple([ file_ for file_ in os.listdir(dir_) if file_.endswith('.txt') ])
if len(TXTs) == 0:
    print(f'Error: No valid file has been found in the directory {dir_}')
    sys.exit(1)

for TXT in TXTs:
    with open(os.path.join(dir_,TXT), 'r') as in_file:
        array = np.loadtxt(in_file)
        
    new_file = TXT.removesuffix('.txt') + '.pickle'
    with open(os.path.join(dir_, new_file),'wb') as fp:
        pickle.dump(array, fp)    # z_coordinate_NAR is np.ndarray
    print(array,timer()-timer_start)