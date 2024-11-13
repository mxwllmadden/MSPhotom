# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:02:54 2024

@author: mbmad
"""
import sys
sys.path.append('K:/Rutabaga/MSPhotom')

import glob
from MSPhotom.analysis.imageprocess import process_run, process_run_async_wrapper, get_valid_images, npy_circlemask
import time
import MSPhotom
import pickle


def main():
    global data
    with open(r'K:\Rutabaga\LFE_ANALYSIS\datasource\PhotometryTraces\DataCleaningProcessing\All_Data_RAW.pkl','rb') as file:
        data = pickle.load(file)
    validimg = get_valid_images(r'K:\Kiwi\Last_Fucking_Experiment\09-22-24\LFE 16 Run 1','lfe0')
    
    fiber_coords_xyr = [(sum(coord[0:3:2])/2, # X coordinate
                            sum(coord[1:4:2])/2, # Y coordinate
                            (coord[2] - coord[0])/2) # Radius of circle
                           for coord in data.fiber_coords]
    fiber_masks = [npy_circlemask(424,424,*coords) 
                   for coords in fiber_coords_xyr]
    
    global results, results_async
    starttime = time.perf_counter()
    results = process_run(validimg,fiber_masks)
    endtime = time.perf_counter()
    print(f"Execution time: {endtime - starttime:.8f} seconds")
    
    
    starttime = time.perf_counter()
    results_async = process_run_async_wrapper(validimg,fiber_masks)
    endtime = time.perf_counter()
    print(f"Execution time: {endtime - starttime:.8f} seconds")
    
if __name__ == '__main__':
    main()