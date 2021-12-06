
from funing.ui.about_ui import AboutToplevel
import webbrowser


import gettext
import os
import re
import subprocess
import sys
import time
import tkinter as tk
import tkinter.filedialog as tkf
import uuid
import webbrowser
from datetime import date, datetime
from enum import Enum
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

import cv2
import numpy as np
import pygubu
import yaml
from PIL import Image, ImageTk

from funing import *
from funing._ui import error
from funing.locale import _

translator = _

class About(pygubu.TkApplication):
    def _create_ui(self):

        # pygubu builder
        self.builder = builder = pygubu.Builder(translator)

        # ui files
        about_ui_path = os.path.join(
            os.path.join(project_path, 'ui'), 'about.ui')

        # add ui files
        self.builder.add_from_file(about_ui_path)

        pass



def view_source_code():
    

def about_toplevel(): return AboutToplevel().about_tl
