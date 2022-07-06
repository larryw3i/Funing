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
from funing.widgets.seperator import SeperatorWidget
from funing.widgets.top import TopWidget


class MainWidget:
    def __init__(self, title=None, test=False):
        self.root = Tk()
        self.test = test
        self._title = title or (_("Funing") + f" ({app_version})")
        self._lr_sep_x = (
            self._width
        ) = self._height = self._x = self._y = self.default_xywh = 10
        self._copy = {}
        self.top_widget = TopWidget(self)
        self.sep_widget = SeperatorWidget(self)

    def set_title(self, title=None):
        if title:
            self._title = title
        self.root.title(self._title)

    def set_x(self, x):
        self._x = x

    def set_y(self, y):
        self._y = y

    def set_height(self, height):
        self._height = height

    def set_width(self, width):
        self._width = width

    def get_x(self):
        if self._x == self.default_xywh:
            self._x = self.get_screenwidth(of=4)
        else:
            self._x = self.root.winfo_rootx()
        return self._x

    def get_y(self):
        if self._y == self.default_xywh:
            self._y = self.get_screenheight(of=4)
        else:
            self._x = self.root.winfo_rooty()
        return self._y

    def get_seperator_x(self):
        return self.sep_widget.get_x()

    def get_sep_x(self):
        return self.get_seperator_x()

    def get_geometry(self):
        return (
            self.get_width(),
            self.get_height(),
            self.get_x(),
            self.get_y(),
        )

    def get_width(self, of=1):
        self._width = (
            self.get_screenwidth(of=2)
            if self._width == self.default_xywh
            else self.root.winfo_width()
        )
        return int(self._width / of)

    def get_height(self, of=1):
        self._height = (
            self.get_screenheight(of=2)
            if self._height == self.default_xywh
            else self.root.winfo_height()
        )
        return int(self._height / of)

    def get_geometry_str(self, geometry=None):
        geometry = geometry or self.get_geometry()
        return f"{geometry[0]}x{geometry[1]}" + f"+{geometry[2]}+{geometry[3]}"

    def set_geometry(self, geometry=None, update_widget=True):
        if geometry:
            self._width, self._height, self._x, self._y = geometry
        if update_widget:
            self.root.geometry(self.get_geometry_str())

    def get_screenheight(self, times=1, of=1):
        return int(self.root.winfo_screenheight() * times / of)

    def get_screenwidth(self, times=1, of=1):
        return int(self.root.winfo_screenwidth() * times / of)

    def get_copy(self, key=None, default=None):
        if self._copy == {}:
            with open(copy_path, "rb") as f:
                self._copy = pickle.load(f, encoding="utf-8")

        return (
            self._copy.get(key, None)
            if key
            else default
            if default
            else self._copy
        )

    def save_copy(self):
        with open(copy_path, "wb") as f:
            pickle.dump(self._copy, f)
        if self.test:
            print(_("Copy Saved!"))

    def set_copy(self, key, value, save_now=False):
        if self._copy == None:
            with open(copy_path, "r") as f:
                self._copy = pickle.load(f)
        self._copy[key] = value
        if save_now:
            self.save_copy()

    def sys_exit(self):
        self.root.destroy()
        sys.exit(0)

    def wm_delete_window_protocol(self):
        self.save_copy()
        self.sys_exit()

    def bind(self):
        self.root.bind("<Configure>", self.configure)

    def protocol(self):
        self.root.protocol("WM_DELETE_WINDOW", self.wm_delete_window_protocol)

    def set_widgets(self):
        self.top_widget.set_widgets()
        self.sep_widget.set_widgets()

    def place(self):
        self.top_widget.place()
        self.sep_widget.place()

    def configure(self, event):
        self.place()

    def mainloop(self):
        self.set_title()
        self.set_geometry()
        self.set_widgets()
        self.bind()
        self.protocol()

        self.root.mainloop()
