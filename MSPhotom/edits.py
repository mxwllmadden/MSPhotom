#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:03:25 2025

@author: chloeschaefgen
"""

import os
from matplotlib import pyplot as plt
import numpy as np
from pathlib import Path
import re

def applyedits(traces_raw_by_run_reg):
    global traces, THIS_TRACE
    THIS_TRACE = 'K:/Kiwi/Last_Fucking_Experiment/09-08-24/LFE 12 Run 1'
    traces = traces_raw_by_run_reg[THIS_TRACE]
    plottraces(traces, THIS_TRACE)
    swap(traces)
    plottraces(traces, THIS_TRACE)
    traces_raw_by_run_reg[THIS_TRACE] = traces

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
        
def plottraces(traces, title):
    plt.title(title)
    for trace in traces:
        plt.plot(trace[0::2], color=(1,0,1))
        plt.plot(trace[1::2], color = (0,0,1))
    plt.show()

def extract_temporal_discontinuity(record, source, traces_raw_by_run_reg):
    def time_get(path):
        return [(os.path.getmtime(os.path.join(path, f)), f)
                for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))]
    def get_consecutive_duplicate_indexes(arr):
        return [i for i in range(len(arr) - 1) if arr[i] == arr[i+1]]
    run_path = os.path.join(source, *list(Path(record).parts)[-3:])
    plt.figure()
    plt.title(run_path)
    time_file = time_get(run_path)
    time_file = [(time, int(re.sub(r'\D', '', fname.split('_')[-1]))) for time, fname in time_file]
    time_file = sorted(time_file, key=lambda x : x[1])
    times = [time for time, file in time_file]
    times = np.asarray(times)
    times = np.diff(times)
    plt.plot(times)
    plt.show()
    print(record, len(time_file))
    t_bool = (times > 0.07) | (times < 0)
    disconts = np.flatnonzero(t_bool)
    print('temporal discontinuities:', disconts)
    tm = times.mean()
    print('mean intersample distance', tm)
    for d in disconts:
        print('magnitude at ', d, 'is', times[d], 'estimated sample distance of ', times[d]/0.05)
    for trace in traces_raw_by_run_reg[record]:
        mn = trace.mean()
        tbool = trace > mn
        print('MultiplexMismatches', get_consecutive_duplicate_indexes(tbool), 'out of', len(trace))
        plt.plot(trace[::2])
        plt.plot(trace[1::2])
    plt.show()
    print(*disconts,sep='\n')
    
def get_suspicious_records(records):
    return [name for name, traces in records.items() 
            if evaluate_traces(traces, name=name)]

def evaluate_traces(traces, name = 'name'):
    for ind, trace in enumerate(traces):
        if issuspect(trace, corr = (ind == 1)):
            print(name)
            return True
    return False

def issuspect(trace, corr = False):
    if len(trace) != 12000 and len(trace) != 18000:
        print('incorrect length in', end=' ')
        return True
    if corr == False:
        return False
    mn = np.nanmean(trace)
    tbool = np.where(np.isnan(trace), np.nan, trace > mn)
    if any(a == b for a, b in zip(tbool, tbool[1:]) if np.nan not in (a,b)):
        print('switch discontinuity in', end=' ')
        return True
    if mn<150:
        return False
    if any(np.nan_to_num(tbool[0::2]).astype(bool)) or any(np.nan_to_num(~(tbool[1::2]).astype(bool))):
        print('thresholding error in', end=' ')
        return True
    return False

