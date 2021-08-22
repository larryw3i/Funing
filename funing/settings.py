
import getopt
import os
import re
import shutil
import sys
from pathlib import Path

import yaml

version = "0.2.40"


def debug(): return os.environ.get('FUNING_TEST') == '1'


project_path = \
    os.path.abspath(os.path.dirname(__file__))
_usr_home =  \
    os.path.expanduser('~')
_test_user_home =\
    os.path.join(project_path, '.home')
usr_home = \
    _test_user_home if debug else _usr_home
base_dir = \
    os.path.join(usr_home, '.funing')
locale_path = \
    os.path.join(project_path, 'locale')
_config_path = \
    os.path.join(base_dir, 'config.yml')
config_path = _config_path if os.path.exists(_config_path) \
    else os.path.join(project_path, 'config.example.yml')
config_yml = \
    yaml.safe_load(open(config_path, 'r'))
data_dir = \
    os.path.join(base_dir, 'data')
faces_path = \
    os.path.join(data_dir, 'faces')
infos_path = \
    os.path.join(data_dir, 'infos')
locale_langcodes =  \
    [d for d in os.listdir(locale_path)
     if os.path.isdir(os.path.join(locale_path, d))]
infos_len = \
    config_yml.get("infos_len", 5)
face_enter_count = \
    config_yml.get("face_enter_count", 5)
source_page = \
    'https://github.com/larryw3i/Funing'
prev_version = \
    config_yml.get('version', version)
initialized = \
    config_yml.get('initialized', False) and (version == prev_version)
backup_dir_path = \
    os.path.join(base_dir, '.cp')


def data_empty(): return \
    (not os.path.exists(faces_path)) or len(os.listdir(faces_path)) < 1
