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
from tkinter import filedialog, messagebox, ttk

import cv2
from appdirs import user_data_dir
from cv2.face import EigenFaceRecognizer_create
from pygubu.widgets import simpletooltip
from pygubu.widgets.scrolledframe import ScrolledFrame

from funing.abc import *
from funing.locale import _
from funing.path import *
from funing.settings import *
from funing.settings4t import *
from funing.widgets.abc import *
from funing.widgets.enum import *


class InfoWidget(WidgetABC):
    def __init__(self, mw):
        super().__init__(mw)
        self.fw = self.frame_widget = None
        self.set_msg = self.mw.set_msg
        self.info = None
        self.info_ids = None
        self.info_id = None
        self.face_casecade = None
        self.picked_frames = []
        self.picked_frame_labels = []
        self.picked_frames_for_recog = []
        self.picked_frame_labels_for_recog = []
        self.recog_picked_frame_labels_borderwidth = None
        self.frame_label_margin = 10
        self.picked_frame_label_margin = self.frame_label_margin
        self.resize_width = None
        self.resize_height = None
        self.info_frames = None
        self.info_text = None
        self.save_button = None
        self.pick_scrolledframe = None
        self.pick_scrolledframe_innerframe = None
        self.action = None
        self.saved_info_combobox = None
        self.saved_info_combobox_var = StringVar()
        self.saved_frames_for_active_id = self.saved_frames = None
        self.saved_frame_labels = []
        self.basic_infos = None
        self.new_info_added_signal = (
            self.new_info_signal
        ) = NEW_INFO_SIGNAL.OTHER.value
        self.innerframe_for_recog = frame_labels_innerframe_for_recog = None
        self.current_clicked_label = None
        self.info_template_name = None
        self.info_template_copy_name = "info_template"
        self.info_template_list = None
        self.info_template_var = StringVar()
        self.info_templates_combobox = None
        self.info_template_dir_path = None
        self.info_template_dir_path_copy_name = "info_template_dir"
        self.info_template_file_exts = [".txt"]
        self.open_info_template_dir_str = _("Open Directory")

    def update_info_templates_combobox(self):
        if not self.info_templates_combobox:
            return
        self.info_templates_combobox[
            "values"
        ] = self.get_info_template_list() + [self.open_info_template_dir_str]

        pass

    def get_info_template_dir_path(self):
        if self.info_template_dir_path is None:
            self.set_info_template_dir_path(update_ui=False)
            if (
                self.info_template_dir_path is None
                or self.info_template_dir_path == ()
            ):
                _path = str(Path.home())
                self.set_info_template_dir_path(
                    self.info_template_dir_path_copy_name, _path
                )

        if not os.path.exists(self.info_template_dir_path):
            print(_("Path does not exist."))
            return str(Path.home())
        return self.info_template_dir_path

    def set_info_template_dir_path(self, _dir=None, update_ui=False):
        if _dir == None:
            _dir_copy = self.get_copy(
                key=self.info_template_dir_path_copy_name
            )
            if _dir_copy == None or _dir_copy == ():
                _dir = str(Path.home())
            else:
                if not os.path.exists(_dir_copy):
                    print(_("Path does not exist."))
                    _dir = str(Path.home())
                else:
                    _dir = _dir_copy
        else:
            self.set_copy(self.info_template_dir_path_copy_name, _dir)
        #         _dir = _dir[0] if isinstance(_dir,tuple) else _dir
        self.info_template_dir_path = _dir
        if update_ui:
            self.update_info_templates_combobox()
        pass

    def list_info_templates_dir(self):
        if self.get_info_template_dir_path() is None:
            return None
        listed_contents = os.listdir(self.get_info_template_dir_path())
        listed_contents = [
            f
            for f in listed_contents
            if os.path.isfile(
                os.path.join(self.get_info_template_dir_path(), f)
            )
        ]
        new_listed_contents = []
        for f in listed_contents:
            for e in self.info_template_file_exts:
                if f.lower().endswith(e):
                    new_listed_contents.append(f)
                    break
        listed_contents = None
        return new_listed_contents

    def get_info_template_list(self, _refresh=False):
        if not self.info_template_list or _refresh:
            self.info_template_list = self.list_info_templates_dir()
        if not self.info_template_list:
            return []
        return self.info_template_list

    def update_info_template_list(self):
        self.info_template_list = None
        self.get_info_template_list()

    # def set_info_template_name(self, name=None):
    #    if not name:
    #        return
    #    self.info_template_name = name

    def get_info_template_name(self):
        name = None
        if self.info_template_name:
            return self.info_template_name

        if self.info_template_dir_path_copy_name in self.get_copy_keys():
            name = self.get_copy(self.info_template_dir_path_copy_name)
            if info_template_exists(name):
                return name

        names = self.get_info_template_list()
        if len(names) < 1:
            return None
        name = names[0]
        return name

    def get_info_template_path_by_name(self, name):
        _path = os.path.join(self.get_info_template_dir_path(), name)
        return _path

    def get_info_template_content(self, name=None):
        if not name:
            name = self.get_info_template_name()
            self.mk_tmsg(name)
        if not name:
            return None
        assert not name is None
        template_path = self.get_info_template_path_by_name(name)
        if not os.path.exists(template_path):
            return None

        self.mk_tmsg(f"template_path\t{template_path}")
        content = None
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def set_info_template_name(self, name=None, update_ui=False):
        print(205, name)
        if not name:
            return
        self.set_copy(self.info_template_copy_name, name)
        self.info_template_name = name
        if update_ui:
            self.set_info_text_content_use_template()

    def get_frame_label_margin(self):
        return self.frame_label_margin

    def set_frame_label_margin(self, margin=10):
        self.frame_label_margin = margin

    def show_click(self, x=0, y=0, w=0, h=0, width=0, height=0):
        self.show_current_click_label(
            x=x, y=y, w=w, h=h, width=width, height=height
        )
        pass

    def show_current_click_label(self, x=0, y=0, w=0, h=0, width=0, height=50):
        if self.current_clicked_label is None:
            return
        self.hide_current_click_label()
        w = width if w == 0 else w
        h = height if h == 0 else h
        self.current_clicked_label.place(x=x, y=y, width=w, height=h)
        pass

    def hide_current_click_label(self):
        self.current_clicked_label.place_forget()
        pass

    def del_info_id(self):
        self.fw.del_info_id()

    def get_picked_frame_labels_for_recog_len(self):
        return len(self.picked_frame_labels_for_recog)

    def add_picked_frame_label_for_recog(self, label):
        self.picked_frame_labels_for_recog.append(label)
        pass

    def del_picked_frame_labels_for_recog(self, update_widgets=True):
        if update_widgets:
            for w in self.get_picked_frame_labels_for_recog():
                w.place_forget()
                w.destroy()
        self.picked_frame_labels_for_recog = []

    def update_picked_frame_labels_for_recog_widgets(self):
        self.update_picked_frame_labels_for_recog()

    def update_picked_frame_labels_for_recog(self):
        self.update_frame_labels_for_recog()

    def set_frame_labels_innerframe_for_recog(self, innerframe=None):
        if innerframe is None:
            innerframe = self.pick_scrolledframe_innerframe
        self.frame_labels_innerframe_for_recog = (
            self.innerframe_for_recog
        ) = innerframe
        pass

    def set_frame_labels_innerframe_forrecog(self, innerframe=None):
        if innerframe is None:
            innerframe = self.pick_scrolledframe_innerframe
        self.set_frame_labels_image_use_picked_frames_for_recog(innerframe)
        pass

    def get_frame_labels_innerframe_forrecog(self):
        return self.innerframe_for_recog

    def get_frame_labels_innerframe_for_recog(self):
        return self.get_frame_labels_innerframe_forrecog()

    def del_recogframe_by_index(self, index=None):
        self.del_picked_frame_for_recog_by_index(index)
        pass

    def del_picked_frame_for_recog_by_index(
        self, index=0, update_widgets=True
    ):
        if self.is_test():
            print(
                "index",
                index,
                "picked_frames_for_recog len",
                self.get_picked_frames_for_recog_len(),
            )
        if index < self.get_picked_frames_for_recog_len():
            del self.picked_frames_for_recog[index]
            if update_widgets:
                self.update_frame_labels_for_recog()
            pass
        else:
            print("Out of range.")
        pass

    def update_frame_labels_for_recog_use_video_frame(self, frames=None):
        if self.get_picked_frames_for_recog_len() > 0:
            frames = frames + self.picked_frames_for_recog
        if frames is not None:
            self.update_frame_labels_for_recog(frames)
            self.set_picked_frames_for_recog(frames)
        else:
            self.set_msg(_("Nothing picked."))
            if self.is_test():
                print(_("Picked frame is None."))
        pass

    def update_frame_labels_for_recog(self, frames=None):
        if not frames:
            frames = self.picked_frames_for_recog
        self.clear_picked_frame_labels_for_recog()
        if frames == None:
            self.mk_tmsg("frames is None.")
            return
        index = 0
        for f in frames:
            label = ttk.Label(self.get_frame_labels_innerframe_forrecog())
            self.set_label_image(f, label)
            label.bind(
                "<Button-1>",
                lambda event, idx=index: self.recog_frame_by_index(idx),
            )
            label.bind(
                "<Button-3>",
                lambda event, idx=index: self.del_recogframe_by_index(idx),
            )
            label.pack(
                side="left",
                anchor="nw",
                padx=self.picked_frame_label_margin / 2,
            )
            simpletooltip.create(
                label,
                _("Click to recognize,") + _("right click to delete."),
            )
            self.add_picked_frame_label_for_recog(label)
            index += 1
        # self.set_picked_frames_without_update_widgets(frames)

    def set_picked_frames_for_recog(self, frames=None):
        if frames is None:
            return

        self.picked_frames_for_recog = frames

    def get_fw_pick_scrolledframe(self):
        return self.get_fw_pick_scrolledframe_forrecog()

    def get_fw_pick_scrolledframe_forrecog(self):
        scrolledframe = self.fw.get_pick_scrolledframe_forrecog()
        return scrolledframe

    def del_picked_frames_for_recog_deprecated(
        self, update_widgets=True, update_label_list=True
    ):
        self.picked_frames_for_recog = []
        if update_label_list:
            self.del_picked_frame_labels_for_recog(update_widgets)
        pass

    def add_picked_frame_for_recog(self, frame):
        self.picked_frames_for_recog.append(frame)
        pass

    def add_picked_frames_for_recog(self, frames, del_prev=False):

        assert isinstance(frames, list)
        if not isinstance(frames, list):
            self.mk_tmsg("`add_picked_frames_for_recog.frames` is `None`.")
            return
        if del_prev:
            self.del_picked_frames_for_recog()
        self.picked_frames_for_recog += frames

    def set_new_info_signal(self, signal=NEW_INFO_SIGNAL.OTHER.value):
        self.new_info_added_signal = self.new_info_signal = signal

    def get_new_info_signal(self):
        return self.new_info_signal

    def switch_new_info_signal_by_default(self):
        if self.new_info_added_signal == NEW_INFO_SIGNAL.ADD.value:
            self.new_info_added_signal = (
                self.new_info_signal
            ) = NEW_INFO_SIGNAL.OTHER.value
        else:
            self.new_info_added_signal = (
                self.new_info_signal
            ) = NEW_INFO_SIGNAL.ADD.value

    def new_info_signal_is_add(self):
        return self.new_info_signal == NEW_INFO_SIGNAL.ADD.value

    def new_info_signal_is_other(self):
        return self.new_info_signal == NEW_INFO_SIGNAL.OTHER.value

    def get_saved_frames_for_active_id(self):
        return self.get_saved_frames()

    def get_saved_frames(self):
        if self.saved_frames is None:
            info_id = self.get_info_id()
            if info_id is None:
                return None
            return self.get_saved_frames_by_id()
        return self.saved_frames

    def set_saved_frames_for_active_id(self, frames=None, to_none=False):
        self.set_saved_frames(frames, to_none)

    def set_saved_frames_with_frame_id(self, frames=None, to_none=False):
        self.set_saved_frames(frames, to_none)

    def set_saved_frames(
        self, frames=None, to_none=False, update_widgets=False
    ):
        if to_none:
            self.saved_frames = None
        if frames is None:
            return
        self.saved_frames = self.saved_frames_for_active_id = frames

        if update_widgets:
            pass

    def set_action(self, action=ACTION.NONE, to_none=False):
        self.fw.set_action(action, to_none)

    def get_picked_frame_labels_for_recog(self):
        return self.picked_frame_labels_for_recog

    def clear_picked_frame_labels_for_recog(self):
        self.del_picked_frame_labels_for_recog()
        pass

    def clear_all_frame_labels(self):
        self.clear_picked_frame_labels()
        self.clear_saved_frame_labels()
        self.clear_picked_frame_labels_for_recog()

    def del_saved_frames(self, update_widgets=True):
        if update_widgets:
            self.clear_saved_frame_labels()
        self.saved_frames = []
        pass

    def del_picked_frames(self, update_widgets=True):
        if update_widgets:
            self.clear_picked_frame_labels()
        self.picked_frames = []
        pass

    def del_picked_frames_for_recog(self, update_widgets=True):
        if update_widgets:
            self.clear_picked_frame_labels_for_recog()
        self.picked_frames_for_recog = []
        pass

    def del_info_frames(self):
        self.info_frames = None
        pass

    def del_all_frames(self):
        self.del_picked_frames()
        self.del_saved_frames()
        self.del_picked_frames_for_recog()
        pass

    def del_picked_frames_recog_included(self):
        self.del_picked_frames_for_recog()
        self.del_picked_frames()

    def set_action_to_none(self):
        self.del_picked_frames_recog_included()
        self.set_action(ACTION.NONE)

    def set_action_to_read(self):
        if not self.is_action_read():
            # self.del_picked_frames_for_recog()
            self.delete_button_place()
            self.set_action(ACTION.READ)
            self.place_forget_info_templates_combobox()
            pass

    def set_action_to_pick(self):
        if not self.is_action_pick():
            self.del_picked_frames()
            # self.del_picked_frames_for_recog()
            self.set_action(ACTION.PICK)

    def set_action_to_recog(self):
        if not self.is_action_recog():
            self.del_picked_frames()
            self.set_action(ACTION.RECOG)
            self.place_forget_info_templates_combobox()

    def get_action(self):
        return self.fw.get_action()

    def get_info_id(self):
        if not self.info_id:
            self.info_id = self.fw.get_info_id()
        return self.info_id

    def del_info_id(self):
        self.fw.del_info_id()
        self.info_id = None

    def set_info_id(self, _id):
        self.fw.set_info_id(_id=_id)
        self.info_id = _id

    def set_info_ids(self, info_ids=None, to_none=False, refresh=False):
        return self.fw.set_info_ids(info_ids, to_none, refresh)

    def get_info_ids(self, refresh=False):
        return self.fw.get_info_ids(refresh)

    def set_resize_width(self):
        self.resize_width = self.fw.get_resize_width()

    def get_resize_width(self):
        if not self.resize_width:
            self.set_resize_width()
        return self.resize_width

    def set_resize_height(self):
        self.resize_height = self.fw.get_resize_height()

    def get_resize_height(self):
        if not self.resize_height:
            self.set_resize_height()
        return self.resize_height

    def set_face_casecade(self):
        self.face_casecade = self.fw.get_face_casecade()

    def get_face_casecade(self):
        if not self.face_casecade:
            self.set_face_casecade()
        return self.face_casecade

    def get_info(self, id: uuid.UUID = None):
        return self.fw.get_info(id)

    def set_frame_widget(self):
        if not self.mw.frame_widget:
            return
        self.fw = self.frame_widget = self.mw.frame_widget

    def get_info_widget(self):
        return self.fw

    def get_x(self):
        return self.mw.get_sep_x() + self.mw.get_sep_width()

    def get_y(self):
        return 0

    def get_width(self):
        return self.mw.get_width() - self.get_x()

    def get_height(self):
        return self.mw.get_height() - self.mw.get_bottom_height()

    def get_pick_scrolledframe_innerframe_height(self):
        return self.get_resize_height() + self.picked_frame_label_margin

    def get_basic_info_entry_content(self):
        return self.basic_info_entry.get()

    def get_info_text_content(self):
        return self.info_text.get(1.0, "end-1c")

    def save_information(
        self,
        info_id=None,
        save_basic_info=True,
        save_info=True,
        save_image=True,
        refresh=True,
        update_widgets=True,
    ):

        if not self.is_action_read() and len(self.picked_frames) < 1:
            self.set_msg(_("Nothing picked."))
            return
        basic_info_entry_get = self.get_basic_info_entry_content()
        info_text_get = self.get_info_text_content()
        info_id = info_id or self.get_info_id() or str(uuid.uuid4())

        if not self.get_info_id():
            self.set_info_id(_id=info_id)

        if save_basic_info:
            with open(get_basic_info_path(info_id), "w") as f:
                f.write(basic_info_entry_get)
        if save_info:
            with open(get_info_path(info_id), "w") as f:
                f.write(info_text_get)
        if save_image:
            for f in self.picked_frames:
                cv2.imwrite(get_new_random_face_image_path(info_id), f)
        if refresh:
            self.set_info_ids(refresh=True)
            self.update_saved_info_combobox_values()
        if update_widgets:
            self.set_action_to_read()  # First `read` after adding.
            self.set_picked_frames(to_none=True)
            self.clear_picked_frame_labels()
            self.clear_saved_frame_labels()
            self.set_saved_info_combobox_content_by_info_id(info_id)
            self.update_widgets_by_info_id()
            pass

        self.set_msg(_("Information saved."))
        pass

    def set_msg(self, text=""):
        self.fw.set_msg(text)

    def save_button_command(self):
        self.save_information()
        pass

    def is_action_read(self):
        return self.fw.is_action_read()

    def is_action_recog(self):
        return self.fw.is_action_recog()

    def is_action_pick(self):
        return self.fw.is_action_none()

    def is_action_none(self):
        return self.fw.is_action_none()

    def get_picked_frames(self, from_frame=False, info_id=None):
        if from_frame:
            return self.get_picked_frames_from_frame()
        if info_id is not None:
            return self.get_saved_frames_by_id(info_id)
        if self.picked_frames == []:
            return None
        return self.picked_frames

    def set_picked_frames_without_update_widgets(self, frames=None):
        self.set_picked_frames(frames, update_label=False)

    def set_picked_frames(self, frames=None, to_none=False, update_label=True):
        if to_none:
            self.picked_frames = []
            return
        if frames is None:
            self.picked_frames = []
            return
        if not isinstance(frames, list):
            frames = [frames]
        self.picked_frames = frames

        if update_label:
            self.update_picked_frame_labels()

    def get_saved_frames_by_info_id(self, info_id=None, set_self=True):
        return self.get_saved_frames_by_id(info_id, set_self)

    def get_saved_frame_id_by_frame_path(self, frame_path=None):
        if frame_path is None:
            return None
        frame_id = frame_path.split(os.sep)[-1]
        frame_id = frame_id.split(".")[0]
        if self.is_test():
            print("frame_id", frame_id)
        return frame_id

    def set_saved_frames_by_info_id(self, info_id=None, update_widgets=True):
        info_id = info_id or self.get_info_id()
        assert info_id is not None
        if info_id is None:
            self.mk_tmsg("`set_saved_frames_by_info_id.info_id` is None.")
            return
        image_path_list = get_face_image_path_list(info_id)
        saved_frames = []
        for p in image_path_list:
            image = cv2.imread(p, cv2.IMREAD_COLOR)
            saved_frames.append(
                (self.get_saved_frame_id_by_frame_path(p), image)
            )
        self.set_saved_frames(saved_frames)
        if update_widgets:
            pass

    def get_saved_frames_by_id(self, info_id=None, set_self=True):

        info_id = info_id or self.get_info_id()
        if info_id is None:
            if self.is_test():
                print(_("info ID is None."))
            return None
        image_path_list = get_face_image_path_list(info_id)
        saved_frames = []
        for p in image_path_list:
            image = cv2.imread(p, cv2.IMREAD_COLOR)
            saved_frames.append(
                (self.get_saved_frame_id_by_frame_path(p), image)
            )
        if set_self:
            self.set_saved_frames(saved_frames)
        return saved_frames

    def set_infos_and_images_by_id(
        self, info_id=None, set_picked_frames=True, update_widgets=True
    ):
        info_id = info_id or self.get_info_id()
        if info_id is None:
            if self.is_test():
                print("set_infos_and_images_by_id: `info_id` is None.")
            return
        basic_info_path = get_basic_info_path(info_id)
        info_path = get_info_path(info_id)
        basic_info = None
        info = None
        with open(basic_info_path, "r") as f:
            basic_info = f.read()
        with open(info_path, "r") as f:
            info = f.read()
        self.get_saved_frames_by_id(info_id)
        if update_widgets:
            self.set_frame_labels_image()
            self.set_basic_info_entry_content(basic_info)
            self.set_info_text_content(info)
            pass

    def update_infos_widgets_by_info_id(self, info_id=None):
        info_id = info_id or self.get_info_id()
        assert info_id is not None
        if info_id is None:
            self.mk_tmsg("`update_infos_widgets_by_info_id.info_id` is None.")
            return
        basic_info_path = get_basic_info_path(info_id)
        info_path = get_info_path(info_id)
        basic_info = None
        info = None
        with open(basic_info_path, "r") as f:
            basic_info = f.read()
        with open(info_path, "r") as f:
            info = f.read()
        self.set_saved_frames_by_info_id(info_id)
        self.set_basic_info_entry_content(basic_info)
        self.set_info_text_content(info)
        pass

    def clear_info_widgets_content(self):
        self.del_info_widgets_content()
        pass

    def del_info_widgets_content(self):
        self.set_basic_info_entry_content(to_none=True)
        self.set_info_text_content(to_none=True)
        pass

    def set_basic_info_entry_content(self, content=None, to_none=False):
        if content is None or to_none:
            self.basic_info_entry.delete("0", "end")
            return
        self.basic_info_entry.delete("0", "end")
        self.basic_info_entry.insert("end", content)

    def set_info_text_content(self, content=None, to_none=False):
        if content is None or to_none:
            self.info_text.delete("1.0", "end")
            return
        self.info_text.delete("1.0", "end")
        self.info_text.insert("end", content)

    def get_id_by_saved_info_combobox_var(self, var_get=None):
        if var_get is None:
            return None
        if "(" not in var_get:
            return None
        var_get = var_get.split("(")[-1]
        if ")" not in var_get:
            return None
        info_id = var_get.split(")")[0]
        return info_id

    def saved_info_combobox_var_trace_w(self, *args):
        self.update_widgets_by_info_id()
        pass

    def set_adding_status(self):
        self.set_action_to_pick()
        self.del_info_id()
        # self.del_picked_frames_for_recog()
        self.del_saved_frames()
        self.del_picked_frames()
        self.clear_info_widget_area_content()
        self.place_info_templates_combobox()
        self.set_info_text_content_use_template()

    def update_widgets_by_info_id(self, info_id=None):
        self.clear_picked_frame_labels()
        self.clear_saved_frame_labels()
        self.set_saved_frames(to_none=True)
        self.set_picked_frames(to_none=True)
        var_get = self.saved_info_combobox_var.get()
        info_id = info_id or self.get_id_by_saved_info_combobox_var(var_get)
        if info_id is None:
            if self.is_test():
                print(var_get, info_id)
            return
        if info_id == _("Add"):
            self.set_adding_status()
            return
        self.set_info_id(info_id)
        self.set_infos_and_images_by_id()
        self.set_action_to_read()

        pass

    def update_widgets_by_info_id_for_recog(self, info_id=None):
        if info_id is None:
            if self.is_test():
                print(
                    "`update_widgets_by_info_id_for_recog.info_id` is `None`."
                )
            return
        self.set_info_id(info_id)
        self.update_infos_widgets_by_info_id()
        self.set_saved_info_combobox_content_by_info_id()
        pass

    def set_basic_infos(self, refresh=False, to_none=False):
        if to_none:
            self.basic_infos = None
            return
        info_ids = self.get_info_ids()
        if info_ids is None:
            self.set_msg(_("Information IDs is None."))
            return
        basic_infos = []
        for i in info_ids:
            if os.path.exists(get_basic_info_path(i)):
                with open(get_basic_info_path(i), "r") as f:
                    basic_infos.append((i, f.read()))
        self.basic_infos = basic_infos

    def get_basic_infos(self):
        """
        Returns:
            list: [(id, info),(id0, info0),...]
        """
        if self.basic_infos is None:
            self.set_basic_infos()
        if self.basic_infos == []:
            return None
        return self.basic_infos

    def get_saved_info_combobox_values(self):
        basic_infos = self.get_basic_infos()
        if basic_infos is None:
            return []
        combobox_values = [info + "(" + _id + ")" for _id, info in basic_infos]
        combobox_values += [_("New information") + "(" + _("_Add") + ")"]
        return combobox_values

    def update_saved_info_combobox_values(self):
        self.set_basic_infos()
        self.saved_info_combobox.configure(
            values=self.get_saved_info_combobox_values()
        )

    def clear_info_widget_area_content(self):
        self.clear_saved_info_combobox_content()
        self.clear_picked_frame_labels()
        self.set_basic_info_entry_content("")
        self.set_info_text_content("")

    def clear_saved_info_combobox_content(self):
        self.del_saved_info_combobox_content()

    def del_saved_info_combobox_content(self):
        self.saved_info_combobox.set("")
        pass

    def set_saved_info_combobox_content_by_info_id(self, info_id=None):
        info_id = info_id or self.get_info_id()
        if not info_id:
            return
        values = self.get_saved_info_combobox_values()
        id_str = f"({info_id})"
        content = [c for c in values if c.endswith(id_str)][0]
        self.saved_info_combobox.set(content)
        pass

    def clear_showed_info(self):
        self.clear_info_widget_area_content()
        pass

    def get_basic_info_by_info_id(self, info_id=None):
        info_id = info_id or self.get_info_id()
        basic_info = None
        basic_info_path = get_basic_info_path(info_id)
        with open(basic_info_path, "r") as f:
            basic_info = f.read()
        return basic_info

    def get_info_by_info_id(self, info_id=None):
        info_id = info_id or self.get_info_id()
        info = None
        info_path = get_info_path(info_id)
        with open(info_path, "r") as f:
            info = f.read()
        return info

    def del_saved_info_by_info_id(self, info_id=None):
        info_id = info_id or self.get_info_id()
        if not info_id:
            if self.is_test():
                print(_("'info_id' is None."))
            return
        basic_info_path = get_basic_info_path(info_id)
        info_path = get_info_path(info_id)
        image_dir_path = get_image_dir_path(info_id)
        basic_info = self.get_basic_info_by_info_id(info_id)
        deleted_paths = [basic_info_path, info_path, image_dir_path]
        for src in deleted_paths:
            if os.path.exists(src):
                shutil.move(src, get_new_backup_path())
        self.set_basic_infos(to_none=True)
        self.update_saved_info_combobox_values()
        self.clear_showed_info()
        self.set_msg(
            _("Information of %(basic_info)s (%(info_id)s) is deleted.")
            % ({"basic_info": basic_info, "info_id": info_id})
        )
        pass

    def delete_button_command(self):
        if not self.is_action_read():
            if self.is_test():
                print(_("ACTION isn't 'READ'."))
            return
        self.del_saved_info_by_info_id()
        pass

    def add_button_command(self):
        self.set_adding_status()
        self.fw.play_button_command()
        pass

    def get_info_template_values(self):
        template_names = self.get_info_template_list()
        # template_names = [ Path(n).stem for n in template_names ]
        template_names += [self.open_info_template_dir_str]
        return template_names

    def get_info_templates_combobox_x(self):
        return self.get_x()

    def get_info_templates_combobox_y(self):
        return self.get_save_button_y()

    def get_info_templates_combobox_width(self):
        return int((self.get_save_button_x() - self.get_x()) * 0.7)

    def get_info_templates_combobox_height(self):
        return self.info_templates_combobox.winfo_reqheight()

    def place_info_templates_combobox(self):
        if not self.info_templates_combobox:
            return
        self.info_templates_combobox.place(
            x=self.get_info_templates_combobox_x(),
            y=self.get_info_templates_combobox_y(),
            width=self.get_info_templates_combobox_width(),
            height=self.get_info_templates_combobox_height(),
        )
        pass

    def place_forget_info_templates_combobox(self):
        if not self.info_templates_combobox:
            return
        self.info_templates_combobox.place_forget()
        pass

    def open_dir(self, dist="~"):
        _open = (
            sys.platform == "darwin"
            and "open"
            or sys.platform == "win32"
            and "explorer"
            or "xdg-open"
        )
        subprocess.Popen([_open, dist])
        pass

    def info_template_exists(self, name):
        _exist = os.path.exists(
            os.path.join(self.get_info_template_dir_path(), name)
        )
        return _exist

    def info_template_var_trace_w(self, *args):
        info_template_name = self.info_template_var.get()
        # self.mk_tmsg(f"info_template_name\t{info_template_name}")
        if info_template_name == self.open_info_template_dir_str:
            # self.open_dir(get_info_templates_path())
            _path = filedialog.askdirectory(
                parent=self.root,
                title=_("Select a template directory."),
                initialdir=str(Path.home()),
                mustexist=True,
            )
            if _path is None:
                return
            self.set_copy(self.info_template_dir_path_copy_name, _path)
            self.set_info_template_dir_path(_dir=_path, update_ui=True)
            return

        if not self.info_template_exists(info_template_name):
            self.update_info_template_list()
            return
        self.set_info_template_name(name=info_template_name, update_ui=True)
        # self.set_info_text_content_use_template()
        pass

    def set_widgets(self):
        super().set_widgets()
        self.set_frame_widget()

        self.current_clicked_label = ttk.Label(self.root, background="blue")

        self.saved_info_combobox = ttk.Combobox(
            self.root,
            textvariable=self.saved_info_combobox_var,
            values=self.get_saved_info_combobox_values(),
            justify="center",
        )
        self.saved_info_combobox_var.trace(
            "w", self.saved_info_combobox_var_trace_w
        )
        self.add_button = tk.Button(
            self.root,
            text=_("Add"),
            command=self.add_button_command,
            background=self.get_add_button_background(),
        )

        self.pick_scrolledframe = ScrolledFrame(
            self.root, scrolltype="horizontal"
        )
        self.pick_scrolledframe_innerframe = self.pick_scrolledframe.innerframe
        self.pick_scrolledframe_innerframe.configure(
            height=self.get_pick_scrolledframe_innerframe_height()
        )
        self.info_tip_label = ttk.Label(
            self.root, text=_("Write information in your strict format.")
        )
        self.basic_info_entry = tk.Entry(self.root, justify="center")
        simpletooltip.create(
            self.basic_info_entry, _("Write basic information here.")
        )
        self.info_text = tk.Text(self.root)
        simpletooltip.create(
            self.info_text, _("Write additional information here.")
        )

        self.info_templates_combobox = ttk.Combobox(
            self.root,
            textvariable=self.info_template_var,
            values=self.get_info_template_values(),
            justify="center",
        )
        self.info_template_var.trace("w", self.info_template_var_trace_w)

        self.save_button = ttk.Button(
            self.root, text=_("Save"), command=self.save_button_command
        )
        self.delete_button = tk.Button(
            self.root,
            text=_("Delete"),
            background="red",
            activebackground="red",
            command=self.delete_button_command,
        )

        fw_scrolledframe = self.get_fw_pick_scrolledframe_forrecog()
        self.set_frame_labels_innerframe_for_recog(fw_scrolledframe.innerframe)

    def get_frame(self, copy=False):
        return self.fw.get_frame(copy)

    def get_pick_scrolledframe_x(self):
        return self.get_x()

    def get_pick_scrolledframe_y(self):
        _above_max_height = (
            self.get_saved_info_combobox_height()
            if self.get_saved_info_combobox_height()
            > self.get_add_button_height()
            else self.get_add_button_height()
        )
        return self.get_saved_info_combobox_y() + _above_max_height

    def get_pick_scrolledframe_width(self):
        return self.get_width()

    def get_pick_scrolledframe_height(self):
        return (
            self.get_resize_height()
            + self.pick_scrolledframe.hsb.winfo_reqheight()
            + self.picked_frame_label_margin
        )

    def get_info_text_x(self):
        return self.get_x()

    def get_info_text_y(self):
        return (
            self.get_basic_info_entry_y() + self.get_basic_info_entry_height()
        )

    def get_info_text_width(self):
        return self.get_width()

    def get_info_text_height(self):
        return (
            self.get_height()
            - self.get_info_text_y()
            - self.get_save_button_height()
        )

    def get_info_tip_label_x(self):
        return self.get_x()

    def get_info_tip_label_y(self):
        return (
            self.get_pick_scrolledframe_y()
            + self.get_pick_scrolledframe_height()
        )

    def get_info_tip_label_width(self):
        return self.get_width()

    def get_info_tip_label_height(self):
        return self.info_tip_label.winfo_reqheight()

    def get_save_button_x(self):
        return self.get_x() + int(
            (self.get_width() - self.get_save_button_width()) / 2
        )

    def get_save_button_y(self):
        return self.get_height() - self.get_save_button_height()

    def get_save_button_width(self):
        return self.save_button.winfo_reqwidth()

    def get_save_button_height(self):
        return self.save_button.winfo_reqheight()

    def get_basic_info_entry_x(self):
        return self.get_x()

    def get_basic_info_entry_y(self):
        return self.get_info_tip_label_y() + self.get_info_tip_label_height()

    def get_basic_info_entry_width(self):
        return self.get_width()

    def get_basic_info_entry_height(self):
        return self.basic_info_entry.winfo_reqheight()

    def get_saved_info_combobox_x(self):
        return self.get_x()

    def get_saved_info_combobox_y(self):
        return self.get_y()

    def get_saved_info_combobox_width(self):
        return self.get_width() - self.get_add_button_width()

    def get_saved_info_combobox_height(self):
        return self.saved_info_combobox.winfo_reqheight()

    def get_delete_button_x(self):
        return self.get_x() + self.get_width() - self.get_delete_button_width()

    def get_delete_button_y(self):
        return self.get_save_button_y()

    def get_delete_button_width(self):
        return self.delete_button.winfo_reqwidth()

    def get_delete_button_height(self):
        return self.delete_button.winfo_reqheight()

    def delete_button_place(self):
        self.delete_button.place(
            x=self.get_delete_button_x(),
            y=self.get_delete_button_y(),
            width=self.get_delete_button_width(),
            height=self.get_delete_button_height(),
        )
        pass

    def delete_button_place_forget(self):
        self.delete_button.place_forget()
        pass

    def get_add_button_x(self):
        return self.get_x() + self.get_width() - self.get_add_button_width()

    def get_add_button_y(self):
        return self.get_y()

    def get_add_button_width(self):
        return self.add_button.winfo_reqwidth()

    def get_add_button_height(self):
        return self.add_button.winfo_reqheight()

    def get_add_button_background(self):
        return "blue"

    def place(self):
        super().place()

        self.saved_info_combobox.place(
            x=self.get_saved_info_combobox_x(),
            y=self.get_saved_info_combobox_y(),
            width=self.get_saved_info_combobox_width(),
            height=self.get_saved_info_combobox_height(),
        )
        self.add_button.place(
            x=self.get_add_button_x(),
            y=self.get_add_button_y(),
            width=self.get_add_button_width(),
            height=self.get_add_button_height(),
        )

        self.pick_scrolledframe.place(
            x=self.get_pick_scrolledframe_x(),
            y=self.get_pick_scrolledframe_y(),
            width=self.get_pick_scrolledframe_width(),
            height=self.get_pick_scrolledframe_height(),
            anchor="nw",
        )
        self.info_tip_label.place(
            x=self.get_info_tip_label_x(),
            y=self.get_info_tip_label_y(),
            width=self.get_info_tip_label_width(),
            height=self.get_info_tip_label_height(),
        )
        self.basic_info_entry.place(
            x=self.get_basic_info_entry_x(),
            y=self.get_basic_info_entry_y(),
            width=self.get_basic_info_entry_width(),
            height=self.get_basic_info_entry_height(),
        )
        self.info_text.place(
            x=self.get_info_text_x(),
            y=self.get_info_text_y(),
            width=self.get_info_text_width(),
            height=self.get_info_text_height(),
        )
        self.save_button.place(
            x=self.get_save_button_x(),
            y=self.get_save_button_y(),
            width=self.get_save_button_width(),
            height=self.get_save_button_height(),
        )

        if self.is_action_read():
            self.delete_button_place()
        if not self.get_info_id():
            self.place_info_templates_combobox()
        else:
            self.place_forget_info_templates_combobox()

    def get_picked_frames_len(self):
        return len(self.picked_frames)

    def del_picked_frame_by_index(self, index, del_label=True):
        if del_label:
            self.picked_frame_labels[index].destroy()
            del self.picked_frame_labels[index]
        if index < self.get_picked_frames_len():
            del self.picked_frames[index]
        self.set_picked_frame_labels_image()

    def clear_saved_frame_labels(self):
        for l in self.saved_frame_labels:
            l.destroy()
        self.saved_frame_labels = []
        pass

    def clear_picked_frame_labels(self):
        for l in self.picked_frame_labels:
            l.destroy()
        self.picked_frame_labels = []

    def add_picked_frames(self, frames=None, update_label=True):
        if not isinstance(frames, list):
            frames = [frames]
        self.picked_frames = frames + self.picked_frames

        info_id = self.get_info_id()
        print("info_id", info_id)
        if (not info_id) and self.get_picked_frames_len() < 2:
            self.place_info_templates_combobox()
            self.set_info_text_content_use_template()

        if update_label:
            new_added_frames = []
            if self.is_action_read():
                pass
            self.set_picked_frame_labels_image(self.picked_frames)

    def set_info_text_content_use_template(self):
        content = self.get_info_template_content()
        if not content:
            print(1326)
            return
        self.set_info_text_content(content)
        pass

    def get_info_frame(self):
        frame = ttk.Frame(self.info_scrolledframe_innerframe)
        return frame

    def update_picked_frame_labels(self, frames=None):
        self.set_picked_frame_labels_image(frames)

    def set_picked_frame_labels_image(self, frames=None):
        self.set_frame_labels_image(frames)

    def get_saved_frame_labels(self):
        if len(self.saved_frame_labels) < 1:
            return None
        return self.saved_frame_labels

    def del_saved_frame_by_id(
        self, frame_id=None, index=0, ask=True, update_widgets=True
    ):
        if frame_id is None:
            return

        self.show_widget_click(self.get_saved_frame_labels(), index)

        if ask:
            if not messagebox.askyesno(
                _("Delete saved frame"),
                _("Do you want to delete saved frame?"),
            ):
                return

        image_path = get_frame_path_by_ids(self.get_info_id(), frame_id)

        if not os.path.exists(image_path):
            if self.is_test():
                print(_("Image(%s) doesn't exist.") % image_path)
            return

        backup_file_path = get_new_backup_file_path(frame_id)
        if not os.path.exists(backup_file_path):
            with open(backup_file_path, "wb") as f:
                pass
        shutil.move(image_path, backup_file_path)
        index = 0
        for _id, f in self.get_saved_frames():
            if _id == frame_id:
                del self.saved_frames[index]
                if update_widgets:
                    self.saved_frame_labels[index].destroy()
                    del self.saved_frame_labels[index]
                break
            index += 1
            pass
        self.set_frame_labels_image()
        pass

    def set_frame_labels_image_use_picked_frames(
        self, frames=None, from_new_frame=False
    ):
        """
        Set frame label images using picked_frames
        Args:
            frames (Unit[int, numpy.array]): The video or image frame or the
            the `return` signal if `frames` is 0.
        """

        if frames == 0:
            return
        if frames is None:
            frames = (
                self.get_picked_frames()
                or (from_new_frame and self.get_picked_frames_from_frame())
                or None
            )
        if frames is not None:
            for f in frames:
                label = ttk.Label(
                    self.pick_scrolledframe_innerframe, state="active"
                )
                self.set_label_image(f, label)
                index = len(self.picked_frame_labels)
                label.bind(
                    "<Button-1>",
                    lambda event, idx=index: self.del_picked_frame_by_index(
                        idx
                    ),
                )
                label.pack(
                    side="left",
                    anchor="nw",
                    padx=self.picked_frame_label_margin / 2,
                )
                simpletooltip.create(label, _("Click to delete."))
                self.picked_frame_labels.append(label)
        else:
            if self.is_test():
                print(_("Picked frame is None."))

    def set_frame_labels_image_use_saved_frames(
        self, frames=None, for_read=False
    ):
        if for_read:
            if not self.is_action_read():
                print("`NOT` is_action_read.")
                return
        saved_frames = frames or self.get_saved_frames()
        if saved_frames is None:
            if self.is_test():
                print(self.get_info_id(), _("Saved frames is None."))
            return
        if self.is_test():
            print("saved_frames_len", len(saved_frames))
        index = 0
        for _id, f in saved_frames:
            if self.is_test():
                print("`saved_frame.id`", _id)
            label = ttk.Label(self.pick_scrolledframe_innerframe)
            self.set_label_image(f, label)
            i = index
            label.bind(
                "<Button-1>",
                lambda event, _id=_id, i=i: self.del_saved_frame_by_id(_id, i),
            )
            label.pack(
                side="left",
                anchor="nw",
                padx=self.frame_label_margin / 2,
            )
            simpletooltip.create(label, _("Saved frame, Click to delete."))
            self.saved_frame_labels.append(label)
            index += 1
        pass

    def show_labels_image_by_frames(
        self, frames=None, parent_widget=None, label_func=None
    ):
        return self.set_labels_image_by_frames_return_labels(
            frames, parent_widget, label_func
        )

    def set_labels_image_by_frames_return_labels(
        self, frames=None, parent_widget=None, label_func=None
    ):
        assert frames is not None
        label_func = label_func or (
            lambda: print("`set_labels_image_by_frames.label_func` is None.")
        )
        parent_widget = parent_widget or self.pick_scrolledframe_innerframe
        index = 0
        labels = []
        for f in frames:
            label = ttk.Label(parent_widget)
            self.set_label_image(f, label)
            label.bind(
                "<Button-1>",
                lambda event, _index=index: label_func(_index),
            )
            label.pack(
                side="left",
                anchor="nw",
                padx=self.frame_label_margin / 2,
            )
            simpletooltip.create(label, _("Saved frame, Click to delete."))
            labels.append(label)

        return labels

    def set_frame_labels_image_use_picked_frames_for_recog(self, frames=None):
        """
        Set frame label images for recognition using picked_frames
        """
        self.update_frame_labels_for_recog_use_video_frame(frames)

    def get_picked_frame_by_index(self, index=None):
        if index is None:
            if self.is_test():
                print("`get_picked_frame_by_index.index` is `None`.")
            return
        if index < self.get_picked_frames_len():
            return self.picked_frames[index]
        if self.is_test():
            print(
                "index",
                index,
                "\n",
                "get_picked_frames_len",
                self.get_picked_frames_len(),
                "\n",
                "`get_picked_frame_by_index.index` out of range.",
            )
        return None

    def get_picked_frames_for_recog_len(self):
        return len(self.picked_frames_for_recog)

    def get_picked_frame_by_index_for_recog(self, index=None):
        if index is None:
            return None
        if index < self.get_picked_frames_for_recog_len():
            return self.picked_frames_for_recog[index]
        return None

    def recog_frame_by_index(self, index=None):
        self.recog_picked_frame_by_index(index)
        pass

    def recog_pk_frame_by_index(self, index=None):
        self.recog_picked_frame_by_index(index)
        pass

    def get_labels_by_frames(self, frame=None):
        return self.fw.get_labels_by_frames(frame)

    def get_label_by_frame(self, frame=None):
        return self.fw.get_label_by_frame(frame)

    def get_info_id_by_frame(self, frame=None):
        return self.fw.get_info_id_by_frame(frame)

    def recog_picked_frame_by_index(self, index=None, show_click=True):
        assert index is not None
        if self.is_info_ids_none():
            self.set_msg(_("Saved dateset doesn't exist."))
            return
        if index is None:
            if self.is_test():
                print("`recog_picked_frame_by_index.index` is `None`.")
            return

        self.mk_tmsg(f"recog_picked_frame_by_index.index --> {index}")
        frame = self.get_picked_frame_by_index_for_recog(index)
        if frame is None:
            self.set_warning_msg(_("`Picked Frames is None.`"))
            self.mk_tmsg("`recog_picked_frame_by_index.frame` is `None`.")
            return
        assert frame is not None
        info_id = self.get_info_id_by_frame(frame)
        assert info_id is not None
        if info_id is None:
            self.mk_tmsg("`recog_picked_frame_by_index.info_id` is `None`.")
            return
        self.update_widgets_by_info_id_for_recog(info_id)

        if show_click:
            labels = self.get_picked_frame_labels_for_recog()

            self.show_widget_click(labels, index)

        pass

    def show_widget_click(self, widget_list=None, index=0):
        self.show_widget_click_by_default(widget_list, index)
        pass

    def show_widget_click_by_default(
        self, widget_list=None, index=0, borderwidth=8, background="blue"
    ):

        if widget_list is None:
            return

        for w in widget_list:
            w.config(borderwidth=0, background="")

        w = widget_list[index]
        w.config(
            borderwidth=borderwidth,
            background=background,
        )

        pass

    def get_recog_picked_frame_labels(self):
        return self.get_picked_frame_labels_for_recog()

    def get_recog_picked_frame_labels_len(self):
        return len(self.get_recog_picked_frame_labels())

    def get_recog_picked_frame_label_by_index(self, index=0):
        if self.get_recog_picked_frame_labels_len() > index:
            return self.picked_frame_labels_for_recog[index]
        return None

    def get_default_recog_picked_frame_labels_borderwidth(self):
        return 5

    def get_recog_picked_frame_labels_borderwidth(self):
        return (
            self.recog_picked_frame_labels_borderwidth
            or self.get_default_recog_picked_frame_labels_borderwidth()
        )

    def set_recog_picked_frame_labels_borderwidth(self, borderwidth=None):
        self.recog_picked_frame_labels_borderwidth = (
            borderwidth
            or self.get_default_recog_picked_frame_labels_borderwidth()
        )

    def get_fw_pick_scrolledframe_forrecog_x(self):
        return self.fw.get_pick_scrolledframe_forrecog_x()

    def get_fw_pick_scrolledframe_forrecog_y(self):
        return self.fw.get_pick_scrolledframe_forrecog_y()

    def get_fw_pick_scrolledframe_forrecog_height(self):
        return self.fw.get_pick_scrolledframe_forrecog_height()

    def set_frame_labels_image(
        self, show_saved_frames=True, show_picked_frames=True
    ):
        self.clear_picked_frame_labels()
        self.clear_saved_frame_labels()
        if show_picked_frames:
            self.set_frame_labels_image_use_picked_frames()
        if show_saved_frames:
            self.set_frame_labels_image_use_saved_frames()

    def set_label_image(self, image, label):
        self.set_label_frame(image, label)

    def set_label_frame(self, frame, label):
        self.fw.set_label_image(frame, label)

    def get_picked_frames_from_frame(self, frame=None, set_self=False):
        face_casecade = self.get_face_casecade()
        frame = frame or self.get_frame(copy=True)
        if frame is None:
            self.set_warning_msg(_("Frame is None."))
            return None
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_rects = face_casecade.detectMultiScale(gray_img, 1.3, 5)
        frames = []
        for (x, y, w, h) in face_rects:
            pick_frame = frame[y : y + h, x : x + w]
            pick_frame = cv2.resize(
                pick_frame,
                (self.get_resize_width(), self.get_resize_height()),
                interpolation=cv2.INTER_LINEAR,
            )
            frames.append(pick_frame)
        del frame
        del gray_img
        if set_self:
            self.set_picked_frames(frames)
        return frames

    def pick_frame_for_add_by_default(self):
        frames = self.get_picked_frames_from_frame()
        if frames is None:
            self.mk_tmsg("`pick_frame_for_add_by_default.frames` is None.")
            return
        self.add_picked_frames(frames)
        pass

    def pick_frame_by_default(self):
        frames = self.get_picked_frames_from_frame()
        if frames is None:
            return
        self.add_picked_frames(frames)
        pass

    def is_info_ids_none(self):
        return self.fw.is_info_ids_none()

    def recog_frame_by_default(self):
        # if self.is_info_ids_none():
        #    return
        self.clear_picked_frame_labels()
        self.clear_saved_frame_labels()
        frames = self.get_picked_frames_from_frame()
        self.set_frame_labels_image_use_picked_frames_for_recog(frames)
        pass


#
