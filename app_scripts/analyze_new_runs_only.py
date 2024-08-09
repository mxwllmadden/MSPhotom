# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 13:50:39 2024

@author: mbmad
"""

from app_scripts.MSPhotom_AppInspector import AppInspector
from copy import deepcopy

inspector = AppInspector()
print('Please open data file to update')
data = inspector.waitfor_change('data_ref')
inspector.data = data
print('Looking for existance of valid masks')
inspector.waitfor('fiber_masks', limit = None)

old_data = deepcopy(data)

print('Confirmed that data object is ready, enabling parameter edits')
inspector.app.view.update_state('IP - Parameter Entry')
print('Load runs when ready')
inspector.data.run_path_list = None
detected_runs = inspector.waitfor('run_path_list', limit = None)
print(f'Identified {len(detected_runs)} available runs')
old_runs = old_data.run_path_list
runs_already_analysed = [f'{runpath.split("/")[-2]}/{runpath.split("/")[-1]}'
                         for runpath in old_runs]
new_runs = [run for run in data.run_path_list if 
            all([old_run not in run for old_run in runs_already_analysed])]
print(f'Identified {len(new_runs)} new runs:')
for run in new_runs: print(run)
input('\nPress Enter to Begin Processing New Runs...')

data.run_path_list = new_runs
data.traces_by_run_signal_trial = None
inspector.app.processimages()
inspector.waitfor('traces_by_run_signal_trial', limit = None)
data.run_path_list = [*old_runs, *data.run_path_list]
data.traces_raw_by_run_reg = {**old_data.traces_raw_by_run_reg,
                                  **data.traces_raw_by_run_reg}
data.traces_by_run_signal_trial = {**old_data.traces_by_run_signal_trial,
                                  **data.traces_by_run_signal_trial}
print('Please save data manually via app')
inspector.close()