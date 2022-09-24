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
from enum import Enum
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


class SRC_TYPE(Enum):
    VIDEO = VIDEO_FILE = 0
    IMAGE = IMAGE_FILE = 1
    CAMERA = 2
    NONE = 3


class ACTION(Enum):
    PICK = 0
    RECOG = 1
    NONE = 2
    READ = 3


class VIDEO_SIGNAL(Enum):
    REFRESH = UPDATE = 0
    PAUSE = 1
    NONE = 2


class PLAY_MODE(Enum):
    EVERY_FRAME = 0
    IN_TIME = 1


class NEW_INFO_SIGNAL(Enum):
    ADD = 0
    OTHER = 1
