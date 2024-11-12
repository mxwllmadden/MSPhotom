# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:19:43 2024

@author: mbmad
"""

from MSPhotom.inspectiontools import MSPInspector, MonitoredClass
from MSPhotom import MSPApp
from MSPhotom.data import DataManager
from MSPhotom.analysis import imageprocess
from copy import deepcopy
from datetime import datetime
import threading
import numpy as np

def main()
    # Create 'fake images' in local directory
    trace_corr = np.zeros(200)+5
    trace_TOP = np.linspace(0, 100, num=200)
    trace_BOT = np.linspace(0, 200, num=200)
    trace_LEF = np.sin(trace_1/20)
    trace_RIGHT = np.sin(trace_2/20)

def createimage(bk, top, bot, left, right)
    image_workspace = np.zeros((424,424)) + bk
    image_workspace
    



def main():
    app: MonitoredClass = MSPInspector()
    app.monitor_method_call('run', trigger_on_run_call)
    return app.run()


def trigger_on_run_call(self, *args, **kwargs):
    self.view.root.title("MSPhotomApp - REMIXED!!! Use at own risk")
    self.data_old = deepcopy(self.data)
    self._remix_runs_done = []
    print(__doc__)
    return args, kwargs

main()