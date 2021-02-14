
import os
import shutil
import yaml
import re
from pathlib import Path
import getopt
import sys

args = getopt.getopt( sys.argv[1:], '' )[1]; test_args = ['ts','st','test']
debug =  len( set(args)&set(test_args) ) > 0

project_path = os.path.abspath( os.path.dirname(  __file__  ) )

usr_home = os.path.join( project_path, '_home' ) if debug \
    else os.path.expanduser('~')
base_dir = os.path.join( usr_home , '.funing')

locale_path = os.path.join( project_path, 'flocale') 

setting_path = os.path.join( base_dir , 'setting.yml') 
setting_example_path = os.path.join( project_path , 'setting.yml.example') 

if not os.path.exists( setting_path ):
    if not os.path.exists( base_dir): os.makedirs( base_dir, exist_ok = True )
    shutil.copyfile( setting_example_path, setting_path )
    
setting_yml = yaml.safe_load( open( setting_path, 'r' ) )

version = setting_yml.get('version','unknown')

data_dir = os.path.join( base_dir, 'data' )
face_encodings_path = os.path.join( data_dir, \
    f'{version}_face_encodings.data' )
data_file_path = os.path.join( data_dir, \
    f'{version}_funing.sqlite')

lang_code = setting_yml.get('lang_code', 'en-US')
initialized  = setting_yml.get('initialized', False)
comparison_tolerance = setting_yml.get('comparison_tolerance', 0.6)

f_lang_codes =  [ d for d in os.listdir(locale_path) \
    if re.match('^\w+-\w+$', d) ]

