
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

setting_exam_path = os.path.join( project_path , 'setting.yml.example') 

setting_exam_yml = yaml.safe_load( open( setting_exam_path, 'r' ))

version =  setting_exam_yml.get('version','unknown')
prev_version = setting_exam_yml.get('prev_version','unknown')
if debug:
    print('prev_version: ', prev_version, 'version: ', version)

prev_setting_path = os.path.join(base_dir, f'setting_{prev_version}_.yml') 
setting_path = os.path.join( base_dir , f'setting_{version}_.yml') 

setting_yml = yaml.safe_load( open( \
    setting_path if os.path.exists( setting_path ) else \
    setting_exam_path , 'r' ) )
    
data_dir = os.path.join( base_dir, 'data' )
face_encodings_path = os.path.join( data_dir, \
    f'face_encodings_{version}_.data' )

data_file_path = os.path.join( data_dir, \
    f'funing_{version}_.sqlite')

p_data_file_path = os.path.join( data_dir, \
    f'funing_{prev_version}_.sqlite')

lang_code = setting_yml.get('lang_code', 'en-US')
initialized  = setting_yml.get('initialized', False)
comparison_tolerance = setting_yml.get('comparison_tolerance', 0.6)
bk_db_upd = setting_yml.get('bk_db_upd', True)

f_lang_codes =  [ d for d in os.listdir(locale_path) \
    if re.match('^\w+-\w+$', d) ]
