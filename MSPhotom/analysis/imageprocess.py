# -*- coding: utf-8 -*-
"""
Load images and extract and organize trace data
"""
from typing import List
import os
import re
import numpy as np
from PIL import Image
import time

def process_main(data,
                 controller=None):
    # STEP 1: Generate all the mask arrays for each region from the dataset info.
    # Each mask is a boolean numpy array with the selected region as "True" and all else as "False"
    fiber_coords_xyr = [(sum(coord[0:3:2])/2, # X coordinate
                            sum(coord[1:4:2])/2, # Y coordinate
                            (coord[2] - coord[0])/2) # Radius of circle
                           for coord in data.fiber_coords]
    fiber_masks = [npy_circlemask(424,424,*coords) 
                   for coords in fiber_coords_xyr]
    
    traces_raw_by_run_reg = {}
    traces_by_run_signal_trial = {}
    run_path_list_len = len(data.run_path_list)
    # Pull from images
    for ind, run_path in enumerate(data.run_path_list):
        # Update view if needed
        if controller is not None:
            controller.view.image_tab.longprog['value'] = (ind/run_path_list_len)*100
            controller.view.image_tab.longprogstat.set(
                f'Processing run {run_path.split("/")[-2]}/{run_path.split("/")[-1]}')
    
        valid_imgs = get_valid_images(run_path, data.img_prefix)
        if len(valid_imgs) == 0:
            continue
        traces_raw = process_run(valid_imgs, fiber_masks, controller)
        traces_raw_by_run_reg[run_path] = (traces_raw)
        # STEP 1: REMOVE BACKGROUND
        traces = subtractbackgroundsignal(traces_raw)
        # STEP 2: SPLIT TRACES BY CHANNEL
        traces = splittraces(traces, data.num_interpolated_channels)
        # STEP 3: RESHAPE TRACES ACCORDING TO TRIALS
        traces = reshapetraces(traces, data.img_per_trial_per_channel)
        
        fiber_labels = data.fiber_labels[1:]
        fiber_labels[0] = 'corrsig'
        
        trace_labels = [f'sig_{label}_ch{ch}'
                        for label in fiber_labels
                        for ch in range(data.num_interpolated_channels)]
                        
        for label in fiber_labels:
            for ch in range(data.num_interpolated_channels):
                trace_labels.append(f'sig_{label}_ch{ch}')
        
        traces_by_run_signal_trial[run_path] = {label : trace for label, trace 
                                           in zip(trace_labels, traces)}

    data.fiber_masks = {label : mask for label, mask 
                        in zip(data.fiber_labels, fiber_masks)}
    data.traces_raw_by_run_reg = traces_raw_by_run_reg
    data.traces_by_run_signal_trial = traces_by_run_signal_trial
    runs_names = [f'{run_path.split("/")[-2]}/{run_path.split("/")[-1]}' for run_path in data.run_path_list]
    data.log('imageprocess finished processing: \n {"\n".join(runs_names)}')

    if controller is not None:
        controller.view.update_state('RG - Processing Done Ready to Input Bin')
        controller.view.image_tab.longprog['value'] = 100
        controller.view.image_tab.runprog['value'] = 100
        controller.view.image_tab.shortprogstat.set('All Images Processed')
        controller.view.image_tab.longprogstat.set('All Runs Processed')

def process_run(valid_imgs, masks, controller = None):
    start_time = time.time()
    # Preallocate trace arrays
    traces_raw = []
    for region in masks:
        trace = np.empty(len(valid_imgs))
        trace.fill(np.nan)
        traces_raw.append(trace)
    max_img = len(valid_imgs)
    # Iterate through all images
    for ind, img_nm in enumerate(valid_imgs):
        try:
            img_PIL = Image.open(img_nm)
            img_np = np.array(img_PIL)
        except:
            print('Failed to load {img_nm}, trace value was skipped')
            continue
        for trace, mask in zip(traces_raw, masks):
            trace[ind] = img_np[mask].mean()
        if controller is not None:
            controller.view.image_tab.runprog['value'] = (ind/max_img)*100
            controller.view.image_tab.shortprogstat.set(f'{img_nm.split("/")[-1]}')
            controller.view.image_tab.speedout.set(f'{round(ind/(time.time()-start_time),1)} images/second')
    return traces_raw

def get_valid_images(path, prefix):
    img_paths = os.listdir(path)
    img_paths = [path for path in img_paths if path[-4:] == '.tif']
    prefix_len = len(prefix)
    img_paths = [path for path in img_paths if path[:prefix_len] == prefix]
    img_paths = sorted(img_paths, key = lambda imgnm : int(re.sub('[^0-9]','',imgnm[prefix_len+1:-4])))
    return [f'{path}/{name}' for name in img_paths]

def npy_circlemask(sizex : int, sizey : int,circlex : int,circley : int,radius : int):
    """
    Creates a numpy mask array with a circle region. Is used for masking image 
    files to pull only the selected fiber region.

    Parameters
    ----------
    sizex : in
        DESCRIPTION.
    sizey : TYPE
        DESCRIPTION.
    circlex : TYPE
        DESCRIPTION.
    circley : TYPE
        DESCRIPTION.
    radius : TYPE
        DESCRIPTION.

    Returns
    -------
    mask : np.array of numpy.bool_
        Array of bool values to be used a mask over a specific circular region.

    """
    mask = np.empty((sizex,sizey), dtype="bool_")
    for x in range(sizex):
        for y in range(sizey):
            if ((x-circlex)**2 + (y-circley)**2)**(0.5) <= radius:
                mask[y,x] = 1
            else:
                mask[y,x] = 0
    return mask

def subtractbackgroundsignal(traces : List[np.ndarray]): 
    """
    Subtract background signal from each trace.

    This function subtracts the background signal, represented by the first array in the list, 
    from each subsequent array in the input list of traces.

    Parameters
    ----------
    traces : list of numpy.ndarray
        DESCRIPTION.

    Returns
    -------
    subtrace : list of numpy.ndarray
        List containing the traces data with background signal subtracted.

    """
    subtrace = []
    for i in range(1,len(traces)):
        subtrace.append(np.subtract(traces[i],traces[0]))
    return subtrace

def splittraces(traces,channels) -> List[np.ndarray]:
    """
    Split traces data into individual channels.

    Parameters
    ----------
    traces : (list of numpy.ndarray)
        List containing traces data..
    channels : int
        Number of channels in the traces data.

    Returns
    -------
    splittraces : TYPE
        DESCRIPTION.

    """
    splittraces = []
    for i in range(len(traces)):
        for j in range(channels): splittraces.append(traces[i][j::channels])
    return splittraces

def reshapetraces(traces,imgptrial):
    """
    Reshape traces data into a specified number of trials per image.
    
    Parameters
    ----------
    traces : (list of numpy.ndarray)
        List containing traces data..
    imgptrial : int
        Number of trials per image.

    Returns
    -------
    reshapedtraces : (list of numpy.ndarray)
        List containing reshaped traces data with specified trials per image.

    """
    reshapedtraces = []
    for i in range(len(traces)):
        size = np.prod(traces[i].shape)
        trials, remainder = divmod(size,imgptrial)
        x = traces[i][0:(trials*imgptrial)]
        reshapedtraces.append(np.reshape(x,(trials,imgptrial)))
    return reshapedtraces

def loadimg(path):
    """
    Load an image from the specified path.

    Parameters
    ----------
    path : str
        pathlike object specifying location of image file.

    Returns
    -------
    imarray : np.array
        Array representing pixels of image.

    """
    # img = tf.imread(path)
    with Image.open(path) as img:
        imarray = np.array(img)
    return imarray
