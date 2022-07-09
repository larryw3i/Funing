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
import yaml
from appdirs import user_data_dir
from cv2.data import haarcascades
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
        self.copy = self.get_copy()
        self.test = self.mw.test
        self.width = self.height = self.y = self.x = self.mw.default_xywh

    def set_widgets(self):
        pass

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
        self.text = None

    def get_text_widget(self):
        return self.text

    def get_text(self):
        return self.get_text_widget()

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

    def get_vscrollbar_width(self):
        return int(self.vscrollbar.winfo_reqwidth() * 0.8)

    def get_vscrollbar_height(self):
        return self.get_height()

    def get_vscrollbar_x(self):
        return int(self.get_x() + self.get_text_width())

    def get_vscrollbar_y(self):
        return 0

    def get_text_width(self):
        return int(self.get_width() - self.get_vscrollbar_width())

    def get_text_height(self):
        return self.get_vscrollbar_height()

    def get_text_x(self):
        return int(self.get_x())

    def get_text_y(self):
        return int(self.get_y())

    def set_widgets(self):
        super().set_widgets()
        self.text = tk.Text(self.root)
        self.vscrollbar = Scrollbar(self.root, orient="vertical")

    def place(self):
        self.text.place(
            x=self.get_text_x(),
            y=self.get_text_y(),
            width=self.get_text_width(),
            height=self.get_text_height(),
        )
        self.vscrollbar.place(
            x=self.get_vscrollbar_x(),
            y=self.get_vscrollbar_y(),
            width=self.get_vscrollbar_width(),
            height=self.get_vscrollbar_height(),
        )
        self.vscrollbar.configure(command=self.text.yview)
        self.text.config(yscrollcommand=self.vscrollbar.set)


class TextSubWidgetABC(WidgetABC):
    def __init__(self, mid_widget):
        self.mid_widget = mid_widget
        super().__init__(self.mid_widget.mw)
        self.parent = self.parent_widget = self.mid_widget
        self.text = self.parent.text

    def get_text_widget(self):
        return self.mid_widget.get_text()

    def get_text(self):
        return self.get_text_widget()
