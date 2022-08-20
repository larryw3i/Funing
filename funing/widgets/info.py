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
from cv2.data import haarcascades
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

    def get_saved_frames_for_active_id(self):
        return self.get_saved_frames()

    def get_saved_frames(self):
        if self.saved_frames is None:
            return self.get_saved_frames_by_id()
        return self.saved_frames

    def set_saved_frames_for_active_id(self, frames=None, to_none=False):
        self.set_saved_frames(frames, to_none)

    def set_saved_frames_with_frame_id(self, frames=None, to_none=False):
        self.set_saved_frames(frames, to_none)

    def set_saved_frames(self, frames=None, to_none=False):
        if to_none:
            self.saved_frames = None
        if frames is None:
            return
        self.saved_frames = self.saved_frames_for_active_id = frames

    def set_action(self, action=ACTION.NONE, to_none=False):
        self.fw.set_action(action, to_none)

    def set_action_to_none(self):
        self.set_action(ACTION.NONE)

    def set_action_to_read(self):
        if not self.is_action_read():
            self.delete_button_place()
            pass
        self.set_action(ACTION.READ)
        self.set_infos_and_images_by_id(self.info_id)

    def set_action_to_pick(self):
        self.set_action(ACTION.PICK)

    def set_action_to_recog(self):
        self.set_action(ACTION.RECOG)

    def get_action(self):
        return self.fw.get_action()

    def get_info_id(self):
        self.info_id = self.fw.get_info_id()
        return self.info_id

    def set_info_id(self, _id):
        self.info_id = self.fw.set_info_id(_id, return_id=True)

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

    def get_saved_frames_by_id(self, info_id=None, set_self=True):
        if info_id is None:
            info_id = self.get_info_id()
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
        if info_id is None:
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
            self.set_picked_frame_labels_image()
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
            self.set_action_to_pick()
            self.clear_info_widget_area_content()
            return
        self.set_info_id(info_id)
        self.set_action_to_read()
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
            if os.path.exists(p):
                shutil.move(src, get_new_backup_path())
        self.set_basic_infos(to_none=True)
        self.update_saved_info_combobox_values()
        self.del_showed_info()
        self.set_msg(
            _("Information of %s(%s) is deleted." % (basic_info, info_id))
        )
        pass

    def delete_button_command(self):
        if not self.is_action_read():
            if self.is_test():
                print(_("ACTION isn't 'READ'."))
            return
        self.del_save_info_by_info_id()
        pass

    def set_widgets(self):
        super().set_widgets()
        self.set_frame_widget()

        self.saved_info_combobox = ttk.Combobox(
            self.root,
            textvariable=self.saved_info_combobox_var,
            values=self.get_saved_info_combobox_values(),
            justify="center",
        )
        self.saved_info_combobox_var.trace(
            "w", self.saved_info_combobox_var_trace_w
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
        self.save_button = ttk.Button(
            self.root, text=_("Save"), command=self.save_button_command
        )
        self.delete_button = tk.Button(
            self.root,
            text=_("Delete"),
            background="red",
            activebackground="red",
            command=self.delete_button_command(),
        )

    def get_frame(self, copy=False):
        return self.fw.get_frame(copy)

    def get_pick_scrolledframe_x(self):
        return self.get_x()

    def get_pick_scrolledframe_y(self):
        return (
            self.get_saved_info_combobox_y()
            + self.get_saved_info_combobox_height()
        )

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
        return self.get_width()

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

    def place(self):
        super().place()

        self.saved_info_combobox.place(
            x=self.get_saved_info_combobox_x(),
            y=self.get_saved_info_combobox_y(),
            width=self.get_saved_info_combobox_width(),
            height=self.get_saved_info_combobox_height(),
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
        if update_label:
            new_added_frames = []
            if self.is_action_read():
                pass
            self.set_picked_frame_labels_image(self.picked_frames)

    def get_info_frame(self):
        frame = ttk.Frame(self.info_scrolledframe_innerframe)
        return frame

    def update_picked_frame_labels(self, frames=None):
        self.set_picked_frame_labels_image(frames)

    def set_picked_frame_labels_image(self, frames=None):
        self.set_frame_labels_image(frames)

    def del_saved_frame_by_id(
        self, frame_id=None, ask=True, update_widgets=True
    ):
        if frame_id is None:
            return
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

    def set_frame_labels_image_use_picked_frames(self, frames=None):
        if frames is None:
            frames = (
                self.get_picked_frames() or self.get_picked_frames_from_frame()
            )
        if frames is not None:
            for f in frames:
                label = ttk.Label(
                    self.pick_scrolledframe_innerframe, state="active"
                )
                index = len(self.picked_frame_labels)
                label.bind(
                    "<Button-1>",
                    lambda event, index=index: self.del_picked_frame_by_index(
                        index
                    ),
                )
                label.pack(
                    side="left",
                    anchor="nw",
                    padx=self.picked_frame_label_margin / 2,
                )
                simpletooltip.create(label, _("Click to delete."))
                self.set_label_image(f, label)
                self.picked_frame_labels.append(label)
        else:
            if self.is_test():
                print(_("Picked frame is None."))

    def set_frame_labels_image_use_saved_frames(
        self, frames=None, for_read=True
    ):
        if for_read:
            if not self.is_action_read():
                return
        saved_frames = self.get_saved_frames()
        if saved_frames is None:
            if self.is_test():
                print(_("Saved frames is None."))
            return
        if self.is_test():
            print("saved_frames", len(saved_frames))
        for _id, f in saved_frames:
            label = ttk.Label(
                self.pick_scrolledframe_innerframe, state="active"
            )
            label.bind(
                "<Button-1>",
                lambda event, _id=_id: self.del_saved_frame_by_id(_id),
            )
            label.pack(
                side="left",
                anchor="nw",
                padx=self.frame_label_margin / 2,
            )
            simpletooltip.create(label, _("Saved frame, Click to delete."))
            self.set_label_image(f, label)
            self.saved_frame_labels.append(label)
        pass

    def set_frame_labels_image(self, frames=None):
        self.clear_picked_frame_labels()
        self.clear_saved_frame_labels()
        self.set_frame_labels_image_use_picked_frames()
        self.set_frame_labels_image_use_saved_frames()

    def set_label_image(self, image, label):
        self.set_label_frame(image, label)

    def set_label_image(self, image, label):
        self.set_label_frame(image, label)

    def set_label_frame(self, frame, label):
        self.fw.set_label_image(frame, label)

    def get_picked_frames_from_frame(self, frame=None, set_self=False):
        face_casecade = self.get_face_casecade()
        frame = frame or self.get_frame(copy=True)
        if frame is None:
            self.set_msg(_("Frame is None."))
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

    def pick_frame_by_default(self):
        frames = self.get_picked_frames_from_frame()
        if frames is None:
            return
        self.add_picked_frames(frames)
        pass
