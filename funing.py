#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
import getopt
from funing import settings
import re

# DON't IMPORT ANYTHING FROM THIS FILE
class Funing():
    def __init__(self):
        self.dir = os.path.abspath( os.path.dirname(  __file__  ) )
        self.data_dir = os.path.join( self.dir, 'data' )
        self.xgettext_path = os.path.join( self.data_dir, 'xgettext_f.txt' )
        pass

    def start( self ):
        sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
        from funing import run
        sys.exit(run())

    def xgettext( self ):
        from funing import settings
        mo_files = []
        xgettext_files = []
        for root, dirs, files in os.walk( settings.project_path ):
            for f in files:
                if  f.endswith('.py'): 
                    xgettext_files.append( os.path.join( root, f ) )
        xgettext_files = '\n'.join( xgettext_files )
        open( self.xgettext_path , 'w+').write( xgettext_files )        
        for root, dirs, files in os.walk( settings.locale_path ):
            for f in files:
                if  f.endswith('.po'): 
                    f_path = os.path.join( root, f )
                    os.system(f'xgettext -f {self.xgettext_path} '+\
                    f'--join-existing -d funing -o {f_path}' )
        os.remove( self.xgettext_path )
    def msgfmt( self ):
        from funing._fui import Enjoy
        Enjoy().msgfmt()

if __name__ == '__main__':
    f = Funing()
    sys_argv = sys.argv[1:]
    optlist , args  = getopt.getopt( sys_argv, '' )
    if len(args) < 1: f.start()
    for a in args:
        if a in [ 's', 'ts' ,'st', 'start' ]:   f.start()
        if a in [ 'xgettext', 'xg' ]:           f.xgettext()
        if a in [ 'm' , 'msg' , 'msgfmt' ]:     f.msgfmt()
        
