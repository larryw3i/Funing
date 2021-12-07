
import gettext
import math
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
import pygubu
import yaml
from PIL import Image, ImageTk

from funing import *
from funing._ui import *
from funing.locale import _
from funing.ui.about_ui import AboutToplevel

translator = _


class DataTkApplication(pygubu.TkApplication):
    def __init__(self, master=None):
        if master is None:
            master = tk.Toplevel()
            master.title('Funing Data')
        super().__init__(master)

    def _create_ui(self):
        # pygubu builder
        self.builder = builder = pygubu.Builder(translator)
        # ui files
        data_ui_path = os.path.join(
            os.path.join(project_path, 'ui'), 'data.ui')

        # add ui files
        self.builder.add_from_file(data_ui_path)

        self.data_frame = self.mainwindow = builder.get_object(
            'data_frame', self.master)

        # data
        self.id_name_dict = {}
        self.data_ids = os.listdir(data_path)

        # page
        self.d_item_count = len(self.data_ids)

        self.get_name_data()

        self.face_labels = []

        # Configure callbacks
        self.builder.connect_callbacks(self)

    def get_first_face_pic_path(self, info_id):
        data_dir_path = os.path.join(data_path, info_id)
        return os.path.join(data_dir_path, '1.jpg')

    def get_info_file_path(self, info_id):
        return get_info_file_path(info_id)

    def get_name_from_info_file(self, info_id):
        info_file_path = get_info_file_path(info_id)
        name = ''
        with open(info_file_path, 'r') as f:
            name = f.readline()
        return name

    def get_name_data(self, p_item_count=10, page_num=0):
        max_page_num = math.ceil(self.d_item_count / p_item_count)
        if page_num > max_page_num:
            page_num = max_page_num
        start_index = page_num * p_item_count
        end_index = (page_num + 1) * p_item_count
        if end_index > (self.d_item_count - 1):
            end_index = self.d_item_count - 1

        name_scrolledframe = self.builder.get_object(
            'name_scrolledframe', self.master)

        for d in self.data_ids[start_index:end_index]:
            name = self.get_name_from_info_file(d)
            name_id = name + f'({d})'
            self.id_name_dict[d] = name
            tk.Button(name_scrolledframe, text=name_id,
                      command=lambda d=d:self.show_data(d)).pack()

        self.builder.get_object(
            'page_num_label', self.master)['text'] = str(
            page_num + 1) + '/' + str(max_page_num)

    def show_data(self,info_id):
        
        face_pic_frame = self.builder.get_object(
            'face_pic_frame', self.master)
        info_text = self.builder.get_object(
            'info_text', self.master)
        
        for l in self.face_labels:
            l.destroy()
        self.face_labels = []

        subpath = os.path.join(data_path, info_id)
        if os.path.isdir(subpath):
            for filename in os.listdir(subpath):
                if filename == '0.txt':
                    continue  # '0.txt' is the info file.
                imgpath = os.path.join(subpath, filename)

                new_face_label = tk.Label(face_pic_frame)
                img = cv2.imread(imgpath)
                vid_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                vid_img = Image.fromarray(vid_img)
                imgtk = ImageTk.PhotoImage(image=vid_img)
                new_face_label.imgtk = imgtk
                new_face_label.configure(image=imgtk)
                # new_face_label.bind("<Double-Button-1>", lambda e:
                #                     self.del_face_label(e, index))
                new_face_label.pack()
                self.face_labels.append(new_face_label)


        info_file_path = self.get_info_file_path(info_id)
        info_text.delete(1.0, END)
        if not os.path.exists(info_file_path):
            _nif_ = _('No informations found')
            info_text.insert('1.0', _nif_)
        with open(info_file_path, 'r') as f:
            info_text.insert('1.0', f.read())
        
