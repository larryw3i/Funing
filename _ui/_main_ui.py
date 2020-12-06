
from tkinter import ttk, Tk, OptionMenu, StringVar
from ui.main_ui import MainUI

class InitUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        self.mainui.optionmenu_var.trace( 'w', self.optionmenu_optins_w )
        self.mainui.mainloop()

    def optionmenu_optins_w(self,*args):
        print( self.mainui.optionmenu_optins.get() )