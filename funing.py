#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getopt
import os
import re
import shutil
import sys
import uuid
from pathlib import Path

from funing import *
from funing import settings
from funing.settings import *


def get_dev_dep_requirements_full():
    return [
        (
            "opencv-contrib-python >= 4.6.0.66",
            "https://github.com/opencv/opencv_contrib",
            "Apache License 2.0",
            "https://github.com/opencv/opencv_contrib/blob/4.x/LICENSE",
        ),
        (
            "virtualenv >= 4.5.3.56",
            "https://github.com/pypa/virtualenv",
            "MIT license",
            "https://github.com/pypa/virtualenv/blob/main/LICENSE",
        ),
        (
            "pip >= 22.1.2",
            "https://github.com/pypa/pip",
            "MIT License",
            "https://github.com/pypa/pip/blob/main/LICENSE.txt",
        ),
        (
            "thonny >= 3.3.14",
            "https://github.com/thonny/thonny",
            "MIT License",
            "https://github.com/thonny/thonny/blob/master/LICENSE.txt",
        ),
        (
            "black >= 22.3.0",
            "https://github.com/psf/black",
            "MIT License",
            "https://github.com/psf/black/blob/main/LICENSE",
        ),
        (
            "isort >= 5.10.0",
            "https://github.com/pycqa/isort",
            "MIT License",
            "https://github.com/PyCQA/isort/blob/main/LICENSE",
        ),
    ]


def get_dev_dep_requirements():
    return [
        f[0] for f in get_dev_dep_requirements_full()
    ] + get_dep_requirements()


def install_dev_dep_requirements():
    install_dep_requirements(
        test=True, dep_requirements=get_dev_dep_requirements()
    )


def install_dev_dep_requirements_u():
    install_dep_requirements(
        test=True, dep_requirements=get_dev_dep_requirements(), upgrade=True
    )


def start(test=False):
    from funing import run

    run(test)


def settings4xget():
    _pwd = os.path.abspath(os.path.dirname(__file__))
    settings4t = ""
    settings4t_txt_path = os.path.join(_pwd, app_name, "settings4t.txt.py")
    settings4t_path = os.path.join(_pwd, app_name, "settings4t.py")
    with open(settings4t_txt_path, "r") as f:
        settings4t = f.read()
    _attrs = dir(settings)
    for _attr in _attrs:
        _attr_value = getattr(settings, _attr)
        if not isinstance(_attr_value, str):
            continue
        settings4t = settings4t.replace(f"@{_attr}", _attr_value)
    with open(settings4t_path, "w") as f:
        f.write(settings4t)


def print_class_def(max_col=80):
    print_file(filter_func=lambda l: "def " in l or "class " in l)


def print_file(max_col=80, filter_func=None):
    if not filter_func:
        filter_func = lambda l: True
    for (root, dirs, files) in os.walk(app_name, topdown=True):
        for f in files:
            if not (f.endswith(".py") or f.endswith(".sh")):
                continue
            file_path = os.path.join(root, f)
            with open(file_path, "r") as f:
                lines = f.readlines()
                max_len = max_line_number_len = len(str(len(lines)))
                max_len = max_line_number_len = max_len > 4 and max_len or 4
                ln = line_number = 1
                start_end_char_len = max_col + 2 + max_len
                _file_path = file_path + "\u2193"
                print(f"{_file_path:^{start_end_char_len}}")
                print("\u005f" * (start_end_char_len - 1))
                for l in lines:
                    if filter_func(l):
                        l = str.rstrip(l)
                        print(f"{ln:>{max_len}}|", end="")
                        print(f"{l:<{max_col}}", end="|\n")
                    line_number += 1
                    ln = line_number
                print("\u203e" * (start_end_char_len - 1))


def print_version():
    print(app_version)


if __name__ == "__main__":
    sys_argv = sys.argv[1:]
    optlist, args = getopt.getopt(sys_argv, "")
    if len(args) < 1:
        pass
    for a in args:
        if a in ["s", "start"]:
            start(test=any(_a in ["t", "test"] for _a in args))
        if a in ["4xget"]:
            settings4xget()
        if a in ["dep"]:
            install_dev_dep_requirements()
        if a in ["depu"]:
            install_dev_dep_requirements_u()
        if a in ["ver"]:
            print_version()
        if a in ["pcd"]:
            print_class_def()
        if a in ["prtf"]:
            print_file()
        if a in ["pass"]:
            break
        else:
            print('''
                
                ''')
