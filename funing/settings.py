#!/usr/bin/python3

"""
Usually, the UI scripts are placed in directory ui and the related function \
scripts are placed in directory ui_.
Neither directory ui nor directory ui_ is mandatory, take the easiest way.
"""

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

from funing import *


locale_langcodes = [
    d for d in os.listdir(locale_path) if os.path.isdir(os.path.join(locale_path, d))
]
face_enter_count = config_yml.get("face_enter_count", 5)
source_page = "https://github.com/larryw3i/Funing"
prev_version = config_yml.get("version", "")
backup_path = os.path.join(user_data_path, ".cp")

user_dirs = [faces_path, infos_path, backup_path, data_path]
for p in user_dirs:
    os.path.exists(p) or os.makedirs(p)

info_file_name = "info.toml"

# cv2
hff_xml_path = os.path.join(haarcascades, "haarcascade_frontalface_default.xml")
recognizer = EigenFaceRecognizer_create()
face_casecade = cv2.CascadeClassifier(hff_xml_path)

if not os.path.exists(_config_path):
    shutil.copyfile(config_path, _config_path)
elif prev_version != version:
    config_yml.update({"version": version})
    with open(_config_path, "w") as f:
        yaml.safe_dump(config_yml, f)


def data_empty():
    return len(os.listdir(data_path)) < 1


start_args = ["s", "st" "start"]
test_args = ["ts", "t", "test"]
