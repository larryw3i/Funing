import asyncio
import getopt
import importlib
import os
import pickle
import queue
import re
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import uuid
import webbrowser
from enum import Enum
from functools import partial
from importlib import import_module
from itertools import zip_longest
from multiprocessing import Pipe, Process, Queue
from pathlib import Path
from queue import Queue
from threading import Thread
from tkinter import *
from tkinter import filedialog, ttk

import cv2
import yaml
from appdirs import user_data_dir
from cv2.data import haarcascades
from cv2.face import EigenFaceRecognizer_create
from PIL import Image, ImageTk
from PIL.Image import fromarray as pil_image_fromarray

from funing.abc import *
from funing.locale import _
from funing.path import *
from funing.settings import *
from funing.settings4t import *
from funing.widgets.abc import *
from funing.widgets.enum import *


class FrameWidget(WidgetABC):
    def __init__(self, mw):
        super().__init__(mw)
        self.video_frame_label = None
        self.video_frame_size = None
        self.video_src_path = None
        self.video_frame_fps = None
        self.video_frame_size = None
        self.video_exts = ["mp4", "avi", "3gp", "webm", "mkv"]
        self.video_signal = VIDEO_SIGNAL.PAUSE
        self.video_capture = None
        self.video_update_identifier = None
        self.video_frame = None
        self.video_frame_fxfy = None
        self.video_frame_width = None
        self.video_frame_height = None
        self.video_refresh_time = None
        self.image_src_path = None
        self.image_exts = ["jpg", "png", "jpeg", "webp"]
        self.image_size = None
        self.face_casecade = None
        self.face_recognizer = None
        self.openfrom_combobox_var = StringVar()
        self.openfrom_combobox_file_str = _("File")
        self.openfrom_combobox_camera_str = _("Camera")
        self.openfrom_Combobox = None
        self.opensrc_button = None
        self.play_button = None
        self.pause_button = None
        self.pick_button = None
        self.recog_button = None
        self.oper_widgets = None
        self.src_type = None
        self.action = None
        self.oper_widgets_x_list = None
        self.oper_widgets_width_list = None
        self.oper_widgets_width = None
        self.oper_widgets_height = None
        self.oper_widgets_margin = 2
        self.oper_widget_min_height = None

    def set_video_refresh_time(self):
        self.video_refresh_time = int(1000 / self.get_video_frame_fps())

    def get_video_refresh_time(self):
        if not self.video_refresh_time:
            self.set_video_refresh_time()
        return self.video_refresh_time

    def get_recognizer(self):
        if not self.face_recognizer:
            self.set_face_recognizer()
            self.train_recognizer()
        return self.face_recognizer

    def set_face_recognizer(self):
        self.recognizer = cv2.face.EigenFaceRecognizer_create()

    def train_recognizer(self):
        self.mw.set_msg(_("Train face recognizer."))
        self.mw.set_msg(_("Finish Training."))
        pass

    def set_face_casecade(self):
        hff_xml_path = os.path.join(
            haarcascades, "haarcascade_frontalface_default.xml"
        )
        if not os.path.exists(hff_xml_path):
            self.mw.set_msg(_("haarcascades data doesn't exist."))
            self.release_video_capture()
            return
        self.face_casecade = cv2.CascadeClassifier(hff_xml_path)

    def get_face_casecade(self):
        if not self.face_casecade:
            self.set_face_casecade()
        return self.face_casecade

    def switch_video_signal(self):
        if self.video_signal == VIDEO_SIGNAL.PAUSE:
            self.video_signal = REFRESH
        elif self.video_signal == VIDEO_SIGNAL.REFRESH:
            self.video_signal = PAUSE

    def set_oper_widgets_width_list(self):
        prev_width = width = self.get_oper_widgets()[0].winfo_reqwidth()
        self.oper_widgets_width_list = []
        for w in self.get_oper_widgets()[1:]:
            prev_width = width
            reqwidth = w.winfo_reqwidth()
            width += self.get_oper_widgets_margin() + reqwidth
            if width > self.get_width():
                self.oper_widgets_width_list.append(prev_width)
                width = reqwidth
        self.oper_widgets_width_list.append(width)

    def get_oper_widgets_width_list(self):
        self.set_oper_widgets_width_list()
        return self.oper_widgets_width_list

    def get_oper_widgets_margin(self):
        return self.oper_widgets_margin

    def set_oper_widgets_margin(self, margin=2):
        self.oper_widgets_margin = margin

    def set_oper_widgets_margin(self, margin=2):
        self.oper_widgets_margin = margin

    def get_oper_widgets_width(self):
        self.oper_widgets_width = 0
        for b in self.get_oper_widgets():
            self.oper_widgets_width += b.winfo_reqwidth()
        return self.oper_widgets_width

    def get_oper_widgets_height(self):
        self.get_oper_widgets()
        return self.oper_widgets[0].winfo_reqheight()

    def oper_widgets_x_list(self):
        self.get_oper_widgets()
        if not self.oper_widgets_width:
            self.oper_widgets_width()
        if not self.oper_widgets_height:
            self.get_oper_widgets_height()
        if self.oper_widgets_width < self.get_width():
            return int((self.get_width() - self.get_oper_widgets()) / 2)
        else:
            pass

    def set_oper_widgets(self):
        self.oper_widgets = [
            self.openfrom_combobox,
            self.opensrc_button,
            self.play_button,
            self.pause_button,
            self.pick_button,
            self.recog_button,
        ]

    def get_oper_widgets(self):
        if not self.oper_widgets:
            self.set_oper_widgets()
        return self.oper_widgets

    def refresh_video_frame(self):
        self.update_video_frame()

    def pause_video_frame(self):
        self.stop_video_frame()

    def read_video_src(self, src_path=None):
        if (not self.video_src_path) or src_path:
            self.set_video_src_path(src_path)
        self.video_signal = VIDEO_SIGNAL.REFRESH
        self.video_frame_label.configure(background="")
        self.update_video_frame()

    def play_video(self, src_path=None, check_video_capture=True):
        if check_video_capture:
            self.check_video_capture()
        self.read_video_src(src_path)

    def pause_video(self):
        pass

    def show_image(self, src_path=None):
        if not src_path:
            self.set_image_src_path(src_path)
        pass

    def get_src_frame(self):
        pass

    def get_video_src_path(self):
        if not self.video_src_path:
            self.set_video_src_path()
        return (
            int(self.video_src_path)
            if str.isnumeric(self.video_src_path)
            else self.video_src_path
        )

    def set_video_src_path(self, src_path="0"):
        self.video_src_path = (
            "0"
            if (src_path == 0 or src_path is None)
            else str(src_path)
            if isinstance(src_path, int)
            else src_path
        )
        self.image_src_path = None

    def get_image_src_path(self):
        return self.image_src_path

    def set_image_src_path(self, src_path):
        self.image_src_path = src_path
        self.video_src_path = None

    def set_video_frame_fps(self, fps=25):
        self.video_frame_fps = fps

    def get_video_frame_fps(self, fps=25):
        if not self.video_frame_fps:
            self.set_video_frame_fps()
        return self.video_frame_fps

    def get_video_frame_width(self):
        if not self.video_frame_width:
            self.video_frame_width = self.video_capture.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        return self.video_frame_width

    def get_video_frame_height(self):
        if not self.video_frame_height:
            self.video_frame_height = self.video_capture.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        return self.video_frame_height

    def set_video_frame_size(self, size=25):
        self.video_frame_size = size

    def get_video_frame_size(self):
        if not self.video_frame_size:
            self.set_video_frame_size()
        return self.video_frame_size

    def get_video_frame_label_max_width(self):
        return int(self.get_width())

    def get_video_frame_label_max_height(self):
        return int(self.get_height() * 0.5)

    def get_video_frame_label_x(self):
        return self.get_x()

    def get_video_frame_label_y(self):
        return self.get_y()

    def get_video_frame_label_width(self):
        return self.get_video_frame_label_max_width()

    def get_video_frame_label_height(self):
        return self.get_video_frame_label_max_height()

    def get_openfrom_combobox_x(self):
        pass

    def get_openfrom_combobox_y(self):
        pass

    def get_openfrom_combobox_width(self):
        return self.openfrom_combobox.winfo_reqwidth()

    def get_openfrom_combobox_height(self):
        return self.openfrom_combobox.winfo_reqheight()

    def set_x(self):
        pass

    def get_x(self):
        return 0

    def get_y(self):
        return 0

    def set_y(self):
        pass

    def set_width(self):
        pass

    def get_width(self):
        return int(self.mw.get_sep_x())

    def set_height(self):
        pass

    def get_height(self):
        return int(self.mw.get_height() - self.mw.get_bottom_height())

    def open_video_capture(self):
        self.set_video_capture()

    def turnon_video_capture(self):
        self.set_video_capture()

    def set_video_capture(self):
        src_path = self.get_video_src_path()
        self.video_capture = cv2.VideoCapture(src_path)
        if not self.video_capture.isOpened():
            self.mw.set_msg(_("Unable to open video source %s.") % src_path)

    def get_video_capture(self):
        if not self.video_capture:
            self.set_video_capture()
        return self.video_capture

    def turnon_camera(self, src_path=0):
        if (
            self.video_signal == VIDEO_SIGNAL.PAUSE
            or self.get_video_src_path() != src_path
        ):
            self.play_video(src_path)

    def set_video_frame_fxfy(self):
        if self.video_capture is None:
            return
        if not self.video_capture.isOpened():
            return
        w = self.get_video_frame_label_width()
        h = self.get_video_frame_label_height()
        r = w / h
        r0 = self.get_video_frame_width() / self.get_video_frame_height()
        r1 = r0 / r
        self.video_frame_fxfy = (
            h / self.get_video_frame_height()
            if r1 < r
            else w / self.get_video_frame_width()
        )

    def get_video_frame_fxfy(self):
        if not self.video_frame_fxfy:
            self.set_video_frame_fxfy()
        return self.video_frame_fxfy

    def show_video_frame(self):
        frame = self.video_frame
        face_casecade = self.get_face_casecade()
        video_frame_fxfy = self.get_video_frame_fxfy()
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = face_casecade.detectMultiScale(gray_img, 1.3, 5)
        for (x, y, w, h) in rects:
            frame = cv2.rectangle(
                frame, (x, y), (x + w, y + h), (255, 0, 0), 2
            )
        rects = None
        vid_img = cv2.resize(
            frame,
            (0, 0),
            fx=self.get_video_frame_fxfy(),
            fy=self.get_video_frame_fxfy(),
        )
        vid_img = cv2.cvtColor(vid_img, cv2.COLOR_BGR2RGB)
        vid_img = pil_image_fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        self.video_frame_label.imgtk = imgtk
        self.video_frame_label.configure(image=imgtk)

    def update_video_frame(self):
        video_capture = self.get_video_capture()
        video_refresh_time = self.get_video_refresh_time()
        if self.video_signal == VIDEO_SIGNAL.REFRESH:
            _, frame = video_capture.read()
            if frame is None:
                self.stop_video_frame()
                return
            self.video_frame = frame
            self.show_video_frame()
            self.video_update_identifier = self.root.after(
                video_refresh_time, self.update_video_frame
            )

    def filepath_is_video_type(self, path):
        return any(path.endswith(ext) for ext in self.video_exts)

    def filepath_is_image_type(self, path):
        return any(path.endswith(ext) for ext in self.image_exts)

    def open_filedialog(self):
        if self.video_signal == VIDEO_SIGNAL.REFRESH:
            self.stop_video_frame()
        src_path = filedialog.askopenfilename(
            initialdir="~/Videos",
            title=_("Select video or image file"),
            filetypes=[
                ("", f"*.{ext}") for ext in self.video_exts + self.image_exts
            ],
        )
        if src_path == ():
            return
        if self.filepath_is_image_type(src_path):
            self.show_image(src_path)
        elif self.filepath_is_video_type(src_path):
            self.play_video(src_path)
        else:
            return
        self.openfrom_combobox_var.set(src_path)

    def openfrom_combobox_var_trace_w(self, *args):
        src_path = openfrom_combobox_get = self.openfrom_combobox_var.get()
        if src_path == self.openfrom_combobox_camera_str:
            self.turnon_camera()
        elif src_path == self.openfrom_combobox_file_str:
            self.open_filedialog()
        elif str.isnumeric(src_path):
            self.play_video(src_path)

    def opensrc_button_command(self):
        src_path = openfrom_combobox_get = self.openfrom_combobox_var.get()
        if self.filepath_is_image_type(src_path):
            self.show_image(src_path)
        elif self.filepath_is_video_type(src_path):
            self.play_video(src_path)

    def play_button_command(self):
        if self.video_signal == VIDEO_SIGNAL.PAUSE:
            self.play_video()

    def pause_button_command(self):
        if self.video_signal == VIDEO_SIGNAL.REFRESH:
            self.stop_video_frame()

    def pick_button_command(self):
        pass

    def recog_button_command(self):
        pass

    def get_openfrom_combobox_values(self):
        return [
            self.openfrom_combobox_file_str,
            self.openfrom_combobox_camera_str,
        ]

    def set_widgets(self):
        self.video_frame_label = Label(
            self.root,
            text=_("Video frame."),
            background="black",
            foreground="white",
            justify="center",
        )
        self.openfrom_combobox = ttk.Combobox(
            self.root,
            textvariable=self.openfrom_combobox_var,
            values=self.get_openfrom_combobox_values(),
        )
        self.openfrom_combobox_var.trace(
            "w", self.openfrom_combobox_var_trace_w
        )
        self.opensrc_button = tk.Button(
            self.root, text=_("Open"), command=self.opensrc_button_command
        )
        self.play_button = tk.Button(
            self.root, text=_("Play"), command=self.play_button_command
        )
        self.pause_button = tk.Button(
            self.root, text=_("Pause"), command=self.pause_button_command
        )
        self.pick_button = tk.Button(
            self.root, text=_("Pick"), command=self.pick_button_command
        )
        self.recog_button = tk.Button(
            self.root, text=_("Recognize"), command=self.recog_button_command
        )

    def set_oper_widget_min_height(self):
        self.oper_widget_min_height = (
            max(w.winfo_reqheight() for w in self.get_oper_widgets())
            + self.get_oper_widgets_margin()
        )

    def get_oper_widget_min_height(self):
        if not self.oper_widget_min_height:
            self.set_oper_widget_min_height()
        return self.oper_widget_min_height

    def oper_widgets_place(self):
        widgets = self.get_oper_widgets()
        width_list = self.get_oper_widgets_width_list()
        width_index = 0
        x = int((self.get_width() - width_list[width_index]) / 2)
        y = (
            self.get_video_frame_label_height()
            + self.get_oper_widgets_margin()
        )
        min_y = self.get_oper_widget_min_height()
        prev_widget = widgets[0]
        prev_widget.place(x=x, y=y)
        for w in widgets[1:]:
            x += prev_widget.winfo_reqwidth() + self.get_oper_widgets_margin()
            if (x + w.winfo_reqwidth()) > self.get_width():
                width_index += 1
                x = int((self.get_width() - width_list[width_index]) / 2)
                y += min_y
            w.place(x=x, y=y)
            prev_widget = w

    def place(self):
        self.video_frame_label.place(
            x=self.get_video_frame_label_x(),
            y=self.get_video_frame_label_y(),
            width=self.get_video_frame_label_width(),
            height=self.get_video_frame_label_height(),
        )

        self.oper_widgets_place()

        self.set_video_frame_fxfy()

    def check_video_capture(self):
        self.stop_video_frame()

    def turnoff_video_capture(self):
        self.release_video_capture()

    def close_video_capture(self):
        self.release_video_capture()

    def stop_video_frame(self):
        if self.video_update_identifier:
            self.root.after_cancel(self.video_update_identifier)
            self.video_update_identifier = None
        self.release_video_capture()
        self.video_frame_label.configure(background="black")
        self.video_signal = VIDEO_SIGNAL.PAUSE

    def release_video_capture(self):
        if not self.video_capture:
            return
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.video_capture = None

    def __del__(self):
        self.video_capture_release()
