#!/usr/bin/python3

import os
import sys
from pathlib import Path
sys.path.append( str(Path( os.path.abspath( __file__)  ).parent.absolute() ) )
import getopt
from setting import base_dir, initialized, data_dir, setting_path, \
    setting_yml, face_encodings_path, locale_path, f_lang_codes, debug,\
    data_file_path
import yaml
import json
import pickle
from _fui import _Fui

def run():
    sys_argv = sys.argv[1:]

    f = _Fui()

    optlist , args  = getopt.getopt( sys_argv, '' )

    for a in args:
        # arg 'ts' with test
        if a in ['s' , 'ts' ,'st', 'start' ]:
            f.start()
        elif a in [ 'm' , 'msg' , 'msgfmt' ]:
            f.msgfmt()
        
        elif a in ['pip' , 'pip_install']:
            f.pip_install_r()
        
        elif a in [ 'init', 'initial' ]:
            f.initialize()

        