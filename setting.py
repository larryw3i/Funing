
import os
import yaml

base_dir = os.path.abspath( os.path.dirname(  __file__  ) )

locale_path = os.path.join( base_dir, 'locale')

setting_path = os.path.join( base_dir , 'setting.yml') \
    if os.path.exists( os.path.join( base_dir , 'setting.yml') ) \
    else os.path.exists( os.path.join( base_dir , 'setting.yml.example') )

data_dir = os.path.join( base_dir, 'data' )
face_encodings_path = os.path.join( base_dir, 'data', 'face_encodings.data' )

setting_yml = yaml.load( open( setting_path, 'r' ) , Loader = yaml.SafeLoader )

lang_code = setting_yml['lang_code']
initialized  = setting_yml['initialized']
