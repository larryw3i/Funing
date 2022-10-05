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
from cv2.face import EigenFaceRecognizer_create

from funing.abc import *
from funing.locale import _
from funing.path import *
from funing.settings import *
from funing.settings4t import *
from funing.widgets.abc import *
from funing.widgets.color_common import *


class BottomWidget(WidgetABC):
    def __init__(self, mw):
        super().__init__(mw)
        self.main_msg_label = None
        self.resize_label = None

    def set_widgets(self):
        self.main_msg_label = ttk.Label(
            self.root, text=_("Hello, Welcome to Funing.")
        )
        self.resize_label = ttk.Label(self.root, text="\u25F0")
        self.resize_label.bind("<Button-1>", self.resize_window)

    def mw_reset_geometry(self):
        self.mw.reset_geometry()
        pass

    def resize_window(self, event):
        self.mw_reset_geometry()
        self.mk_tmsg("Window resized.")
        pass

    def set_x(self):
        pass

    def get_x(self):
        return 0

    def set_y(self):
        pass

    def get_y(self):
        return int(self.mw.get_height() - self.get_height())

    def set_width(self):
        pass

    def get_width(self):
        return self.mw.get_width()

    def set_height(self):
        pass

    def get_height(self):
        return self.main_msg_label.winfo_reqheight()

    def get_mw_height(self):
        return self.mw.get_height()

    def get_mw_width(self):
        return self.mw.get_width()

    def set_msg(self, msg=None, label=None, fg=MSG_COLOR.INFO, bg=None):
        msg = msg or _("Hello!")
        label = label or self.main_msg_label
        fg = fg.value
        bg = bg and bg.value or None
        label.configure(text=msg, foreground=fg, background=bg)

    def get_resize_label_x(self):
        return self.get_width() - self.get_resize_label_width()

    def get_resize_label_y(self):
        return self.get_mw_height() - self.get_resize_label_height()

    def get_resize_label_width(self):
        return self.resize_label.winfo_reqwidth()

    def get_resize_label_height(self):
        return self.resize_label.winfo_reqheight()

    def place(self):
        self.main_msg_label.place(
            x=self.get_x(),
            y=self.get_y(),
            width=self.get_width(),
            height=self.get_height(),
        )
        self.resize_label.place(
            x=self.get_resize_label_x(),
            y=self.get_resize_label_y(),
            width=self.get_resize_label_width(),
            height=self.get_resize_label_height(),
        )
        pass
