#!/usr/bin/python3

import getopt
import os
import subprocess
import sys
from pathlib import Path

from funing import settings
from funing.locale import _

app_version = settings.app_version


def get_dep_requirements_full():
    return [
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
        (
            "appdirs >= 1.4.4",
            "http://github.com/ActiveState/appdirs",
            "MIT License",
            "https://github.com/ActiveState/appdirs/blob/master/LICENSE.txt",
        ),
        (
            "pygubu >= 0.23.1",
            "https://github.com/alejandroautalan/pygubu",
            "MIT License",
            "https://github.com/alejandroautalan/pygubu/blob/master/LICENSE",
        ),
        (
            "isort >= 5.10.1",
            "https://github.com/pycqa/isort",
            "MIT License",
            "https://github.com/PyCQA/isort/blob/main/LICENSE",
        ),
    ]


def get_dep_requirements():
    return [f[0] for f in get_dep_requirements_full()]


def get_install_dep_requirements_name():
    return [d.split(" ")[0] for d in get_dep_requirements()]


def get_unsatisfied_deps(full=False):
    sh_output = subprocess.check_output("pip list", shell=True)
    requirements_full = get_dep_requirements_full()
    unsatisfied_deps = []
    for d in requirements_full:
        d_name = d.splite(" ")[0]
        if d_name not in sh_output:
            unsatisfied_deps.append(d if full else d_name)
    return unsatisfied_deps


def dep_unsatisfied():
    return len(get_unsatisfied_deps) < 1


def install_dep_requirements(test=False, dep_requirements=None, upgrade=False):
    dep_requirements = dep_requirements or get_dep_requirements()
    sh = ""
    if upgrade:
        dep_requirements = get_install_dep_requirements_name()
        sh = "pip3 install -U " + (" ".join(dep_requirements))
    else:
        dep_requirements = [d.replace(" ", "") for d in dep_requirements]
        sh = "pip3 install '" + ("' '".join(dep_requirements)) + "'"
    if test:
        print(sh)
    os.system(sh)


def run(test=False):
    if test:
        print(_("Hello, Welcome to Funing!"))
    print(_("Version: %s") % (app_version))
    from funing.widgets import show

    show(test)


def get_help(_print=True):
    _help = """
    -h:---------Shows help.
    -v:---------Shows version.
    -s:---------Start funing.
    """
    if _print:
        print(_help)
    return _help
