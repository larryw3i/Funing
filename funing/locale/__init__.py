
import os
from funing import settings

f_mo_path  = os.path.join(settings.locale_path, settings.locale_langcodes[0] ,\
'LC_MESSAGES', 'funing.mo' )
if not os.path.exists( f_mo_path ):
    from funing._fui import Enjoy
    Enjoy().msgfmt()