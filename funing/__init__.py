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

__version__ = version = "0.2.50"
__appname__ = appname = 'Funing'
__appauthor__ = appauthor = 'larryw3i'
__appauthor_email__ = appauthor_email = 'larryw3i@163.com'

debug = os.environ.get('FUNING_TEST') == '1'

product_req = [
    # ('package','version','project_url','license','license_url')
    (
        'opencv-contrib-python', '',
        'https://github.com/opencv/opencv-python',
        'MIT License',
        'https://github.com/opencv/opencv-python/blob/master/LICENSE.txt'
    ),
    (
        'PyYAML', '',
        'https://github.com/yaml/pyyaml',
        'MIT License', 'https://github.com/yaml/pyyaml/blob/master/LICENSE'
    ),
    (
        'Pillow', '',
        'https://github.com/python-pillow/Pillow',
        'HPND License',
        'https://github.com/python-pillow/Pillow/blob/main/LICENSE'
    ),
    (
        'numpy', '', 'https://github.com/numpy/numpy',
        'BSD 3-Clause "New" or "Revised" License',
        'https://github.com/numpy/numpy/blob/main/LICENSE.txt'
    ),
    (
        'appdirs', '', 'http://github.com/ActiveState/appdirs',
        'MIT license',
        'https://github.com/ActiveState/appdirs/blob/master/LICENSE.txt'
    ),
    (
        'pygubu', '', 'https://github.com/alejandroautalan/pygubu',
        'MIT License',
        'https://github.com/alejandroautalan/pygubu/blob/master/LICENSE'
    )

]


def get_product_req():
    return [r[0] + r[1] for r in product_req]


def simple():
    from funing._ui import main
    main.start()
