

import gettext
import os
import re
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
import yaml
from cv2 import haarcascades
from PIL import Image, ImageTk

from funing import settings
from funing._ui import error
from funing._ui.lang import _
from funing.ui.about_ui import about_toplevel
from funing.ui.main_ui import MainUI

# from funing._ui.lang import _
# self.frame_width, self.frame_height, __ = self.cur_frame.shape


class SourceType(Enum):
    NULL = 0
    IMG = 1
    VID = 2


class FDoing(Enum):
    REC = 0
    PICK = 1


class _MainUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()
        self.source = -1
        self.root_after = -1
        self.fxfy = None
        self.showf_sv = None
        self.showfm = self.mainui.showframe
        self.infofm = self.mainui.infoframe
        self.bottomframe = self.mainui.bottomframe
        self.status_label_sv = self.bottomframe.status_label_sv
        self.about_tl = None
        # vid
        self.vid = None
        self.frame_width = 0
        self.frame_height = 0
        self.vid_fps = 0

        self.source_type = SourceType.NULL

        self.cur_frame = None
        self.face_rects = []
        self.picked_face_frames = []
        self.showed_face_frames = []
        self.show_size = (200, 200)
        self.zoom_in_size = (210, 210)
        self.save_size = (100, 100)
        self.zoomed_in_face_label = (0, 0)

        self.fdoing = FDoing.PICK

        self.paused = False
        # rec_result
        self.rec_gray_img = None
        # rec_faces
        self.recfs = []
        # info
        self.cur_info_id = None
        self.info_ids = []
        # cv2
        self.hff_xml_path = os.path.join(haarcascades,
                                         "haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.EigenFaceRecognizer_create()
        self.face_casecade = cv2.CascadeClassifier(self.hff_xml_path)

        self.image_exts = [
            'jpg', 'png', 'jpeg', 'webp'
        ]
        self.video_exts = [
            'mp4', 'avi', '3gp', 'webm', 'mkv'
        ]
        self.filetype_exts = '*.' + \
            ' *.'.join(self.image_exts + self.video_exts)

        # screen
        try:
            self.screenwidth = self.mainui.root.winfo_screenwidth()
            self.screenheight = self.mainui.root.winfo_screenheight()
        except BaseException:
            print(_('No desktop environment is detected! '))
            exit()
        if settings.data_empty():
            self.show_status_msg(_("You haven't entered anything yet!"))
        else:
            self.recognizer_train()
        self.set_ui_events()
        self.mainui.mainloop()

    def load_images(self):
        '''
        :reference https://www.cnblogs.com/do-hardworking/p/9867708.html
        '''
        images = []
        ids = []
        labels = []
        label = 0
        subdirs = os.listdir(settings.faces_path)
        for subdir in subdirs:
            subpath = os.path.join(settings.faces_path, subdir)
            if os.path.isdir(subpath):
                ids.append(subdir)
                for filename in os.listdir(subpath):
                    imgpath = os.path.join(subpath, filename)
                    img = cv2.imread(imgpath, cv2.IMREAD_COLOR)
                    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    images.append(gray_img)
                    labels.append(label)
                label += 1
        images = np.asarray(images)
        labels = np.asarray(labels)
        return images, labels, ids

    def about_tl_destroy(self):
        self.about_tl.destroy()
        self.about_tl = None

    def about_fn(self):
        if self.about_tl is None:
            self.about_tl = about_toplevel()
            self.about_tl.protocol("WM_DELETE_WINDOW", self.about_tl_destroy)
            self.about_tl.mainloop()
        else:
            self.about_tl.destroy()
            self.about_tl = None
        pass

    def show_status_msg(self, msg):
        self.status_label_sv.set(msg)

    def recognizer_train(self):
        self.show_status_msg(_('Recognizer training. . .'))
        images, labels, self.info_ids = self.load_images()
        self.recognizer.train(images, labels)
        self.show_status_msg(_('Recognizer finish training.'))

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

    def set_ui_events(self):
        self.showfm.pp_btn['command'] = self.pause_play
        self.showfm.rec_btn['command'] = self.recf_v0
        self.showfm.pick_btn['command'] = self.pick_v0
        self.showfm.showf_go_btn['command'] = self.show_go
        self.showfm.showf_optionmenu_sv.trace('w', self.show_from)
        self.infofm.save_btn['command'] = self.savef
        self.bottomframe.about_fn_btn['command'] = self.about_fn
        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy)

    def destroy(self):
        if self.vid is not None:
            self.vid.release()
        exit()

    def pause_play(self, *args):
        if self.source_type != SourceType.VID:
            return
        if self.paused:
            self.paused = False
            self.refresh_frame()
            self.showfm.pp_sv.set(_('Pause'))
            self.show_status_msg('')
            if settings.debug():
                print('Play. . .')

        else:
            self.cancel_root_after()
            self.showfm.pp_sv.set(_('Play'))
            self.paused = True
            if len(self.face_rects) > 0:
                self.show_face_was_detected_status_msg()
            else:
                self.show_no_face_was_detected_status_msg()
            if settings.debug():
                print('Pause. . .')

    def clear_face_text(self):
        self.infofm.face_text.delete(1.0, END)

    def add_face_label_p(self, num):
        x, y, w, h = self.face_rects[num]
        _w = max(w, h)

        new_fl = Label(self.infofm.faces_frame)
        frame = self.cur_frame[y:y + _w, x:x + _w]
        frame = cv2.resize(frame, self.show_size)
        vid_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        new_fl.imgtk = imgtk
        new_fl.configure(image=imgtk)
        new_fl.bind("<Button-1>", lambda e: self.del_face_label_p(e, num))

        new_fl.pack(side=LEFT)

        picked_face_frame = cv2.resize(self.cur_frame[y:y + h, x:x + w],
                                       self.save_size,
                                       interpolation=cv2.INTER_LINEAR)
        self.picked_face_frames.append(picked_face_frame)

    def del_face_label_p(self, e, num):
        del self.picked_face_frames[num]
        e.widget.destroy()
        if settings.debug():
            print(len(self.picked_face_frames))

    def show_go(self, *args):
        self.showf_sv = self.showfm.showf_sv.get()
        if len(self.showf_sv.strip()) < 1:
            return
        self.rec_img = False
        self.cancel_root_after()
        showf_ext = self.showf_sv.split('.')[-1]
        if showf_ext in self.video_exts:
            self.source = self.showf_sv
            self.play_video()
            return
        if re.match(r'\d+', self.showf_sv):
            self.source = int(self.showf_sv)
            self.play_video()
            return
        if showf_ext in self.image_exts:
            self.view_image()
            return
        self.showfm.showf_sv.set('')
        self.show_nsrc_error()

    def get_dict_key_by_value(self, _dict, value):
        keys = _dict.keys()
        values = _dict.values()
        return list(keys)[list(values).index(value)]

    def show_from(self, *args):
        show_f = self.get_dict_key_by_value(
            self.showfm.showf_t_dict,
            self.showfm.showf_optionmenu_sv.get())
        if show_f == 'file':
            self.face_src_path = tkf.askopenfilename(
                title=_('Select a file'),
                filetypes=[(_('Image or video'), self.filetype_exts)],
                initialdir='~')
            if len(self.face_src_path) < 1:
                return
            ext = os.path.splitext(self.face_src_path)[1][1:]
            self.showfm.showf_sv.set(self.face_src_path)
            if ext in self.image_exts:
                self.view_image()
            elif ext in self.video_exts:
                self.source = self.face_src_path
                self.play_video()
        elif show_f == 'camera':
            self.source = 0
            self.showfm.showf_sv.set(self.source)
            self.play_video()

    def cancel_root_after(self):
        if self.root_after != -1:
            self.mainui.root.after_cancel(self.root_after)
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
        self.face_rects = self.face_casecade.detectMultiScale(
            self.rec_gray_img, 1.3, 5)

        for (x, y, w, h) in self.face_rects:
            self.cur_frame = cv2.rectangle(
                self.cur_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        vid_img = cv2.resize(self.cur_frame, (0, 0),
                             fx=self.fxfy, fy=self.fxfy)

        vid_img = cv2.cvtColor(vid_img, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)

        if not self.paused:
            self.root_after = self.mainui.root.after(
                int(1000 / self.vid_fps), self.refresh_frame)

    def get_img_resize_fxfy(self):
        w = self.screenwidth / 2
        h = self.screenheight / 2
        r = w / h

        r0 = self.frame_width / self.frame_height
        r1 = r0 / r
        self.fxfy = h / self.frame_height if r1 < r else w / self.frame_width
        if settings.debug():
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
        self.face_rects = self.face_casecade.detectMultiScale(
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
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)

    def cur_frame2label(self):
        vid_img = cv2.resize(self.cur_frame, (0, 0),
                             fx=self.fxfy, fy=self.fxfy)
        vid_img = cv2.cvtColor(vid_img, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)

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
        if settings.debug():
            print('self.fxfy: ', self.fxfy)

    def show_nsrc_error(self):
        unable_open_s = _('Unable to open video source')
        messagebox.showerror(
            unable_open_s,
            unable_open_s + ': ' + self.showf_sv)

    def savef(self):
        if self.cur_info_id is None:
            return
        info = self.infofm.face_text.get("1.0", "end-1c")
        info_file_path = os.path.join(settings.infos_path, self.cur_info_id)
        open(info_file_path, 'w+').write(info)
        if self.fdoing == FDoing.PICK:
            img_path = os.path.join(settings.faces_path, self.cur_info_id)
            os.makedirs(img_path, exist_ok=True)
            count = 0
            for f in self.picked_face_frames:
                cv2.imwrite(f'{img_path}/{count}.png', f)
                count += 1
            self.cur_info_id = None

        if settings.debug():
            print('info > ' + info)
        self.recognizer_train()

    def restore_face_label_size(self, index):
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

    def show_info(self, label, index):

        if (self.zoomed_in_face_label[0] != 0) and \
                (self.zoomed_in_face_label[0] != label):
            self.restore_face_label_size(index)

        frame = self.showed_face_frames[index]
        frame = cv2.resize(frame, self.zoom_in_size)

        vid_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.zoomed_in_face_label = (label, index)

        info_file_path = os.path.join(
            settings.infos_path, self.cur_info_id)
        self.infofm.face_text.delete(1.0, END)

        if not os.path.exists(info_file_path):
            _nif = _('No informations found')
            self.infofm.face_text.insert('1.0', _nif)
            self.show_status_msg(_nif)

        self.infofm.face_text.insert('1.0',
                                     open(info_file_path, 'r').read())

    def add_face_label_r(self, num):
        index = len(self.showed_face_frames)

        new_fl = Label(self.infofm.faces_frame)

        x, y, w, h = self.face_rects[num]
        roi_gray = self.rec_gray_img[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, self.save_size,
                              interpolation=cv2.INTER_LINEAR)

        label, confidence = self.recognizer.predict(roi_gray)

        self.cur_info_id = self.info_ids[label]
        _h = max(h, w)
        frame = self.cur_frame[y:y + _h, x:x + _h]
        frame = cv2.resize(frame, self.show_size)

        self.showed_face_frames.append(frame)

        vid_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vid_img = Image.fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        new_fl.imgtk = imgtk
        new_fl.configure(image=imgtk)

        new_fl.bind("<Double-Button-1>", lambda e:
                    self.del_face_label_r(e, index))

        new_fl.bind("<Button-1>", lambda e: self.show_info(new_fl, index))

        new_fl.pack(side=LEFT)

        self.show_info(new_fl, index)

    def del_face_label_r(self, e, index):
        if self.zoomed_in_face_label[0] == e.widget:
            self.zoomed_in_face_label = (0, 0)
        e.widget.destroy()
        self.showed_face_frames[index] = None
        self.infofm.face_text.delete(1.0, END)

    def clear_faces_frame(self):
        for child in self.infofm.faces_frame.winfo_children():
            child.destroy()

    def pick_v0(self):

        if self.source_type == SourceType.NULL:
            return

        if self.fdoing == FDoing.REC:
            self.clear_faces_frame()
            self.fdoing = FDoing.PICK  # 'p'

        if self.cur_frame is None:
            return

        self.clear_face_text()

        self.cur_info_id = str(uuid.uuid4())

        if len(self.face_rects) < 1:
            self.show_no_face_was_detected_status_msg()
            if settings.debug():
                print('len( self.face_rects ) < 1 ')
            return

        self.show_face_was_detected_status_msg()

        if settings.debug():
            print(self.face_rects)
            print(type(self.face_rects))

        for i in range(len(self.face_rects)):
            self.add_face_label_p(i)

    def recf_v0(self):

        if self.source_type == SourceType.NULL:
            return

        if settings.data_empty():
            self.show_data_empty()
            return

        if self.fdoing == FDoing.PICK:
            self.clear_faces_frame()
            self.fdoing = FDoing.REC

        if self.cur_frame is None:
            return

        self.clear_face_text()

        if len(self.face_rects) < 1:
            self.show_no_face_was_detected_status_msg()
            if settings.debug():
                print('len( self.face_rects ) < 1 ')
            return

        self.show_face_was_detected_status_msg()

        for i in range(len(self.face_rects)):
            self.add_face_label_r(i)

    def show_nsrc_error(self):
        unable_open_s = _('Unable to open video source')
        messagebox.showerror(
            unable_open_s,
            unable_open_s + ': ' + self.showf_sv)

    def show_data_empty(self):
        unable_open_s = _('Nothing enter')
        msg = _("You haven't entered anything yet!")
        self.show_status_msg(msg)
        messagebox.showerror(unable_open_s, msg, )

    def show_no_face_was_detected_status_msg(self):
        self.show_status_msg(_('No face was detected.'))

    def show_face_was_detected_status_msg(self):
        self.show_status_msg(_('Face was detected.'))
