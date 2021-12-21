

import os
import shutil
import sys
import uuid

import cv2
import yaml

from funing import *


from funing.settings import *


def get_info_file_path(info_id):
    data_dir_path = os.path.join(data_path, info_id)
    return os.path.join(data_dir_path, info_file_name)
