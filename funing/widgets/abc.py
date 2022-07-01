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

from funing.hi.common import tk_text_insert
from funing.locale import _
from funing.path import user_screenshot_dir_path
from funing.settings import *


class WidgetABC(ABC):
    def __init__(self, hf):
        self.hf = hf
        self.root = self.hf.root

    def palace(self):
        pass

    def set_widgets(self):
        pass
