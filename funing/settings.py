
import os
import shutil
import yaml
import re
from pathlib import Path
import getopt
import sys
from cv2 import haarcascades

args = \
    getopt.getopt( sys.argv[1:], '' )[1]
test_args = \
    ['ts','st','test']
debug =  \
    len( set(args)&set(test_args) ) > 0
project_path = \
    os.path.abspath( os.path.dirname(  __file__  ) )
usr_home = \
    os.path.join( project_path, '_home' ) if debug \
    else os.path.expanduser('~')
base_dir = \
    os.path.join( usr_home , '.funing')
locale_path = \
    os.path.join( project_path, 'locale') 
config_path = \
    os.path.join( project_path , 'config.yml') 
config_yml = \
    yaml.safe_load( open( config_path, 'r' ))
version =  \
    config_yml.get('version','unknown')
data_dir = \
    os.path.join( base_dir, 'data' )
faces_path = \
    os.path.join( data_dir, 'faces' )
infos_path = \
    os.path.join( data_dir, 'infos' )
lang_code = \
    config_yml.get('lang_code', 'en-US')
initialized  = \
    config_yml.get('initialized', False)
comparison_tolerance = \
    config_yml.get('comparison_tolerance', 0.6)
locale_langcodes =  \
    [ d for d in os.listdir(locale_path) if re.match('^\w+-\w+$', d) ]
hff_xml_path = \
    os.path.join( haarcascades , "haarcascade_frontalface_default.xml" )
infos_len = \
    config_yml.get( "infos_len", 5 )