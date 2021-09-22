#!/usr/bin/python3

'''
Usually, the UI scripts are placed in directory ui and the related function \
scripts are placed in directory _ui.
Neither directory ui nor directory _ui is mandatory, take the easiest way.
'''

import getopt
import os
import re
import shutil
import sys
from pathlib import Path

import yaml
from appdirs import user_data_dir

__version__ = version = "0.2.41"
__appname__ = appname = 'Funing'
__appauthor__ = appauthor = 'Larry & Contributors'

debug = os.environ.get('FUNING_TEST') == '1'

project_path = \
    os.path.abspath(os.path.dirname(__file__))
user_data_path = \
    user_data_dir(__appname__, __appauthor__)
locale_path = \
    os.path.join(project_path, 'locale')
_config_path = \
    os.path.join(user_data_path, 'config.yml')
config_path = _config_path if os.path.exists(_config_path) \
    else os.path.join(project_path, 'config.example.yml')
config_yml = \
    yaml.safe_load(open(config_path, 'r'))
faces_path = \
    os.path.join(user_data_path, 'faces')
infos_path = \
    os.path.join(user_data_path, 'infos')
locale_langcodes =  \
    [d for d in os.listdir(locale_path)
     if os.path.isdir(os.path.join(locale_path, d))]
face_enter_count = \
    config_yml.get("face_enter_count", 5)
source_page = \
    'https://github.com/larryw3i/Funing'
prev_version = \
    config_yml.get('version', '')
backup_path = \
    os.path.join(user_data_path, '.cp')

for p in [faces_path, infos_path, backup_path]:
    if not os.path.exists(p):
        os.makedirs(p)

if not os.path.exists(_config_path):
    shutil.copyfile(config_path, _config_path)
elif prev_version != __version__:
    config_yml.update({'version': __version__})
    with open(_config_path, 'w') as f:
        yaml.safe_dump(config_yml, f)
else:
    pass


def data_empty(): return len(os.listdir(faces_path)) < 1


start_args = ['s', 'st' 'start']
test_args = ['ts', 't', 'test']


def simple():
    from funing._ui import _main_ui
    _main_ui._MainUI()
