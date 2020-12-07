
import os
import gettext
import sys
from langcodes import Language
import gettext
import locale
from tkinter import messagebox

default_lang_code = locale.getdefaultlocale()[0]\
    .replace('_','-')

default_lang = gettext.translation(
    'funing',
    localedir = 'locale',
    languages = [ default_lang_code ])

default_lang.install()

_ = default_lang.gettext


def change_language( lang ):
    is_restart = messagebox.askyesno(
        message = _('Restart Funing now?'),
        icon='question',
        title='Restart Funing'
    )
    if is_restart:
        sys_executable = sys.executable
        os.execl(sys_executable, sys_executable, * sys.argv)
    pass

def locale_lang_display_names():
    lang_codes = os.listdir('locale/')
    display_names = []
    for i in lang_codes:
        display_names.append( Language.make(i).display_name(i) )
        
    return display_names


if __name__ == '__main__':

    pass