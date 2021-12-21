

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
import pygubu
import yaml
from PIL import Image, ImageTk

from funing import *
from funing._ui import *
from funing._ui.about import AboutTkApplication
from funing.locale import _
from funing.settings import *

'''
# __  --> assign a variable that is not used.
# _   --> used for gettext.

from funing.locale import _
self.frame_width, self.frame_height, __ = self.cur_frame.shape
'''

translator = _


class SourceType(Enum):
    NULL = 0    # default
    IMG = 1     # IMAGE
    VID = 2     # VIDEO


class Status(Enum):
    REC = 0     # recognize
    PICK = 1    # pick image


class MainApplication(pygubu.TkApplication):

    def _create_ui(self):

        # master
        self.master.title(_('Funing') + ' (' + version + ')')

        self.status = Status.PICK
        # pygubu builder
        self.builder = builder = pygubu.Builder(translator)
        # ui files
        main_ui_path = os.path.join(
            os.path.join(project_path, 'ui'), 'main.ui')
        # add ui files
        self.builder.add_from_file(main_ui_path)

        # mix variables
        self.status_label_stringvar = tk.StringVar(self.master, value='(^_^)')
        self.pause_play_btn_stringvar = tk.StringVar(self.master, value='Play')
        self.var_face_was_detected_str = _('Face was detected.')
        self.var_no_face_was_detected_str = _('No face was detected.')
        self.var_nothing_was_entered_str = \
            _("You haven't entered anything yet!")
        self.var_unable_to_open_vid_source_str = \
            _('Unable to open video source.')
        self.var_image_exts = ['jpg', 'png', 'jpeg', 'webp']
        self.var_video_exts = ['mp4', 'avi', '3gp', 'webm', 'mkv']
        self.var_img_vid_exts = '*.' + ' *.'.join(
            self.var_image_exts + self.var_video_exts)
        self.var_click_to_remove_p = _(
            'Click the picked face image to remove.')
        self.var_double_click_to_remove_r = _(
            'Double click the face image to remove.')

        # widgets
        self.main_window = builder.get_object('main_frame', self.master)
        self.vidframe_label = builder.get_object('vidframe_label', self.master)
        self.info_text = builder.get_object('info_text', self.master)
        self.go_combobox = builder.get_object('go_combobox', self.master)
        self.face_frame = builder.get_object(
            'face_frame', self.master)  # not vid frame, it shows picture.
        self.pause_play_btn = builder.get_object('pause_play_btn', self.master)
        self.data_toplevel = None

        self.pause_play_btn.config(textvariable=self.pause_play_btn_stringvar)

        # tk application
        self.about_tkapp = AboutTkApplication()
        self.data_tkapp = None

        # initial widget
        self.go_combobox.config(values=[_('File'), _('Camera')])
        self.go_combobox.current(1)

        # vid
        self.vid = None
        self.frame_width = self.frame_height = 0
        self.vid_fps = 0
        self.fxfy = None
        self.source = -1
        self.source_type = SourceType.NULL
        self.paused = False

        # vid frame
        self.cur_frame = None
        self.face_rects = []
        self.picked_face_frames = self.showed_face_frames = []
        self.show_size = (200, 200)
        self.zoom_in_size = (210, 210)
        self.save_size = (100, 100)
        self.zoomed_in_face_label = (0, 0)
        self.rec_gray_img = None
        self.root_after = -1    # for vid frame refreshing.

        # info
        self.cur_info_id = None
        self.info_ids = []  # uuid str array

        # screen
        try:
            self.screenwidth = self.master.winfo_screenwidth()
            self.screenheight = self.master.winfo_screenheight()
        except BaseException:
            print(_('No desktop environment is detected! '))
            exit()

        # train recognizer
        if data_empty():
            self.set_status_msg(self.var_nothing_was_entered_str)
        else:
            self.recognizer_train()

        # connect callbacks
        self.builder.connect_callbacks(self)

    def load_images(self):
        '''
        :reference https://www.cnblogs.com/do-hardworking/p/9867708.html
        '''
        images = []
        ids = []
        labels = []
        label = 0
        subdirs = os.listdir(data_path)
        for subdir in subdirs:
            subpath = os.path.join(data_path, subdir)
            if os.path.isdir(subpath):
                ids.append(subdir)
                for filename in os.listdir(subpath):
                    if filename == info_file_name:
                        continue
                    imgpath = os.path.join(subpath, filename)
                    img = cv2.imread(imgpath, cv2.IMREAD_COLOR)
                    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    images.append(gray_img)
                    labels.append(label)
                label += 1
        images = np.asarray(images)
        labels = np.asarray(labels)
        return images, labels, ids

    def recognizer_train(self):
        self.set_status_msg(_('Recognizer training. . .'))
        images, labels, self.info_ids = self.load_images()
        if len(labels) < 1:
            self.show_data_empty()
            return
        recognizer.train(images, labels)
        self.set_status_msg(_('Recognizer finish training.'))

    def on_about_btn_clicked(self):
        self.about()

    def about(self):
        self.about_tkapp.trigger()

    def on_data_btn_clicked(self):
        self.data()

    def data(self):

        self.cancel_root_after()

        if self.data_tkapp is None:
            from funing._ui.data import DataTkApplication
            self.data_tkapp = DataTkApplication()
            self.data_tkapp.master.protocol(
                "WM_DELETE_WINDOW", self.data)
            self.master.withdraw()
        else:
            self.data_tkapp.quit()
            self.data_tkapp = None
            self.master.deiconify()

    def set_status_msg(self, msg):
        self.status_label_stringvar.set(msg)

    def open_vid_cap(self):
        self.vid = cv2.VideoCapture(self.source)
        if not self.vid.isOpened():
            self.show_nsrc_error()
            return
        self.frame_width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.vid_fps = self.vid.get(cv2.CAP_PROP_FPS)

    def close_vid_cap(self):
        if self.vid is None:
            return
        self.vid.release()
        self.vid = None

    def on_pause_play_btn_clicked(self, *args):
        self.pause_play(*args)

    def pause_play(self, *args):
        if self.source_type != SourceType.VID:
            return
        if self.paused:
            self.paused = False
            self.refresh_frame()
            self.pause_play_btn_stringvar.set(_('Pause'))
            self.set_status_msg('')
            if debug:
                print('Play. . .')

        else:
            self.cancel_root_after()
            self.pause_play_btn_stringvar.set(_('Play'))
            self.paused = True
            if len(self.face_rects) > 0:
                self.show_face_was_detected_status_msg()
            else:
                self.show_no_face_was_detected_status_msg()
            if debug:
                print('Pause. . .')

    def clear_face_text(self):
        self.info_text.delete(1.0, END)

    def add_face_label_pick(self, index):
        x, y, w, h = self.face_rects[index]
        _w = max(w, h)

        frame = self.cur_frame[y:y + _w, x:x + _w]
        frame = cv2.resize(frame, self.show_size)
        vid_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)

        new_face_label = Label(self.face_frame)
        new_face_label.imgtk = imgtk
        new_face_label.configure(image=imgtk)

        menu = Menu(self.master, tearoff=0)
        menu.add_command(
            label=_("delete"),
            command=(lambda label=new_face_label, index=index:
                     self.del_face_label_pick(label, index)))

        new_face_label.bind(
            "<Button-3>",
            (lambda event: menu.tk_popup(
                event.x_root,
                event.y_root)))
        new_face_label.bind("<Button-1>",
                            (lambda e, label=new_face_label, index=index:
                             self.del_face_label_pick(label, index)))

        new_face_label.pack(side=LEFT)

        picked_face_frame = cv2.resize(self.cur_frame[y:y + h, x:x + w],
                                       self.save_size,
                                       interpolation=cv2.INTER_LINEAR)
        self.picked_face_frames.append(picked_face_frame)

    def del_face_label_pick(self, label, index):
        del self.picked_face_frames[index]
        label.destroy()
        if len(self.picked_face_frames) < 1:
            self.clear_status_msg()
        if debug:
            print(len(self.picked_face_frames))

    def show_from_file(self):
        self.face_src_path = tkf.askopenfilename(
            title=_('Select a file'),
            filetypes=[(_('Image or video'), self.var_img_vid_exts)],
            initialdir='~')

        if len(self.face_src_path) < 1:
            return

        ext = os.path.splitext(self.face_src_path)[1][1:]
        self.go_combobox.set(self.face_src_path)

        if ext in self.var_image_exts:
            self.view_image()
        elif ext in self.var_video_exts:
            self.source = self.face_src_path
            self.play_video()

    def show_from_camera(self):
        self.source = 0
        self.go_combobox.set(self.source)
        self.play_video()

    def go_combobox_selected(self, args):

        go_combobox_var = self.go_combobox.get()
        if len(go_combobox_var.strip()) < 1:
            return
        self.rec_img = False
        self.cancel_root_after()

        if go_combobox_var == _('File'):
            self.show_from_file()
            return
        elif go_combobox_var == _('Camera'):
            self.show_from_camera()
            return

    def on_go_btn_clicked(self, *args):
        self.open_src(*args)

    def open_src(self, *args):
        '''
        Entry source and open it.
        '''
        go_combobox_var = self.go_combobox.get()
        if len(go_combobox_var.strip()) < 1:
            return
        self.rec_img = False
        self.cancel_root_after()

        show_from_ext = go_combobox_var.split('.')[-1]

        if show_from_ext in self.var_video_exts:
            self.source = go_combobox_var
            self.play_video()
            return
        elif re.match(r'\d+', go_combobox_var):
            self.source = int(go_combobox_var)
            self.play_video()
            return
        elif show_from_ext in self.var_image_exts:
            self.view_image()
            return
        elif go_combobox_var == _('File'):
            self.show_from_file()
            return
        elif go_combobox_var == _('Camera'):
            self.show_from_camera()
            return

        self.go_combobox.current(1)
        self.show_nsrc_error()

    def get_dict_key_by_value(self, _dict, value):
        keys = _dict.keys()
        values = _dict.values()
        if value in values:
            return list(keys)[list(values).index(value)]
        else:
            return value

    def show_from_opt_command(self, *args):
        '''
        Show file dialog or turn on the camera.
        '''
        show_from = self.get_dict_key_by_value(
            self.show_from_opt_dict,
            self.show_from_opt_stringvar.get())
        if show_from == 'file':
            self.face_src_path = tkf.askopenfilename(
                title=_('Select a file'),
                filetypes=[(_('Image or video'), self.var_img_vid_exts)],
                initialdir='~')

            if len(self.face_src_path) < 1:
                return

            ext = os.path.splitext(self.face_src_path)[1][1:]
            self.show_from_opt_stringvar.set(self.face_src_path)

            if ext in self.var_image_exts:
                self.view_image()
            elif ext in self.var_video_exts:
                self.source = self.face_src_path
                self.play_video()

        elif show_from == 'camera':
            self.source = 0
            self.show_from_opt_stringvar.set(self.source)
            self.play_video()

    def cancel_root_after(self):
        '''
        Finish refreshing.
        '''
        if self.root_after != -1:
            self.master.after_cancel(self.root_after)
            self.close_vid_cap()
            self.vid = None

    def play_video(self):
        self.paused = False
        self.source_type = SourceType.VID
        self.close_vid_cap()
        self.open_vid_cap()
        self.get_vid_resize_fxfy()
        self.refresh_frame()

    def refresh_frame(self):
        if self.source_type != SourceType.VID:
            return

        if self.vid is None:
            self.vid = cv2.VideoCapture(self.source)
        if not self.vid.isOpened():
            self.show_nsrc_error()
            return

        __, self.cur_frame = self.vid.read()

        self.rec_gray_img = cv2.cvtColor(self.cur_frame, cv2.COLOR_BGR2GRAY)
        self.face_rects = face_casecade.detectMultiScale(
            self.rec_gray_img, 1.3, 5)

        for (x, y, w, h) in self.face_rects:
            self.cur_frame = cv2.rectangle(
                self.cur_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        vid_img = cv2.resize(self.cur_frame, (0, 0),
                             fx=self.fxfy, fy=self.fxfy)

        vid_img = cv2.cvtColor(vid_img, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        self.vidframe_label.imgtk = imgtk
        self.vidframe_label.configure(image=imgtk)

        if not self.paused:
            self.root_after = self.master.after(
                int(1000 / self.vid_fps), self.refresh_frame)

    def get_img_resize_fxfy(self):
        w = self.screenwidth / 2
        h = self.screenheight / 2
        r = w / h

        r0 = self.frame_width / self.frame_height
        r1 = r0 / r
        self.fxfy = h / self.frame_height if r1 < r else w / self.frame_width
        if debug:
            print('self.fxfy: ', self.fxfy)

    def view_image(self):
        self.source_type = SourceType.IMG
        self.cancel_root_after()

        self.cur_frame = cv2.imread(self.face_src_path)

        self.frame_width, self.frame_height, __ = self.cur_frame.shape

        self.get_img_resize_fxfy()

        self.cur_frame = cv2.resize(self.cur_frame, (0, 0),
                                    fx=self.fxfy, fy=self.fxfy)

        self.rec_gray_img = cv2.cvtColor(self.cur_frame, cv2.COLOR_BGR2GRAY)
        self.face_rects = face_casecade.detectMultiScale(
            self.rec_gray_img, 1.3, 5)

        if len(self.face_rects) < 1:
            self.show_no_face_was_detected_status_msg()
        else:
            self.show_face_was_detected_status_msg()
            for (x, y, w, h) in self.face_rects:
                self.cur_frame = cv2.rectangle(
                    self.cur_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        frame = cv2.cvtColor(self.cur_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.vidframe_label.imgtk = imgtk
        self.vidframe_label.configure(image=imgtk)

    def cur_frame2label(self):
        vid_img = cv2.resize(self.cur_frame, (0, 0),
                             fx=self.fxfy, fy=self.fxfy)
        vid_img = cv2.cvtColor(vid_img, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        self.vidframe_label.imgtk = imgtk
        self.vidframe_label.configure(image=imgtk)

    def get_vid_resize_fxfy(self):
        if self.frame_width == self.frame_height == 0:
            if debug:
                print('self.iru is None')
            return
        w = self.screenwidth / 2
        h = self.screenheight / 2
        r = w / h
        r0 = self.frame_width / self.frame_height
        r1 = r0 / r
        self.fxfy = h / self.frame_height if r1 < r else w / self.frame_width
        if debug:
            print('self.fxfy: ', self.fxfy)

    def show_nsrc_error(self):
        messagebox.showerror(
            self.var_unable_to_open_vid_source_str,
            self.var_unable_to_open_vid_source_str + ': ' +
            str(self.go_combobox.get()))

    def on_save_info_btn_clicked(self):
        self.save_info()

    def save_info(self):
        if self.cur_info_id is None:
            return
        if len(self.picked_face_frames) < 1:
            self.set_status_msg(_('No face picture picked'))
            return
        data_dir_path = os.path.join(data_path, self.cur_info_id)
        os.makedirs(data_dir_path, exist_ok=True)

        info = self.info_text.get("1.0", "end-1c")
        info_file_path = self.get_info_file_path(self.cur_info_id)
        with open(info_file_path, 'w+') as f:
            f.write(info)
        if self.status == Status.PICK:
            for f in self.picked_face_frames:
                if len(f) < 1:
                    continue
                cv2.imwrite(f'{data_dir_path}/{str(uuid.uuid4())}.jpg', f)
            self.cur_info_id = None

        if debug:
            print('info > ' + info)
        self.recognizer_train()

    def restore_face_label_size_rec(self, index):
        label, index = self.zoomed_in_face_label
        if not label.winfo_exists():
            return

        frame = self.showed_face_frames[index]
        frame = cv2.resize(frame, self.show_size)

        vid_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        label.imgtk = imgtk
        label.configure(image=imgtk)

    def get_info_file_path(self, info_id):
        return get_info_file_path(info_id)

    def show_info(self, label, index, cur_info_id):

        if (self.zoomed_in_face_label[0] != 0) and \
                (self.zoomed_in_face_label[0] != label):
            self.restore_face_label_size_rec(index)

        frame = self.showed_face_frames[index]
        frame = cv2.resize(frame, self.zoom_in_size)

        vid_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.zoomed_in_face_label = (label, index)

        info_file_path = self.get_info_file_path(cur_info_id)

        self.info_text.delete(1.0, END)
        if not os.path.exists(info_file_path):
            _nif_ = _('No informations found')
            self.info_text.insert('1.0', _nif_)
            self.set_status_msg(_nif_)

        with open(info_file_path, 'r') as f:
            self.info_text.insert('1.0', f.read())

    def add_face_label_rec(self, f_index):
        showed_face_index = len(self.showed_face_frames)

        new_face_label = Label(self.face_frame)

        x, y, w, h = self.face_rects[f_index]
        roi_gray = self.rec_gray_img[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, self.save_size,
                              interpolation=cv2.INTER_LINEAR)

        _label, confidence = recognizer.predict(roi_gray)

        self.cur_info_id = cur_info_id = \
            self.info_ids[_label]  # global self.x and x are different.

        _h = max(h, w)
        frame = self.cur_frame[y:y + _h, x:x + _h]
        frame = cv2.resize(frame, self.show_size)

        self.showed_face_frames.append(frame)

        vid_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        new_face_label.imgtk = imgtk
        new_face_label.configure(image=imgtk)

        menu = Menu(self.master, tearoff=0)
        menu.add_command(
            label=_("delete"),
            command=(lambda _label=new_face_label, _index=showed_face_index:
                     self.del_face_label_rec(_label, _index)))

        new_face_label.bind("<Double-Button-1>",
                            lambda e, _label=new_face_label,
                            _index=showed_face_index:
                            self.del_face_label_rec(_label, _index))
        new_face_label.bind(
            "<Button-1>",
            (lambda e, _label=new_face_label,
             _index=showed_face_index,
             _info_id=cur_info_id:
             self.show_info(
                 _label,
                 _index,
                 _info_id)))
        new_face_label.bind(
            "<Button-3>",
            (lambda event: menu.tk_popup(
                event.x_root,
                event.y_root)))

        new_face_label.pack(side=LEFT)

        self.show_info(new_face_label, showed_face_index, cur_info_id)

    def del_face_label_rec(self, label, index):
        if self.zoomed_in_face_label[0] == label:
            self.zoomed_in_face_label = (0, 0)
        label.destroy()
        self.showed_face_frames[index] = None
        self.info_text.delete(1.0, END)
        if np.all(np.array(self.showed_face_frames, dtype=object) is None):
            self.clear_status_msg()

    def clear_faces_frame(self):
        for child in self.face_frame.winfo_children():
            child.destroy()
        self.picked_face_frames = []

    def on_pick_btn_clicked(self):
        self.pick()

    def pick(self):

        if self.source_type == SourceType.NULL:
            return

        if self.status == Status.REC:
            self.clear_faces_frame()
            self.status = Status.PICK  # 'p'

        if self.cur_frame is None:
            return

        self.clear_face_text()

        self.cur_info_id = str(uuid.uuid4())

        if len(self.face_rects) < 1:
            self.show_no_face_was_detected_status_msg()
            if debug:
                print('len( self.face_rects ) < 1 ')
            return

        self.status_label_stringvar.set(
            self.var_face_was_detected_str +
            f'({self.var_click_to_remove_p})'
        )

        if debug:
            print(self.face_rects)
            print(type(self.face_rects))

        for index in range(len(self.face_rects)):
            self.add_face_label_pick(index)

    def on_recognize_btn_clicked(self):
        self.rec()

    def rec(self):

        if self.source_type == SourceType.NULL:
            return

        if data_empty():
            self.show_data_empty()
            return

        if self.status == Status.PICK:
            self.clear_faces_frame()
            self.status = Status.REC

        if self.cur_frame is None:
            return

        self.clear_face_text()

        if len(self.face_rects) < 1:
            self.show_no_face_was_detected_status_msg()
            if debug:
                print('len( self.face_rects ) < 1 ')
            return

        self.status_label_stringvar.set(
            self.var_face_was_detected_str +
            f'({self.var_double_click_to_remove_r})'
        )

        for index in range(len(self.face_rects)):
            self.add_face_label_rec(index)

    def show_data_empty(self):
        unable_open_s = _('Nothing enter')
        self.set_status_msg(self.var_nothing_was_entered_str)
        messagebox.showerror(unable_open_s, self.var_nothing_was_entered_str)

    def show_no_face_was_detected_status_msg(self):
        self.set_status_msg(self.var_no_face_was_detected_str)

    def show_face_was_detected_status_msg(self):
        self.set_status_msg(self.var_face_was_detected_str)

    def clear_status_msg(self):
        self.status_label_stringvar.set('')


def start():
    root = tk.Tk()
    app = MainApplication(root)
    app.run()
