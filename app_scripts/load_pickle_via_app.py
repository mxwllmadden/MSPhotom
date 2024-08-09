# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 15:55:40 2024

@author: mbmad
"""

from app_scripts.MSPhotom_AppInspector import AppInspector

inspector = AppInspector()
data = inspector.waitfor_change('data_ref')
inspector.close()