# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 10:00:19 2024

@author: mbmad
"""

import MSPhotom as msp
import threading
import time

def main():
    reporter = {'App' : None,
                'Data' : None}
    app_thread = threading.Thread(target=MSPhotom_Automated,
                                  args=(reporter,),
                                  daemon=True)
    app_thread.start()
    
    print('Waiting for App to load')
    app : MSPhotom_Automated = waitfor(reporter,'App')
    return app
    
class MSPhotom_Automated(msp.MSPApp):
    def __init__(self, reporter : list):
        self.reporter = reporter
        reporter['App'] = self
        super().__init__()

    def load_data(self):
        super().load_data()
        self.view.update_state('None')
        print('loaded!')
        self.reporter['Data'] = self.data

def waitfor(value, index):
    while True:
        print('check')
        time.sleep(1)
        if value[index] is not None:
            break
    return value[index]

if __name__ == '__main__':
    app = main()