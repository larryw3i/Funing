
import os
import gettext
from .settings import _
from langcodes import Language
def change_language( lang ):

    t = gettext.translation(
        'funing',
        localedir = 'locale',
        languages = [ lang ])

    _ = t.gettext
    pass

def locale_lang_display_names():
    lang_codes = os.listdir('locale/')
    display_names = []
    for i in lang_codes:
        i = i.replace('_','-')
        display_names.append( Language.make(i).display_name(i) )
    print( display_names )
    return display_names


if __name__ == '__main__':

    pass