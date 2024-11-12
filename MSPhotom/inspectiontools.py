# -*- coding: utf-8 -*-
"""
Contains resources for inspecting or changing the behavior of the MSPhotom
Application.

Created on Wed Aug  7 10:07:07 2024

@author: mbmad
"""
from MSPhotom import MSPApp
from MSPhotom.mxtools.classes import create_monitored_class, MonitoredClass

MSPInspector = create_monitored_class(MSPApp, do_not_monitor = ('region_selection_drag'))


if __name__ == '__main__':
    MSPInspector().run()