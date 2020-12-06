
import gettext
import locale

default_lang_code = locale.getdefaultlocale()[0]

t = gettext.translation(
    'funing',
    localedir = 'locale',
    languages = [ default_lang_code ])

_ = t.gettext