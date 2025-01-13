#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:10:59 2025

@author: chloeschaefgen
"""
import matplotlib.pyplot as plt
import numpy as np

def plot_traces(traces, dft):
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
    
    traces = [np.random.randint(0,100,(1200)) for x in range(4)]
    for trace in traces:
        trace[0::2] = trace[0::2]+500
        
    dft = []

    plot_traces(traces, dft)