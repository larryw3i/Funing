#!/usr/bin/python3

import getopt
import os
import sys
from pathlib import Path

from funing import settings


def get_dep_requirements():
    return [
        "opencv-contrib-python >= 4.5.3.56",
        "Pillow >= 8.3.0",
        "numpy >= 1.21.1",
    ]


def install_dep_requirements(test=False,dep_requirements = None, upgrade = False):
    dep_requirements = dep_requirements or get_dep_requirements()
    sh = ""
    if upgrade:
        dep_requirements = [ d.split(" ")[0] for d in dep_requirements]
        sh = "pip3 install -U " + (" ".join(dep_requirements))
    else:
        dep_requirements = [ d.replace(" ","" ) for d in dep_requirements]
        sh = "pip3 install -U -v " + (" ".join(dep_requirements))
    if test:
        print(sh)
    os.system(sh)


def show():
    pass


def run():
    sys_argv = sys.argv[1:]
    optlist, args = getopt.getopt(sys_argv, "")
    print(args)
    if len(args) < 1:
        show()
    for a in args:
        if a in ["dep"]:
            install_dep_requirements()
        if a in ["depu"]:
            install_dep_requirements(upgrade = True)
        if a in ["ok"]:
            break
