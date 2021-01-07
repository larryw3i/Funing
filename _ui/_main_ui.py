

from tkinter import messagebox
import tkinter as tk
from ui.main_ui import MainUI
from langcodes import Language
import gettext
import sys

class MainUIdef():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        # self.mainui.optionmenu_var.trace( 'w', self.optionmenu_optins_w )
        # self.mainui.lang_combobox_var.trace( 'w' , self.lang_combobox_var_w )

        # self.restartapp_ask_toplevel = None
        # self.restartapp_ask_toplevel_exists = True 
        self.mainui.lang_combobox.bind('<<ComboboxSelected>>',
            self.change_language )
        self.mainui.mainloop()

    # def lang_combobox_var_w( self, *args ):
    #     lang = Language.find( self.mainui.lang_combobox_var.get() ).to_tag()
    #     self.change_language( lang )
    #     pass


    def change_language(self, lang ):

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:
            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)

        # self.restartapp_ask_toplevel = tk.Toplevel( self.mainui.root )

        # ask_label = tk.Label( self.restartapp_ask_toplevel, 
        #     text = _('Restart Funing Now?') )
        # yes_button  = tk.Button( self.restartapp_ask_toplevel, 
        #     text = _('Yes'),
        #     command = self.restartapp )
        # no_button  = tk.Button( self.restartapp_ask_toplevel , 
        #     text = _('No') ,
        #     command = self.close_ask_toplevel )

        # ask_label.grid(column = 0, row = 0 ,columnspan = 2)
        # yes_button.grid(column = 0, row = 1 )
        # no_button.grid(column = 1, row = 1  )
        
        # self.restartapp_ask_toplevel.resizable(0, 0)
        # if self.restartapp_ask_toplevel_exists :
        #     self.restartapp_ask_toplevel.update()
        #     self.restartapp_ask_toplevel.deifonify()
        # else :
        #     self.restartapp_ask_toplevel.mainloop()

        pass

    # def restartapp(self):
    #     sys_executable = sys.executable
    #     os.execl(sys_executable, sys_executable, * sys.argv)

    # def close_ask_toplevel(self):
    #     self.restartapp_ask_toplevel.withdraw()

    def optionmenu_optins_w(self,*args):
        pass