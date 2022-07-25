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
from cv2.data import haarcascades
from cv2.face import EigenFaceRecognizer_create

from funing.abc import *
from funing.locale import _
from funing.path import *
from funing.settings import *
from funing.settings4t import *
from funing.widgets.abc import *


class BottomWidget(WidgetABC):
    def __init__(self, mw):
        super().__init__(mw)
        self.main_msg_label = None

    def set_widgets(self):
        self.main_msg_label = ttk.Label(
            self.root, text=_("Hello, Welcome to Funing.")
        )

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

    def set_msg(self, msg=None, label=None):
        msg = msg or _("Hello!")
        label = label or self.main_msg_label
        label.configure(text=msg)

    def place(self):
        self.main_msg_label.place(
            x=self.get_x(),
            y=self.get_y(),
            width=self.get_width(),
            height=self.get_height(),
        )
        pass
