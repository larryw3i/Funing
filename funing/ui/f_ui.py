
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
from funing.ui.menubar_ui import MenubarUI
from funing.ui.r_ui import Rui
import uuid
import webbrowser

class Fnui():
    def __init__( self ):
        self.title =  _('Funing') +f'({settings.version})'
        self.root = Tk()
        self.root.title( self.title )
        self.set_menubar()
        self.get_screen_hw()
        self.root.geometry(\
        f'{int(self.screenwidth/2)}x{int(self.screenheight/2)}')
        self.menubar_ui = MenubarUI( self.root )
        self.set_fn_canvas()
        self.set_r_ui()

    def set_r_ui(self):
        self.rui= Rui(self.main_frame)
        self.rui.set_c_ui()
        pass

    def set_fn_canvas( self ):
        self.main_canvas=Canvas(self.root) 
        self.main_frame=Frame(self.main_canvas) 
        vbar=Scrollbar(self.main_canvas,orient=VERTICAL)
        vbar.configure(command=self.main_canvas.yview)
        self.main_canvas.config(yscrollcommand=vbar.set) 
        self.main_frame.pack(fill=BOTH,expand=True)
        vbar.pack(side=RIGHT)
        self.main_canvas.pack(fill=BOTH,expand=True)

    def get_screen_hw(self):
        try:self.screenwidth = self.root.winfo_screenwidth();\
            self.screenheight = self.root.winfo_screenheight()
        except: print(_('No desktop environment is detected! (^_^)')); exit()  

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
        self.preferences_menu = Menu(self.menubar)
        self.set_preferences_menubar()
        self.set_about_fn_menubar()
        pass
    
    def set_about_fn_menubar( self ):
        self.menubar.add_cascade(label=_("About"), menu=self.about_menu)
        self.about_menu.add_command(label=_("About Funing"), \
        command=self.about_fn)
        pass
    
    def set_preferences_menubar( self ):
        self.menubar.add_cascade(label=_("Preferences"), \
        menu=self.preferences_menu)
        self.preferences_menu.add_command(label=_("Settings"), \
        command=self.edit_config_yaml)
        pass

    def edit_config_yaml(self):
        self.menubar_ui.preferences_menu_ui_mainloop()
        
    def about_fn(self):
        self.menubar_ui.about_menu_ui_mainloop()

def mainloop():
    fnui = Fnui()
    fnui.mainloop()
    pass