#!/usr/bin/python3

import os
import sys
from pathlib import Path
import getopt
from funing import settings

def get_dep_requirements():
    return [
    'opencv-contrib-python >= 4.5.3.56',
    'Pillow >= 8.3.0',
    'numpy >= 1.21.1',
    ]

def install_dep_requirements(test =False):
    dep_requirements = get_dep_requirements()
    sh = "pip3 install -U "+(" ".join(dep_requirements))
    if test:
        print(sh)
    os.system(sh)

def show():
    pass

def run():
    sys_argv = sys.argv[1:]
    optlist , args  = getopt.getopt( sys_argv, '' )   
    print(args) 
    if len(args) < 1: show()
    for a in args:
        if a in [ 'dep' ]:      install_dep_requirements()
        if a in [ 'ok' ]:       break
        