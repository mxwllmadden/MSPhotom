# -*- coding: utf-8 -*-
"""
Contains Controller Class for the App

Define all app behavior/events in this class.
"""


from tkinter import filedialog
import os
from PIL import Image, ImageTk
import threading
from typing import List, Tuple
from matplotlib import pyplot as pp
import numpy as np

from MSPhotom.data import MSPData, DataManager
from MSPhotom.gui.main import AppView
from MSPhotom import analysis


class MSPApp:
    def __init__(self):
        """
        Initialize an instance of the MSPhotom App.

        Returns
        -------
        None.

        """
        self.view = AppView()
        self.data = MSPData()

        # Setup Events
        self.view.image_tab.fileselectbutton.config(
            command=self.get_image_directory)
        self.view.image_tab.loadbutton.config(
            command=self.load_runs)
        self.view.image_tab.regselbutton.config(
            command=self.region_selection)
        self.view.image_tab.processbutton.config(
            command=self.processimages)
        self.view.image_tab.reset_button.config(
            command=self.reset_data)

        self.view.data_tab.refresh_but.config(
            command=self.refresh_data_view)
        self.view.data_tab.sv_data_but.config(
            command=self.save_data)
        self.view.data_tab.load_data_but.config(
            command=self.load_data)

        self.refresh_data_view()
    
    def run(self):
        self.view.mainloop()

    def get_image_directory(self):
        """
        Get directory with filedialog then place directory path in corresponding text field.
        """
        self.view.image_tab.topdirectory.set(
            filedialog.askdirectory())

    def load_runs(self):
        """
        Scan target directory for appropriate run folders then display runs
        and update state and photometry data object.

        """
        # Pull the data we need from View
        target_directory = self.view.image_tab.topdirectory.get()
        date_start = self.view.image_tab.date_start
        date_end = self.view.image_tab.date_end
        date_start_num = datetonum(date_start.get())
        date_end_num = datetonum(date_end.get())

        ani_prefix = self.view.image_tab.ani_prefix.get()
        ani_start = self.view.image_tab.ani_start
        ani_end = self.view.image_tab.ani_end

        img_prefix = self.view.image_param_tab.img_prefix.get()
        img_per_trial_per_channel = self.view.image_param_tab.img_per_trial_per_channel
        num_interpolated_channels = self.view.image_param_tab.num_interpolated_channels
        roi_names = [var.get() for var in self.view.image_param_tab.roi_names]
        
        # Check to ensure user input is appropriate
        if not os.path.exists(target_directory):
            self.view.image_tab.topdirectory.set('BAD PATH')
            return

        if (date_end_num is None) and (date_end_num is None):
            date_start.set("ERROR")
            date_end.set("ERROR")
            return

        if not (ani_start.get().isdigit() and ani_end.get().isdigit()):
            ani_start.set('ERROR')
            ani_end.set('ERROR')
            return
        ani_start = int(ani_start.get())
        ani_end = int(ani_end.get())

        if not img_per_trial_per_channel.get().isdigit():
            img_per_trial_per_channel.set('ERROR')
            return
        img_per_trial_per_channel = int(img_per_trial_per_channel.get())

        if not num_interpolated_channels.get().isdigit():
            num_interpolated_channels.set('ERROR')
            return
        num_interpolated_channels = int(num_interpolated_channels.get())
        
        # Generate candidate run path and filter to only existing paths
        candidate_date_paths = [target_directory+"/"+numtodate(date)
                                for date in range(date_start_num, date_end_num+1)]
        candidate_date_paths = [path for path in candidate_date_paths
                                if os.path.exists(path)]

        candidate_run_paths = [f'{path}/{ani_prefix} {ani_num} Run {run_num}'
                               for run_num in range(50)
                               for ani_num in range(ani_start, ani_end+1)
                               for path in candidate_date_paths]

        run_paths = [path for path in candidate_run_paths
                     if os.path.exists(path)]

        filetree_entries = [(path.split('/')[-2], path.split('/')[-1])
                            for path in run_paths]

        animal_names = list(set([path.split('/')[-1] for path in run_paths]))

        # Update View
        self.view.updatefiletreedisplay(filetree_entries)
        self.view.update_state('IP - Create Fiber Masks')

        # Update Data
        self.data.target_directory: str = target_directory
        self.data.img_date_range: Tuple[str, str] = (date_start.get(),
                                                     date_end.get())
        self.data.animal_names: List[str] = animal_names
        self.data.animal_basename: str = ani_prefix
        self.data.run_path_list: List[str] = run_paths
        self.data.img_prefix: str = img_prefix
        self.data.img_per_trial_per_channel: int = img_per_trial_per_channel
        self.data.num_interpolated_channels: int = num_interpolated_channels
        self.data.roi_names: List[str] = roi_names

    def region_selection(self):
        """
        Generate a popup region selection window and define its behavior.
        """
        self.view.update_state('None')
        self.data_regsel = {'ROIs':
                            ['Background Fiber', 'Correction Fiber']
                            +
                            [roi.get() for roi in
                             self.view.image_param_tab.roi_names
                             if roi.get() != ''],
                            'roi_cursor': 0,
                            'displayimg': self.region_selection_get_image(),
                            'mask_coords': []
                            }
        popout = self.view.popout_regsel(reg_names=self.data_regsel['ROIs'],
                                         img=self.data_regsel['displayimg'])
        
        popout.bind('<Destroy>', self.region_selection_prematureclose)
        self.view.regsel.selectioncanvas.bind(
            "<B1-Motion>", self.region_selection_drag)
        self.view.regsel.confirmbutton.config(
            command=self.region_selection_button_select)

    def region_selection_get_image(self):
        """
        Load an image from the first runpath to use as a backdrop for region/fiber
        selection.
        """
        frpath = self.data.run_path_list[0]
        imprefix = self.data.img_prefix
        impath = f'{frpath}/{imprefix}_2.tif'
        impath2 = f'{frpath}/{imprefix}_1.tif'
        cmap = pp.get_cmap('nipy_spectral')
        with Image.open(impath) as im:
            np_im = np.asarray(im)
        with Image.open(impath2) as im2:
            np_im2 = np.asarray(im2)
        np_im = np_im2 / np_im
        np_im = np_im - np_im.min()
        np_im = np_im / np_im.max()
        im_array : np.ndarray = np.asarray(cmap(np_im))*255
        im_array : np.ndarray = im_array.astype(np.uint8)[:,:,:3]
        return ImageTk.PhotoImage(Image.fromarray(im_array, mode='RGB'))

    def region_selection_prematureclose(self, event):
        """
        Reset view state if window is closed prematurely.
        """
        if event.widget == event.widget.winfo_toplevel():
            self.view.update_state('IP - Create Fiber Masks')
            self.data_regsel = None

    def region_selection_drag(self, event):
        """
        Allow user to move selection oval on left mouse click+drag
        """
        selcanvs = self.view.regsel.selectioncanvas
        selectoval = self.view.regsel.selectoval
        selcanvs.moveto(selectoval, event.x-50, event.y-50)

    def region_selection_button_select(self):
        """
        On selection of region, store information and display selected fiber.
        Proceeds to next fiber/region when done or closes region selection window
        and updates data and view correspondingly
        """
        selcanvs = self.view.regsel.selectioncanvas
        selectoval = self.view.regsel.selectoval
        currentregionstrvar = self.view.regsel.currentregion
        # Get location of oval
        x, y, dx, dy = selcanvs.coords(selectoval)
        # Leave behind a marker for the location
        new_circle_marker = selcanvs.create_oval(x, y, dx, dy,
                                                 outline='blue', width=3)
        # Save the coordinates
        self.data_regsel['mask_coords'].append((x, y, dx, dy))
        # Iterate to next region
        self.data_regsel['roi_cursor'] += 1
        if self.data_regsel['roi_cursor'] >= len(self.data_regsel['ROIs']):
            # Time to quit and dump all data_regsel into data
            self.data.fiber_labels = self.data_regsel['ROIs']
            self.data.fiber_coords = self.data_regsel['mask_coords']
            self.view.regsel.container.destroy()
            self.view.update_state('IP - Ready to Process')
        else:
            currentregionname = self.data_regsel['ROIs'][
                self.data_regsel['roi_cursor']]
            # Set the label for the current region
            currentregionstrvar.set(f'Currently selecting {currentregionname}')

    def processimages(self):
        """
        Update view and start image processing in another thread
        """
        # Update View
        self.view.update_state('IP - Processing')
        # Create and initialize the thread for image loading/processing
        pross_thread = threading.Thread(target=analysis.imageprocess.process_main,
                                        args=(self.data,
                                              self),
                                        daemon=True)
        pross_thread.start()

    def reset_data(self):
        """
        Remove data object and create new. Update state accordingly.
        """
        # Update View
        self.view.update_state('IP - Parameter Entry')

        # Recreate Data
        self.data = MSPData()

    def refresh_data_view(self):
        """
        Refresh the inspection window with current information about the data
        object
        """
        self.view.data_tab.update(self.data.__dict__)

    def save_data(self):
        """
        Save data object to file in pickle format
        """
        file = filedialog.asksaveasfilename(defaultextension='.pkl',
                                            filetypes=[
                                                ('Python Pickle', '*.pkl')],
                                            title='Save Data')
        if file is not None:
            manage = DataManager(self.data)
            manage.save(file)

    def load_data(self):
        """
        Load data from pickle file
        
        UNSAFE! Depickling allows the execution of arbitrary code. You should
        NEVER open a pickle file from a non-trusted source.
        """
        file = filedialog.askopenfilename(defaultextension='.pkl',
                                          filetypes=[
                                              ('Python Pickle', '*.pkl')],
                                          title='Load Data')
        if file is not None:
            manage = DataManager(self.data)
            self.data = MSPData(**manage.load(file).__dict__)
        self.unpack_params_from_data()
        self.set_state_based_on_data()
        
    def unpack_params_from_data(self):
        loaded_data = self.data.__dict__
        loaded_data['animal_start'] = 0
        loaded_data['animal_end'] = 100
        if loaded_data['img_date_range'] is not None:
            loaded_data['date_start'] = loaded_data['img_date_range'][0]
            loaded_data['date_end'] = loaded_data['img_date_range'][1]
        corresponding_params = {'target_directory' : self.view.image_tab.topdirectory,
                                'date_start' : self.view.image_tab.date_start,
                                'date_end':self.view.image_tab.date_end,
                                'animal_prefix' : self.view.image_tab.ani_prefix,
                                'animal_start' : self.view.image_tab.ani_start,
                                'animal_end' : self.view.image_tab.ani_end,
                                'img_prefix' : self.view.image_param_tab.img_prefix,
                                'img_per_trial_per_channel' : self.view.image_param_tab.img_per_trial_per_channel,
                                'num_interpolated_channels' : self.view.image_param_tab.num_interpolated_channels,
                                }
        for key, param in corresponding_params.items():
            if key in loaded_data.keys():
                if loaded_data[key] is not None:
                    param.set(loaded_data[key])
                    continue
            param.set('')
        
        if 'roi_names' in loaded_data.keys():
            if loaded_data['roi_names'] is not None:
                for roi, strvar in zip(loaded_data['roi_names'], self.view.image_param_tab.roi_names):
                    strvar.set(roi)
        
    def set_state_based_on_data(self):
        """
        Based on the stored data in data object, update view.
        """
        humaninputs = multikey(self.data.__dict__,
                               'target_directory',
                               'img_date_range',
                               'img_prefix',
                               'img_per_trial_per_channel',
                               'num_interpolated_channels',
                               'roi_names')
        fileload = multikey(self.data.__dict__,
                            'animal_names',
                            'run_path_list')
        regionselect = multikey(self.data.__dict__,
                                'fiber_labels',
                                'fiber_coords')
        processingdone = multikey(self.data.__dict__,
                                  'fiber_masks',
                                  'traces_raw_by_run_reg',
                                  'traces_by_run_signal_trial')
        if not all(val is None for val in processingdone):
            self.view.update_state('RG - Ready for Regression')
            return
        if not all(val is None for val in regionselect):
            self.view.update_state('IP - Ready to Process')
            return
        if not all(val is None for val in fileload):
            self.view.update_state('IP - Create Fiber Masks')
            return
        if not all(val is None for val in humaninputs):
            self.view.update_state('IP - Parameter Entry')
            return

