
from tkinter import Tk, Frame, Menu
import tkinter as tk
from tkinter import ttk
from tkinter import *
from funing.locale.lang import _
from langcodes import Language
from funing import settings
import os
import re
from datetime import datetime
from funing.ui.menubar import MenubarUI
import uuid

class Fnui():
    def __init__( self ):
        self.title =  _('Funing') +f'({settings.version})'
        self.root = Tk()
        self.root.title( self.title )
        self.set_menubar()
        self.menubar_ui = MenubarUI( self.root )
    
    def set_indicator(self):
        pass
    
    def mainloop(self):
        self.root.mainloop()
    
    def pack( self ):
        pass

    def pack_forget( self):
        pass
            

    def set_menubar(self):
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)
        self.about_menu = Menu(self.menubar)
        self.set_about_fn_menubar()
        pass
    
    def set_about_fn_menubar( self ):
        self.about_menu.add_command(label=_("About Funing"), command=self.about_fn)
        self.menubar.add_cascade(label=_("About"), menu=self.about_menu)
        pass

    def about_fn(self):
            self.menubar_ui.about_menu_ui_mainloop()