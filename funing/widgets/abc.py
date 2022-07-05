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

    def palace(self):
        pass

    def set_widgets(self):
        pass
