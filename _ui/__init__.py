
import os
import gettext
import sys
from langcodes import Language
import gettext
import locale
import tkinter as tk

default_lang_code = locale.getdefaultlocale()[0]\
    .replace('_','-')

default_lang = gettext.translation(
    'funing',
    localedir = 'locale',
    languages = [ default_lang_code ])

default_lang.install()

_ = default_lang.gettext

