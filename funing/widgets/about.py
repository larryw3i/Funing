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
from funing.widgets.abc import *
from funing.widgets.common import tk_text_insert


class AboutToplevel:
    def __init__(
        self,
        mw,
        w=None,
        h=None,
        x=None,
        y=None,
        title=None,
        place=True,
        set_text_content=True,
        resizable=(False, False),
        text_spacing1=8,
        text_spacing2=8,
    ):
        self.mw = mw
        self.root = self.mw.root
        self.w = w or self.mw.get_screenwidth(of=4)
        self.h = h or self.mw.get_screenheight(of=4)
        self.x = x or 3 * self.mw.get_screenwidth(of=8)
        self.y = y or 3 * self.mw.get_screenheight(of=8)
        self.withdraw = False
        self.toplevel = tk.Toplevel(self.root)
        self.toplevel.resizable(*resizable)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.ok)
        self.scrollbar = tk.Scrollbar(self.toplevel)
        self.text = tk.Text(
            self.toplevel,
            spacing1=text_spacing1,
            spacing2=text_spacing2,
        )
        self.ok_btn = tk.Button(self.toplevel, text=_("OK"), command=self.ok)

        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)

        self.set_title()
        self.set_geometry()

        if set_text_content:
            self.set_text_content()
        if place:
            self.place()

    def set_title(self, title=None):
        self.toplevel.title(title or _("About Funing"))

    def set_geometry(self, geometry=None):
        self.toplevel.geometry(
            geometry or (f"{self.w}x{self.h}" + f"+{self.x}+{self.y}")
        )

    def get_text_ok_btn_space(self):
        return 8

    def get_text_h(self):
        return self.h - self.get_ok_btn_h() - self.get_text_ok_btn_space()

    def get_ok_btn_x(self):
        return int((self.w - self.get_ok_btn_w()) / 2)

    def get_ok_btn_y(self):
        return self.get_text_h() + self.get_text_ok_btn_space()

    def get_ok_btn_h(self):
        return self.ok_btn.winfo_reqheight()

    def get_ok_btn_w(self):
        return self.ok_btn.winfo_reqwidth()

    def get_scrollbar_w(self):
        return self.scrollbar.winfo_reqwidth()

    def get_text_w(self):
        return self.w - self.get_scrollbar_w()

    def ok(self):
        if self.withdraw:
            self.toplevel.deiconify()
        else:
            self.toplevel.withdraw()
        self.withdraw = not self.withdraw

    def get_text_content_len(self):
        return len(self.text.get("1.0", "end-1c"))

    def default_text_insert(
        self,
        content,
        newline=True,
        font=None,
        justify="center",
        foreground=None,
        background=None,
        cursor=None,
    ):
        return tk_text_insert(
            self.text,
            content,
            newline=newline,
            font=font,
            justify=justify,
            foreground=foreground,
            background=background,
            cursor=cursor,
        )

    def set_text_content(self):

        self.default_text_insert(
            content=app_name_t,
            font="None 18",
        )
        self.default_text_insert(
            content=app_version,
            font="None 10",
        )
        self.default_text_insert(
            content=app_description_t,
            font="None 10",
        )
        app_url_tag = self.default_text_insert(
            content=app_url,
            font="None 10",
            foreground="blue",
            cursor="shuttle",
        )
        self.text.tag_bind(app_url_tag, "<1>", self.open_app_url)

        self.default_text_insert(
            content=_("Author:"), font="None 10", justify="center"
        )

        self.default_text_insert(
            content=app_author[0], font="None 10", justify="center"
        )

        self.default_text_insert(
            content=_("Contributors:"), font="None 10", justify="center"
        )

        for app_contributor in app_contributors[1:]:
            self.default_text_insert(
                content=app_contributor[0], font="None 10", justify="center"
            )

        self.text.config(state="disabled")

    def open_app_url(self, event):
        webbrowser.open(app_url)

    def place(self):
        self.scrollbar.place(
            x=self.get_text_w(), y=0, height=self.get_text_h()
        )
        self.text.place(
            x=0, y=0, width=self.get_text_w(), height=self.get_text_h()
        )
        self.ok_btn.place(y=self.get_ok_btn_y(), x=self.get_ok_btn_x())
