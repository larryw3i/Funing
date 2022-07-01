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
from funing.path import user_screenshot_dir_path
from funing.settings import *
from funing.settings4t import *


class Widget:
    def __init__(self):
        self.root = Tk()
        pass

    def get_screenheight(self):
        return self.root.winfo_screenheight()
        
    
    def get_screenwidth(self):
        return self.root.winfo_screenwidth()
    