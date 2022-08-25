import getopt
import os
import re
import shutil
import sys
from pathlib import Path

import cv2
import yaml
from appdirs import user_data_dir
from cv2.data import haarcascades
from cv2.face import EigenFaceRecognizer_create

project_path = os.path.abspath(os.path.dirname(__file__))
user_data_path = user_data_dir(appname, appauthor)
locale_path = os.path.join(project_path, "locale")
_config_path = os.path.join(user_data_path, "config.yml")
config_path = (
    os.path.exists(_config_path)
    and _config_path
    or os.path.join(project_path, "config.example.yml")
)
config_yml = yaml.safe_load(open(config_path, "r"))
faces_path = os.path.join(user_data_path, "faces")
infos_path = os.path.join(user_data_path, "infos")
data_path = os.path.join(user_data_path, "data")
