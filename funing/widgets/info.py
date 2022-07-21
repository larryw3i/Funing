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
from functools import partial
from importlib import import_module
from itertools import zip_longest
from multiprocessing import Pipe, Process, Queue
from pathlib import Path
from queue import Queue
from threading import Thread
from tkinter import *
from tkinter import ttk

import cv2
from appdirs import user_data_dir
from cv2.data import haarcascades
from cv2.face import EigenFaceRecognizer_create
from pygubu.widgets import simpletooltip
from pygubu.widgets.scrolledframe import ScrolledFrame

from funing.abc import *
from funing.locale import _
from funing.path import *
from funing.settings import *
from funing.settings4t import *
from funing.widgets.abc import *


class InfoWidget(WidgetABC):
    def __init__(self, mw):
        super().__init__(mw)
        self.fw = self.frame_widget = None
        self.set_msg = self.mw.set_msg
        self.info = None
        self.info_ids = None
        self.face_casecade = None
        self.picked_frames = []
        self.picked_frame_labels = []
        self.picked_frame_label_margin = 10
        self.resize_width = None
        self.resize_height = None
        self.info_frames = None
        self.info_text = None
        self.save_button = None
        self.pick_scrolledframe = None
        self.pick_scrolledframe_innerframe = None

    def set_resize_width(self):
        self.resize_width = self.fw.get_resize_width()

    def get_resize_width(self):
        if not self.resize_width:
            self.set_resize_width()
        return self.resize_width

    def set_resize_height(self):
        self.resize_height = self.fw.get_resize_height()

    def get_resize_height(self):
        if not self.resize_height:
            self.set_resize_height()
        return self.resize_height

    def set_face_casecade(self):
        self.face_casecade = self.fw.get_face_casecade()

    def get_face_casecade(self):
        if not self.face_casecade:
            self.set_face_casecade()
        return self.face_casecade

    def get_info(self, id: uuid.UUID = None):
        return self.fw.get_info(id)

    def get_info_ids(self):
        return self.fw.get_info_ids()

    def set_frame_widget(self):
        if not self.mw.frame_widget:
            return
        self.fw = self.frame_widget = self.mw.frame_widget

    def get_info_widget(self):
        return self.fw

    def get_x(self):
        return self.mw.get_sep_x() + self.mw.get_sep_width()

    def get_y(self):
        return 0

    def get_width(self):
        return self.mw.get_width() - self.get_x()

    def get_height(self):
        return self.mw.get_height() - self.mw.get_bottom_height()

    def get_pick_scrolledframe_innerframe_height(self):
        return self.get_resize_height() + self.picked_frame_label_margin

    def set_widgets(self):
        super().set_widgets()
        self.set_frame_widget()
        self.pick_scrolledframe = ScrolledFrame(
            self.root, scrolltype="horizontal"
        )
        self.pick_scrolledframe_innerframe = self.pick_scrolledframe.innerframe
        self.pick_scrolledframe_innerframe.configure(
            height=self.get_pick_scrolledframe_innerframe_height()
        )
        self.info_tip_label = ttk.Label(
            self.root, text=_("Write information in your strict format.")
        )
        self.info_text = tk.Text(self.root)
        self.save_button = ttk.Button(self.root, text=_("Save"))

    def get_frame(self, copy=False):
        return self.fw.get_frame(copy)

    def get_pick_scrolledframe_x(self):
        return self.get_x()

    def get_pick_scrolledframe_y(self):
        return 0

    def get_pick_scrolledframe_width(self):
        return self.get_width()

    def get_pick_scrolledframe_height(self):
        return (
            self.get_y()
            + self.get_resize_height()
            + self.pick_scrolledframe.hsb.winfo_reqheight()
            + self.picked_frame_label_margin
        )

    def get_info_text_x(self):
        return self.get_x()

    def get_info_text_y(self):
        return (
            self.get_pick_scrolledframe_height()
            + self.get_info_tip_label_height()
        )

    def get_info_text_width(self):
        return self.get_width()

    def get_info_text_height(self):
        return (
            self.get_height()
            - self.get_info_text_y()
            - self.get_save_button_height()
        )

    def get_info_tip_label_x(self):
        return self.get_x()

    def get_info_tip_label_y(self):
        return self.get_pick_scrolledframe_height()

    def get_info_tip_label_width(self):
        return self.get_width()

    def get_info_tip_label_height(self):
        return self.info_tip_label.winfo_reqheight()

    def get_save_button_x(self):
        return self.get_x() + int(
            (self.get_width() - self.get_save_button_width()) / 2
        )

    def get_save_button_y(self):
        return self.get_height() - self.get_save_button_height()

    def get_save_button_width(self):
        return self.save_button.winfo_reqwidth()

    def get_save_button_height(self):
        return self.save_button.winfo_reqheight()

    def place(self):
        super().place()
        self.pick_scrolledframe.place(
            x=self.get_pick_scrolledframe_x(),
            y=self.get_pick_scrolledframe_y(),
            width=self.get_pick_scrolledframe_width(),
            height=self.get_pick_scrolledframe_height(),
            anchor="nw",
        )
        self.info_tip_label.place(
            x=self.get_info_tip_label_x(),
            y=self.get_info_tip_label_y(),
            width=self.get_info_tip_label_width(),
            height=self.get_info_tip_label_height(),
        )
        self.info_text.place(
            x=self.get_info_text_x(),
            y=self.get_info_text_y(),
            width=self.get_info_text_width(),
            height=self.get_info_text_height(),
        )
        self.save_button.place(
            x=self.get_save_button_x(),
            y=self.get_save_button_y(),
            width=self.get_save_button_width(),
            height=self.get_save_button_height(),
        )

    def del_picked_frame(self, index, del_label=True):
        if del_label:
            self.picked_frame_labels[index].destroy()
            del self.picked_frame_labels[index]
        del self.picked_frames[index]
        self.set_picked_frame_labels_image()

    def clear_picked_frame_labels(self):
        for l in self.picked_frame_labels:
            l.destroy()
        self.picked_frame_labels = []

    def add_pick_frames(
        self, frames=None, update_label=True, set_info_text=True
    ):
        if not isinstance(frames, list):
            frames = [frames]
        self.picked_frames = frames + self.picked_frames
        if update_label:
            self.set_picked_frame_labels_image(self.picked_frames)

    def get_info_frame(self):
        frame = ttk.Frame(self.info_scrolledframe_innerframe)
        return frame

    def set_info_text(self):
        pass

    def set_picked_frame_labels_image(self, frames=None):
        self.clear_picked_frame_labels()
        if frames is None:
            frames = self.picked_frames
        for f in frames:
            label = ttk.Label(
                self.pick_scrolledframe_innerframe, state="active"
            )
            index = len(self.picked_frame_labels)
            label.bind(
                "<Button-1>",
                lambda event, index=index: self.del_picked_frame(index),
            )
            label.pack(
                side="left",
                anchor="nw",
                padx=self.picked_frame_label_margin / 2,
            )
            simpletooltip.create(label, _("Click to delete."))
            self.set_label_image(f, label)
            self.picked_frame_labels.append(label)

    def set_label_image(self, image, label):
        self.set_label_frame(image, label)

    def set_label_frame(self, frame, label):
        self.fw.set_label_image(frame, label)

    def get_pick_frames(self, frame=None):
        face_casecade = self.get_face_casecade()
        frame = frame or self.get_frame(copy=True)
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_rects = face_casecade.detectMultiScale(gray_img, 1.3, 5)
        frames = []
        for (x, y, w, h) in face_rects:
            pick_frame = frame[y : y + h, x : x + w]
            pick_frame = cv2.resize(
                pick_frame,
                (self.get_resize_width(), self.get_resize_height()),
                interpolation=cv2.INTER_LINEAR,
            )
            frames.append(pick_frame)
        del frame
        del gray_img
        return frames

    def pick_frame_by_default(self):
        frames = self.get_pick_frames()
        self.add_pick_frames(frames)
        pass
