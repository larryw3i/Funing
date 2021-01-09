#!/usr/bin/python3

import os
import sys

from _ui._main_ui import MainUIdef
from model.funing_m import FuningM, data_file_path


class Funing():
    def __init__(self):
        self.base_dir = os.path.abspath(
            os.path.dirname(__file__))
    
    def start(self):
        MainUIdef()
        

if __name__ == '__main__':
    sys_argv = sys.argv
    f = Funing()
    fm = FuningM()
       
    if sys_argv[1] in ['start', 'st']:
        f.start()