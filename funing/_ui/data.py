
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
from PIL import Image, ImageTk

from funing import *
from funing._ui import *
from funing.locale import _
from funing.settings import *

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
        self.face_frame = 0    # default:  add new face label

        self.added_face_frames = []

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

        self.show_per_page_entry = self.builder.get_object(
            'show_per_page_entry', self.master)

        builder.get_object('del_btn', self.master).config(bg='red')

        self.get_name_data()

        # Configure callbacks
        self.builder.connect_callbacks(self)

    def show_per_page_entry_validatecommand(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

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

    def get_p_item_count(self):
        return int(self.show_per_page_entry.get()) - 1 if \
            len(self.show_per_page_entry.get()) > 0 else 10

    def on_prev_btn_clicked(self):
        self.get_name_data(self.get_p_item_count(), self.cur_page_num - 1)

    def on_next_btn_clicked(self):
        self.get_name_data(self.get_p_item_count(), self.cur_page_num + 1)

    def get_name_data(self, p_item_count=10, page_num=0):
        max_page_num = math.ceil(self.d_item_count / p_item_count)
        if page_num > max_page_num - 1 or page_num < 0:
            page_num = max_page_num
            return
        self.clear_name_btns()
        self.cur_p_item_count = p_item_count
        self.cur_page_num = page_num
        start_index = page_num * p_item_count
        end_index = (page_num + 1) * p_item_count
        if end_index > (self.d_item_count - 1):
            end_index = self.d_item_count - 1

        name_frame = self.builder.get_object('name_frame', self.master)

        p_item_count_root_ceil = math.ceil(p_item_count**0.5)
        item_index = 0
        for d in self.data_ids[start_index:end_index + 1]:
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

    def clear_info_text(self):
        self.builder.get_object('info_text', self.master).delete(1.0, END)

    def del_face_pic_file(self, info_id, filename='', del_all=False):
        if debug:
            print(info_id, filename)
        _is_last_pic_ = del_all or len(self.cur_face_labels) < 2
        ask_str = _("Do you want to delete this face picture?")
        if _is_last_pic_:
            ask_str += '\n' +\
                _('All data of {0} will be removed').format(
                    self.cur_name)
        del_or_not = messagebox.askyesnocancel(
            _("Delete face picture?"), ask_str, parent=self.master)

        if del_or_not:
            info_path = os.path.join(data_path, info_id)
            if _is_last_pic_:

                self.clear_face_labels()

                # shutil.rmtree(info_path)
                shutil.move(info_path, backup_path)

                self.data_ids = os.listdir(data_path)
                self.d_item_count = len(self.data_ids)

                self.get_name_data(self.cur_p_item_count, self.cur_page_num)
                self.set_msg(_('face picture has been removed!'))

                self.clear_info_text()

            else:
                img_path = os.path.join(info_path, filename)
                os.remove(img_path)
                self.set_msg(_('All data of {0} have been removed!').format(
                    self.cur_name))
                self.show_data(info_id)

                self.data_ids = os.listdir(data_path)
                self.d_item_count = len(self.data_ids)

    def grid_face_labels(self):
        img_len_root_ceil = math.ceil(len(self.cur_face_labels)**0.5)
        for i, l in enumerate(self.cur_face_labels):
            l.grid(row=i // img_len_root_ceil,
                   column=i % img_len_root_ceil)

    def show_data(self, info_id):

        info_path = os.path.join(data_path, info_id)
        if not os.path.isdir(info_path):
            return
        self.cur_info_id = info_id

        self.clear_face_labels()
        self.added_face_frames = []

        self.cur_name = name = self.get_name_from_info_file(info_id)

        img_len = len(os.listdir(info_path))
        img_len_root_ceil = math.ceil(img_len**0.5)
        img_index = 0
        for filename in os.listdir(info_path):
            if filename == info_file_name:
                continue
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

            menu = Menu(self.master, tearoff=0)
            menu.add_command(
                label=_("delete"),
                command=(lambda info_id=info_id, filename=filename:
                         self.del_face_pic_file(info_id, filename)))

            new_face_label.bind(
                "<Button-3>",
                (lambda event: menu.tk_popup(event.x_root, event.y_root)))

            self.cur_face_labels.append(new_face_label)
            img_index += 1

        self.add_face_label = tk.Label(self.face_pic_frame, text=_('ADD'),
                                       font=("NONE", 16), cursor='hand2')
        self.add_face_label.grid(row=img_index // img_len_root_ceil,
                                 column=img_index % img_len_root_ceil)
        self.add_face_label.bind(
            "<Button-1>",
            (lambda e: self.add_face_pic()))
        self.cur_face_labels.append(self.add_face_label)

        self.grid_face_labels()
        self.clear_info_text()

        info_file_path = self.get_info_file_path(info_id)
        if not os.path.exists(info_file_path):
            _nif_ = _('No informations found')
            self.info_text.insert('1.0', _nif_)
        with open(info_file_path, 'r') as f:
            self.info_text.insert('1.0', f.read())

        self.set_msg(_('Click the face image to pick.'))

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
        face_rects = face_casecade.detectMultiScale(
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

    def del_added_face_frame(self, index):
        if len(self.added_face_frames) - 1 < index:
            return
        self.added_face_frames[index] = None

    def del_face_pic_new(self, label, index):
        self.cancel_master_after()
        self.cur_face_labels.remove(label)
        self.del_added_face_frame(index)
        label.grid_forget()
        self.grid_face_labels()

    def _update_pause_play_(self):
        if self.master_after == -1:
            self.refresh_frame()
        else:
            if self.face_frame is not None:
                self.added_face_frames[-1] = self.face_frame
            self.cancel_master_after()
            self.grid_face_labels()

    def scroll_face_pic_tkscrolledframe_bottom(self):
        face_pic_tkscrolledframe = self.builder.get_object(
            'face_pic_tkscrolledframe', self.master)
        face_pic_tkscrolledframe.yview(mode='moveto', value=1)
        face_pic_tkscrolledframe.xview(mode='moveto', value=1)

    def add_face_pic(self):
        if self.master_after == -1:
            if self.face_frame is not None:

                # default value of self.face_frame is 0.
                if not isinstance(self.face_frame, int) and \
                        self.face_frame is not None:
                    self.added_face_frames.append(self.face_frame)

                new_face_label = tk.Label(self.face_pic_frame)
                added_face_frames_len = len(self.added_face_frames)

                menu = Menu(self.master, tearoff=0)
                menu.add_command(
                    label=_("delete"),
                    command=(
                        lambda label=new_face_label,
                        index=added_face_frames_len:
                        self.del_face_pic_new(new_face_label, index)))
                menu.add_command(
                    label=_("pick/stop"),
                    command=(lambda: self._update_pause_play_()))

                new_face_label.bind(
                    "<Button-1>", (lambda e: self._update_pause_play_()))
                new_face_label.bind(
                    "<Button-3>",
                    lambda event: menu.tk_popup(event.x_root, event.y_root))

                self.cur_face_labels.insert(-1, new_face_label)
                self.grid_face_labels()
                self.face_frame = None

                self.added_face_frames.append(self.face_frame)

                self.scroll_face_pic_tkscrolledframe_bottom()

                self.set_msg(
                    _('Right click: pause or play, double click: delete.'))

            self.refresh_frame()

    def cancel_master_after(self):
        if self.master_after != -1:
            self.master.after_cancel(self.master_after)
            self.vid.release()
            self.master_after = -1
            self.vid = None

            if self.face_frame is None:
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

        for f in self.added_face_frames:
            if f is None or len(f) < 1:
                return
            cv2.imwrite(f'{data_dir_path}/{str(uuid.uuid4())}.jpg', f)

        self.cancel_master_after()

        self.get_name_data()
        self.show_data(self.cur_info_id)
