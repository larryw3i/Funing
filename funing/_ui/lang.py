
import gettext
import locale
import os
import sys

import yaml

from funing import settings

sys_lang_code = locale.getdefaultlocale()[0]

if sys_lang_code not in settings.locale_langcodes:
    sys_lang_code = 'en_US'

if settings.debug():
    print(sys_lang_code, settings.locale_path)

lang = gettext.translation(
    'funing', localedir=settings.locale_path,
    languages=[sys_lang_code])

lang.install()

_ = lang.gettext
