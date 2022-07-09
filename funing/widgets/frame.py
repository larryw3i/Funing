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


class FrameWidget(TextSubWidgetABC):
    def __init__(self, mid_widget):
        super().__init__(mid_widget)
        self.frame_label = None
        self.frame_size = 25
        self.video_src = None
        self.image_src = None
        self.openfrom_combobox_var = StringVar()
        self.openfrom_Combobox = None
        self.opensrc_button = None
        self.play_button = None
        self.pause_button = None
        self.pick_button = None
        self.recog_button = None
        self.image_exts = ["jpg", "png", "jpeg", "webp"]
        self.video_exts = ["mp4", "avi", "3gp", "webm", "mkv"]

    def play_video(self):
        pass

    def pause_video(self):
        pass

    def show_image(self):
        pass

    def get_frame(self):
        pass

    def get_video_src(self):
        pass

    def set_video_src(self):
        pass

    def get_image_src(self):
        pass

    def set_image_src(self):
        pass

    def set_frame_size(self, frame=25):
        self.frame_size = frame

    def get_frame_size(self):
        return self.frame_size

    def get_max_width(self):
        return self.parent.get_text_width()

    def get_max_height(self):
        return int(self.parent.get_text_height() * 0.8)

    def get_frame_label_x(self):
        pass

    def get_frame_label_y(self):
        pass

    def get_frame_label_width(self):
        pass

    def get_frame_label_height(self):
        pass

    def set_widgets(self):
        if not self.text:
            self.text = self.get_text()

        self.frame_label = Label(self.text, text=_("Video frame label."))
        self.openfrom_combobox = ttk.Combobox(
            self.text, textvariable=self.openfrom_combobox_var
        )

        self.text.window_create("end", window=self.frame_label)
        self.text.window_create("end", window=self.openfrom_combobox)
        pass

    def set_x(self):
        pass

    def get_x(self):
        return self.text.get_x()

    def get_y(self):
        return 0

    def set_y(self):
        pass

    def set_width(self):
        pass

    def get_width(self):
        pass

    def set_height(self):
        pass

    def place(self):
        pass
