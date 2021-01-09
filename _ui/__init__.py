
import os
import gettext
import sys
from langcodes import Language
import gettext
import locale
import tkinter as tk
from pony.orm import *
from model import funing_m as fm

lang_code = locale.getdefaultlocale()[0]\
    .replace('_','-')
with db_session:
    fd_first = select( d for d in fm.FuningData ).first()
    lang_code = lang_code if fd_first is None else fd_first.lang_code

default_lang = gettext.translation(
    'funing',
    localedir = 'locale',
    languages = [ lang_code ])

default_lang.install()

_ = default_lang.gettext

