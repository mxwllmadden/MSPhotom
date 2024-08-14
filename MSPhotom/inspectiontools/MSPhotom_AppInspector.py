# -*- coding: utf-8 -*-
"""
Contains resources for inspecting or changing the behavior of the MSPhotom
Application.

Created on Wed Aug  7 10:07:07 2024

@author: mbmad
"""

from MSPhotom import MSPApp
import threading
from copy import deepcopy
import os
import time

class AppInspector:
    def __init__(self):
        self._reporter = {'APP' : None,
                          'STATUS' : 'RUN'}
        self.app_thread = threading.Thread(target = initialize_app,
                                           args=(self._reporter,),
                                           daemon=True)
        self.monitor_thread = threading.Thread(target= self._monitorapp,
                                               daemon=True)
        self.app_thread.start()
        self.app = self.waitfor('APP')
        self.monitor_thread.start()
        
    def waitfor(self, index, limit = 20):
        count = 0
        while True:
            time.sleep(1)
            count += 1
            if self._reporter[index] is not None:
                break
            if limit is not None:
                if count > limit:
                    print('Waitfor limit exceeded')
                    break
        return self._reporter[index]
     
    def waitfor_change(self, index, limit = None):
        try:
            old_val = self._reporter[index]
        except KeyError:
            self._reporter[index] = None
            self._reporter[index] = self.waitfor(index, limit = limit)
            old_val = self._reporter[index]
        count = 0
        while True:
            time.sleep(1)
            count += 1
            if self._reporter[index] != old_val:
                break
            if limit is not None:
                if count > limit:
                    print('Waitfor limit exceeded')
                    break
        return self._reporter[index]

    def _monitorapp(self):
        while True:
            time.sleep(1)
            if self._reporter['STATUS'] == 'KILL':
                break
            self._reporter['data_ref'] = self.app.data
            self.data = self.app.data
            self._reporter.update(self.app.data.__dict__)

    def close(self):
        print('Initiating gracefull closure of monitor thread...')
        self._reporter['STATUS'] = 'KILL'
        self.monitor_thread.join()
        print('Monitor Thread Closed')
        print('Close the App Manually')

def initialize_app(reporter):
    app = MSPApp()
    reporter['APP'] = app
    app.run()

if __name__ == '__main__':
    Inspector = AppInspector()
