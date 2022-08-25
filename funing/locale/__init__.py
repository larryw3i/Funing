import gettext
import locale
import os
import sys

from funing.settings import *

sys_lang_code = locale.getdefaultlocale()[0]
locale_path = locale_dir_path = os.path.abspath(os.path.dirname(__file__))
mo0_path = os.path.join(locale_path, "en_US", "LC_MESSAGES", "funing.mo")


def default_gettext(self, *args):
    return args


if os.path.exists(mo0_path):
    locale_langcodes = [
        d
        for d in os.listdir(locale_path)
        if os.path.isdir(os.path.join(locale_path, d))
    ]

    if sys_lang_code not in locale_langcodes:
        sys_lang_code = "en_US"

    lang = gettext.translation(
        app_name, localedir=locale_path, languages=[sys_lang_code]
    )

    lang.install()

    _ = lang.gettext
else:
    print("Message files are NOT compiled.")
    _ = default_gettext

t = T = _
