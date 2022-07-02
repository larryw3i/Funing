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


def get_dev_dep_requirements_full():
    return [
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
        if a in ["pass"]:
            break
