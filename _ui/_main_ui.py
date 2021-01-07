

from tkinter import messagebox
import tkinter as tk
from ui.main_ui import MainUI
from langcodes import Language
import gettext
import sys,os

class MainUIdef():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        self.mainui.lang_combobox.bind('<<ComboboxSelected>>',
            self.change_language )
        self.mainui.mainloop()

    def change_language(self, lang ):

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:
            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)

        pass

