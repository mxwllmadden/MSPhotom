# -*- coding: utf-8 -*-
"""
Regression related GUI elements
"""
import tkinter as tk
from tkinter import ttk


class RegressionTab(tk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # Organizational Canvas
        buttoncanvas = tk.Canvas(self)
        buttoncanvas.grid(column=4, row=0, padx=(0, 10), pady=0, sticky="e", rowspan=4)
        self.graphcanvas = tk.Canvas(self, width=330, height=330, highlightbackground="#5C5C5C", highlightthickness=1)
        self.graphcanvas.grid(column=0, row=10, padx=(10, 0), pady=(23, 0), sticky="nw", columnspan=4, rowspan=2)
        graphbuttoncanvas = tk.Canvas(self, height=320)
        graphbuttoncanvas.grid(column=4, row=10, padx=(0, 10), pady=(0,4), sticky="w", columnspan=1, rowspan=12)

        # Buttons
        self.load_button = tk.Button(buttoncanvas, text="Set Bin")
        self.regress_button = tk.Button(buttoncanvas, text="REGRESS!!!")
        self.reset_button = tk.Button(buttoncanvas, text="RESET")

        self.graph_corrsig_button = tk.Button(graphbuttoncanvas, text="Corrsig Reg Graph")
        self.graph_channel_button = tk.Button(graphbuttoncanvas, text="Ch0 Reg Graph")
        self.reset_graph_button = tk.Button(graphbuttoncanvas, text="Reset Graph")

        self.load_button.grid(column=0, row=1, padx=0, pady=(0, 10), sticky="se")
        self.regress_button.grid(column=0, row=2, padx=0, pady=(0, 10), sticky="se")
        self.reset_button.grid(column=0, row=3, padx=2, pady=(0, 10), sticky="se")

        self.graph_corrsig_button.grid(column=0, row=9, padx=0, pady=(0, 10), sticky="sw")
        self.graph_channel_button.grid(column=0, row=10, padx=0, pady=(0, 10), sticky="sw")
        self.reset_graph_button.grid(column=0, row=11, padx=0, pady=(0, 10), sticky="sw")

        # String Variables and Defaults
        self.bin_size = tk.StringVar()

        self.ch_select = tk.StringVar()
        self.run_select = tk.StringVar()
        self.reg_select = tk.StringVar()

        self.trial_select = tk.StringVar()
        self.bin_size.set("1")
        self.num_regs = tk.StringVar()
        self.num_runs = tk.StringVar()
        self.trial_select.set("10")

        # Entry Fields
        tk.Label(self, width=13, text="Total Runs", anchor='w').grid(column=1, row=0, padx=(7, 0), pady=(10, 0),
                                                                     sticky="nw")
        tk.Label(self, width=13, text="Regions", anchor='w').grid(column=2, row=0, padx=(7, 0), pady=(10, 0),
                                                                  sticky="nw")
        tk.Label(self, text="Bin Size", anchor="w", width=15).grid(column=0, row=0, padx=7, pady=(10, 0), sticky='nw')

        tk.Label(self, width=13, textvariable=self.num_runs, anchor='w').grid(column=1, row=1, padx=(7, 0), pady=0,
                                                                              sticky="nw")
        tk.Label(self, width=13, textvariable=self.num_regs, anchor='w').grid(column=2, row=1, padx=(7, 0), pady=0,
                                                                              sticky="nw")
        self.binsizeentry = tk.Entry(self, width=15, textvariable=self.bin_size)
        self.binsizeentry.grid(column=0, row=1, padx=7, pady=(0, 10), sticky="nw")

        # Static Labels
        tk.Label(graphbuttoncanvas, text="Run Select", anchor="w").grid(column=0, row=0, sticky="sw")
        tk.Label(graphbuttoncanvas, text="Channel Select", anchor="w").grid(column=0, row=2, sticky="sw")
        tk.Label(graphbuttoncanvas, text="Region Select", anchor="w").grid(column=0, row=4, sticky="sw")
        tk.Label(graphbuttoncanvas, text="Trial Select", anchor="w").grid(column=0, row=6, sticky="sw")

        self.run_selector = ttk.Combobox(graphbuttoncanvas, width=15, state="readonly", textvariable=self.run_select)
        self.run_selector.grid(column=0, row=1, pady=(0, 10), sticky="sw")
        self.ch_selector = ttk.Combobox(graphbuttoncanvas, width=15, state="readonly", textvariable=self.ch_select)
        self.ch_selector.grid(column=0, row=3, pady=(0, 10), sticky="sw")
        self.reg_selector = ttk.Combobox(graphbuttoncanvas, width=15, state="readonly", textvariable=self.reg_select)
        self.reg_selector.grid(column=0, row=5, pady=(0, 10), sticky="sw")
        self.trial_selector = tk.Entry(graphbuttoncanvas, width=18, textvariable=self.trial_select)
        self.trial_selector.grid(column=0, row=7, pady=(0, 10), sticky="sw")

        self.run_selector["state"] = "disabled"
        self.ch_selector["state"] = "disabled"
        self.reg_selector["state"] = "disabled"
        self.trial_selector["state"] = "disabled"

        # Progress Bars
        self.runprog = ttk.Progressbar(self, orient="horizontal", length=480, mode="determinate")
        self.runprog["value"] = 0
        self.runprog.grid(column=0, row=13, columnspan=6, padx=(8, 0), pady=(20, 0), sticky="ew")
        self.shortprogstat = tk.StringVar()
        self.shortprogstat.set("Regressing Images...")
        tk.Label(self, width=18, textvariable=self.shortprogstat).grid(column=0, row=14, padx=10, pady=0, columnspan=6)
