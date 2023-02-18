import gettext
import os
import pickle
import platform
import re
import sys
import time
import tkinter as tk
import tkinter.filedialog as tkf
import uuid
import webbrowser
from datetime import date, datetime
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

from appdirs import *

from funing.settings import *

user_data_dir_path = user_data_dir(app_name, app_author[0])
user_config_dir_path = user_config_dir(app_name, app_author[0])

project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

copy_path = os.path.join(user_data_dir_path, "copy.pkl")
recog_datas_dir_path = os.path.join(user_data_dir_path, "recog_datas")
faces_dir_path = os.path.join(recog_datas_dir_path, "face_images")
infos_dir_path = os.path.join(recog_datas_dir_path, "infos")
backup_dir_path = os.path.join(user_data_dir_path, "backup")
app_data_dir_path = os.path.join(project_path, "data")
data_cv2_dir_path = os.path.join(app_data_dir_path, "cv2")
info_templates_path = os.path.join(user_data_dir_path, "info_templates")

default_image_ext = ".jpg"
image_ext = default_image_ext
info_ext = ".txt"
basic_info_ext = ".basic.txt"
backup_ext = ".bk"
alternative_cascade_path_linux = os.path.join(
    os.sep,
    "usr",
    "share",
    "opencv4",
    "haarcascades",
    "haarcascade_frontalface_default.xml",
)
alternative_cascade_path_from_data_dir = os.path.join(
    data_cv2_dir_path,
    "haarcascade_frontalface_default.xml",
)
alternative_cascade_path = (
    alternative_cascade_path_linux
    if os.path.exists(alternative_cascade_path_linux)
    else alternative_cascade_path_from_data_dir
    if os.path.exists(alternative_cascade_path_from_data_dir)
    else None
)

for d in [
    user_data_dir_path,
    user_config_dir_path,
    infos_dir_path,
    faces_dir_path,
    backup_dir_path,
    app_data_dir_path,
    info_templates_path,
]:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

for f in [copy_path]:
    if not os.path.exists(f):
        with open(f, "wb") as f:
            pickle.dump({}, f)


def get_new_backup_file_path(
    file_id=None, create_now=False, is_file=False, mode="w"
):
    return get_new_backup_path(file_id, create_now, is_file, mode)


def get_new_backup_path(
    file_id=None, create_now=False, is_file=False, mode="w"
):
    file_id = file_id or str(uuid.uuid4())
    backup_path = os.path.join(backup_dir_path, file_id + backup_ext)
    if create_now:
        if is_file:
            with open(backup_path, mode) as f:
                f.write("")
            pass
        else:
            os.makedirs(backup_path, exist_ok=True)
            pass
    return backup_path


def get_info_path(info_id):
    return os.path.join(infos_dir_path, info_id + info_ext)


def get_basic_info_path(info_id):
    return os.path.join(infos_dir_path, info_id + basic_info_ext)


def get_image_dir_path(info_id):
    image_dir_path = os.path.join(faces_dir_path, info_id)
    return image_dir_path


def get_new_random_face_image_path(info_id):
    face_image_dir_path = os.path.join(faces_dir_path, info_id)
    if not os.path.exists(face_image_dir_path):
        os.makedirs(face_image_dir_path, exist_ok=True)
    return os.path.join(faces_dir_path, info_id, str(uuid.uuid4()) + image_ext)


def get_frame_path_by_ids(info_id, frame_id):
    return os.path.join(faces_dir_path, info_id, frame_id + image_ext)


def get_image_path_by_ids(info_id, frame_id):
    return get_frame_path_by_ids(info_id, frame_id)


def get_face_image_path_list(info_id):
    face_image_dir_path = os.path.join(faces_dir_path, info_id)
    if not os.path.exists(face_image_dir_path):
        return None
    return [
        os.path.join(face_image_dir_path, f)
        for f in os.listdir(face_image_dir_path)
        if f.endswith(image_ext)
    ]


def get_info_templates_path():
    return info_templates_path


# Deprecated
def get_info_template_path_by_name(name=None):
    if not name:
        return None
    template_path = os.path.join(info_templates_path, name)
    return template_path


def list_info_templates_dir():
    info_templates = os.listdir(info_templates_path)
    return info_templates


def info_template_exists(name=None):
    if not name:
        return
    exist = name in list_info_templates_dir()
    return exist
