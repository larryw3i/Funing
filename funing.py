#!/usr/bin/python3

import os
import sys
from setting import base_dir


class Funing():
    def __init__(self):
        if not os.path\
            .exists(base_dir + '/locale/en-US/LC_MESSAGES/funing.po'):
            self.msgfmt()
        pass    

    def start(self):
        from _ui._main_ui import MainUIdef
        MainUIdef()
    
    def msgfmt( self ):
        locale_path =  base_dir + '/locale'
        for d in os.listdir( locale_path ):
            po_p_p =  f'{locale_path}/{d}/LC_MESSAGES'
            os.system(f'msgfmt -o {po_p_p}/funing.mo {po_p_p}/funing.po')
        

if __name__ == '__main__':
    sys_argv = sys.argv
    f = Funing()
       
    if sys_argv[1] in ['start', 'st']:
        f.start()

    if sys_argv[1] in ['msgfmt' ]:
        f.msgfmt()