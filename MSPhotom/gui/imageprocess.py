# -*- coding: utf-8 -*-
"""
Image Processing related GUI elements
"""

import tkinter as tk
from tkinter import ttk
from MSPhotom.gui.generalframes import ParameterWindow


class ImageProcessTab(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        
        #Organizational Canvas
        buttoncanvas = tk.Canvas(self)
        buttoncanvas.grid(column=2,row=9,padx=10,pady=0,sticky="se")
        runcanvas = tk.Canvas(self)
        runcanvas.grid(column=0,row=8,padx=10,pady=10,sticky="nw", columnspan=3, rowspan=2)
        
        #Buttons
        self.fileselectbutton = tk.Button(self, text="Open...")
        self.loadbutton = tk.Button(buttoncanvas, text="Load Runs")
        self.regselbutton = tk.Button(buttoncanvas, text="Select Regions")
        self.processbutton = tk.Button(buttoncanvas, text="PROCESS!!!!!")
        self.reset_button = tk.Button(buttoncanvas, text="RESET")
        
        self.fileselectbutton.grid(column=2,row=1,padx=10, pady=(0,10), sticky="w")
        self.loadbutton.grid(column=0, row=0,padx=0, pady=(0,10), sticky="se")
        self.regselbutton.grid(column=0, row=1,padx=0, pady=(0,10), sticky="se")
        self.processbutton.grid(column=0, row=2,padx=0, pady=(0,10), sticky="se")
        self.reset_button.grid(column=0, row=5,padx=2, pady=(0,10), sticky="se")
        

        #String Variables and Defaults
        self.topdirectory = tk.StringVar()
        self.date_start = tk.StringVar()
        self.date_end = tk.StringVar()
        self.ani_prefix = tk.StringVar()
        self.ani_start = tk.StringVar()
        self.ani_end = tk.StringVar()
        
        self.topdirectory.set("Use button to right")
        self.date_start.set("05-17-23")
        self.date_end.set("05-17-43")
        self.ani_prefix.set("MRKPFCREV")
        self.ani_start.set("1")
        self.ani_end.set("40")

        
        #Entry Fields
        tk.Entry(self, width=50, textvariable=self.topdirectory).grid(column=0, row=1, columnspan=2, padx=(10,0), pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.date_start).grid(column=0, row=4, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.date_end).grid(column=1, row=4, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_prefix).grid(column=0, row=7, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_start).grid(column=1, row=7, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_end).grid(column=2, row=7, padx=10, pady=(0,10), sticky="w")
        
        
        #Integer Variables and defaults
        self.threading_enabled = tk.IntVar()
        self.autosave_enabled = tk.IntVar()
        
        self.threading_enabled.set(1)
        self.autosave_enabled.set(1)
        
        #Checkbox and Numerical Entry
        self.threading_checkbox = tk.Checkbutton(buttoncanvas, text = 'Enable High Speed\n(EXPERIMENTAL)', variable=self.threading_enabled)
        self.threading_checkbox.grid(column = 0, row = 3, padx=(0,0), pady=(0,10), sticky="e")
        self.autosave_checkbox = tk.Checkbutton(buttoncanvas, text = 'Enable Autosave', variable=self.autosave_enabled)
        self.autosave_checkbox.grid(column = 0, row = 4, padx=(10,0), pady=(0,10), sticky="e")
        
        #Static Labels
        tk.Label(self, text="Dataset Folder Path", anchor="w",width=20).grid(column=0, row=0, padx=10, pady=(10,0))
        tk.Label(self, text="Start Date", anchor="w",width=20).grid(column=0, row=3, padx=10, pady=(10,0))
        tk.Label(self, text="End Date", anchor="w",width=20).grid(column=1, row=3, padx=10, pady=(10,0))
        tk.Label(self, text="Animal Basename", anchor="w",width=20).grid(column=0, row=6, padx=10, pady=(10,0))
        tk.Label(self, text="Start #", anchor="w",width=20).grid(column=1, row=6, padx=10, pady=(10,0))
        tk.Label(self, text="End #", anchor="w",width=20).grid(column=2, row=6, padx=10, pady=(10,0))
        
        #FileTree Viewer
        self.filetree = ttk.Treeview(runcanvas, height=10, columns=('date','run'),selectmode='browse')
        self.filetree.grid(row=0,column=0)
        self.filetree.column("#0", width=20)
        self.filetree.column("date", width=130)
        self.filetree.column("run", width=130)
        self.filetree.heading("date", text="Date", anchor="w")
        self.filetree.heading("run", text="Run", anchor="w")
        rtreescroll = ttk.Scrollbar(runcanvas, orient="vertical", command=self.filetree.yview)
        rtreescroll.grid(row=0,column=1,sticky="ns")
        self.filetree.config(yscrollcommand=rtreescroll.set)
        self.filetree.bind('<Motion>', 'break')
        
        #Progress bars
        self.longprog = ttk.Progressbar(self, orient="horizontal",length=480,mode="determinate")
        self.longprog["value"] = 0
        self.longprog.grid(column=0,row=10,columnspan=5)
        self.runprog = ttk.Progressbar(self, orient="horizontal",length=480,mode="determinate")
        self.runprog["value"] = 0
        self.runprog.grid(column=0,row=12,columnspan=5)
        self.longprogstat = tk.StringVar()
        self.longprogstat.set("Processing Runs...")
        tk.Label(self, width=18, textvariable=self.longprogstat).grid(column=0, row=11, padx=10, pady=(0,10), columnspan=5, sticky="nsew")
        self.shortprogstat = tk.StringVar()
        self.shortprogstat.set("Processing Images...")
        tk.Label(self, width=18, textvariable=self.shortprogstat).grid(column=0, row=13, padx=10, pady=0, columnspan=5, sticky="nsew")
        self.speedout = tk.StringVar()
        self.speedout.set("...")
        tk.Label(self,width=18, textvariable=self.speedout, anchor="w").grid(column=0,row=14,padx = 10,pady=0, sticky="w")
        
class ImageParamTab(ParameterWindow):
    def __init__(self, container):
        paramlabels = ['Image Prefix',
                       'Images per Trial per Channel',
                       '# of Interpolated Channels']
        for ind in range(5):
            paramlabels.append(f'ROI {ind} Name')
        
        self.img_prefix = tk.StringVar()
        self.img_per_trial_per_channel = tk.StringVar()
        self.num_interpolated_channels = tk.StringVar()
        self.roi_names = [tk.StringVar() for i in range(5)]
        
        self.img_prefix.set('mrk_pfc0')
        self.img_per_trial_per_channel.set('130')
        self.num_interpolated_channels.set('2')
        self.roi_names[0].set('PTA')
        
        paramvars = [self.img_prefix,
                     self.img_per_trial_per_channel,
                     self.num_interpolated_channels,
                     *self.roi_names]
        
        super().__init__(container, paramlabels, paramvars)

class RegionSelection(tk.Frame):
    def __init__(self, container, region_names, img):
        super().__init__(container)
        #dataset setup
        self.regions = region_names
        self.container = container
        container.geometry("420x520")
        container.resizable(0,0)
        self.selectioncanvas = tk.Canvas(container,height=424,width=424)
        self.selectioncanvas.place(x=0,y=0)
        self.selectioncanvas.create_image(0,0,image=img,anchor="nw")
        self.selectoval = self.selectioncanvas.create_oval(0,0,100,100,width=4,outline='red')
        tk.Label(container, text="Drag and drop the red circle to cover the selected region").place(x = 10, y = 430)
        self.currentregion = tk.StringVar()
        self.currentregion.set("Currently selecting "+self.regions[0])
        tk.Label(container, textvariable=self.currentregion).place(x=10, y = 470)
        self.confirmbutton = tk.Button(container, text="CONFIRM REGION")
        self.confirmbutton.place(x = 270, y = 470)
        self.activeregion = 0
        self.regshapelist = [] # List that will contain all the circle selectors marking the image