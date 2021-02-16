
try:
    import cv2
except Exception as e:
    print(e)
    print('::::::::::::::::::::::::::::::::::::::::::::')
    print("cv2 can't be found, read "+\
    "https://docs.opencv.org/master/d5/de5/tutorial_py_setup_in_windows.html "+\
        'and install it. (^_^)')
    print('::::::::::::::::::::::::::::::::::::::::::::')
import os
import sys
import yaml
import json
import pickle
import shutil

from setting import base_dir, initialized, data_dir, setting_path, \
    setting_yml, face_encodings_path, locale_path, f_lang_codes, debug,\
    data_file_path, prev_setting_path, bk_db_upd, p_data_file_path

from fmodel import migrate_db


class _Fui():
    def __init__(self):
        if not initialized:
            self.initialize()

    def start(self):
        from ._main_ui import _MainUI
        _MainUI()
    
    def msgfmt( self ):
        for d in f_lang_codes:
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
                print('::::::::::::::::::::::::::::::::::::::::::::')
                print( 'Make sure gettext is installed, '+\
                    'read https://www.gnu.org/software/gettext/ '+\
                    'and install it. (^_^)' )
                print('::::::::::::::::::::::::::::::::::::::::::::')

        if not os.path.exists( data_dir ): os.mkdir( data_dir )
        if not os.path.exists( face_encodings_path ):
            pickle.dump({}, open(face_encodings_path, 'wb'))
        
        if os.path.exists( prev_setting_path ):
            p_setting_yml = yaml.safe_load( open( prev_setting_path , 'r' ) )
            if debug: print( 'p_setting_yml: ', p_setting_yml, \
                'setting_exam_yml:', setting_yml )
            setting_yml.update( p_setting_yml )    
            if debug: 
                print('setting_yml.update( p_setting_yml )', setting_yml)

            setting_yml['prev_version']= prev_version
            setting_yml['version'] = version
            os.remove( prev_setting_path )
        
        if not os.path.exists( data_file_path ):
            if bk_db_upd and os.path.exists( p_data_file_path ):
                shutil.copyfile(p_data_file_path, data_file_path)
                migrate_db()
            else:
                with open( data_file_path ,"w") : pass

        initialized = True
        setting_yml['initialized'] = initialized
        yaml.dump( setting_yml, open( setting_path, 'w') )
