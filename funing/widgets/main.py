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


class MainWidget:
    def __init__(self, title=None):
        self.root = Tk()
        self._title = title or (_("Funing") + f" ({app_version})")
        self._width = self._height = self._x = self._y = self.default_xywh = 10
        self._copy = {}

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
        return self._x

    def get_y(self):
        if self._y == self.default_xywh:
            self._y = self.get_screenheight(of=4)
        return self._y

    def get_geometry(self):
        return (
            self.get_width(),
            self.get_height(),
            self.get_x(),
            self.get_y(),
        )

    def get_width(self):
        self._width = (
            self.get_screenwidth(of=2)
            if self._width == self.default_xywh
            else self._width
        )
        return self._width

    def get_height(self):
        self._height = (
            self.get_screenheight(of=2)
            if self._height == self.default_xywh
            else self._height
        )
        return self._height

    def get_geometry_str(self, geometry=None):
        geometry = geometry or self.get_geometry()
        return f"{geometry[0]}x{geometry[1]}" + f"+{geometry[2]}+{geometry[3]}"

    def set_geometry(self, geometry=None, update_widget=True):
        if geometry:
            self._width, self._height, self._x, self._y = geometry
        if update_widget:
            self.root.geometry(self.get_geometry_str())

    def get_screenheight(self, of=1):
        return int(self.root.winfo_screenheight() / of)

    def get_screenwidth(self, of=1):
        return int(self.root.winfo_screenwidth() / of)

    def get_copy(self, key):
        if self._copy == None:
            with open(copy_path, "r") as f:
                self._copy = pickle.load(f)
        return self._copy.get(key, None)

    def save_copy(self):

        with open(copy_path, "wb") as f:
            pickle.dump(self._copy, f)

    def set_copy(self, key, value, save_now=False):
        if self._copy == None:
            with open(copy_path, "r") as f:
                self._copy = pickle.load(f)
        self._copy.set(key, value)
        if save_now:
            self.save_copy()

    def about_command(self):
        if self.abouttoplevel:
            self.abouttoplevel.ok()
        else:
            self.abouttoplevel = AboutToplevel(self)

    def sys_exit(self):
        self.root.destroy()
        sys.exit(0)
    
    def wm_delete_window_protocol(self):
        self.save_copy()
        self.sys_exit()
    
    def bind(self):
        self.root.bind("<Configure>",self.configure)
    
    def protocol(self):
        self.root.protocol("WM_DELETE_WINDOW",self.WM_DELETE_WINDOW_protocol)

    def configure(self):
        pass

    def mainloop(self):
        self.set_title()
        self.set_geometry()
        self.bind()
        self.protocol()

        self.root.mainloop()
