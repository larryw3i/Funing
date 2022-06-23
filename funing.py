#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getopt
import os
import sys

from funing import simple
from funing.settings import test_args

if __name__ == "__main__":
    _argv = sys.argv[1:]
    if _argv in test_args:
        os.environ["FUNING_TEST"] = "1"
        sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
        simple()
    elif _argv in ["p3"]:
        from funing.dev_req import install_dev_req

        install_dev_req()
