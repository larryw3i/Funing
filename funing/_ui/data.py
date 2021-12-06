
import gettext
import os
import re
import subprocess
import sys
import time
import tkinter as tk
import tkinter.filedialog as tkf
import uuid
import webbrowser
from datetime import date, datetime
from enum import Enum
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

import cv2
import numpy as np
import math
import pygubu
import yaml
from PIL import Image, ImageTk

from funing import *
from funing._ui import error
from funing.locale import _
from funing.ui.about_ui import AboutToplevel

translator = _


class DataTkApplication(pygubu.TkApplication):
    def __init__(self):
        # pygubu builder
        self.builder = pygubu.Builder(translator)
        # ui files
        data_ui_path = os.path.join(
            os.path.join(project_path, 'ui'), 'data.ui')
        # add ui files
        self.builder.add_from_file(data_ui_path)

        self.mainwindow = None
        self.is_showing = False

        # data
        self.id_name_dict= {}
        self.data_ids = os.listdir(data_path)

        # page
        self.d_item_count = len(self.data_ids)

    def get_first_face_pic_path(self, info_id):
        data_dir_path = os.path.join(data_path, info_id)
        return os.path.join(data_dir_path,  '1.jpg')

    def get_name_data(self, p_item_count=10, page_num=0):
        max_page_num = math.ceil(self.d_item_count/p_item_count)
        if page_num > max_page_num :
            page_num = max_page_num
        start_index = page_num*p_item_count - 1
        end_index = (page_num+1)*p_item_count  - 1
        for d in self.data_ids[start_index:end_index]:
            

        pass

    def quit(self, event=None):
        self.mainwindow.withdraw()
        self.is_showing = False

    def run(self):
        if not self.mainwindow:
            self.mainwindow = self.builder.get_object('data_toplevel')
            self.mainwindow.title(_('Funing Data'))
            self.mainwindow.protocol("WM_DELETE_WINDOW", self.on_closing)
            # connect callbacks
            self.builder.connect_callbacks(self)
        else:
            self.mainwindow.deiconify()
        self.is_showing = True

    def on_closing(self):
        self.quit()

    def trigger(self):
        if not self.is_showing:
            self.run()
        else:
            self.quit()
