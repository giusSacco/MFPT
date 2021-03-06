import os, sys
import numpy as np
from argparse import ArgumentParser
from timeit import default_timer as timer

timer_start = timer()

PROGNAME = os.path.basename(sys.argv[0])
parser = ArgumentParser(prog = PROGNAME)
parser.add_argument('-d',dest= 'dir_', default = 'NewFiles')
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

files_created = []
print('Files created:')
for i,TXT in enumerate(TXTs):
    array = np.loadtxt(os.path.join(dir_,TXT))
        
    new_file = TXT.removesuffix('.txt') + '.npy'
    np.save(os.path.join(dir_, new_file), array)
    files_created.append(new_file)
    print(f'{i+1}/{len(TXTs)} \t {new_file} \t {timer() - timer_start:.1f}s')