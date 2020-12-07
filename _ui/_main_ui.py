
from tkinter import ttk, Tk, OptionMenu, StringVar
from ui.main_ui import MainUI
from langcodes import Language
from _ui import change_language
import gettext

class InitUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        self.mainui.optionmenu_var.trace( 'w', self.optionmenu_optins_w )
        self.mainui.lang_combobox_var.trace( 'w' , self.lang_combobox_var_w )
        self.mainui.mainloop()

    def lang_combobox_var_w( self, *args ):
        lang = Language.find( self.mainui.lang_combobox_var.get() ).to_tag()
        change_language( lang )
        pass

    def optionmenu_optins_w(self,*args):
        pass