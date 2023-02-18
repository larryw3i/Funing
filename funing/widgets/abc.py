import asyncio
import getopt
import importlib
import os
import pickle
import platform
import queue
import re
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import uuid
import webbrowser
from abc import ABC
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

from funing.locale import _
from funing.path import *
from funing.settings import *


class WidgetABC(ABC):
    def __init__(self, mw):
        self.mw = mw
        self.root = self.mw.root
        self.get_copy = self.mw.get_copy
        self.set_copy = self.mw.set_copy
        self.get_copies_keys = self.mw.get_copies_keys
        self.copy = self.get_copy()
        self.test = self.mw.test
        self.mk_test_msg = self.mw.mk_test_msg
        self.mk_tmsg = self.mw.mk_tmsg
        self.set_primary_msg = self.mw.set_primary_msg
        self.set_secondary_msg = self.mw.set_primary_msg
        self.set_success_msg = self.mw.set_success_msg
        self.set_info_msg = self.mw.set_info_msg
        self.set_warning_msg = self.mw.set_warning_msg
        self.set_light_msg = self.mw.set_light_msg
        self.set_dark_msg = self.mw.set_dark_msg
        self.width = self.height = self.y = self.x = self.mw.default_xywh

    def is_platform_windows(self):
        return "Windows" in platform.system()

    def is_platform_linux(self):
        return "Linux" in platform.system()

    def set_widgets(self):
        pass

    def is_test(self):
        return self.get_test()

    def get_test(self):
        return self.test

    def set_x(self):
        pass

    def get_x(self):
        pass

    def set_y(self):
        pass

    def get_y(self):
        pass

    def set_width(self):
        pass

    def get_width(self):
        pass

    def set_height(self):
        pass

    def get_height(self):
        pass

    def place(self):
        pass


class MidWidgetABC(WidgetABC):
    def __init__(self, mw):
        super().__init__(mw)
        self.max_width = self.mw.default_xywh

    def set_x(self):
        pass

    def get_x(self):
        pass

    def set_y(self):
        pass

    def get_y(self):
        return 0

    def set_width(self):
        pass

    def get_width(self):
        pass

    def set_height(self):
        pass

    def get_height(self):
        return int(self.mw.get_height() - self.mw.get_bottom_height())

    def set_widgets(self):
        super().set_widgets()

    def place(self):
        pass
