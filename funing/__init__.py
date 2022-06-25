#!/usr/bin/python3

import getopt
import os
import sys
from pathlib import Path

from funing import settings
from funing.locale import _


def get_dep_requirements_full():
    return [
        (
            "opencv-contrib-python >= 4.6.0.66",
            "https://github.com/opencv/opencv_contrib",
            "Apache License 2.0",
            "https://github.com/opencv/opencv_contrib/blob/4.x/LICENSE",
        ),
        (
            "numpy >= 1.23.0",
            "https://github.com/numpy/numpy",
            'BSD 3-Clause "New" or "Revised" License',
            "https://github.com/numpy/numpy/blob/main/LICENSE.txt",
        ),
        (
            "Pillow >= 9.1.0",
            "https://github.com/python-pillow/Pillow",
            "Historical Permission Notice and Disclaimer (HPND)",
            "https://github.com/python-pillow/Pillow/blob/main/LICENSE",
        ),
    ]


def get_dep_requirements():
    return [
        f[0] for f in get_dep_requirements_full()
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
