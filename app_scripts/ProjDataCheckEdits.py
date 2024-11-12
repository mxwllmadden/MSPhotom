# -*- coding: utf-8 -*-
"""
Check for compliance
"""

import glob

# %% Get all files
large_file_list = glob.glob('K:\\Last_Fucking_Experiment\\**\\*.tif', recursive=True)

# %% Split the paths

Split_files = [file.split('\\') for file in large_file_list]

# %%
f_counts = {}
for file in Split_files:
    ident = (file[-3], file[-2])
    if ident in f_counts.keys():
        f_counts[ident] += 1
    else:
        f_counts[ident] = 1
        
# %% Identify warnings

f_counts_wrong = {key : val for key, val in f_counts.items() if val != 12000}

# %% Identify forgotten set 0

vid_name_wrong = [file for file in Split_files if '1_' in file[-1]]

vid_wrong_counts = {}
for file in vid_name_wrong:
    ident = (file[-3], file[-2])
    if ident in vid_wrong_counts.keys():
        vid_wrong_counts[ident] += 1
    else:
        vid_wrong_counts[ident] = 1
        
# %% Rename all problem files

def rename(old_name):
    return old_name.replace('1_','0_')

for file in Split_files:
    ident = (file[-3], file[-2])
    if not (ident == ('07-25-24', 'LFE 2 Run 1') or ident == ('08-20-24', 'LFE 8 Run 1')):
        continue
    with open('\\'.join(file), 'rb') as orig_fio:
        image = orig_fio.read()
    new_name = file.copy()
    new_name[-1] = rename(file[-1])
    with open('\\'.join(new_name), 'wb') as new_f:
        new_f.write(image)
    print(f'renamed {ident} {file[-1]}')
    
# %% Go and get all timestamps
import os
from matplotlib import pyplot as pp
time_ranges = {}
for file in Split_files:
    day = file[-3]
    ident = (file[-3], file[-2])
    if day != '07-24-24':
        continue
    if ident not in time_ranges.keys():
        time_ranges[ident] = []
    time_ranges[ident].append(os.path.getctime('\\'.join(file)))
# %% Plot above
for num, rng in enumerate(time_ranges.values()):
    pp.scatter( rng,[num]*len(rng))
pp.show()