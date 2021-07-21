

import os
import sys
import yaml
import cv2
from funing import settings
from funing._fui import error

error.lib_check()

class Enjoy():
    def __init__(self):
        if not settings.initialized:
            self.initialize()

    def start(self):
        from ._main_ui import _MainUI
        _MainUI()
    
    def msgfmt( self ):
        for d in settings.locale_langcodes:
            po_p_p =  f'{settings.locale_path}/{d}/LC_MESSAGES'
            os.system(f'msgfmt -o {po_p_p}/funing.mo {po_p_p}/funing.po')

    def pip_install_r( self ):
        os.system('pip3 install -r requirements.txt ')
        
    def initialize( self ):
        first_mo_path = os.path.join( settings.locale_path, 'en-US', \
        'LC_MESSAGES', 'funing.mo')        
        if not os.path.exists( first_mo_path ):
            try: self.msgfmt()
            except Exception as e:
                print( e );error.gettext_nf();exit()
        for d in [ settings.faces_path, settings.infos_path ]:
            if not os.path.exists( d ): os.makedirs( d, exist_ok=True )  
        settings.config_yml["initialized"] = True
        config_path = os.path.join( settings.project_path , 'config.yml') 
        yaml.safe_dump( settings.config_yml ,  open( config_path, 'w' ) )
    
    def keep_code( self ):
        rm_dirs = [os.path.join( settings.project_path, '_home', '.funing' ),
            os.path.join( os.path.expanduser('~'), '.funing' ),
            os.path.join(settings.project_path, 'config.yml' )
        ]
        for root, dirs, files in os.walk( settings.project_path ):
            for f in files:
                if f.endswith( '.mo' ): rm_dirs += [os.path.join(root,f)]
        os.system('rm -rf '+' '.join( rm_dirs ))
