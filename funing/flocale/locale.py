
import os
import gettext
import sys
from langcodes import Language
import gettext
import locale
import tkinter as tk
from pony.orm import *
from fmodel import funing_m as fm
from setting import base_dir, locale_path, lang_code, setting_yml, setting_path, debug, f_lang_codes
import yaml

sys_lang_code = locale.getdefaultlocale()[0]\
    .replace('_','-')

if lang_code == 'en-US' and \
    sys_lang_code != lang_code and \
    sys_lang_code in f_lang_codes:
    lang_code = sys_lang_code
    setting_yml['lang_code'] = lang_code
    yaml.dump( setting_yml, open( setting_path, 'w') )

if debug:
    print(lang_code, locale_path)

lang = gettext.translation(
    'funing',
    localedir = locale_path,
    languages = [ lang_code ])

lang.install()

_ = lang.gettext
