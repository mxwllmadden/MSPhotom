# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 16:03:56 2025

@author: mbmad
"""

from MSPhotom import tracefix
from MSPhotom.tracefix import swap, wipe, insert

#Load photometry data
data = tracefix.load('/Users/chloeschaefgen/Desktop/photometry/2025-01-13_11-22.pkl')

raw_traces = data['traces_raw_by_run_reg']

#Edits
this_trace = 'A:/photometry recordings/10-25-24/C1 1 Run 1'
traces = raw_traces[this_trace]
insert(traces, 19, 3)

this_trace = 'A:/photometry recordings/10-25-24/C1 2 Run 1'
traces = raw_traces[this_trace]
insert(traces, 19, 3)

this_trace = 'A:/photometry recordings/10-25-24/C1 1 Run 2'
traces = raw_traces[this_trace]
insert(traces, 19, 3)

this_trace = 'A:/photometry recordings/10-25-24/C1 2 Run 2'
traces = raw_traces[this_trace]
insert(traces, 19, 3)

this_trace = 'A:/photometry recordings/10-25-24/C1 1 Run 3'
traces = raw_traces[this_trace]
insert(traces, 19, 3)

this_trace = 'A:/photometry recordings/10-25-24/C1 2 Run 3'
traces = raw_traces[this_trace]
insert(traces, 19, 3)





#Evaluate and find errors
tracefix.evaluate(data,
                  expected_trial_length_samples = 600,
                  expected_image_count = [12000],
                  expected_trial_number = [20],
                  ignored_runs = [])

tracefix.save_and_regress('output.pkl', data)


