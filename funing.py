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

    def test( self ):
        os.environ['FUNING_TEST'] = '1'
        self.start()

    def start( self ):
        sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
        from funing import run
        sys.exit(run())

    def pybabel_extract( self ):
        os.system(f'pybabel extract -o {settings.locale_path}/funing.pot'+
        f'  --omit-header {settings.project_path}/*')
    
    def pybabel_update( self ):
        for l in settings.locale_langcodes:
            os.system( f'pybabel  update -D funing  -i {settings.locale_path}'+
            f'/funing.pot   -d {settings.locale_path}  --omit-header -l {l}')

    def msgfmt( self ):
        from funing._ui import Enjoy

        f_mo_path  = os.path.join(settings.locale_path, 'en_US' ,\
        'LC_MESSAGES', 'funing.mo' )
        if not os.path.exists( f_mo_path ):
            Enjoy()
        else:
            Enjoy().msgfmt()

    def keep_code( self ):
        from funing._ui import Enjoy
        Enjoy().keep_code()

    def pip_install_r( self ):
        os.system('pip3 install -r requirements.txt ')
       
    def help( self ):
        print(
            '''

        start_args = ['s', 'st', 'start']
        test_args = [ 'ts','t', 'test' ]
        xgettext_args = [ 'xgettext', 'xg']
        msgfmt_args = ['m' , 'msg' , 'msgfmt']
        keep_code_args = ['kc', 'keep_code']    
        pip_install_r_args = ['pip' , 'pip_install']
        pybabel_extract_args = ['be' , 'pbe']
        help_args = ['h','help', ]
        pybabel_update_args = [ 'bu' , 'pbu']

        
        if a in help_args:              f.help()
        if a in test_args:              f.test()
        if a in start_args:             f.start()
        if a in xgettext_args:          f.xgettext()
        if a in msgfmt_args:            f.msgfmt()
        if a in keep_code_args:         f.keep_code()
        if a in pip_install_r_args:     f.pip_install_r()
        if a in pybabel_extract_args:   f.pybabel_extract()
        if a in pybabel_update_args:    f.pybabel_update()

        '''
        )
        
if __name__ == '__main__':

    start_args = ['s', 'st' 'start']
    test_args = [ 'ts', 't','test']
    xgettext_args = [ 'xgettext', 'xg']
    msgfmt_args = ['m' , 'msg' , 'msgfmt']
    keep_code_args = ['kc', 'keep_code']    
    pip_install_r_args = ['pip' , 'pip_install']
    pybabel_extract_args = ['be' , 'pbe']
    help_args = ['h','help', ]
    pybabel_update_args = [ 'bu' , 'pbu']
    autopep8_args = [ 'p8', 'ap8' ]

    all_args = test_args + xgettext_args + msgfmt_args + keep_code_args + \
    pip_install_r_args + pybabel_extract_args + pybabel_update_args \
    + start_args+ autopep8_args
    
    f = Funing()
    sys_argv = sys.argv[1:]
    
    optlist , args  = getopt.getopt( sys_argv, 'stmh', all_args )

    if len(args) < 1: f.start()

    for a in args:
        if a in help_args:              f.help()
        if a in test_args:              f.test()
        if a in start_args:             f.start()
        if a in xgettext_args:          f.xgettext()
        if a in msgfmt_args:            f.msgfmt()
        if a in keep_code_args:         f.keep_code()
        if a in pip_install_r_args:     f.pip_install_r()
        if a in pybabel_extract_args:   f.pybabel_extract()
        if a in pybabel_update_args:    f.pybabel_update()
        if a in autopep8_args:          f.autopep8()
        
