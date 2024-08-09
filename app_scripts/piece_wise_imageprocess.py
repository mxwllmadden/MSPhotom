# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:53:09 2024

@author: mbmad
"""

import MSPhotom as msp
import threading
import copy
import time

def main():
    reporter = {'App' : None,
                'Data' : None}
    app_thread = threading.Thread(target=MSPhotom_Automated.run,
                                  args=(reporter,),
                                  daemon=True)
    app_thread.start()
    
    print('Waiting for App to load')
    app = waitfor(reporter,'App')
    
    print('Please load the pckl data file you would like to update')
    data = waitfor(reporter,'Data')
    old_runs = copy.deepcopy(data.run_path_list)
    old_data = copy.deepcopy(data)
    
    print('Loading Runs')
    data.run_path_list = None
    app.load_runs()
    run_path_list = waitfor(reporter, 'run_path_list')
    print(f'Identified {len(run_path_list)} runs')
    
    runs_already_analysed = [f'{runpath.split("/")[-2]}/{runpath.split("/")[-1]}'
                             for runpath in old_runs]
    print(run_path_list)
    new_runs = [run for run in data.run_path_list if 
                all([old_run not in run for old_run in runs_already_analysed])]
    print(f'Identified {len(new_runs)} new runs:')
    for run in new_runs: print(run)
    
    input('\nPress Enter to Begin Processing New Runs...')
    
    data.run_path_list = new_runs
    data.traces_by_run_signal_trial = None
    app.processimages()
    
    while True:
        time.sleep(5)
        if data.traces_by_run_signal_trial is not None:
            break
    data.run_path_list = [*old_runs, *data.run_path_list]
    data.traces_raw_by_run_reg = {**old_data.traces_raw_by_run_reg,
                                      **data.traces_raw_by_run_reg}
    data.traces_by_run_signal_trial = {**old_data.traces_by_run_signal_trial,
                                      **data.traces_by_run_signal_trial}
    
    print('Processing has finished. Please manually save in a new location')
    return data
    
class MSPhotom_Automated(msp.MSPApp):
    def __init__(self, reporter : list):
        self.reporter = reporter
        reporter['App'] = self
        super().__init__()

    def load_data(self):
        super().load_data()
        self.view.update_state('None')
        self.reporter['Data'] = self.data
    
    def load_runs(self):
        super().load_runs()
        self.view.update_state('None')
        self.reporter['run_path_list'] = self.data.run_path_list

def waitfor(value, index):
    while True:
        time.sleep(1)
        if value[index] is not None:
            break
    return value[index]

if __name__ == '__main__':
    data = main()
    