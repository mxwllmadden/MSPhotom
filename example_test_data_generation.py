# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 15:00:35 2024

@author: mbmad
"""

from MSPhotom.data import MSPData
import numpy as np
import random
import MSPhotom.analysis.regression as reg

class FakeData(MSPData):
    def __init__(self):
        super().__init__(self)
        v_laser_fluct = self.sig_s(100, 4)
        b_laser_fluct = self.sig_s(100, 5)
        
        v_noise = self.randpeaks(100, 40)
        self.true_sig = self.randpeaks(100, 20)
        self.traces_by_run_signal_trial = {
            'run1': {
                'sig_region1_ch0': np.expand_dims(v_laser_fluct + v_noise, axis=1),  # Trials as columns
                'sig_region1_ch1': np.expand_dims(b_laser_fluct + self.true_sig + v_noise, axis=1),  # Trials as columns
                'sig_corrsig_ch0': np.expand_dims(v_laser_fluct, axis=1),  # Trials as columns
                'sig_corrsig_ch1': np.expand_dims(b_laser_fluct, axis=1),  # Trials as columns
            }
        }

    
    @staticmethod
    def sig_s(num_points, const):
        time = np.arange(num_points)
        return np.sin(const * np.pi * time / (num_points))
    
    @staticmethod
    def randpeaks(num_points, num_peaks):
        time = np.zeros(num_points)
        for i in range(num_peaks):
            time[random.randint(0, num_points-1)] = 10
        return time

binsize = 1
if __name__ == '__main__':
    f_dat = FakeData()
    out_trace = reg.regression_main(f_dat)