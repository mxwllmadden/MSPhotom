# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:52:56 2024

@author: mbmad
"""

import pickle
from matplotlib import pyplot as plt
import numpy as np

# data_path = input('path to pickle file: ')
data_path = 'G:\\Last_Fucking_Experiment\\ALL_PROCESSED_8.29.24.pkl'

with open(data_path, 'rb') as file:
    data = pickle.load(file)
    
print(f'Loaded data object with {list(data.__dict__.keys())} attributes')

# Unpack desired data
traces_raw_by_run_reg = data.traces_raw_by_run_reg

def plot(item):
    for trace in item:
        plt.plot(trace[0::2])
        plt.plot(trace[1::2])
    plt.show()
    
def issuspect(item):
    for trace in item:
        mn = trace.mean()
        tbool = trace > mn
        if has_consecutive_duplicates(tbool):
            return True
    return False
        
def has_consecutive_duplicates(arr):
    return any(arr[i] == arr[i+1] for i in range(len(arr) - 1))

def find_consecutive_duplicate_index(arr):
    for i in range(len(arr) - 1):
        if arr[i] == arr[i+1]:
            return i
    return None

def insert_nan_between_duplicates_recursive(bool_arr, arr):
    while True:
        bool_arr, arr, val = insert_nan_between_duplicates(bool_arr, arr)
        if val is False:
            return arr

def insert_nan_between_duplicates(bool_arr, arr):
    for i in range(len(bool_arr) - 1):
        if bool_arr[i] == bool_arr[i+1]:
            arr = np.insert(arr, i+1, np.nan)
            bool_arr = np.insert(bool_arr, i+1, np.nan)  # Update the boolean array as well
            return bool_arr, arr, True
    return bool_arr, arr, False

for key, item in traces_raw_by_run_reg.items():
    if issuspect(item):
        print(key)
        plt.figure()
        plt.title(key)
        plot(item)
        new_item = []
        for trace in item:
            mn = trace.mean()
            tbool = trace > mn 
            new_item.append(insert_nan_between_duplicates_recursive(tbool,trace))
        plt.figure()
        plt.title(f'{key} FIXED')
        plot(new_item)
    