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
import numpy
import numpy as np
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
        self.image_label = self.video_frame_label = None
        self.video_frame_count = self.video_file_frame_count = None
        self.video_src_path = None
        self.video_frame_fps = None
        self.video_frame_size = None
        self.video_exts = ["mp4", "avi", "3gp", "webm", "mkv"]
        self.video_signal = VIDEO_SIGNAL.NONE
        self.video_capture = None
        self.video_update_identifier = None
        self.video_frame = None
        self.video_frame_fxfy = None
        self.video_frame_width = None
        self.video_frame_height = None
        self.video_refresh_time = None
        self.video_black_image = np.zeros(shape=[512, 512, 3], dtype=np.uint8)
        self.video_scrollbar = None
        self.image_src_path = None
        self.image_exts = ["jpg", "png", "jpeg", "webp"]
        self.image_size = None
        self.image = None
        self.image_size = None
        self.image_fxfy = None
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
        self.info = None
        self.info_ids = []
        self.face_recognizer = self.recognizer = None
        self.iw = self.info_widget = None

    def set_info_ids(self, info_ids=None):
        if not info_ids:
            return
        self.info_ids = info_ids

    def get_info_ids(self):
        if not self.info_ids:
            return []
        return self.info_ids

    def set_info_widget(self):
        if not self.mw.info_widget:
            return
        self.iw = self.info_widget = self.mw.info_widget

    def get_info_widget(self):
        return self.iw

    def set_video_refresh_time(self, to_none=False):
        if to_none:
            self.video_refresh_time = None
            return
        self.video_refresh_time = int(1000 / self.get_video_frame_fps())

    def get_video_refresh_time(self):
        if not self.video_refresh_time:
            self.set_video_refresh_time()
        return self.video_refresh_time

    def set_info(self, key=None, value=None, save_now=False, to_none=False):
        """
        Use multiple parameters to set the information.

        Args:
            key (Union[uuid.UUID,str]): the information key.
            value (str): the information value.
            save_now (bool): save information or not.
            to_none (bool): clear information.

        """
        self.set_info_by_default(
            key=None, value=None, save_now=False, to_none=False
        )

    def save_info(self):
        self.set_info(save_now=True)

    def set_info_by_default(
        self, key=None, value=None, save_now=False, to_none=False
    ):
        """
        The default method using multiple parameters to set the information.
        """
        if to_none:
            self.info = None
        if key:
            self.info[key] = value
        if save_now:
            id = self.info.get("id", None)
            if not id:
                return
            cleared_data = self.info.copy()
            del cleared_data["id"]
            info_path = os.path.join(info_dir_path, id + ".pkl")
            with open(info_path, "wb") as f:
                pickle.dump(cleared_data, f)
        pass

    def get_info(self, id: uuid.UUID = None):
        """
        Get information by id.

        Args:
            id (uuid.UUID): The ID of information.

        Returns:
            dict: the keys and values of information.
        """
        return self.get_info_by_default(id)

    def get_info_by_default(self, id: uuid.UUID = None):
        """
        The default method for getting information.
        """
        if not id:
            return
        id = str(id)
        if self.info and id == self.info.get("id", None):
            return self.info
        info_path = os.path.join(info_dir_path, id + ".pkl")
        info = None
        if not os.path.exists(info_path):
            self.set_msg(_("Information of %s doesn't exist."))
            return info
        with open(info_path, "rb") as f:
            self.info = pickle.load(f)
        self.info.set("id", id)
        return self.info

    def get_infos_dataset(self):
        """
        recog_datas_dir:
            id
                face_image
                face_image0
                ...
            id0
                face_image
                face_image0
                ...
            ...
        """
        images = ids = labels = []
        label = 0
        subdirs = os.listdir(faces_dir_path)
        for subdir in subdirs:
            subpath = os.path.join(faces_dir_path, subdir)
            if os.path.isdir(subpath):
                ids.append(subdir)
                for filename in os.listdir(subpath):
                    imgpath = os.path.join(subpath, filename)
                    img = cv2.imread(imgpath, cv2.IMREAD_COLOR)
                    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    images.append(gray_img)
                    labels.append(label)
                label += 1
        if images is None:
            return None
        images = np.asarray(images)
        labels = np.asarray(labels)
        return images, labels, ids

    def get_id_by_label(self, label=None):
        if not label:
            print(_("Label is None."))
            return
        return self.info_ids[label] if label < len(self.info_ids) else None

    def get_face_recognizer(self):
        return self.get_recognizer()

    def get_recognizer(self):
        if not self.face_recognizer:
            self.set_face_recognizer()
            self.train_face_recognizer()
        return self.face_recognizer

    def set_face_recognizer(self):
        self.set_recognizer()

    def set_recognizer(self):
        """
        Set face recognizer
        """
        self.face_recognizer = (
            self.recognizer
        ) = cv2.face.EigenFaceRecognizer_create()

    def train_face_recognizer(self):
        self.train_recognizer()

    def train_recognizer(self):
        """
        Train face recognizer.
        """
        self.set_msg(_("Train face recognizer."))
        infos_dataset = self.get_infos_dataset()
        if not infos_dataset:
            return
        images, labels, ids = infos_dataset
        self.set_info_ids(ids)
        self.face_recognizer.train(images, labels)
        self.set_msg(_("Finish Training."))
        pass

    def set_face_casecade(self):
        self.set_face_casecade_by_default()

    def set_face_casecade_by_default(self):
        hff_xml_path = os.path.join(
            haarcascades, "haarcascade_frontalface_default.xml"
        )
        if not os.path.exists(hff_xml_path):
            self.mw.set_msg(_("haarcascades data doesn't exist."))
            self.release_video_capture()
            return
        self.face_casecade = cv2.CascadeClassifier(hff_xml_path)

    def set_src_type(self, src_type=SRC_TYPE.NONE):
        self.src_type = src_type

    def get_src_type(self):
        if not self.src_type:
            self.set_src_type()
        return self.src_type

    def set_action(self, action=ACTION.NONE):
        self.action = action

    def get_action(self):
        if not self.action:
            self.set_action()
        return self.action

    def set_video_signal(self, video_signal=VIDEO_SIGNAL.NONE):
        self.video_signal = video_signal

    def get_video_signal(self):
        if not self.video_signal:
            self.get_video_signal()
        return self.video_signal

    def get_face_casecade(self):
        return self.get_face_casecade_by_default()

    def get_face_casecade_by_default(self):
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

    def del_prev_video_capture_values(self):
        self.set_video_frame_fxfy(to_none=True)
        self.set_video_frame_width(to_none=True)
        self.set_video_frame_height(to_none=True)

    def read_video_src(
        self,
        src_path=None,
    ):
        self.del_prev_video_capture_values()
        if (not self.video_src_path) or isinstance(src_path, int) or src_path:
            self.set_video_src_path(src_path)
        self.video_signal = VIDEO_SIGNAL.REFRESH
        self.update_video_frame()

    def play_camera_video(self, src_path=None, check_video_capture=True):
        self.src_type = SRC_TYPE.CAMERA
        self.play_video(src_path, check_video_capture)

    def play_file_video(self, src_path=None, check_video_capture=True):
        self.src_type = SRC_TYPE.VIDEO
        self.play_video(src_path, check_video_capture)

    def play_video(self, src_path=None, check_video_capture=True):
        if check_video_capture:
            self.check_video_capture()
        self.read_video_src(src_path)

    def pause_video(self):
        self.stop_video_frame()
        pass

    def get_frame(self):
        return self.video_frame or self.image or None

    def show_image(self, src_path=None, resize=True, draw_face_rect=True):
        if src_path:
            self.set_image_src_path(src_path)
            self.image = cv2.imread(self.image_src_path)
            image = self.image.copy()
            if draw_face_rect:
                image = self.draw_face_rect(image)
            if resize:
                image = self.resize_by_image_label_size(image)
            self.update_video_frame_label(image)

    def set_image_size(self, and_channels=False, to_none=False):
        if to_none:
            self.image_size = None
            return
        if self.image is None:
            return (0, 0)
        self.image_size = (
            self.image.shape if and_channels else self.image.shape[:2]
        )

    def get_labels(self):
        return self.get_labels_by_frame()

    def get_labels_by_frame(self, frame=None):
        if not frame:
            frame = self.get_frame()
            if not frame:
                return
        labels = []
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_rects = self.face_casecade.detectMultiScale(gray_img, 1.3, 5)
        for (x, y, w, h) in face_rects:
            gray_img_0 = gray_img[y : y + h, x : x + w]
            gray_img_0 = cv2.resize(
                gray_img_0, (92, 112), interpolation=cv2.INTER_LINEAR
            )
            labels.append(self.recognizer.predict(gray_img_0))
        return labels

    def get_image_size(self):
        if not self.image_size:
            self.set_image_size()
        return self.image_size

    def get_image_width(self):
        return self.get_image_size()[1]

    def get_image_height(self):
        return self.get_image_size()[0]

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

    def set_video_src_path(self, src_path="0", to_none=False):
        if to_none:
            self.video_src_path = None
            return
        self.video_src_path = (
            src_path is None
            and "0"
            or isinstance(src_path, int)
            and str(src_path)
            or src_path
        )
        self.image_src_path = None

    def get_image_src_path(self):
        return self.image_src_path

    def set_image_src_path(self, src_path):
        self.src_type = SRC_TYPE.IMAGE
        self.video_signal = VIDEO_SIGNAL.NONE
        self.set_video_src_path(to_none=True)
        self.image_src_path = src_path

    def set_video_frame_fps(self, fps=None, to_none=False):
        if to_none:
            self.video_frame_fps = None
            return
        self.video_frame_fps = fps or int(
            self.video_capture.get(cv2.CAP_PROP_FPS)
        )

    def get_video_frame_fps(self, fps=25):
        if not self.video_frame_fps:
            self.set_video_frame_fps()
        return self.video_frame_fps

    def set_video_frame_width(self, to_none=False):
        if to_none:
            self.video_frame_width = None
            return
        self.video_frame_width = self.video_capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )

    def get_video_frame_width(self):
        if self.video_signal == VIDEO_SIGNAL.PAUSE:
            return self.video_frame.shape[1]
        if not self.video_frame_width:
            self.set_video_frame_width()
        return self.video_frame_width

    def set_video_frame_height(self, to_none=False):
        if to_none:
            self.video_frame_height = None
            return
        self.video_frame_height = self.video_capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )

    def get_video_frame_height(self):
        if self.video_signal == VIDEO_SIGNAL.PAUSE:
            return self.video_frame.shape[0]
        if not self.video_frame_height:
            self.set_video_frame_height()
        return self.video_frame_height

    def set_video_frame_count(self, to_none=False):
        if to_none:
            self.video_frame_count = None
            return
        self.video_frame_count = self.video_file_frame_count = int(
            self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )

    def get_video_frame_count(self):
        if not self.src_type == SRC_TYPE.VIDEO_FILE:
            return
        if not self.video_frame_count:
            self.set_video_frame_count()
        return self.video_frame_count

    def get_video_frame_label_max_width(self):
        return int(self.get_width())

    def get_video_frame_label_max_height(self):
        return int(self.get_height() * 0.5)

    def get_video_frame_label_x(self):
        return self.get_x()

    def get_video_frame_label_y(self):
        return self.get_y()

    def get_image_label_width(self):
        return self.get_video_frame_label_width()

    def get_image_label_height(self):
        return self.get_video_frame_label_height()

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

    def get_video_scrollbar_x(self):
        return 0

    def get_video_scrollbar_y(self):
        return self.get_video_frame_label_height()

    def get_video_scrollbar_width(self):
        return self.get_width()

    def get_video_scrollbar_height(self):
        return self.video_scrollbar.winfo_reqheight()

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
            self.set_msg(_("Unable to open video source %s.") % src_path)

    def get_video_capture(self):
        if not self.video_capture:
            self.set_video_capture()
        return self.video_capture

    def turnon_camera(self, src_path=0):
        self.play_camera_video(src_path=src_path)

    def set_image_fxfy(self, to_none=False):
        if to_none:
            self.image_fxfy = None
        if self.image is None:
            return
        image_label_width = self.get_image_label_width()
        image_label_height = self.get_image_label_height()
        image_width = self.get_image_width()
        image_height = self.get_image_height()
        rate = image_label_width / image_label_height
        rate0 = image_width / image_height
        rate1 = rate0 / rate
        self.image_fxfy = (
            image_label_height / image_height
            if rate0 < rate
            else image_label_width / image_width
        )

    def get_image_fxfy(self):
        if not self.image_fxfy:
            self.set_image_fxfy()
        return self.image_fxfy

    def set_video_frame_fxfy(self, to_none=False):
        if to_none:
            self.video_frame_fxfy = None
            return
        if self.video_capture is None:
            return
        if not self.video_capture.isOpened():
            return
        video_frame_label_width = self.get_video_frame_label_width()
        video_frame_label_height = self.get_video_frame_label_height()
        video_frame_width = self.get_video_frame_width()
        video_frame_height = self.get_video_frame_height()
        rate = video_frame_label_width / video_frame_label_height
        rate0 = video_frame_width / video_frame_height
        rate1 = rate0 / rate
        self.video_frame_fxfy = (
            video_frame_label_height / video_frame_height
            if rate0 < rate
            else video_frame_label_width / video_frame_width
        )

    def get_video_frame_fxfy(self):
        if not self.video_frame_fxfy:
            self.set_video_frame_fxfy()
        return self.video_frame_fxfy

    def show_video_frame(self, frame=None, resize=True, draw_face_rect=True):
        frame = frame or self.video_frame.copy()
        if frame is None:
            return
        if draw_face_rect:
            frame = self.draw_face_rect(frame)
        if resize:
            frame = self.resize_by_video_frame_label_size(frame)
        self.update_video_frame_label(frame)

    def draw_face_rect(self, frame):
        return self.draw_rect(frame)

    def draw_rect(self, frame):
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_casecade = self.get_face_casecade()
        rects = face_casecade.detectMultiScale(gray_img, 1.3, 5)
        for (x, y, w, h) in rects:
            frame = cv2.rectangle(
                frame, (x, y), (x + w, y + h), (255, 0, 0), 2
            )
        del rects
        return frame

    def resize_by_video_frame_label_size(self, frame):
        video_frame_fxfy = self.get_video_frame_fxfy()
        return self.resize_by_frame_label_size(frame, video_frame_fxfy)

    def resize_by_image_label_size(self, frame):
        image_fxfy = self.get_image_fxfy()
        return self.resize_by_frame_label_size(frame, image_fxfy)

    def resize_by_frame_label_size(self, frame, fxfy):
        vid_img = cv2.resize(
            frame,
            (0, 0),
            fx=fxfy,
            fy=fxfy,
        )
        return vid_img

    def update_video_frame_label(self, image):
        self.update_video_image_label(image)

    def update_video_image_label(self, image):
        vid_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        vid_img = pil_image_fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        self.video_frame_label.imgtk = imgtk
        self.video_frame_label.configure(image=imgtk)

    def update_image_label(self):
        self.update_video_image_label(image)

    def set_msg(self, msg=None):
        self.mw.set_msg(msg, Label=None)

    def finished_video_reading_listener(self):
        self.stop_video_frame()
        self.src_type = SRC_TYPE.NONE

    def update_video_frame(self):
        video_capture = self.get_video_capture()
        video_refresh_time = self.get_video_refresh_time()
        if self.video_signal == VIDEO_SIGNAL.REFRESH:
            _, frame = video_capture.read()
            if frame is None:
                self.finished_video_reading_listener()
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
            self.play_file_video(src_path=src_path)
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
            self.play_camera_video(src_path=src_path)

    def opensrc_button_command(self):
        src_path = openfrom_combobox_get = self.openfrom_combobox_var.get()
        if self.filepath_is_image_type(src_path):
            self.show_image(src_path)
        elif self.filepath_is_video_type(src_path):
            self.play_video(src_path=src_path)

    def play_button_command(self):
        if self.video_signal != VIDEO_SIGNAL.REFRESH:
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

    def set_video_image_label(self, label=None):
        if not label:
            return
        self.image_label = self.video_frame_label = label

    def set_widgets(self):
        label = Label(
            self.root,
            text=_("Video frame."),
            justify="center",
            anchor="center",
        )
        self.set_video_image_label(label)

        self.openfrom_combobox = ttk.Combobox(
            self.root,
            textvariable=self.openfrom_combobox_var,
            values=self.get_openfrom_combobox_values(),
        )
        self.openfrom_combobox_var.trace(
            "w", self.openfrom_combobox_var_trace_w
        )

        self.video_scrollbar = ttk.Scrollbar(
            self.root,
            cursor="spider",
            orient="horizontal",
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

    def get_oper_widgets_x0(self):
        width_list = self.get_oper_widgets_width_list()
        return int((self.get_width() - width_list[0]) / 2)

    def get_oper_widgets_y0(self):
        return (
            self.get_video_frame_label_height()
            + self.get_oper_widgets_margin()
            + self.get_video_scrollbar_height()
        )

    def oper_widgets_place(self):
        widgets = self.get_oper_widgets()
        width_list = self.get_oper_widgets_width_list()
        width_index = 1
        x = self.get_oper_widgets_x0()
        y = self.get_oper_widgets_y0()
        min_y = self.get_oper_widget_min_height()
        prev_widget = widgets[0]
        prev_widget.place(x=x, y=y)
        for w in widgets[1:]:
            x += prev_widget.winfo_reqwidth() + self.get_oper_widgets_margin()
            if (x + w.winfo_reqwidth()) > self.get_width():
                width_index += 1
                x = int((self.get_width() - width_list[0]) / 2)
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
        self.video_scrollbar.place(
            x=self.get_video_scrollbar_x(),
            y=self.get_video_scrollbar_y(),
            width=self.get_video_scrollbar_width(),
            height=self.get_video_scrollbar_height(),
        )
        self.oper_widgets_place()
        self.set_video_frame_fxfy()

        self.show_video_frame4widgets_size_changed()

    def show_video_frame4widgets_size_changed(self):
        if self.video_signal == VIDEO_SIGNAL.PAUSE:
            pass

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
        self.video_signal = VIDEO_SIGNAL.PAUSE

    def release_video_capture(self):
        if not self.video_capture:
            return
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.video_capture = None

    def __del__(self):
        self.release_video_capture()
