#!/usr/bin/python3

import getopt
import os
import sys
from pathlib import Path

from funing import settings
from funing._ui import Enjoy

start_args = ['s', 'st' 'start']
test_args = ['ts', 't', 'test']
keep_code_args = ['kc', 'keep_code']


def run():
    sys_argv = sys.argv[1:]
    f = Enjoy()
    optlist, args = getopt.getopt(sys_argv, '')
    if len(args) < 1:
        f.start()
    for a in args:
        if a in start_args + test_args:
            f.start()
        if a in ['init', 'initial']:
            f.initialize()
        if a in keep_code_args:
            f.keep_code()
