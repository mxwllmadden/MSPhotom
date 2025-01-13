# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:24:38 2025

@author: mbmad
"""
import pickle
import numpy as np
from matplotlib import pyplot as plt
from MSPhotom.analysis.imageprocess import subtractbackgroundsignal,\
    splittraces, reshapetraces
from MSPhotom.analysis.regression import regression_main 
from dataclasses import dataclass

def load(datafile):
    with open(datafile,'rb') as file:
        data = pickle.load(file)
    return data

def save_and_regress(datafile, data, bin_size=1000):
    raw_fixed_traces = data['traces_raw_by_run_reg']
    traces_by_run_signal_trial = {}
    for run_path, traces in raw_fixed_traces.items():
        # STEP 1: REMOVE BACKGROUND
        traces = subtractbackgroundsignal(traces)
        # STEP 2: SPLIT TRACES BY CHANNEL
        traces = splittraces(traces, data['num_interpolated_channels'])
        # STEP 3: RESHAPE TRACES ACCORDING TO TRIALS
        traces = reshapetraces(traces, data['img_per_trial_per_channel'])
    
        fiber_labels = data['fiber_labels'][1:]
        fiber_labels[0] = 'corrsig'
        
        trace_labels = [f'sig_{label}_ch{ch}'
                        for label in fiber_labels
                        for ch in range(data['num_interpolated_channels'])]
                        
        for label in fiber_labels:
            for ch in range(data['num_interpolated_channels']):
                trace_labels.append(f'sig_{label}_ch{ch}')

        traces_by_run_signal_trial[run_path] = {label : trace for label, trace 
                                           in zip(trace_labels, traces)}
    data['traces_by_run_signal_trial'] = traces_by_run_signal_trial
    
    @dataclass
    class MSPDataDummy:
        traces_by_run_signal_trial : any = None
        bin_size : int = None
        regressed_traces_by_run_signal_trial = None
        corrsig_reg_results = None
        
    data_obj = MSPDataDummy(traces_by_run_signal_trial=data['traces_by_run_signal_trial'],
                            bin_size=bin_size)
    regression_main(data_obj)
    data['regressed_traces_by_run_signal_trial'] = data_obj.regressed_traces_by_run_signal_trial
    
    with open(datafile,'wb') as file:
        pickle.dump(data, file)
    print('saved!')
        
def swap(traces):
    for ind, trace in enumerate(traces):
        temp = trace[::2].copy()
        trace[::2] = trace[1::2]
        trace[1::2] = temp

def wipe(traces, span):
    for trace in traces:
        trace[span[0]:span[1]] = np.nan

def insert(traces, num, ind):
    for i, trace in enumerate(traces):
        traces[i] = np.insert(trace, ind, [np.nan] * num)

def evaluate(data,
             expected_trial_length_samples : int = 600,
             expected_image_count : list = [],
             expected_trial_number : list = [],
             ignored_runs = []):
    """
    Evaluate photometry data object and inspect for issues

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # This should be a dictionary of runs, then regions
    runs = data['traces_raw_by_run_reg']
    for run_name, traces in runs.items():
        errors = []
        tlengs = []
        m_sigs = []
        for ind, trace in enumerate(traces):
            # Check the length of the trace
            t_leng = len(trace)
            if t_leng not in expected_image_count and len(expected_image_count) > 0:
                errors.append(f'Expected {" or ".join(str(x) for x in expected_image_count)} but instead got {t_leng}')
            # Prepare the tbool array.
            # tbool is either TRUE, FALSE, or NAN
            mn = np.nanmean(trace)
            m_sigs.append(mn)
            tbool = np.where(np.isnan(trace), np.nan, trace > mn)
            # If the mean signal is < 150, cannot analyze
            if mn < 150:
                continue
            # Check for SWITCH discontinuities
            switch_disconts = [i for i, (a, b) in enumerate(zip(tbool, tbool[1:])) if np.nan not in (a, b) and a == b]
            if len(switch_disconts) > 0:
                errors.append(f'Switch discontinuities detected in trace {ind} at indexes: {",".join(str(x) for x in switch_disconts)}')
            # Check for thresholding errors
            if any(np.nan_to_num(tbool[0::2]).astype(bool)) or any(np.nan_to_num(~(tbool[1::2]).astype(bool))):
                errors.append(f'Extreme signal variation detected in trace {ind}')
        if all(x < 150 for x in m_sigs):
            errors.append('WARNING!!!!! Extreme low signal intensity, consider excluding data')
        if not all(x == tlengs[0] for x in tlengs):
            errors.append('WARNING!!!!! Different traces have different lengths, you should never see this message and it means that something horribly wrong has occurred')
        # Check for temporal discontinuities
        filetimes = data['source_image_modification_times_by_run'][run_name]
        dft = np.diff(filetimes)
        dft_mn = dft.mean()
        dft_std = dft.std()
        dft_thresh = dft_mn + 3 * dft_std
        dft_outliers = dft > dft_thresh
        if dft_outliers.sum() not in expected_trial_number and len(expected_trial_number) > 0:
            errors.append('Temporal discontinuities detected')
        # Check and see if there are any errors
        if len(errors) == 0:
            continue
        # Report errors and graph
        print(*errors,sep = '\n')
        print('-----TEMPORAL DISCONTINUITIES----')
        t_disconts = np.where(dft_outliers)[0]
        t_discont_vals = [str(dft[ind])[:5] for ind in t_disconts]
        print(*[f'index: {ind} - size: {val} seconds' 
                for ind, val in zip(t_disconts,t_discont_vals)],
              sep = '\n')
        if len(expected_trial_number) > 0:
            print('-----EXPECTED TEMPORAL DISCONTINUITIES----')
            print(f'Assuming trial length of {expected_trial_length_samples} samples')
            print([x * expected_trial_length_samples
                   for x in range(1,max(expected_trial_number)+1)],
                  sep = '\n')
        for trace in traces:
            plt.plot(trace[0::2])
            plt.plot(trace[1::2])
        print(f'CURRENT RUN: {run_name}')
        return
    print('ALL CHECKS PASSED!!! DATA IS GOOD, SAVE TO NEW FILE!!')
    
def _plot_traces(traces, dft):
    plt.figure(figsize=(12, 6))
    
    for idx, trace in enumerate(traces):
        # Plot blue (even indices)
         plt.plot(trace[::2], color='blue', label='Blue Signal' if idx == 0 else "", alpha=0.7)

         # Plot violet (odd indices) 
         plt.plot(trace[1::2], color='violet', label='Violet Signal' if idx == 0 else "", alpha=0.7)
         
         plt.title(f"Trace {idx}", fontsize=14)
         plt.xlabel("Time (samples)", fontsize=12)
         plt.ylabel("Signal Amplitude", fontsize=12)
         plt.legend(loc='upper right')
         plt.grid(True)
         plt.show()
    
if __name__ == '__main__':
    data = load('K:/2025-01-13_11-22.pkl')
    evaluate(data, 600, expected_trial_number = [20])
    save_and_regress('K:\\filetest.pkl', data)