#!/usr/bin/python3

'''
Usually, the UI scripts are placed in directory ui and the related function \
scripts are placed in directory ui_.
Neither directory ui nor directory ui_ is mandatory, take the easiest way.
'''

import getopt
import os
import re
import shutil
import sys
from pathlib import Path

__version__ = version = "0.2.47"
__appname__ = appname = 'Funing'
__appauthor__ = appauthor = 'larryw3i'
__appauthor_email__ = appauthor_email = 'null.null@null.null'

debug = os.environ.get('FUNING_TEST') == '1'


def simple():
    from funing._ui import main
    main.start()
