
import os
import sys
import yaml
import json
import pickle

from setting import base_dir, initialized, data_dir, setting_path, \
    setting_yml, face_encodings_path, locale_path, f_lang_codes, debug,\
    data_file_path

class _Fui():
    def __init__(self):
        if not initialized:
            self.initialize()

    def start(self):
        from ._main_ui import _MainUI
        _MainUI()
    
    def msgfmt( self ):
        for d in f_lang_codes:
            if os.path.isfile( f'{locale_path}/{d}' ) or \
                d.startswith('_'): continue
            po_p_p =  f'{locale_path}/{d}/LC_MESSAGES'
            os.system(f'msgfmt -o {po_p_p}/funing.mo {po_p_p}/funing.po')

    def pip_install_r( self ):
        os.system('pip3 install -r requirements.txt ')

    def initialize( self ):
        first_mo_path = os.path.join( \
            base_dir, 'flocale','en-US', 'LC_MESSAGES', 'funing.mo')
        
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
        
        if not os.path.exists( data_file_path ):
            with open( data_file_path ,"w") : pass

        initialized = True
        setting_yml['initialized'] = initialized
        yaml.dump( setting_yml, open( setting_path, 'w') )
