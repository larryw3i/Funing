
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
from funing.locale import _
from funing.settings import *

translator = _


class AboutTkApplication(pygubu.TkApplication):
    def __init__(self):
        # pygubu builder
        self.builder = pygubu.Builder(translator)
        # ui files
        about_ui_path = os.path.join(
            os.path.join(project_path, 'ui'), 'about.ui')
        # add ui files
        self.builder.add_from_file(about_ui_path)

        self.mainwindow = None

        self.is_showing = False

    def on_about_ok_btn_clicked(self):
        self.about_ok()

    def about_ok(self):
        self.trigger()

    def quit(self, event=None):
        self.mainwindow.withdraw()
        self.is_showing = False

    def run(self):
        if not self.mainwindow:
            self.mainwindow = self.builder.get_object('about_toplevel')
            self.mainwindow.title(_('About Funing'))
            self.builder.get_object('version_label')['text'] = version
            self.mainwindow.protocol("WM_DELETE_WINDOW", self.on_closing)
            # connect callbacks
            self.builder.connect_callbacks(self)
        else:
            self.mainwindow.deiconify()
        self.is_showing = True

    def on_closing(self):
        self.quit()

    def trigger(self):
        if not self.is_showing:
            self.run()
        else:
            self.quit()

    def view_source_code(self, *args):
        webbrowser.open(source_page)
