
from pony.orm import *
from tkinter import messagebox
import tkinter as tk
from ui.main_ui import MainUI
from langcodes import Language
import gettext
import sys,os
from model import funing_m as fm
from model.funing_m import FuningData as fd

class MainUIdef():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        self.mainui.lang_combobox.bind(
            '<<ComboboxSelected>>',
            self.change_language )
        self.mainui.mainloop()
    @db_session    
    def change_language(self, lang ):

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:

            lang_code_exists = count( d for d in fm.FuningData ) > 0

            lang_display_name = self.mainui.lang_combobox_var.get()
            lang_code = Language.find( lang_display_name ).to_tag()

            if not lang_code_exists:
                fd( lang_code = lang_code )
            else :
                select( d for d in fm.FuningData ).first()\
                    .lang_code = lang_code
            
            commit()

            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)

        pass

