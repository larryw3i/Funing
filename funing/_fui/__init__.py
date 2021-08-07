

import os
import sys
import yaml
import cv2
import uuid
import shutil
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
            po_p_p = os.path.join( settings.locale_path, d ,'LC_MESSAGES' )
            mo_path = os.path.join( po_p_p, 'funing.mo' )
            po_path = os.path.join( po_p_p, 'funing.po' )
            os.system(f'msgfmt -o {mo_path} {po_path}')

    def initialize( self ):

        try: self.msgfmt()
        except Exception as e:
            print( e );error.gettext_nf();exit()
            
        for d in [ settings.faces_path, settings.infos_path ]:
            if not os.path.exists( d ): os.makedirs( d, exist_ok=True )

        settings.config_yml["version"] = settings.version
        settings.config_yml["initialized"] = True
        yaml.safe_dump( settings.config_yml ,  \
        open( settings._config_path, 'w' ) )
    
    def keep_code( self ):
        rm_dirs = [
            settings._config_path,
            settings.data_dir
        ]
        for root, dirs, files in os.walk( settings.project_path ):
            for f in files:
                if f.endswith( '.mo' ): rm_dirs += [os.path.join(root,f)]
        
        uuid_cp_path = os.path.join( settings.backup_dir_path, \
        str(uuid.uuid4()) )

        if not os.path.exists( uuid_cp_path ):
            os.makedirs(  uuid_cp_path , exist_ok=True )
        for _cp in rm_dirs:
            shutil.move( _cp, uuid_cp_path )
        # os.system('rm -rf '+' '.join( rm_dirs ))    
