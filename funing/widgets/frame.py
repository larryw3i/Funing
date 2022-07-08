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


class FrameWidget(WidgetABC):
    def __init__(self, mw, text):
        super().__init__(mw)
        self.parent = self.parent_widget = self.mw.left_widget
        self.text = text
        self.label = None
        self.frame_size = 25
        self.video_src = None
        self.image_src = None
        self.openfrom_button = None
        self.detectsrc_button = None

    def start_video(self):
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

    def set_widgets(self):
        self.label = Label(self.root, text=_("Video frame label."))
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
