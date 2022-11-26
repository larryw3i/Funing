# Video Frame & Operation Area.
import asyncio
import getopt
import importlib
import math
import os
import pickle
import queue
import random
import re
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import uuid
import webbrowser
from datetime import datetime, timedelta
from enum import Enum
from functools import partial
from importlib import import_module
from itertools import zip_longest
from multiprocessing import Pipe, Process, Queue
from pathlib import Path
from queue import Queue
from threading import Thread
from tkinter import *
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy
import numpy as np
from appdirs import user_data_dir
from cv2.face import EigenFaceRecognizer_create
from PIL import Image, ImageTk
from PIL.Image import fromarray as pil_image_fromarray
from pygubu.widgets.scrolledframe import ScrolledFrame

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
        self.video_refresh_mspf = None
        self.video_black_image = np.zeros(shape=[512, 512, 3], dtype=np.uint8)
        self.video_scale = None
        self.video_scale_label = None
        self.video_file_frame_duration = None
        self.video_file_play_mode_var = IntVar()
        self.video_file_play_pause_frame_index = None
        self.video_file_play_mode_radiobuttons = None
        self.video_capture_mesc = None
        self.video_file_play_mode_radiobuttons_width_list = None
        self.video_file_play_start_time = None
        self.video_file_frame_diff = None
        self.video_scale_passive = True
        self.video_file_play_mode_str = "video_file_play_mode"
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
        self.oper_widgets_pos = None
        self.info = None
        self.info_id = None
        self.info_ids = []
        self.face_recognizer = self.recognizer = None
        self.iw = self.info_widget = None
        self.resize_width = 112
        self.resize_height = self.resize_width
        self.filedialog_initialdir_list = self.file_dialog_initialdir_list = [
            Path.home() / "Videos",
            Path.home() / "Pictures",
            Path.home(),
        ]
        self.picked_frame_label_margin = 10

    def set_info_id(self, _id=None, return_id=False):
        if _id is None:
            return False
        self.info_id = _id
        if return_id:
            return self.info_id
        return True

    def get_info_id(self):
        if not self.info_id:
            return None
        return self.info_id

    def del_info_id(self):
        self.info_id = None

    def get_resize_width(self):
        return self.resize_width

    def set_resize_height(self, height):
        self.resize_height = height

    def get_resize_height(self):
        return self.resize_height

    def set_resize_width(self, width):
        self.resize_width = width

    def set_info_ids(self, info_ids=None, to_none=False, refresh=False):
        if to_none:
            self.info_ids = None
        if refresh:
            self.train_face_recognizer()
        if not info_ids:
            return
        self.info_ids = info_ids

    def get_info_ids(self, refresh=False):
        if not self.info_ids:
            self.train_face_recognizer()
        if refresh:
            self.train_face_recognizer()
        if not self.info_ids:
            return None
        return self.info_ids

    def set_info_widget(self):
        if not self.mw.info_widget:
            print(_("info_widget is None."))
            return
        self.iw = self.info_widget = self.mw.info_widget

    def get_info_widget(self):
        return self.iw

    def set_video_refresh_mspf(self, to_none=False):
        if to_none:
            self.video_refresh_mspf = None
            return
        self.video_refresh_mspf = 1000 / self.get_video_frame_fps()

    def get_video_refresh_mspf(
        self,
    ):
        if not (self.video_capture or self.video_capture.isOpened()):
            return int(1000 / 30)
        if not self.video_refresh_mspf:
            self.set_video_refresh_mspf()
        return self.video_refresh_mspf

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

    def get_info(self, id=None):
        """
        Get information by id.

        Args:
            id (str): The ID of information.

        Returns:
            dict: the keys and values of information.
        """
        return self.get_info_by_default(id)

    def get_info_by_default(self, id=None):
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
        Get informations dataset.
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
        images = []
        info_ids = []
        labels = []
        label = 0
        subdirs = os.listdir(faces_dir_path)
        for subdir in subdirs:
            info_id = subdir
            subpath = os.path.join(faces_dir_path, subdir)
            if os.path.isdir(subpath):
                info_ids.append(info_id)
                for imgpath in get_face_image_path_list(info_id):
                    img = cv2.imread(imgpath, cv2.IMREAD_COLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    images.append(img)
                    labels.append(label)
                label += 1
        if images == []:
            return (None, None, None)
        images = np.asarray(images)
        labels = np.asarray(labels)
        return (images, labels, info_ids)

    def get_info_id_by_frame(self, frame=None):
        if frame is None:
            if self.is_test():
                print("`get_info_id_by_frame.frame` is `None`.")
            return
        label = self.get_label_by_frame(frame)
        if label is None:
            self.set_msg(_("No matching data."))
            return None
        info_id = self.get_info_id_by_label(label)
        if info_id is None:
            self.set_msg(_("Couldn't get `info_id` from specific label."))
            return None
        return info_id

    def get_info_ids_len(self):
        return self.get_info_id_list_len()

    def is_info_ids_none(self):
        info_ids = self.get_info_ids()
        return info_ids is None or len(info_ids) < 1

    def get_info_id_list_len(self):
        return len(self.info_ids)

    def get_id_by_label(self, label=None):
        return self.get_info_id_by_label(label)

    def get_info_id_by_label(self, label=None):
        if label is None:
            print(_("Label is None."))
            return None
        label = label[0]
        return (
            self.info_ids[label] if label < self.get_info_ids_len() else None
        )

    def get_face_recognizer(self):
        return self.get_recognizer()

    def get_recognizer(self):
        if not self.face_recognizer:
            self.set_face_recognizer(train_face_recognizer=False)
        return self.face_recognizer

    def set_face_recognizer(self, train_face_recognizer=False):
        self.set_recognizer(train_face_recognizer)

    def set_recognizer(self, train_face_recognizer=False):
        """
        Set face recognizer
        """
        self.face_recognizer = (
            self.recognizer
        ) = cv2.face.EigenFaceRecognizer_create()
        if train_face_recognizer:
            self.train_face_recognizer()

    def train_face_recognizer(self):
        return self.train_recognizer()

    def train_recognizer(self):
        """
        Train face recognizer.
        """
        (images, labels, info_ids) = self.get_infos_dataset()
        if images is None:
            self.set_msg(_("Dateset doesn't exist."))
            return False
        self.set_msg(_("Train face recognizer."))
        face_recognizer = self.get_face_recognizer()
        self.set_info_ids(info_ids)
        face_recognizer.train(images, labels)
        self.set_msg(_("Finish Training."))
        return True

    def set_face_casecade(self):
        self.set_face_casecade_by_default()

    def set_face_casecade_by_default(self):
        if alternative_cascade_path:
            self.face_casecade = cv2.CascadeClassifier(
                alternative_cascade_path
            )
            msg = _("`%s` used.") % alternative_cascade_path
            self.set_msg(msg)
            self.mk_tmsg(msg)
            return
        try:
            from cv2.data import haarcascades

            hff_xml_path = os.path.join(
                haarcascades, "haarcascade_frontalface_default.xml"
            )
            self.face_casecade = cv2.CascadeClassifier(hff_xml_path)
        except:
            self.mw.set_msg(_("haarcascades data doesn't exist."))
            if messagebox.askyesno(
                _("haarcascades data doesn't exist."),
                _("haarcascades data doesn't exist.")
                + " "
                + _(
                    "Do you want to try to reinstall 'opencv-contrib-python'?"
                ),
            ):
                os.system(
                    "pip3 uninstall -y "
                    + "opencv-contrib-python opencv-python; "
                    + "pip3 install "
                    + "opencv-contrib-python;"
                )
                if messagebox.askyesno(
                    _("Restart Funing?"), _("Do you want to restart Funing?")
                ):
                    self.mw.restart_funing()
                    pass
                pass
            self.release_video_capture()
            self.face_casecade = None
        pass

    def set_src_type(self, src_type=SRC_TYPE.NONE):
        self.src_type = src_type

    def get_src_type(self):
        if not self.src_type:
            self.set_src_type()
        return self.src_type

    def delete_button_place_forget(self):
        self.iw.delete_button_place_forget()

    def clear_saved_info_combobox_content(self):
        self.iw.clear_saved_info_combobox_content()

    def clear_info_widget_area_content(self):
        self.iw.clear_info_widget_area_content()

    def set_action_to_read(self):
        if not self.is_action_read():
            self.set_action(ACTION.READ)

    def set_action_to_pick(self):
        if not self.is_action_pick():
            self.set_action(ACTION.PICK)
            self.delete_button_place_forget()
            self.clear_info_widget_area_content()

    def set_action_to_recog(self):
        if not self.is_action_recog():
            self.set_action(ACTION.RECOG)
            self.delete_button_place_forget()
            self.clear_info_widget_area_content()

    def set_action_to_none(self):
        if not self.is_action_none():
            self.set_action(ACTION.NONE)

    def set_action(self, action=ACTION.NONE, to_none=False):
        if to_none:
            self.action = ACTION.NONE
            return
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
        return self.get_widgets_list_height_center_break(
            self.get_oper_widgets()
        )

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
        self.set_video_capture_msec(to_none=True)
        self.set_video_file_frame_duration(to_none=True)
        self.set_video_frame_fps(to_none=True)
        self.set_video_refresh_mspf(to_none=True)
        self.set_video_frame_count(to_none=True)

    def before_update_camera_video_frame(self):
        pass

    def before_update_video_file_frame(self):
        self.set_video_scale_to(self.get_video_frame_count())
        pass

    def set_video_scale_to(self, to=100):
        self.video_scale.configure(to=int(to))

    def read_video_src(
        self,
        src_path=None,
    ):
        self.del_prev_video_capture_values()
        self.video_signal = VIDEO_SIGNAL.REFRESH
        if self.src_type == SRC_TYPE.VIDEO_FILE:
            self.before_update_video_file_frame()
            self.update_video_frame(
                frame_index=self.get_video_file_play_pause_frame_index()
            )
        if self.src_type == SRC_TYPE.CAMERA:
            self.before_update_camera_video_frame()
            self.update_video_frame()

    def update_widgets_place4file_video(self):
        self.video_scale_area_place()
        self.video_file_play_mode_radiobuttons_place()
        self.oper_widgets_place()

    def update_widgets_place4camera_video(self):
        self.video_scale_area_place_forget()
        self.video_file_play_mode_radiobuttons_place_forget()
        self.oper_widgets_place()

    def play_camera_video(self, src_path=None, check_video_capture=True):
        self.set_video_src_path(src_path)
        self.src_type = SRC_TYPE.CAMERA
        self.update_widgets_place4camera_video()
        self.play_video(src_path, check_video_capture)

    def video_file_play_mode_radiobuttons_place_forget(self):
        for w in self.get_video_file_play_mode_radiobuttons():
            w.place_forget()

    def get_video_file_play_mode(self):
        return self.video_file_play_mode_var.get()

    def set_video_file_play_start_time(self, time=datetime.now()):
        self.video_file_play_start_time = time

    def get_video_file_play_start_time(self):
        if not self.video_file_play_start_time:
            self.set_video_file_play_start_time()
        return self.video_file_play_start_time

    def play_file_video(self, src_path=None, check_video_capture=True):
        self.set_video_src_path(src_path)
        self.update_widgets_place4file_video()
        self.src_type = SRC_TYPE.VIDEO_FILE
        if self.get_video_file_play_mode() == PLAY_MODE.IN_TIME.value:
            pass
        self.play_video(src_path, check_video_capture)

    def play_video(self, src_path=None, check_video_capture=True):
        if check_video_capture:
            self.check_video_capture()
        self.read_video_src(src_path)

    def pause_video(self):
        self.stop_video_frame()
        pass

    def get_frame(self, copy=False):
        frame = (
            self.video_frame
            if not self.video_frame is None
            else self.image
            if not self.image is None
            else None
        )
        if frame is None:
            self.set_msg(_("Video not opened."))
            return None
        if copy:
            return frame.copy()
        return frame

    def update_widgets_place4show_image(self):
        self.oper_widgets_place()
        self.video_scale_area_place_forget()
        self.video_file_play_mode_radiobuttons_place_forget()

    def set_image(self, image):
        self.image = image

    def get_image(self, copy=False, cp=False):
        if self.image is None:
            return None
        return self.image if not (copy and cp) else self.image.copy()

    def show_image(self, src_path=None, resize=True, draw_face_rect=True):
        if src_path:
            self.set_image_src_path(src_path)
            self.update_widgets_place4show_image()
            image = cv2.imread(self.image_src_path)
            # It seems that if the path string is encoded incorrectly
            # , it cannot be read.
            if image is None:
                image = cv2.imdecode(
                    np.fromfile(self.image_src_path, dtype=np.uint8), -1
                )

            if image is None:
                self.set_msg(_("`cv2.imread` gets `None` from %s.") % src_path)
                return
            self.set_image(image)
            image = image.copy()
            if draw_face_rect:
                image = self.draw_face_rect(image)
            if resize:
                image = self.resize_by_image_label_size(image)
            self.update_image_label(image)

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
                if self.is_test():
                    print("`get_labels_by_frame` gets `None`")
                return None
        labels = []
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_rects = self.face_casecade.detectMultiScale(gray_img, 1.3, 5)
        for (x, y, w, h) in face_rects:
            gray_img_0 = gray_img[y : y + h, x : x + w]
            gray_img_0 = cv2.resize(
                gray_img_0,
                (self.resize_width, self.resize_height),
                interpolation=cv2.INTER_LINEAR,
            )
            labels.append(self.recognizer.predict(gray_img_0))
        return labels

    def get_label_by_frame(self, frame=None):
        """
        Get dataset label via frame.
        Args:
            frame (numpy.array): The video or image frame.
        Returns:
            int: The label of dataset.
        """
        if frame is None:
            if self.is_test:
                self.mk_tmsg("`get_label_by_frame.frame` is 'None'.")
            return
        recognizer = self.get_recognizer()
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_img = cv2.resize(
            gray_img,
            (self.resize_width, self.resize_height),
            interpolation=cv2.INTER_LINEAR,
        )
        label = recognizer.predict(gray_img)
        return label

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

    def set_video_frame_index(self, index):
        self.set_video_scale(index)
        self.set_video_file_position(index)

    def get_video_frame_index(self):
        if self.src_type != SRC_TYPE.VIDEO_FILE:
            return
        return self.video_scale.get()

    def get_image_src_path(self):
        return self.image_src_path

    def set_image_src_path(self, src_path):
        self.src_type = SRC_TYPE.IMAGE
        self.video_signal = VIDEO_SIGNAL.NONE
        self.set_video_src_path(to_none=True)
        self.image_src_path = src_path

    def set_video_frame_fps(self, to_none=False):
        if to_none:
            self.video_frame_fps = None
            return
        self.video_frame_fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))

    def get_video_frame_fps(self, default=25):
        if not self.video_capture:
            return default
        elif not self.video_capture.isOpened():
            return default
        if not self.video_frame_fps:
            self.set_video_frame_fps()
        return self.video_frame_fps

    def get_video_frame_fpms(self):
        return self.get_video_frame_fps() / 1000

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
        if not self.video_capture:
            self.get_video_capture()
        self.video_frame_count = self.video_file_frame_count = int(
            self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )

    def get_video_frame_count(self):
        if not self.src_type == SRC_TYPE.VIDEO_FILE:
            return 0
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

    def get_video_scale_x(self):
        return 0

    def get_video_scale_y(self):
        return (
            self.get_video_frame_label_height()
            + self.get_video_file_play_mode_radiobuttons_height()
        )

    def get_video_scale_width(self):
        return self.get_width() - self.get_video_scale_label_width()

    def get_video_scale_height(self, reqheight=True):
        if reqheight:
            return self.video_scale.winfo_reqheight()
        return self.video_scale.winfo_height()

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

    def set_video_capture(self, set_mjpg=False):
        src_path = self.get_video_src_path()
        self.video_capture = cv2.VideoCapture(src_path)
        if not self.video_capture.isOpened():
            self.set_msg(_("Unable to open video source %s.") % src_path)
        if set_mjpg:
            self.video_capture.set(
                cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G")
            )

    def get_video_capture(self):
        if not self.video_capture:
            self.set_video_capture()
        return self.video_capture

    def turnon_camera(self, src_path=0):
        self.play_camera_video(src_path=src_path)

    def set_image_fxfy(self, to_none=False):
        if to_none:
            self.image_fxfy = None
            return
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
        if face_casecade is None:
            return
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

    def resize_by_frame_label_size(self, frame, fxfy=None):
        if not fxfy:
            fxfy = self.get_image_fxfy()
        vid_img = cv2.resize(
            frame,
            (0, 0),
            fx=fxfy,
            fy=fxfy,
        )
        return vid_img

    def update_video_frame_label(self, frame):
        self.update_video_image_label(frame)

    def update_video_image_label(self, image):
        label = self.video_frame_label
        self.set_label_image(image, label)

    def set_label_image(self, image, label):
        vid_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        vid_img = pil_image_fromarray(vid_img)
        imgtk = ImageTk.PhotoImage(image=vid_img)
        label.imgtk = imgtk
        label.configure(image=imgtk)

    def update_image_label(self, image):
        self.update_video_image_label(image)

    def set_msg(self, msg=None):
        self.mw.set_msg(msg, label=None)

    def finished_video_reading_listener(self):
        self.stop_video_frame()
        self.src_type = SRC_TYPE.NONE

    def set_video_capture_msec(self, to_none=False):
        self.set_video_capture_msec_by_frame_index(to_none)

    def set_video_capture_msec_by_frame_index(self, to_none=False):
        if to_none:
            self.video_capture_mesc = None
        if self.src_type != SRC_TYPE.VIDEO_FILE:
            self.video_capture_mesc = 0
            return
        if not self.video_capture:
            self.video_capture_mesc = 0
            return
        pos = self.get_video_position()
        self.video_capture_mesc = pos * 1000 / self.get_video_frame_fps()

    def set_video_capture_msec_by_cv2(self, to_none=False):
        if to_none:
            self.video_capture_mesc = None
        if self.src_type != SRC_TYPE.VIDEO_FILE:
            self.video_capture_mesc = 0
            return
        if not self.video_capture:
            self.video_capture_mesc = 0
            return
        self.video_capture_mesc = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)

    def get_video_capture_msec(self, reset=True):
        if not self.video_capture_mesc:
            self.set_video_capture_msec()
        if reset:
            self.set_video_capture_msec()
        return self.video_capture_mesc

    def set_video_file_frame_duration(self, to_none=False):
        if to_none:
            self.video_file_frame_duration = None
            return
        self.video_file_frame_duration = (
            self.get_video_frame_count() / self.get_video_frame_fps()
        )

    def get_video_file_frame_duration(self, return_str=False, default=0):
        duration = default
        if not self.video_capture:
            pass
        elif self.src_type != SRC_TYPE.VIDEO_FILE:
            pass
        elif not self.video_file_frame_duration:
            self.set_video_file_frame_duration()
        else:
            duration = self.video_file_frame_duration
        if return_str:
            duration = time.localtime(duration)
            duration = time.strftime("%M:%S", duration)
            return duration
        return duration

    def set_video_scale_area(self, set_video_scale=True):
        video_scale_get = self.video_scale.get() + 1
        progress = self.get_video_capture_msec()
        progress = time.localtime(progress / 1000)
        progress = time.strftime("%M:%S", progress)
        if set_video_scale:
            self.set_video_scale(video_scale_get)
        self.video_scale_label.configure(
            text=progress
            + "/"
            + self.get_video_file_frame_duration(return_str=True)
        )

    def set_video_frame(self, frame=None):
        self.video_frame = frame

    def get_video_file_frame_position_intime(self):
        start_time = self.get_video_file_play_start_time()
        timediff = datetime.now() - self.get_video_file_play_start_time()
        msec = timediff.total_seconds() * 1000
        position = (
            self.get_video_position() + self.get_video_frame_fpms() * msec
        )

        return position

    def set_video_file_frame_diff(self, frame_diff=0):
        self.video_file_frame_diff = frame_diff

    def get_video_file_frame_diff(self):
        if not self.video_file_frame_diff:
            self.set_video_file_frame_diff()
        return self.video_file_frame_diff

    def set_video_scale_passive(self, *args):
        self.video_scale_passive = True

    def is_play_file_video_intime(self):
        return self.get_play_file_video_intime()

    def get_play_file_video_intime(self):
        return (
            self.src_type == SRC_TYPE.VIDEO_FILE
            and self.get_video_file_play_mode() == PLAY_MODE.IN_TIME.value
        )

    def get_root_after_ms(self):
        return int(self.get_video_refresh_mspf() / 2)

    def set_video_file_play_pause_frame_index(self, position=None):
        self.video_file_play_pause_frame_index = (
            position or self.get_video_position()
        )

    def get_video_file_play_pause_frame_index(self):
        if not self.video_file_play_pause_frame_index:
            return 0
        return self.video_file_play_pause_frame_index

    def is_play_file_video_everyframe(self):
        return self.get_play_file_video_everyframe()

    def get_play_file_video_everyframe(self):
        return (
            self.src_type == SRC_TYPE.VIDEO_FILE
            and self.get_video_file_play_mode() == PLAY_MODE.EVERY_FRAME.value
        )

    def is_action_read(self):
        return self.get_action() == ACTION.READ

    def is_action_recog(self):
        return self.get_action() == ACTION.RECOG

    def is_action_pick(self):
        return self.get_action() == ACTION.PICK

    def is_action_none(self):
        return self.get_action() == ACTION.NONE

    def update_video_frame(self, frame_index=0):
        time0 = datetime.now()
        video_capture = self.get_video_capture()
        if self.video_signal == VIDEO_SIGNAL.REFRESH:
            if frame_index > 0:  # For video file pausing.
                self.set_video_file_frame_position(frame_index)
            _, frame = video_capture.read()
            if frame is None:
                self.finished_video_reading_listener()
                return
            if self.src_type == SRC_TYPE.VIDEO_FILE:
                self.set_video_scale_area()
                pass
            self.set_video_frame(frame)
            self.show_video_frame()

            if self.is_play_file_video_intime():
                self.set_video_file_frame_position_skip(time0)
            elif self.is_play_file_video_everyframe():
                pass
            else:
                pass

            self.video_update_identifier = self.root.after(
                self.get_root_after_ms(),
                self.update_video_frame,
            )

    def set_video_file_frame_position_skip(self, time0):
        self.set_video_file_frame_position_skip_by_default(time0)

    def set_video_file_frame_position_skip_by_default(self, time0):
        pos = self.get_video_position()
        video_refresh_mspf = self.get_video_refresh_mspf()
        delay_timedelta = datetime.now() - time0
        delay_msec = (
            delay_timedelta.total_seconds() * 1000 + self.get_root_after_ms()
        )
        skip_frame_count = int(delay_msec / video_refresh_mspf)
        self.set_video_file_frame_position(skip_frame_count + pos)

    def filepath_is_video_type(self, path):
        return any(path.endswith(ext) for ext in self.video_exts)

    def filepath_is_image_type(self, path):
        return any(path.endswith(ext) for ext in self.image_exts)

    def get_file_dialog_initialdir_list(self):
        return self.get_filedialog_initialdir_list()

    def get_filedialog_initialdir_list(self):
        for p in self.file_dialog_initialdir_list:
            if not p.exists():
                self.file_dialog_initialdir_list.remove(d)
        return self.file_dialog_initialdir_list

    def get_random_filedialog_initialdir(self):
        initialdir = random.choice(self.get_filedialog_initialdir_list())
        return initialdir

    def get_filedialog_initialdir(self):
        initialdir = self.get_random_filedialog_initialdir()
        return initialdir if isinstance(initialdir, str) else str(initialdir)

    def open_filedialog(self):
        if self.video_signal == VIDEO_SIGNAL.REFRESH:
            self.stop_video_frame()
        src_path = filedialog.askopenfilename(
            initialdir=self.get_filedialog_initialdir(),
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

    def is_play_file_video(self):
        return self.get_play_file_video()

    def get_play_file_video(self):
        return self.src_type == SRC_TYPE.VIDEO_FILE

    def pause_button_command(self):
        self.pause_video_frame()

    def pause_video(self):
        self.pause_video_frame()

    def pause_video_frame(self):
        if self.is_play_file_video():
            self.set_video_file_play_pause_frame_index()
        if self.video_signal == VIDEO_SIGNAL.REFRESH:
            self.stop_video_frame()

    def pick_frame(self):
        self.pick_frame_by_default()
        pass

    def pick_frame_by_default(self):
        self.iw.pick_frame_by_default()
        pass

    def pick_frame_for_add_by_default(self):
        self.iw.pick_frame_for_add_by_default()
        pass

    def pick_button_command(self):
        if self.is_action_recog() or self.is_action_read():
            self.pick_frame_for_add_by_default()
            return
        self.set_action_to_pick()
        self.pick_frame()
        pass

    def recog_frame(self):
        self.recog_frame_by_default()
        pass

    def recog_frame_by_default(self):
        # self.pause_video_frame()
        self.iw.recog_frame_by_default()
        pass

    def recog_button_command(self):
        self.set_action_to_recog()
        self.recog_frame()
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

    def set_video_file_frame_position(self, pos=0):
        self.set_video_position(pos)

    def set_video_frame_position(self, pos=0):
        self.set_video_position(pos)

    def set_video_file_position(self, pos=0):
        if self.src_type != SRC_TYPE.VIDEO_FILE:
            return
        self.set_video_position(pos)

    def get_video_position(self):
        if not self.video_capture:
            return 0
        return self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)

    def set_video_position(self, pos=0, set_video_scale=False):
        if not self.src_type == SRC_TYPE.VIDEO_FILE:
            return
        if not self.video_capture:
            return
        if not self.video_capture.isOpened():
            return
        pos = int(pos)
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, pos)
        if set_video_scale:
            self.set_video_scale(pos)

    def video_scale_bind_buttonrelease_1(self, *args):
        self.set_video_file_position(self.video_scale.get())
        pass

    def video_scale_bind_button_2(self, *args):
        self.set_video_file_position(self.video_scale.get())
        pass

    def video_scale_command(self, *args):
        if self.video_scale_passive:
            self.video_scale_passive = not self.video_scale_passive
            return
        video_scale_get = self.video_scale.get()
        self.set_video_file_frame_diff(
            video_scale_get - self.get_video_file_frame_position_intime()
        )
        self.set_video_file_position(video_scale_get)

    def set_video_file_play_mode_radiobuttons(self, *buttons):
        self.video_file_play_mode_radiobuttons = buttons

    def get_video_file_play_mode_radiobuttons(self, *buttons):
        return self.video_file_play_mode_radiobuttons

    def set_video_file_play_mode_radiobuttons_width_list(self):
        width = 0
        width_list = []
        for radiobutton in radiobuttons:
            pre_width = width + radiobutton.winfo_reqwidth()
            if pre_width > self.get_width():
                width_list.append(width)
                width = 0
            else:
                width = pre_width
        if width != 0:
            width_list.append(width)
        self.video_file_play_mode_radiobuttons_width_list = width_list

    def get_video_file_play_mode_radiobuttons_width_list(self):
        if not self.video_file_play_mode_radiobuttons_width_list:
            self.set_video_file_play_mode_radiobuttons_width_list()
        return self.video_file_play_mode_radiobuttons_width_list

    def get_video_file_play_mode_radiobuttons_x0(self):
        return self.get_x()

    def get_video_file_play_mode_radiobuttons_height(self, reqheight=False):
        return self.get_widgets_list_height_center_break(
            self.get_video_file_play_mode_radiobuttons(), reqheight
        )

    def get_widgets_list_height_center_break(
        self, widgets, parent_width=None, reqheight=False
    ):
        height = 0
        widgets = widgets
        parent_width = parent_width or self.get_width()
        width = sum([w.winfo_reqwidth() for w in widgets])
        if reqheight:
            return max([w.winfo_reqheight() for w in widgets]) * math.ceil(
                width / parent_width
            )
        return max([w.winfo_height() for w in widgets]) * math.ceil(
            width / parent_width
        )

    def get_video_file_play_mode_radiobuttons_y0(self):
        return int(self.get_y() + self.get_video_frame_label_height())

    def video_file_play_mode_radiobuttons_place(self):
        self.widgets_place_center_break(
            self.get_video_file_play_mode_radiobuttons(),
            x0=self.get_video_file_play_mode_radiobuttons_x0(),
            y0=self.get_video_file_play_mode_radiobuttons_y0(),
        )

    def video_file_play_mode_var_trace_w(self, *args):
        video_file_play_mode_var_get = self.video_file_play_mode_var.get()
        self.set_copy(
            self.video_file_play_mode_str, video_file_play_mode_var_get
        )

    def set_widgets(self):
        self.set_info_widget()
        label = ttk.Label(
            self.root,
            text=_("Video frame."),
            justify="center",
            anchor="center",
        )
        self.set_video_image_label(label)

        video_file_play_everyframe_mode = ttk.Radiobutton(
            self.root,
            text=_("Every Frame"),
            variable=self.video_file_play_mode_var,
            value=PLAY_MODE.EVERY_FRAME.value,
        )

        video_file_play_intime_mode = ttk.Radiobutton(
            self.root,
            text=_("In Time"),
            variable=self.video_file_play_mode_var,
            value=PLAY_MODE.IN_TIME.value,
        )
        mode_copy = self.get_copy(self.video_file_play_mode_str)
        self.video_file_play_mode_var.set(
            PLAY_MODE.IN_TIME.value if mode_copy == None else mode_copy
        )
        self.video_file_play_mode_var.trace(
            "w", self.video_file_play_mode_var_trace_w
        )
        self.set_video_file_play_mode_radiobuttons(
            video_file_play_everyframe_mode,
            video_file_play_intime_mode,
        )

        self.openfrom_combobox = ttk.Combobox(
            self.root,
            textvariable=self.openfrom_combobox_var,
            values=self.get_openfrom_combobox_values(),
        )
        self.openfrom_combobox_var.trace(
            "w", self.openfrom_combobox_var_trace_w
        )

        self.video_scale = ttk.Scale(
            self.root, orient="horizontal", command=self.video_scale_command
        )
        self.video_scale_label = ttk.Label(self.root, text="00:00/00:00")

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
        self.pick_scrolledframe_forrecog = ScrolledFrame(
            self.root, scrolltype="horizontal"
        )

    def get_pick_scrolledframe_forrecog(self):
        if self.pick_scrolledframe_forrecog:
            return self.pick_scrolledframe_forrecog
        return None

    def get_pick_scrolledframe_forrecog_width(self):
        return self.get_width()

    def get_pick_scrolledframe_forrecog_height(self):
        return (
            self.get_resize_height()
            + self.pick_scrolledframe_forrecog.hsb.winfo_reqheight()
            + self.picked_frame_label_margin
        )

    def get_pick_scrolledframe_forrecog_x(self):
        return 0

    def get_pick_scrolledframe_forrecog_y(self):
        return self.get_oper_widgets_bottom_y()

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
        return self.get_x()

    def is_play_camera_video(self):
        return self.get_play_camera_video()

    def get_play_camera_video(self):
        return self.src_type == SRC_TYPE.CAMERA

    def get_oper_widgets_y0(self):
        return (
            self.get_video_frame_label_height()
            + self.get_oper_widgets_margin()
            + (
                0
                if self.is_play_camera_video()
                else (
                    self.get_video_scale_height(reqheight=False)
                    + self.get_video_file_play_mode_radiobuttons_height(
                        reqheight=False
                    )
                )
            )
        )

    def set_oper_widgets_pos(self, pos=None):
        self.oper_widgets_pos = pos

    def get_oper_widgets_pos(self):
        return self.oper_widgets_pos

    def get_oper_widgets_bottom_y(self):
        widgets = self.get_oper_widgets()
        last_widget = widgets[-1]
        if last_widget is None:
            return int(self.get_height() / 4)
        (x0, y0), (x1, y1) = self.get_oper_widgets_pos()
        return last_widget.winfo_reqheight() + y1

    def widgets_place_center_break(
        self, widgets, x0=0, y0=0, parent_width=None
    ):
        widgets = widgets
        width = 0
        width_list = []
        parent_width = parent_width or self.get_width()
        for w in widgets:
            pre_width = width + w.winfo_reqwidth()
            if pre_width > parent_width:
                width_list.append(width)
                width = w.winfo_reqwidth()
            else:
                width = pre_width
        if width > 0:
            width_list.append(width)
        x = x0
        y = y0
        x0y0 = (x, y)
        width_index = 0
        min_height = max([w.winfo_reqheight() for w in widgets])
        for w in widgets:
            if x == x0:
                x = x0 + int((parent_width - width_list[width_index]) / 2)
            new_x = x + w.winfo_reqwidth()
            if new_x > parent_width:
                width_index += 1
                x = x0 + int((parent_width - width_list[width_index]) / 2)
                y += min_height
                w.place(x=x, y=y)
                x += w.winfo_reqwidth()
            else:
                w.place(x=x, y=y)
                x = new_x
        x1y1 = (x, y)
        return (x0y0, x1y1)

    def oper_widgets_place(self):
        widgets = self.get_oper_widgets()
        self.oper_widgets_pos = self.widgets_place_center_break(
            widgets,
            x0=self.get_oper_widgets_x0(),
            y0=self.get_oper_widgets_y0(),
        )

    def get_video_scale_label_x(self):
        return (
            self.get_x()
            + self.get_width()
            - self.video_scale_label.winfo_reqwidth()
        )

    def get_video_scale_label_y(self):
        return (
            self.get_video_frame_label_height()
            + self.get_video_file_play_mode_radiobuttons_height()
        )

    def get_video_scale_label_width(self):
        return self.video_scale_label.winfo_reqwidth()

    def get_video_scale_label_height(self):
        return self.video_scale_label.winfo_reqheight()

    def video_scale_area_place_forget(self):
        self.video_scale.place_forget()
        self.video_scale_label.place_forget()

    def video_scale_area_place(self):
        self.video_scale.place(
            x=self.get_video_scale_x(),
            y=self.get_video_scale_y(),
            width=self.get_video_scale_width(),
            height=self.get_video_scale_height(),
        )
        self.video_scale_label.place(
            x=self.get_video_scale_label_x(),
            y=self.get_video_scale_label_y(),
            width=self.get_video_scale_label_width(),
            height=self.get_video_scale_label_height(),
        )

    def place(self):
        self.video_frame_label.place(
            x=self.get_video_frame_label_x(),
            y=self.get_video_frame_label_y(),
            width=self.get_video_frame_label_width(),
            height=self.get_video_frame_label_height(),
        )
        if self.src_type == SRC_TYPE.VIDEO_FILE:
            self.video_scale_area_place()
            self.video_file_play_mode_radiobuttons_place()
        self.oper_widgets_place()
        self.pick_scrolledframe_forrecog.place(
            x=self.get_pick_scrolledframe_forrecog_x(),
            y=self.get_pick_scrolledframe_forrecog_y(),
            width=self.get_pick_scrolledframe_forrecog_width(),
            height=self.get_pick_scrolledframe_forrecog_height(),
        )

        self.set_video_frame_fxfy()
        self.show_video_frame_if_widgets_size_changed()
        if self.face_recognizer is None:
            self.train_recognizer()

    def show_video_frame_if_widgets_size_changed(self):
        if self.video_signal == VIDEO_SIGNAL.PAUSE:
            pass

    def check_video_capture(self):
        self.stop_video_frame()

    def turnoff_video_capture(self):
        self.release_video_capture()

    def close_video_capture(self):
        self.release_video_capture()

    def set_video_scale(self, value=0):
        self.video_scale_passive = True
        self.video_scale.set(value)

    def stop_video_frame(self):
        if self.video_update_identifier:
            self.root.after_cancel(self.video_update_identifier)
            self.video_update_identifier = None
        self.release_video_capture()
        self.video_signal = VIDEO_SIGNAL.PAUSE
        self.set_video_scale(0)

    def release_video_capture(self):
        if not self.video_capture:
            return
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.video_capture = None

    def __del__(self):
        self.release_video_capture()


#
