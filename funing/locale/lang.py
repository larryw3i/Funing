
import os
import sys
from langcodes import Language
import gettext
import locale
from funing import settings
import yaml

sys_lang_code = locale.getdefaultlocale()[0]\
    .replace('_','-')

if settings.lang_code == 'en-US' and \
    sys_lang_code != settings.lang_code and \
    sys_lang_code in settings.locale_langcodes:
    settings.config_yml['lang_code'] = settings.lang_code = sys_lang_code
    yaml.dump( settings.config_yml, open( settings.config_path, 'w') )

if settings.debug:
    print( settings.lang_code, settings.locale_path)

lang = gettext.translation(
    'funing',
    localedir = settings.locale_path,
    languages = [ settings.lang_code ])
lang.install()
_ = lang.gettext
