
from tkinter import *
import os
from funing import settings
import webbrowser

class MenubarUI():
    def __init__(self, root ):
        self.root = root
        self.about_tl = None; 
        pass
    
    def about_menu_ui_mainloop(self):
        if self.about_tl == None:
            self.about_tl = Toplevel(borderwidth = 10)
            self.about_tl.resizable(0,0)
            Label( self.about_tl, text =_('Funing'), font=("", 25)).pack()
            Label(  self.about_tl, text = settings.version ).pack()
            self.source_page_label = Label(self.about_tl,text=\
            settings.source_page,fg="blue", cursor="hand2")
            self.source_page_label.bind("<Button-1>",lambda e: \
            webbrowser.open_new(settings.source_page ))
            self.source_page_label.pack()
            Label(self.about_tl,text=_('Licensed under the MIT license') ).pack()
            self.about_tl.mainloop()
        else:
            self.about_tl.destroy()
            self.about_tl = None
        pass