def multikey(x, *args):
    """
    

    Parameters
    ----------
    x : dict
        Dictionary to access multiple items.
    *args : TYPE
        Multiple keys to access within x.

    Returns
    -------
    result : TYPE
        List of values in order of supplied keys from within x.

    """
    result = []
    for arg in args:
        result.append(x[arg])
    return result

def datetonum(date: str):
    """
    Convert a date string in the format 'MM-DD-YY' to a numerical representation.

    Parameters
    ----------
    date : str
        Date string in the format 'MM-DD-YY'.

    Returns
    -------
    int
        Date in numerical format.

    """
    
    if len(date) != 8:
        return False
    if date[2] != "-" or date[5] != "-":
        return False
    mdyextract = [date[0:2], date[3:5], date[6:8]]
    if all(x.isdigit() for x in mdyextract):
        mdyextract = [int(i) for i in mdyextract]
        return ((mdyextract[1]) + (mdyextract[0]*40) + (mdyextract[2]*500))
    return False
    
def numtodate(numcode: int):
    assert isinstance(numcode, int), 'numtodate accepts integers only'
    y, d = divmod(numcode,500)
    m, d = divmod(d,40)
    return (str(m).zfill(2)+"-"+str(d).zfill(2)+"-"+str(y).zfill(2))


if __name__ == '__main__':
    MSPApp().run()
