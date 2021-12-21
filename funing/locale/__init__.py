
import gettext
import locale
import os
import sys

import yaml

from funing import *
from funing.settings import *

sys_lang_code = locale.getdefaultlocale()[0]

if sys_lang_code not in locale_langcodes:
    sys_lang_code = 'en_US'

if debug:
    print(sys_lang_code, locale_path)

lang = gettext.translation(
    'funing', localedir=locale_path,
    languages=[sys_lang_code])

lang.install()

_ = lang.gettext
