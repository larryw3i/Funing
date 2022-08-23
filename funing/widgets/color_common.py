import getopt
import importlib
import math
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
from datetime import datetime, timedelta
from enum import Enum
from functools import partial
from importlib import import_module
from itertools import zip_longest
from multiprocessing import Pipe, Process, Queue
from pathlib import Path
from queue import Queue
from threading import Thread
from tkinter import *
from tkinter import filedialog, messagebox, ttk


class MSG_COLOR(Enum):
    """
    Reference:
        https://getbootstrap.com/docs/5.0/utilities/colors/
    """

    PRIMARY = "#0d6efd"
    SECONDARY = "#6c757d"
    SUCCESS = "#198754"
    INFO = "#0dcaf0"
    WARNING = "#ffc107"
    LIGHT = "#f8f9fa"
    DARK = "#212529"
    pass
