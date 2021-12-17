
import gettext
import math
import os
import re
import shutil
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
from cv2.data import haarcascades
from cv2.face import EigenFaceRecognizer_create as recognizer
from PIL import Image, ImageTk

from funing import *
from funing._ui import *
from funing.locale import _

translator = _


class DataTkApplication(pygubu.TkApplication):
    def __init__(self, master=None):
        if master is None:
            master = tk.Toplevel()
            master.title(_('Funing Data'))

        # data
        self.id_name_dict = {}
        self.data_ids = os.listdir(data_path)
        self.cur_name = ''
        self.cur_face_labels = []
        self.name_btns = []
        self.cur_page_num = 0
        self.cur_p_item_count = 10
        self.source = 0
        self.cur_info_id = None

        # widgets
        self.add_face_label = None

        # page
        self.d_item_count = len(self.data_ids)
        # vid
        self.vid = None
        self.vid_fps = 30
        self.save_size = (100, 100)
        self.master_after = -1
        self.face_frame = None

        self.added_face_frames = []

        # cv2
        self.hff_xml_path = os.path.join(haarcascades,
                                         "haarcascade_frontalface_default.xml")
        self.recognizer = recognizer()
        self.face_casecade = cv2.CascadeClassifier(self.hff_xml_path)

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

        self.face_pic_frame = self.builder.get_object(
            'face_pic_frame', self.master)
        self.info_text = self.builder.get_object(
            'info_text', self.master)

        builder.get_object('del_btn', self.master).config(bg='red')

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
        if len(self.name_btns) < 1:
            return
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
        if len(self.cur_face_labels) < 1:
            return
        for l in self.cur_face_labels:
            l.grid_forget()
        self.cur_face_labels = []

    def del_face_pic_file(self, info_id, filename='', del_all=False):
        if debug:
            print(info_id, filename)
        is_last_pic = del_all or len(self.cur_face_labels) < 2
        ask_str = _("Do you want to delete this face picture?")
        if is_last_pic:
            ask_str += '\n' +\
                _('All data of {0} will be removed').format(
                    self.cur_name)
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

    def grid_face_labels(self):
        img_len_root_ceil = math.ceil(len(self.cur_face_labels))
        for i, l in enumerate(self.cur_face_labels):
            l.grid(row=i // img_len_root_ceil,
                   column=i % img_len_root_ceil)

    def show_data(self, info_id):

        info_path = os.path.join(data_path, info_id)
        if not os.path.isdir(info_path):
            return

        self.cur_info_id = info_id

        self.clear_face_labels()

        self.cur_name = name = self.get_name_from_info_file(info_id)

        img_len = len(os.listdir(info_path))
        img_len_root_ceil = math.ceil(img_len**0.5)
        img_index = 0
        for filename in os.listdir(info_path):
            if filename == '0.txt':
                continue  # '0.txt' is the info file.
            imgpath = os.path.join(info_path, filename)
            img = cv2.imread(imgpath)
            vid_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            vid_img = Image.fromarray(vid_img)
            imgtk = ImageTk.PhotoImage(image=vid_img)

            new_face_label = tk.Label(self.face_pic_frame)
            new_face_label.imgtk = imgtk
            new_face_label.configure(image=imgtk)

            new_face_label.bind(
                "<Double-Button-1>",
                (lambda e, a=info_id, b=filename:
                 self.del_face_pic_file(a, b)))

            self.cur_face_labels.append(new_face_label)
            img_index += 1
        self.grid_face_labels()

        self.add_face_label = tk.Label(self.face_pic_frame, text=_('ADD'),
                                       font=("NONE", 16), background='blue',
                                       cursor='hand2')
        self.add_face_label.grid(row=img_index // img_len_root_ceil,
                                 column=img_index % img_len_root_ceil)

        self.add_face_label.bind(
            "<Button-1>",
            (lambda e, a=info_id: self.add_face_pic(a)))

        self.cur_face_labels.append(self.add_face_label)

        info_file_path = self.get_info_file_path(info_id)
        self.info_text.delete(1.0, END)
        if not os.path.exists(info_file_path):
            _nif_ = _('No informations found')
            self.info_text.insert('1.0', _nif_)
        with open(info_file_path, 'r') as f:
            self.info_text.insert('1.0', f.read())

        self.set_msg(_('Double click the face image to delete.'))

    def refresh_frame(self):
        if self.cur_face_labels is None:
            return

        if self.vid is None:
            self.vid = cv2.VideoCapture(self.source)
        if not self.vid.isOpened():
            self.set_msg(_('Unable to open video source.'))
            return

        rect, cur_frame = self.vid.read()
        rec_gray_img = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2GRAY)
        face_rects = self.face_casecade.detectMultiScale(
            rec_gray_img, 1.3, 5)

        (x, y, w, h) = (
            int((cur_frame.shape[1] - self.save_size[0]) / 2),
            int((cur_frame.shape[0] - self.save_size[0]) / 2),
            self.save_size[0], self.save_size[1])
        if len(face_rects) > 0:
            (x, y, w, h) = face_rects[0]
            self.face_frame = cur_frame = cv2.resize(
                cur_frame[y:y + h, x:x + w], self.save_size,
                interpolation=cv2.INTER_LINEAR)
        else:
            _h = cur_frame.shape[0]
            _w = cur_frame.shape[1]
            _wh_min = _h if _h < _w else _w
            _wh_diff_d2 = int(abs(_h - _w) / 2)
            _y_start = 0 if _h < _w else _wh_diff_d2
            _x_start = 0 if _w < _h else _wh_diff_d2

            cur_frame = cv2.resize(
                cur_frame[_y_start:_wh_min, _x_start:_wh_min], self.save_size,
                interpolation=cv2.INTER_LINEAR)
            self.face_frame = None
        vid_img = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)

        new_label = self.cur_face_labels[-2]
        new_label.imgtk = imgtk
        new_label.configure(image=imgtk)

        self.master_after = self.master.after(
            int(1000 / self.vid_fps), self.refresh_frame)

    def del_face_pic_new(self, label_index=-1):

        pass

    def add_face_pic(self, info_id):
        if self.master_after == -1:
            if self.face_frame != None:
                new_face_label = tk.Label(self.face_pic_frame)
                new_face_label.bind(
                    "<Double-Button-1>",
                    (lambda e, index=len(self.cur_face_labels):
                    self.del_face_pic_new(index)))
                new_face_label.grid(row=img_index // img_len_root_ceil,
                                    column=img_index % img_len_root_ceil)
                self.cur_face_labels.insert(-1,new_face_label)
                self.grid_face_labels()
                self.face_frame = None
            self.refresh_frame()
        else:
            self.cancel_master_after()

    def cancel_master_after(self):
        if self.master_after != -1:
            self.master.after_cancel(self.master_after)
            self.vid.release()
            self.master_after = -1
            self.vid = None

            if self.face_frame is None:
                self.add_face_label.imgtk = None
                self.add_face_label.configure(image=None)
                self.set_msg(_('No face picture picked'))

    def on_del_btn_clicked(self):
        if self.cur_info_id is None:
            return
        self.del_face_pic_file(self.cur_info_id, del_all=True)

    def on_save_btn_clicked(self):
        self.save()

    def save(self):
        if self.cur_info_id is None:
            return
        if self.face_frame is None:
            self.set_msg(_('No face picture picked'))
            return
        data_dir_path = os.path.join(data_path, self.cur_info_id)
        os.makedirs(data_dir_path, exist_ok=True)

        info = self.info_text.get("1.0", "end-1c")
        info_file_path = self.get_info_file_path(self.cur_info_id)
        with open(info_file_path, 'w+') as f:
            f.write(info)

        img_num = len(os.listdir(data_dir_path))
        cv2.imwrite(f'{data_dir_path}/{img_num}.jpg', self.face_frame)

        self.cancel_master_after()
