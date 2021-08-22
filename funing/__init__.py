#!/usr/bin/python3

'''
Usually, the UI scripts are placed in directory ui and the related function \
scripts are placed in directory _ui.
Neither directory ui nor directory _ui is mandatory, take the easiest way.
'''

import getopt
import os
import sys
from pathlib import Path

from funing import settings
from funing._ui import Enjoy

__version__ = settings.version


start_args = ['s', 'st' 'start']
test_args = ['ts', 't', 'test']
keep_code_args = ['kc', 'keep_code']


def run():

    sys_argv = sys.argv[1:]
    optlist, args = getopt.getopt(sys_argv, '')

    e = Enjoy()

    if len(args) < 1:
        e.start()
    for a in args:
        if a in start_args + test_args:
            e.start()
        if a in ['init', 'initial']:
            e.initialize()
        if a in keep_code_args:
            e.keep_code()
