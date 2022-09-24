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


def tk_text_insert(text_widget, content, **kwargs):
    newline = kwargs.get("newline", True)
    font = kwargs.get("font", f"None {kwargs.get('fontsize',12)}")
    justify = kwargs.get("justify", "left")
    foreground = kwargs.get("foreground", None)
    background = kwargs.get("background", None)
    cursor = kwargs.get("cursor", None)

    if newline:
        text_widget.insert("end", "\n")

    _tag = str(uuid.uuid4()).replace("-", "")
    text_widget.insert("end", content, (_tag))
    text_widget.tag_configure(
        _tag,
        font=font,
        justify=justify,
        foreground=foreground,
        background=background,
    )
    if cursor:
        text_widget.tag_bind(
            _tag,
            "<Enter>",
            lambda e, cursor=cursor: text_widget.config(cursor=cursor),
        )
        text_widget.tag_bind(
            _tag, "<Leave>", lambda e: text_widget.config(cursor="")
        )
    return _tag
