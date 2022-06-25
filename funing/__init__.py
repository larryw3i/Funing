#!/usr/bin/python3

import getopt
import os
import sys
from pathlib import Path

from funing import settings
from funing.locale import _


def get_dep_requirements():
    return [
        "opencv-contrib-python >= 4.5.3.56",
        "Pillow >= 8.3.0",
        "numpy >= 1.21.1",
    ]


def install_dep_requirements(test=False, dep_requirements=None, upgrade=False):
    dep_requirements = dep_requirements or get_dep_requirements()
    sh = ""
    if upgrade:
        dep_requirements = [d.split(" ")[0] for d in dep_requirements]
        sh = "pip3 install -U " + (" ".join(dep_requirements))
    else:
        dep_requirements = [d.replace(" ", "") for d in dep_requirements]
        sh = "pip3 install '" + ("' '".join(dep_requirements)) + "'"
    if test:
        print(sh)
    os.system(sh)


def run(test=False):
    if test:
        print(_("Hello, Funing!"))
    pass
