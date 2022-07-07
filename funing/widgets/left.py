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


class LeftWidget(MidWidgetABC):
    def __init__(self, mw):
        super().__init__(mw)

    def get_max_width(self):
        return self.mw.get_sep_x()

    def set_widgets(self):
        super().set_widgets()

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
