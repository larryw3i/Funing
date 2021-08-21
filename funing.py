#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getopt
import os
import re
import shutil
import sys
import uuid
from pathlib import Path

from funing import keep_code_args, settings, start_args, test_args


# DON't IMPORT ANYTHING FROM THIS FILE
class Funing():
    def __init__(self):
        self.dir = os.path.abspath(os.path.dirname(__file__))
        self.data_dir = os.path.join(self.dir, 'data')
        self.pot_path = os.path.join(settings.locale_path, 'funing.pot')

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
        pass

    def test(self):
        os.environ['FUNING_TEST'] = '1'
        self.start()

    def start(self):
        sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
        from funing import run
        sys.exit(run())

    def pybabel_extract(self):
        extract_from_path = os.path.join(settings.project_path, '*')
        os.system(f'pybabel extract -o {self.pot_path} ' +
                  f'--omit-header {extract_from_path}')

    def pybabel_update(self):
        for l in settings.locale_langcodes:
            os.system(
                f'pybabel  update -D funing  -i {self.pot_path} ' +
                f'-d {settings.locale_path}  --omit-header -l {l}')

    # pybabel compile
    def pbc(self):
        os.system(f'pybabel compile -d {settings.locale_path}  -D funing -f')

    def keep_code(self):
        from funing._ui import Enjoy
        Enjoy().keep_code()

    def pip_install_r(self):
        os.system('pip3 install -r requirements.txt ')


if __name__ == '__main__':

    pip_install_r_args = ['pip', 'pip_install']
    pybabel_extract_args = ['be', 'pbe']
    pybabel_update_args = ['bu', 'pbu']
    pybabel_compile_args = ['c', 'bc', 'pbc']

    f = Funing()
    sys_argv = sys.argv[1:]

    optlist, args = getopt.getopt(sys_argv, '')

    if len(args) < 1:
        f.start()

    for a in args:
        if a in keep_code_args:
            f.keep_code()
        if a in pip_install_r_args:
            f.pip_install_r()
        if a in pybabel_extract_args:
            f.pybabel_extract()
        if a in pybabel_update_args:
            f.pybabel_update()
        if a in pybabel_compile_args:
            f.pbc()
        if a in test_args:
            f.test()
        if a in start_args:
            f.start()
