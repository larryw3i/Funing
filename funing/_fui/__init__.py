

import os
import sys
import yaml
import json
import pickle
import shutil
from funing import settings
from funing._fui import error; 

error.lib_check()

class enjoy():
    def __init__(self):
        if not settings.initialized:
            self.initialize()

    def start(self):
        from ._main_ui import _MainUI
        _MainUI()
    
    def msgfmt( self ):
        for d in settings.locale_langcodes:
            po_p_p =  f'{locale_path}/{d}/LC_MESSAGES'
            os.system(f'msgfmt -o {po_p_p}/funing.mo {po_p_p}/funing.po')

    def pip_install_r( self ):
        os.system('pip3 install -r requirements.txt ')
        
    def initialize( self ):
        first_mo_path = os.path.join( \
            settings.locale_path, 'en-US', 'LC_MESSAGES', 'funing.mo')        
        if not os.path.exists( first_mo_path ):
            try: self.msgfmt()
            except Exception as e:
                print( e );     gettext_nf();   exit()
        for d in [ settings.faces_path, settings.infos_path ]:
            if not os.path.exists( d ): os.makedirs( d, exist_ok=True )  
        settings.initialized = True