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
from funing.widgets.about import AboutToplevel
from funing.widgets.common import tk_text_insert


class TopWidget(WidgetABC):
    def __init__(self, mw):
        super().__init__(mw)

        self.abouttoplevel = None

    def set_widgets(self):

        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        self.about_menu = Menu(self.menubar, tearoff=False)
        self.about_menu.add_command(
            label=_("About Funing"), command=self.about_command
        )

        self.menubar.add_cascade(label=_("About"), menu=self.about_menu)

    def place(self):
        pass

    def about_command(self):
        if self.abouttoplevel:
            self.abouttoplevel.ok()
        else:
            self.abouttoplevel = AboutToplevel(self.mw)
