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
        self.resize_width = 92
        self.resize_height = 112

    def set_face_casecade(self):
        self.face_casecade = self.fw.get_face_casecade()

    def get_face_casecade(self):
        if not self.face_casecade:
            self.set_face_casecade()
        return self.face_casecade

    def set_resize_width(self, width):
        self.resize_width = width

    def set_resize_height(self, height):
        self.resize_height = height

    def get_resize_width(self):
        return self.resize_width

    def get_resize_height(self):
        return self.resize_height

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

    def set_widgets(self):
        super().set_widgets()
        self.set_frame_widget()
        self.pick_scrolledframe = ScrolledFrame(
            self.root, scrolltype="horizontal"
        )
        self.pick_scrolledframe_innerframe = self.pick_scrolledframe.innerframe
        self.info_scrolledframe = ScrolledFrame(
            self.root, scrolltype="vertical"
        )
        self.info_scrolledframe_innerframe = self.info_scrolledframe.innerframe

    def get_frame(self, copy=False):
        return self.fw.get_frame(copy)

    def get_pick_scrolledframe_x(self):
        return self.get_x()

    def get_pick_scrolledframe_y(self):
        return 0

    def get_pick_scrolledframe_width(self):
        return self.get_width()

    def get_pick_scrolledframe_height(self):
        return int(self.get_height() / 2)

    def get_info_scrolledframe_x(self):
        return self.get_x()

    def get_info_scrolledframe_y(self):
        return self.get_pick_scrolledframe_height()

    def get_info_scrolledframe_width(self):
        return self.get_width()

    def get_info_scrolledframe_height(self):
        return self.get_height() - self.get_info_scrolledframe_y()

    def place(self):
        super().place()
        self.pick_scrolledframe.place(
            x=self.get_pick_scrolledframe_x(),
            y=self.get_pick_scrolledframe_y(),
            width=self.get_pick_scrolledframe_width(),
            height=self.get_pick_scrolledframe_height(),
            anchor="nw",
        )
        self.info_scrolledframe.place(
            x=self.get_info_scrolledframe_x(),
            y=self.get_info_scrolledframe_y(),
            width=self.get_info_scrolledframe_width(),
            height=self.get_info_scrolledframe_height(),
            anchor="nw",
        )

    def del_picked_frame(self, index, del_label=True):
        if del_label:
            self.picked_frame_labels[index].place_forget()
            del self.picked_frame_labels[index]
        del self.picked_frames[index]

    def add_pick_frames(self, frames, update_label=True):
        if not isinstance(frames, list):
            frames = [frames]
        self.picked_frames += frames
        self.picked_frame_labels = []
        for f in self.picked_frames:
            label = ttk.Label(self.pick_scrolledframe_innerframe)
            index = len(self.picked_frame_labels)
            label.bind(
                "<Button-1>", lambda event, index: del_picked_frame(index)
            )
            label.place(
                x=self.picked_frame_label_margin
                + index * self.get_resize_width(),
                y=self.get_pick_scrolledframe_y(),
            )
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
