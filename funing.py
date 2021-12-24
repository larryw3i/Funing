#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getopt
import os
import sys

from funing import *
from funing.settings import *

if __name__ == '__main__':
    sys_argv = sys.argv[1:]
    _, args = getopt.getopt(sys_argv, '')

    for a in args:
        if a in test_args:
            os.environ['FUNING_TEST'] = '1'
        sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
        simple()
