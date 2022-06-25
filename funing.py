#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getopt
import os
import re
import shutil
import sys
import uuid
from pathlib import Path

from funing.settings import *
from funing import settings
from funing.path import *


def start():
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    from funing import run

    sys.exit(run())


def xgettext():
    from funing import settings

    mo_files = []
    xgettext_files = []
    for root, dirs, files in os.walk(project_path):
        for f in files:
            if f.endswith(".py"):
                xgettext_files.append(os.path.join(root, f))
    xgettext_files = "\n".join(xgettext_files)
    open(xgettext_f_path, "w+").write(xgettext_files)
    for root, dirs, files in os.walk(locale_path):
        for f in files:
            if f.endswith(".po"):
                f_path = os.path.join(root, f)
                os.system(
                    f"xgettext -f {xgettext_f_path} "
                    + f"--join-existing -d funing -o {f_path}"
                )


def msgfmt():
    from funing._fui import Enjoy

    Enjoy().msgfmt()


def keep_code():
    from funing._fui import Enjoy

    Enjoy().keep_code()


def pip_install_r():
    os.system("pip3 install -r requirements.txt ")


def settings4xget():

    _pwd = os.path.abspath(os.path.dirname(__file__))
    settings4t = ""
    settings4t_txt_path = os.path.join(_pwd, app_name, "settings4t.txt")
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
        if a in ["s", "ts", "st", "start"]:
            start()
        if a in ["4xget"]:
            settings4xget()
        if a in ["xgettext", "xg"]:
            xgettext()
        if a in ["m", "msg", "msgfmt"]:
            msgfmt()
        if a in ["kc", "keep_code"]:
            keep_code()
        if a in ["pip", "pip_install"]:
            pip_install_r()
