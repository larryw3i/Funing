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
from tkinter import ttk

import cv2
import yaml
from appdirs import user_data_dir
from cv2.data import haarcascades
from cv2.face import EigenFaceRecognizer_create

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
        self.src_frame_label = None
        self.src_frame_size = None
        self.video_src = None
        self.video_frame_fps = None
        self.video_exts = ["mp4", "avi", "3gp", "webm", "mkv"]
        self.video_signal = VIDEO_SIGNAL.PAUSE
        self.image_src = None
        self.image_exts = ["jpg", "png", "jpeg", "webp"]
        self.openfrom_combobox_var = StringVar()
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

    def video_switch_signal(self):
        pass
        

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
    
    def video_refresh_frame(self):
        pass
    
    def video_pause_frame(self):
        pass

    def video_play(self):
        pass

    def video_pause(self):
        pass

    def image_show(self):
        pass

    def get_src_frame(self):
        pass

    def video_get_src(self):
        pass

    def video_set_src(self):
        pass

    def image_get_src(self):
        pass

    def image_set_src(self):
        pass

    def video_set_frame_fps(self, fps=25):
        pass

    def video_set_frame_size(self, size=None):
        self.frame_size = size

    def get_src_frame_size(self):
        return self.src_frame_size

    def get_frame_label_max_width(self):
        return int(self.get_width())

    def get_frame_label_max_height(self):
        return int(self.get_height() * 0.5)

    def get_frame_label_x(self):
        return self.get_x()

    def get_frame_label_y(self):
        return self.get_y()

    def get_frame_label_width(self):
        return self.get_frame_label_max_width()

    def get_frame_label_height(self):
        return self.get_frame_label_max_height()

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

    def set_widgets(self):

        self.frame_label = Label(
            self.root,
            text=_("Video frame."),
            background="black",
            foreground="white",
            justify="center",
        )
        self.openfrom_combobox = ttk.Combobox(
            self.root, textvariable=self.openfrom_combobox_var
        )

        self.opensrc_button = tk.Button(self.root, text=_("Open"))
        self.play_button = tk.Button(self.root, text=_("Play"))
        self.pause_button = tk.Button(self.root, text=_("Pause"))
        self.pick_button = tk.Button(self.root, text=_("Pick"))
        self.recog_button = tk.Button(self.root, text=_("Recognize"))

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
        y = self.get_frame_label_height() + self.get_oper_widgets_margin()
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

        self.frame_label.place(
            x=self.get_frame_label_x(),
            y=self.get_frame_label_y(),
            width=self.get_frame_label_width(),
            height=self.get_frame_label_height(),
        )

        self.oper_widgets_place()
