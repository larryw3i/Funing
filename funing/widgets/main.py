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
from funing.hi.common import tk_text_insert
from funing.locale import _
from funing.path import user_screenshot_dir_path
from funing.settings import *
from funing.settings4t import *


class MainWidget:
    def __init__(self, title=None):
        self.root = Tk()
        self._title = title or (_("Funing") + f" ({app_version})")
        self._width = self._height = self.x = self.y = self.default_xywh= 10
        self._geometry = (self._width, self._height, self._x, self._y)
        self._defaut_geometry = self._geometry

    def set_title(self, title=None):
        if not title:
            self._title = title
        self.root.title(self._title)

    def get_geometry(self):
        return self._geometry
    
    def get_width(self):
        return self._width

    def get_height(self):
        return self._height
    
    def get_x(self):
        return self._x
    
    def get_y(self):
        return self._y

    def get_geometry_str(self, geometry=None):
        geometry = geometry or self.get_geometry()
        return f"{geometry[0]}x{geometry[1]}" + f"+{geometry[2]}+{geometry[3]}"

    def set_geometry(self, geometry=None, update_widget=True):
        if not geometry:
            self._geometry = (
                self._width,
                self._height,
                self.x,
                self.y,
            ) = geometry
        if update_widget:
            self.root.geometry(self.get_geometry_str())

    def get_screenheight(self, of = 1):
        return int( self.root.winfo_screenheight()/of)

    def get_screenwidth(self, of = 1):
        return int(self.root.winfo_screenwidth()/of)

    def get_cp(self, key):
        if self.cp == None:
            with open(cp_path, "r") as f:
                self.cp = pickle.load(f)
        return self.cp

    def save_cp(self):
        pass

    def about_command(self):
        if self.abouttoplevel:
            self.abouttoplevel.ok()
        else:
            self.abouttoplevel = AboutToplevel(self)

    def sys_exit(self):
        self.root.destroy()
        sys.exit(0)

    def mainloop(self):
        self.set_title()
        self.set_geometry()

        self.root.mainloop()
