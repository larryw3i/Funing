
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
import shutil
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
        builder.get_object('del_btn', self.master).config(bg='red')

        # data
        self.id_name_dict = {}
        self.data_ids = os.listdir(data_path)
        self.cur_name = ''
        self.cur_face_labels = []
        self.name_btns = []
        self.cur_page_num = 0
        self.cur_p_item_count = 10

        # page
        self.d_item_count = len(self.data_ids)

        self.get_name_data()

        # Configure callbacks
        self.builder.connect_callbacks(self)

    def set_msg(self, msg):
        self.builder.get_object('msg_label', self.master)['text'] = msg

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
    
    def clear_name_btns(self):
        if len(self.name_btns) < 1: return
        for b in self.name_btns:
            b.grid_forget()
        self.name_btns = []

    def get_name_data(self, p_item_count=10, page_num=0):
        self.clear_name_btns()
        max_page_num = math.ceil(self.d_item_count / p_item_count)
        if page_num > max_page_num:
            page_num = max_page_num
        self.cur_p_item_count = p_item_count
        self.cur_page_num = page_num
        start_index = page_num * p_item_count
        end_index = (page_num + 1) * p_item_count
        if end_index > (self.d_item_count - 1):
            end_index = self.d_item_count - 1

        name_frame = self.builder.get_object(
            'name_frame', self.master)

        p_item_count_root_ceil = math.ceil(p_item_count**0.5)
        item_index = 0
        for d in self.data_ids[start_index:end_index]:
            self.cur_name = name = self.get_name_from_info_file(d)
            name_id = name + f'\n({d})'
            self.id_name_dict[d] = name
            new_name_btn = tk.Button(
                name_frame, text=name_id,
                command=(lambda d=d: self.show_data(d)))
            new_name_btn.grid(row=item_index % p_item_count_root_ceil,
                      column=item_index // p_item_count_root_ceil)
            self.name_btns.append(new_name_btn)
            item_index += 1

        self.builder.get_object(
            'page_num_label', self.master)['text'] = str(
            page_num + 1) + '/' + str(max_page_num)

    def clear_face_labels(self):
        if len(self.cur_face_labels)<1:return
        for l in self.cur_face_labels:
            l.grid_forget()
        self.cur_face_labels = []


    def del_face_pic(self, info_id, filename, label_index):
        if debug:
            print(info_id, filename, label_index)
        is_last_pic = len(self.cur_face_labels) < 2
        ask_str = _("Do you want to delete this face picture?")
        if is_last_pic:
            ask_str += ('\n' +
                        _('All data of {0} will be removed').format(
                            self.cur_name))
        del_or_not = messagebox.askyesnocancel(
            _("Delete face picture?"), ask_str)

        if del_or_not:
            info_path = os.path.join(data_path, info_id)
            if is_last_pic:
                
                self.clear_face_labels()

                shutil.rmtree(info_path)

                self.data_ids = os.listdir(data_path)
                self.d_item_count = len(self.data_ids)
                
                self.get_name_data(self.cur_p_item_count, self.cur_page_num)
                self.set_msg(_('face picture has been removed!'))
            else:
                img_path = os.path.join(info_path, filename)
                os.remove(img_path)
                self.set_msg(_('All data of {0} have been removed!').format(
                                self.cur_name))
                self.show_data(info_id)

                self.data_ids = os.listdir(data_path)
                self.d_item_count = len(self.data_ids)

    def show_data(self, info_id):

        face_pic_frame = self.builder.get_object(
            'face_pic_frame', self.master)
        info_text = self.builder.get_object(
            'info_text', self.master)

        self.clear_face_labels()

        info_path = os.path.join(data_path, info_id)

        if not os.path.isdir(info_path):
            return

        img_len = len(os.listdir(info_path))
        img_len_root_ceil = math.ceil(img_len**0.5)
        img_index = 0
        for filename in os.listdir(info_path):
            if filename == '0.txt':
                continue  # '0.txt' is the info file.
            imgpath = os.path.join(info_path, filename)
            new_face_label = tk.Label(face_pic_frame)
            img = cv2.imread(imgpath)
            vid_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            vid_img = Image.fromarray(vid_img)
            imgtk = ImageTk.PhotoImage(image=vid_img)
            new_face_label.imgtk = imgtk
            new_face_label.configure(image=imgtk)

            new_face_label.bind(
                "<Double-Button-1>",
                (lambda e, a=info_id, b=filename, c=img_index:
                 self.del_face_pic(a, b, c)))

            new_face_label.grid(row=img_index // img_len_root_ceil,
                                column=img_index % img_len_root_ceil)
            self.cur_face_labels.append(new_face_label)
            img_index += 1

        info_file_path = self.get_info_file_path(info_id)
        info_text.delete(1.0, END)
        if not os.path.exists(info_file_path):
            _nif_ = _('No informations found')
            info_text.insert('1.0', _nif_)
        with open(info_file_path, 'r') as f:
            info_text.insert('1.0', f.read())

        self.set_msg(_('Double click the face image to delete.'))
