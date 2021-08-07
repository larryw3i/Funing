#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
import getopt
from funing import settings
import re
import shutil
import uuid

# DON't IMPORT ANYTHING FROM THIS FILE
class Funing():
    def __init__(self):
        self.dir = os.path.abspath( os.path.dirname(  __file__  ) )
        self.data_dir = os.path.join( self.dir, 'data' )
        self.xgettext_path = os.path.join( self.data_dir, 'xgettext_f.txt' )
        if not os.path.exists( self.data_dir ):
            os.makedirs( self.data_dir,exist_ok=True )
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
        # os.remove( self.xgettext_path )

    def pybabel_extract( self ):
        os.system(f'pybabel extract -o {settings._locale_path}/funing.pot'+
        f'  --omit-header {settings.project_path}/*')
    
    def pybabel_update( self ):
        for l in settings.locale_langcodes:
            os.system( f'pybabel  update -D funing  -i {settings._locale_path}'+
            f'/funing.pot   -d {settings.locale_path}  --omit-header -l {l}')

    def msgfmt( self ):
        from funing._ui import Enjoy
        Enjoy().msgfmt()

    def keep_code( self ):
        from funing._ui import Enjoy
        Enjoy().keep_code()

    def pip_install_r( self ):
        os.system('pip3 install -r requirements.txt ')
        
if __name__ == '__main__':
    f = Funing()
    sys_argv = sys.argv[1:]
    optlist , args  = getopt.getopt( sys_argv, '' )
    if len(args) < 1: f.start()
    for a in args:
        if a in [ 's', 'ts' ,'st', 'start' ]:   f.start()
        if a in [ 'xgettext', 'xg' ]:           f.xgettext()
        if a in [ 'm' , 'msg' , 'msgfmt' ]:     f.msgfmt()
        if a in [ 'kc', 'keep_code' ]:          f.keep_code()
        if a in [ 'pip' , 'pip_install']:       f.pip_install_r()
        if a in [ 'be' , 'pbe']:                f.pybabel_extract()
        if a in [ 'bu' , 'pbu']:                f.pybabel_update()