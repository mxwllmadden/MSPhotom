# -*- coding: utf-8 -*-
"""
Data related GUI elements
"""

import tkinter as tk


class DataTab(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.load_data_but = tk.Button(self, text='Load PICKLE')
        self.refresh_but = tk.Button(self, text='Refresh')
        self.sv_data_but = tk.Button(self, text='to PICKLE')
        self.sv_h5_but = tk.Button(self, text='to h5(for MAT)')

        self.load_data_but.grid(column=0, row=0, sticky='s', padx=10)
        self.refresh_but.grid(column=1, row=0, sticky='s', padx=10)
        self.sv_data_but.grid(column=2, row=0, sticky='s', padx=10)
        self.sv_h5_but.grid(column=3, row=0, sticky='s', padx=20)
        
        for ind in range(5):
            self.columnconfigure(ind, minsize=100)
        
        self.current = []
        
    def update(self, data : dict):
        for widget in self.current:
            widget.destroy()
        self.current = []
        for ind, (key, item) in enumerate(data.items()):
            label = tk.Label(self, text = key)
            label.grid(column = 0, row=ind+1, columnspan=2)
            self.current.append(label)
            if isinstance(item, (int,str,float)) or key == 'roi_names':
                disp_item = str(item)
            elif isinstance(item, (list,dict)):
                disp_item = f'Contains {len(item)} items'
            elif item is None:
                disp_item = 'NA'
            else:
                disp_item = 'Unknown'
            value_label = tk.Label(self, text = disp_item)
            value_label.grid(column=2, row = ind+1, columnspan = 2)
            self.current.append(value_label)
