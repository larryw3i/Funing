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
        self._x = self.mw.default_xywh
        self._x_copy_str = "lr_sep_x"
        self.seperator = ttk.Separator(self.root, orient="vertical")

    def get_x(self):
        if self._x == self.mw.default_xywh:
            self._x = self.copy.get(self._x_copy_str, self.mw.get_width(of=2))
        return self._x

    def set_x(self, x):
        self._x = x
        self.place()
        self.mw.set_copy(self._x_copy_str, self._x)

    def place(self):
        self.seperator.place(self.get_x())
        pass

    def set_widgets(self):
        pass
