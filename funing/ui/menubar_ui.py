
from tkinter import *
import os
from funing import settings
import webbrowser

class MenubarUI():
    def __init__(self, root ):
        self.root = root
        self.about_tl = None
        self.settings_tl = None
        pass
    
    def about_menu_ui_mainloop(self):
        if self.about_tl == None:
            self.about_tl = Toplevel(borderwidth = 10)
            self.about_tl.title('About Funing')
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

    def preferences_menu_ui_mainloop(self):
        if self.settings_tl == None:
            self.settings_tl = Toplevel(borderwidth = 10)
            self.settings_tl.title(_('Edit config.yaml'))
            self.settings_tl.resizable( 0,0 )
            self.edit_frame = Frame( self.settings_tl)
            self.save_frame = Frame( self.settings_tl)
            self.edit_sb = Scrollbar(self.edit_frame, orient=VERTICAL)  
            self.edit_text = Text( self.edit_frame, yscrollcommand = \
            self.edit_sb.set )
            self.edit_text_insert()
            self.save_btn = Button( self.save_frame, text = _("Save") )
            self.edit_sb.config(command = self.edit_text.yview)  
            self.save_btn = Button( self.settings_tl, text =_('Save') )
            self.edit_text.pack(side=LEFT,fill=Y)
            self.edit_sb.pack(side=RIGHT,fill=Y)
            self.save_btn.pack(side=BOTTOM)
            self.edit_frame.pack()
            self.save_frame.pack()
            self.settings_tl.mainloop()
        else:
            self.settings_tl.destroy()
            self.settings_tl = None
        pass
    
    def edit_text_insert(self):
        config_txt = open( settings.config_path ).read()
        self.edit_text.insert( "1.0", config_txt)
        pass
