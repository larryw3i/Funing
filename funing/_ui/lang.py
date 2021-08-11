
import os
import sys
import gettext
import locale
from funing import settings
import yaml

import os
from funing import settings

f_mo_path  = os.path.join(settings.locale_path, 'en_US' ,\
'LC_MESSAGES', 'funing.mo' )

if not os.path.exists( f_mo_path ):
    from funing._ui import Enjoy
    Enjoy().msgfmt()
    
sys_lang_code = locale.getdefaultlocale()[0]

if not sys_lang_code in settings.locale_langcodes:
    sys_lang_code='en_US'

if settings.debug():
    print( sys_lang_code, settings.locale_path)

lang = gettext.translation(
    'funing', localedir = settings.locale_path,
    languages = [ sys_lang_code ])

lang.install()

_ = lang.gettext
