#!/usr/bin/python3

import os
import sys
import getopt
from setting import base_dir, initialized, data_dir, setting_path, setting_yml,\
    face_encodings_path, locale_path
import yaml
import numpy as np
import json
import pickle


class Funing():
    def __init__(self):
        if not initialized:
            self.initialize()

    def start(self):
        from _ui._main_ui import _MainUI
        _MainUI()
    
    def msgfmt( self ):
        for d in os.listdir( locale_path ):
            po_p_p =  f'{locale_path}/{d}/LC_MESSAGES'
            os.system(f'msgfmt -o {po_p_p}/funing.mo {po_p_p}/funing.po')

    def pip_install_r( self ):
        os.system('pip3 install -r requirements.txt ')

    def initialize( self ):
        first_mo_path = os.path.join( \
            base_dir, 'locale','en-US', 'LC_MESSAGES', 'funing.mo')
        
        if not os.path.exists( first_mo_path ):
            try: self.msgfmt()
            except Exception as e:
                print( e )
                print( 'Make sure gettext is installed, '+\
                    'read https://www.gnu.org/software/gettext/ '+\
                    'and install it. (^_^)' )

        if not os.path.exists( data_dir ): os.mkdir( data_dir )
        if not os.path.exists( face_encodings_path ):
            pickle.dump({}, open(face_encodings_path, 'wb'))

        initialized = True
        setting_yml['initialized'] = initialized
        yaml.dump( setting_yml, open( setting_path, 'w') )


if __name__ == '__main__':
    sys_argv = sys.argv[1:]
    
    f = Funing()

    optlist , args  = getopt.getopt( sys_argv, '' )

    for a in args:
        if a in [ 's' ,'st', 'start' ]:
            f.start()
        elif a in [ 'm' , 'msg' , 'msgfmt' ]:
            f.msgfmt()
        
        elif a in ['pip' , 'pip_install']:
            f.pip_install_r()
        
        elif a in [ 'init', 'initial' ]:
            f.initialize()
      