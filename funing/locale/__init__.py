import gettext
import locale
import os
import sys

sys_lang_code = locale.getdefaultlocale()[0]
locale_path = locale_dir_path = os.path.abspath(os.path.dirname(__file__))
locale_langcodes = [
    d
    for d in os.listdir(locale_path)
    if os.path.isdir(os.path.join(locale_path, d))
]

if sys_lang_code not in locale_langcodes:
    sys_lang_code = "en_US"

lang = gettext.translation(
    "primaryschool", localedir=locale_path, languages=[sys_lang_code]
)

lang.install()

_ = lang.gettext

t = T = _
