
import os
import shutil
import yaml
import re
from pathlib import Path
import getopt
import sys

version =  "0.2.38"
args = \
    getopt.getopt( sys.argv[1:], '' )[1]
test_args = \
    ['ts','st','test']
debug =  \
    len( set(args)&set(test_args) ) > 0
project_path = \
    os.path.abspath( os.path.dirname(  __file__  ) )
_usr_home =  \
    os.path.expanduser('~')
_test_user_home =\
    os.path.join( project_path, '.home' ) 
usr_home = _test_user_home if debug else _usr_home
base_dir = \
    os.path.join( usr_home , '.funing')
locale_path = \
    os.path.join( project_path, 'locale') 
_config_path = \
    os.path.join( base_dir , 'config.yml') 
config_path = \
    _config_path
if not os.path.exists( config_path ): config_path = \
    os.path.join( project_path , 'config.example.yml') 
config_yml = \
    yaml.safe_load( open( config_path, 'r' ))
data_dir = \
    os.path.join( base_dir, 'data' )
faces_path = \
    os.path.join( data_dir, 'faces' )
data_empty = lambda:\
    (not os.path.exists( faces_path )) or len( os.listdir( faces_path ) ) < 1
infos_path = \
    os.path.join( data_dir, 'infos' )
lang_code = \
    config_yml.get('lang_code', 'en_US')
comparison_tolerance = \
    config_yml.get('comparison_tolerance', 0.6)
locale_langcodes =  \
    [ d for d in os.listdir(locale_path)  ]
infos_len = \
    config_yml.get( "infos_len", 5 )
face_enter_count = \
    config_yml.get( "face_enter_count", 5 )
source_page = \
    'https://github.com/larryw3i/Funing'
prev_version = \
    config_yml.get('version', version )
initialized  = \
    config_yml.get('initialized', False) and (version == prev_version)
backup_dir_path = \
    os.path.join( base_dir, '.cp' )

_locale_path = \
    os.path.join( project_path, '_locale') 