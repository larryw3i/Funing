#!/usr/bin/python3

import os
import sys
from pathlib import Path
import getopt
from funing import settings
import yaml
import json
import pickle
from funing._fui import Enjoy

sys.path.append( 
    str( Path( os.path.abspath( __file__)  ).parent.absolute() ) )
def run():
    sys_argv = sys.argv[1:]
    f = Enjoy()
    optlist , args  = getopt.getopt( sys_argv, '' )    
    if len(args) < 1: f.start()
    for a in args:
        # arg 'ts' with test
        if a in [ 's', 'ts' ,'st', 'start' ]:   f.start()
        if a in [ 'm' , 'msg' , 'msgfmt' ]:     f.msgfmt()
        if a in [ 'pip' , 'pip_install']:       f.pip_install_r()
        if a in [ 'init', 'initial' ]:          f.initialize()
        if a in [ 'kc', 'keep_code' ]:          f.keep_code()
