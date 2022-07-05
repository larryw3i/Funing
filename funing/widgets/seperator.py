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


class SeperatorWidget(WidgetABC):
    def __init__(self, mw):
        super().__init__(mw)
        self._x_copy_str = "lr_sep_x"
        self._x = self.mw.default_xywh
        self.seperator = None
        self.min_margin = 10

    def seperator_button1_motion_bind(self, event):
        pointerx = self.root.winfo_pointerx()
        if pointerx > (
            self.mw.get_x() + self.mw.get_width() - self.min_margin
        ) or pointerx < (self.root.winfo_rootx() + self.min_margin):
            return
        self.set_x(pointerx - self.mw.get_x())
        pass

    def seperator_button2_bind(self, event):
        self.set_x(self.mw.get_width(of=2))

    def set_widgets(self):
        self.seperator = ttk.Separator(
            self.root, orient="vertical", cursor="sizing"
        )
        self.seperator.bind("<B1-Motion>", self.seperator_button1_motion_bind)
        self.seperator.bind("<Button-3>", self.seperator_button2_bind)

    def get_x(self):
        if self._x == self.mw.default_xywh:
            self._x = self.get_copy(
                self._x_copy_str, None
            ) or self.mw.get_width(of=2)
        return int(self._x)

    def set_x(self, x, update_place=True):
        self._x = int(x)
        if update_place:
            self.place()
        self.set_copy(self._x_copy_str, self._x)

    def get_height(self):
        return self.mw.get_height()

    def get_width(self):
        return 8

    def place(self):
        self.seperator.place(
            x=self.get_x(),
            y=0,
            width=self.get_width(),
            height=self.get_height(),
        )
        pass
