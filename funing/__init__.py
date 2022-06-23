#!/usr/bin/python3

import os
import sys
from pathlib import Path
import getopt
from funing import settings


class LarryFuning():
    def __init__(self):
        pass
        

def run():
    sys_argv = sys.argv[1:]
    optlist , args  = getopt.getopt( sys_argv, '' )    
    if len(args) < 1: f.start()
    for a in args:
        if a in [ 's', 'ts' ,'st', 'start' ]:   f.start()
        if a in [ 'm' , 'msg' , 'msgfmt' ]:     f.msgfmt()
        if a in [ 'init', 'initial' ]:          f.initialize()
        if a in [ 'kc', 'keep_code' ]:          f.keep_code()
