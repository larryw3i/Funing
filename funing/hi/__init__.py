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
from funing.path import *
from funing.settings import *
from funing.settings4t import *


class HiFuning:
    def __init__(self):
        self.root = Tk()
        self.abouttoplevel = None
        self.cp = {}

    def get_screenwidth(self, of=1):
        return int(self.root.winfo_screenwidth() / of)

    def get_screenheight(self, of=1):
        return int(self.root.winfo_screenheight() / of)

    def set_title(self, title=None):
        self.root.title(title or _("Funing"))

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
        self.root.mainloop()
