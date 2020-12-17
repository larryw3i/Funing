#!/usr/bin/python3

import os
import sys

from _ui._main_ui import MainUIdef
from model.funing_m import FuningM


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

    sys.path.append( f.base_dir )
    if sys_argv[1] == 'gm':
        fm.generate_mapping()
    if sys_argv[1] == 'start':
        f.start()