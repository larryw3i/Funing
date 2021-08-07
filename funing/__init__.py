#!/usr/bin/python3

import os
import sys
from pathlib import Path
import getopt
from funing import settings
from funing._ui import Enjoy

def run():
    sys_argv = sys.argv[1:]
    f = Enjoy()
    optlist , args  = getopt.getopt( sys_argv, '' )    
    if len(args) < 1: f.start()
    for a in args:
        if a in [ 's', 'ts' ,'st', 'start' ]:   f.start()
        if a in [ 'm' , 'msg' , 'msgfmt' ]:     f.msgfmt()
        if a in [ 'init', 'initial' ]:          f.initialize()
        if a in [ 'kc', 'keep_code' ]:          f.keep_code()
