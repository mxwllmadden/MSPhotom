 # -*- coding: utf-8 -*-
"""
Contains Dataclass that contains all photometry data and parameters and related
functions for saving/accessing or general utilities for dealing with that data.
"""
from typing import List, Tuple, Dict
from dataclasses import dataclass, field
import numpy as np
from datetime import datetime
import pickle
import h5py


@dataclass
class MSPData:
    # General Data
    data_creation_date: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs: list = field(default_factory=lambda: [])

    # Image Processing and Aquisition - Section 1, Input Parameters
    # Human Inputs
    target_directory: str = None
    img_date_range: Tuple[str, str] = None
    date_start : str = None
    date_end : str = None
    img_prefix: str = None
    img_per_trial_per_channel: int = None
    num_interpolated_channels: int = None
    roi_names: List[str] = None
    # File/Trace/Animal Information
    animal_names: List[str] = None
    animal_basename: str = None
    run_path_list: List[str] = None
    animal_start: str = None
    animal_end: str = None

    # Image Processing and Aquisition - Section 2, Fiber Masking
    fiber_labels: List[str] = None
    fiber_coords: List[Tuple[int, int, int, int]] = None
    fiber_masks: Dict[str, np.ndarray] = None
    traces_raw_by_run_reg: Dict[str, Dict[str, np.ndarray]] = None
    traces_by_run_signal_trial: Dict[str, Dict[str, np.ndarray]] = None
    
    # Regression
    regression_bin_size: int = None
    corrsig_reg_results: Dict[str, Dict[str, np.ndarray]] = None
    regressed_traces_by_run_signal_trial: Dict[str, Dict[str, np.ndarray]] = None
    
    def log(self, msg : str):
        self.logs.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {msg}')
        
    def __add__(self, other):
        # Self is assumed to be the 'primary' instance of data.
        merged_data_attr = {}
        shared_attribs = self.__dict__.keys() & other.__dict__.keys()
        orphan_attribs = self.__dict__.keys() - other.__dict__.keys()
        for attr in shared_attribs:
            merged_data_attr[attr] = agnostic_merge(self.__dict__[attr],
                                                    other.__dict__[attr])
        for attr in orphan_attribs:
            merged_data_attr[attr] = self.__dict__[attr]
            
def agnostic_merge(*args):
    pass

class DataManager:
    def __init__(self, data):
        self.data = data

    def save(self, file):
        with open(file, 'wb') as f:
            pickle.dump(self.data.__dict__, f)
        return

    def load(self, file):
        with open(file, 'rb') as f:
            data_dict = pickle.load(f)
        if isinstance(data_dict, MSPData):
            return data_dict
        return MSPData(**data_dict)

    def saveto_h5(self, path):
        """
        Save specific attributes from the dataclass instance stored in `self.data` to an HDF5 file.
        """
        traces = self.data.traces_by_run_signal_trial
        regressed_traces = self.data.regressed_traces_by_run_signal_trial

        with h5py.File(path, 'w') as hdf5_file:
            if traces is not None:
                traces_group = hdf5_file.create_group('traces_by_run_signal_trial')
                unpack_dict_to_hdf5(traces_group, traces)
            if regressed_traces is not None:
                regressed_traces_group = hdf5_file.create_group('regressed_traces_by_run_signal_trial')
                unpack_dict_to_hdf5(regressed_traces_group, regressed_traces)

def unpack_dict_to_hdf5(group, d):
    for key, value in d.items():
        if isinstance(value, dict):
            sub_group = group.create_group(key)
            unpack_dict_to_hdf5(sub_group, value)
        elif isinstance(value, list):
            group.create_dataset(key, data=value)
        elif isinstance(value, np.ndarray):
            group.create_dataset(key, data=value)
        else:
            group.attrs[key] = value
