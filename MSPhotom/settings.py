# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 16:38:51 2024

@author: mbmad
"""

import os, sys
import json

class Settings:
    def __init__(self):
        self.settings_file = get_settings_directory() + '\\settings.json'
        self.load()
    
    def load(self):
        try:
            settings = json_load(self.settings_file)
        except:
            settings = {}
        self.settings_dict = settings
        return settings
    
    def save(self):
        json_save(self.settings_file, self.settings_dict)

def json_save(filepath, data):
    """Saves data to a JSON file, creating directories if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Ensure directory exists
    
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def json_load(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError:
        raise ValueError(f"The file '{filepath}' contains invalid JSON.")
    except Exception as e:
        raise IOError(f"An error occurred while reading '{filepath}': {e}")


def get_settings_directory(app_name="MSPhotom"):
    # Get the correct base directory for each platform
    if os.name == 'nt':  # Windows
        base_dir = os.getenv('APPDATA', os.path.expanduser("~\\AppData\\Roaming"))
    elif os.name == 'posix':  # macOS/Linux
        if sys.platform == 'darwin':  # macOS
            base_dir = os.path.expanduser("~/Library/Application Support")
        else:  # Linux and other Unix-like OS
            base_dir = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    else:
        base_dir = os.path.expanduser("~")  # Fallback to the home directory
    
    # Create the app settings directory path
    settings_dir = os.path.join(base_dir, app_name)
    
    # Ensure the directory exists
    os.makedirs(settings_dir, exist_ok=True)
    
    return settings_dir
