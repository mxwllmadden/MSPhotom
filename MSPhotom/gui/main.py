# -*- coding: utf-8 -*-
"""
Main GUI class. Define 'View' and define high level GUI appearance and provide
methods for easy manipulation of the GUI.
"""

import tkinter as tk
from tkinter import ttk
from MSPhotom.gui.imageprocess import ImageProcessTab, ImageParamTab, RegionSelection
from MSPhotom.gui.regression import RegressionTab
from MSPhotom.gui.data import DataTab
from typing import List, Tuple
from itertools import chain


class AppView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Multisite Photometry Data Processing/Analysis App")
        self.root.geometry("500x570")
        self.root.resizable(0, 0)

        # Create Tabs/Frames
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=1, fill="both")
        self.data_tab = DataTab(notebook)
        self.image_tab = ImageProcessTab(notebook)
        self.image_param_tab = ImageParamTab(notebook)
        self.regression_tab = RegressionTab(notebook)
        notebook.add(self.data_tab, text = 'Inspect Data')
        notebook.add(self.image_tab, text='Image Processing (IP)')
        notebook.add(self.image_param_tab, text='Image Params (IP)')
        notebook.add(self.regression_tab, text='Regression (RG)')
        
        # Create StateSets for easy manipulation of states
        self.state = 'All'  # Default state for the program
        self.statesets = {
            'IP - Parameter Entry':
                [
                    *[child for child in self.image_tab.winfo_children()
                      if isinstance(child, tk.Entry)],
                    *[child for child in self.image_param_tab.winfo_children()
                      if isinstance(child, tk.Entry)],
                    self.image_tab.fileselectbutton,
                    self.image_tab.loadbutton,
                    self.image_tab.reset_button
                ],
            'IP - Create Fiber Masks':
                [
                    self.image_tab.regselbutton,
                    self.image_tab.reset_button
                ],
            'IP - Ready to Process':
                [
                    self.image_tab.regselbutton,
                    self.image_tab.processbutton,
                    self.image_tab.reset_button,
                    self.image_tab.threading_checkbox,
                    self.image_tab.autosave_checkbox
                ],
            'IP - Processing Images': 
                [
                    self.image_tab.autosave_checkbox
                ],
            'RG - Processing Done Ready to Input Bin' : 
                [
                    self.regression_tab.binsizeentry,
                    self.regression_tab.load_button,
                    self.regression_tab.reset_button
                ],
            'RG - Ready to Regress' :
                [
                    self.regression_tab.regress_button,
                    self.regression_tab.reset_button,
                    self.image_tab.reset_button
                ],
            'RG - Regressing' : [],
            'RG - Regression Done Ready to Graph' : [
                    self.regression_tab.reset_button,
                    self.regression_tab.reset_graph_button,
                    self.image_tab.reset_button,
                    self.regression_tab.run_selector,
                    self.regression_tab.reg_selector,
                    self.regression_tab.ch_selector,
                    self.regression_tab.trial_selector,
                    self.regression_tab.graph_channel_button,
                    self.regression_tab.graph_corrsig_button
                ],
            'RG - Graphing Done': [
                    self.regression_tab.reset_button,
                    self.regression_tab.reset_graph_button,
                    self.image_tab.reset_button
                ],
            
        }
        all_state_elements = list(chain(
            *[ss_list for ss_list in self.statesets.values()]
            ))
        self.statesets['All'] = list(set(all_state_elements)) #Special State Sets
        self.statesets['None'] = [] #Special State Sets

    def mainloop(self):
        self.root.mainloop()

    def updatefiletreedisplay(self, entrylist: List[Tuple[str, str]]):
        for child in self.image_tab.filetree.get_children():
            self.image_tab.filetree.delete(child)

        for ind, entry in enumerate(entrylist):
            self.image_tab.filetree.insert('',
                                           'end',
                                           text=str(ind),
                                           values=entry
                                           )

    def update_state(self, new_state):
        if new_state == 'IP - Parameter Entry':
            self.updatefiletreedisplay([])
        if new_state == 'RG - Regression Done Ready to Graph' or new_state == 'IP - Parameter Entry':
            for widget in self.regression_tab.graphcanvas.winfo_children():
                widget.destroy()
        self._update_state(new_state)

    def _update_state(self, new_state):
        if new_state not in self.statesets.keys():
            raise TypeError(
                f'Attempted to set state to {new_state}, which does not exist')
        for child in self.statesets[self.state]:
            child.config(state = tk.DISABLED)
        for child in self.statesets[new_state]:
            child.config(state = tk.NORMAL)
        self.state = new_state

    def popout_regsel(self, reg_names, img):
        top_lev = tk.Toplevel(self.root)
        self.regsel = RegionSelection(top_lev, reg_names, img)
        return top_lev


if __name__ == '__main__':
    app = AppView()
    app.mainloop()
