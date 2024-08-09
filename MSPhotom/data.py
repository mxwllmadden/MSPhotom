 # -*- coding: utf-8 -*-
"""
Contains Dataclass that contains all photometry data and parameters and related
functions for saving/accessing or general utilities for dealing with that data.
"""
from typing import List, Tuple, Dict
from dataclasses import dataclass, field
import numpy as np
from scipy.io import savemat, loadmat
from datetime import datetime
import pickle


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
    
    def log(self, msg : str):
        self.logs.append(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {msg}')


class DataManager:
    def __init__(self, data):
        self.data = data

    def save(self, file):
        with open(file, 'wb') as f:
            pickle.dump(self.data, f)
        return

    def load(self, file):
        with open(file, 'rb') as f:
            return pickle.load(f)
        return
            

    def saveto_matlab(self, path):
        savemat(path, self.data.__dict__)

    def loadfrom_matlab(self, path):
        pass
