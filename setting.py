
import os
import shutil
import yaml

usr_home = os.path.expanduser('~')
base_dir = usr_home 
project_path = os.path.abspath( os.path.dirname(  __file__  ) )
locale_path = os.path.join( base_dir, 'locale')

setting_path = os.path.join( base_dir , 'setting.yml') 
setting_example_path = os.path.join( base_dir , 'setting.yml.example') 

if not os.path.exists( setting_path ):
    shutil.copyfile( setting_example_path, setting_path )
    
data_dir = os.path.join( base_dir, 'data' )
face_encodings_path = os.path.join( data_dir, 'face_encodings.data' )

setting_yml = yaml.safe_load( open( setting_path, 'r' ) )

lang_code = setting_yml['lang_code']
initialized  = setting_yml['initialized']
comparison_tolerance = setting_yml['comparison_tolerance']
