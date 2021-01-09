#!/usr/bin/python3

import os
import sys

from _ui._main_ui import MainUIdef


class Funing():
    def __init__(self):
        self.base_dir = os.path.abspath(
            os.path.dirname(__file__))
    
    def start(self):
        MainUIdef()
        

if __name__ == '__main__':
    sys_argv = sys.argv
    f = Funing()
       
    if sys_argv[1] in ['start', 'st']:
        f.start()