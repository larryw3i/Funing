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
from funing.path import *
from funing.settings import *


def get_dev_dep_requirements():
    return [
        "opencv-contrib-python >= 4.5.3.56",
        "Pillow >= 8.3.0",
        "numpy >= 1.21.1",
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


if __name__ == "__main__":
    sys_argv = sys.argv[1:]
    optlist, args = getopt.getopt(sys_argv, "")
    if len(args) < 1:
        pass
    for a in args:
        if a in ["s", "start"]:
            start()
        if a in ["t", "test"]:
            start(test=True)
        if a in ["4xget"]:
            settings4xget()
        if a in ["dep"]:
            install_dev_dep_requirements()
        if a in ["depu"]:
            install_dev_dep_requirements_u()
        if a in ["pass"]:
            break
