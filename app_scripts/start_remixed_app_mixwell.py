# -*- coding: utf-8 -*-
"""
  __  __ ____  ____  _           _                    ____  _____ __  __ _____  __
 |  \/  / ___||  _ \| |__   ___ | |_ ___  _ __ ___   |  _ \| ____|  \/  |_ _\ \/ /
 | |\/| \___ \| |_) | '_ \ / _ \| __/ _ \| '_ ` _ \  | |_) |  _| | |\/| || | \  / 
 | |  | |___) |  __/| | | | (_) | || (_) | | | | | | |  _ <| |___| |  | || | /  \ 
 |_|  |_|____/|_|   |_| |_|\___/ \__\___/|_| |_| |_| |_| \_\_____|_|  |_|___/_/\_\
                                                                                  
                                                                        
This is a tweaked version of the multisite photometry app created by
Maxwell Madden for personal use. It is likely less stable and contains tweaks
to increase my personal productivity. It is NOT guarenteed to be without bugs.

If you are a Mathur Lab member, I do not recommend using this version of the
app unless you are confident in your ability to understand both the photometry
data pipeline and this python app.

******************************************************************************

Notable tweaks to app behavior.
------------------------------------------------------------------------------
Partial Analysis
    -Loading a datafile prior to loading runs causes runs already analyzed to
    be excluded.
    -Upon completion of imageprocessing the loaded data and new data will be
    merged.
    -This allows easier 'day to day' processing of images, rather than analyzing
    an entire cohort in one batch at the very end of an experiment.

Autosave
    -App autosaves to pickle upon completion of imageprocessing to prevent data loss.
    -Both a partial save and merged save are completed in case there is an issue
    with data merge

Created on Wed Aug  7 13:50:39 2024

@author: mbmad
"""

from MSPhotom.inspectiontools import MSPInspector, MonitoredClass
from MSPhotom import MSPApp
from MSPhotom.data import DataManager
from MSPhotom.analysis import imageprocess
from copy import deepcopy
from datetime import datetime
import threading


def main():
    app: MonitoredClass = MSPInspector()
    app.monitor_method_call('run', trigger_on_run_call)
    app.monitor_method_return('load_data', trigger_on_data_load_return)
    app.monitor_method_return('load_runs', trigger_on_load_runs_return)
    return app.run()


def trigger_on_run_call(self):
    self.view.root.title("MSPhotomApp - REMIXED!!! Use at own risk")
    self.data_old = deepcopy(self.data)
    print(__doc__)
    return None


def trigger_on_data_load_return(self: MSPApp, *result):
    if self.data.fiber_masks is None:
        print('Loaded data contains no analyzed runs.')
        return result
    runs_done = self.data.run_path_list
    runs_done = [f'{run.split("/")[-2]}/{run.split("/")[-1]}'
                 for run in runs_done]
    self._remix_runs_done = runs_done
    self.data_old = deepcopy(self.data)
    self.view.update_state('IP - Parameter Entry')
    print(f'This file contains {len(runs_done)} runs')
    print(*runs_done, sep='\n')
    return result


def trigger_on_load_runs_return(self, *result):
    if self._remix_runs_done == []:
        return result
    runs_done = self._remix_runs_done
    new_runs = [run for run in self.data.run_path_list if
                all([old_run not in run for old_run in runs_done])]
    self.data.run_path_list = new_runs
    filetree_entries = [(path.split('/')[-2], path.split('/')[-1])
                        for path in new_runs]
    # Update View
    self.view.updatefiletreedisplay(filetree_entries)
    self.view.update_state('IP - Ready to Process')
    self.view.image_tab.regselbutton.config(state='disabled')
    print(f'Identified {len(new_runs)} new runs:')
    print(*new_runs, sep='\n')
    print("""Previously analyzed runs were removed.
          Inspect the filetree or terminal to ensure new runs are detected""")

def processimages_remix(self):
    """
    Update view and start image processing in another thread
    """
    def autosave_wrapper(data, controller):
        imageprocess.process_main(data, controller)
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        manage = DataManager(data)
        manage.save(f'autosave_partial_{timestamp}')
        merged_data = merge_data(data, controller.data_old)
        manage = DataManager(merged_data)
        manage.save(f'autosave_merged_{timestamp}')
        controller.data = merged_data
    # Update View
    self.view.update_state('IP - Processing Images')
    # Create and initialize the thread for image loading/processing
    pross_thread = threading.Thread(target=autosave_wrapper,
                                    args=(self.data,
                                          self),
                                    daemon=True)
    pross_thread.start()

def merge_data(data, old_data):
    data.run_path_list = [*old_data.run_path_list, *data.run_path_list]
    data.traces_raw_by_run_reg = {**old_data.traces_raw_by_run_reg,
                                  **data.traces_raw_by_run_reg}
    data.traces_by_run_signal_trial = {**old_data.traces_by_run_signal_trial,
                                       **data.traces_by_run_signal_trial}

if __name__ == '__main__':
    main()