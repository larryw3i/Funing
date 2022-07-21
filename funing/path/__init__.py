import gettext
import os
import pickle
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


project_path = os.path.abspath(os.path.dirname(__file__))
copy_path = os.path.join(user_data_dir_path, "copy.pkl")
recog_datas_dir_path = os.path.join(user_data_dir_path, "recog_datas")
faces_dir_path = os.path.join(recog_datas_dir_path, "face_images")
infos_dir_path = os.path.join(recog_datas_dir_path, "infos")

for d in [
    user_data_dir_path,
    user_config_dir_path,
    infos_dir_path,
    faces_dir_path,
]:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

for f in [copy_path]:
    if not os.path.exists(f):
        with open(f, "wb") as f:
            pickle.dump({}, f)


def get_info_path(info_id):
    return os.path.join(infos_dir_path, info_id + ".txt")


def get_basic_info_path(info_id):
    return os.path.join(infos_dir_path, info_id + ".basic.txt")


def get_new_random_face_image_path(info_id):
    return os.path.join(faces_dir_path, info_id, str(uuid.uuid4()) + ".jpg")


def get_face_image_path_list(info_id):
    face_image_dir_path = os.path.join(faces_dir_path, info_id)
    if not os.path.exists(face_image_dir_path):
        os.makedirs(face_image_dir_path, exist_ok=True)
    return [
        os.path.join(face_image_dir_path, f)
        for f in os.listdir(face_image_dir_path)
    ]
