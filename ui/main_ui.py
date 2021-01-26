

import tkinter as tk
from tkinter import ttk
from _ui import _, lang_code
from langcodes import Language
import os

class MainUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title( _('Funing') )


        
        # show_frame
        self.show_frame = tk.Frame( self.root )
        self.show_from_optionmenus =  {
            'file':_('File'),
            'camara': _('Camara') }
        self.show_f_optionmenu_var = tk.StringVar( self.root )
        self.show_f_optionmenu_var.set( _('Open') )
        self.show_from_optionmenu = tk.OptionMenu( 
            self.show_frame,
            self.show_f_optionmenu_var , 
            *self.show_from_optionmenus.values() )

        # video label
        self.vid_label = tk.Label( self.show_frame )

        # shoot
        self.pause_button = tk.Button( self.show_frame, text = _('Pause') )

        # entry_frame
        self.entry_frame = tk.Frame( self.root )
        self.face_label = tk.Label( self.entry_frame )
        self.name_label = tk.Label( self.entry_frame, text = _('Name') )
        self.name_entry = tk.Entry( self.entry_frame )

        self.DOB_label = tk.Label( self.entry_frame, text = _('DOB') )
        self.DOB_entry = tk.Entry( self.entry_frame )

        self.address_label = tk.Label( self.entry_frame, text = _('Address') )
        self.address_entry = tk.Entry( self.entry_frame )

        self.note_label = tk.Label( self.entry_frame, text = _('Note') )
        self.note_text = tk.Text( self.entry_frame, height = 6, width = 20 )

        # language_combobox
        self.lang_combobox_var = tk.StringVar( self.root )
        self.lang_code = lang_code
        self.lang_combobox_var.set(
            Language.make( self.lang_code ).display_name( self.lang_code)
          )
        self.lang_combobox = ttk.Combobox(
            self.root,
            textvariable = self.lang_combobox_var,
            values = tuple( self.locale_lang_display_names() )
        )

        # save_button
        self.save_button = tk.Button( self.entry_frame, text = _('Save') )

    def place(self):

        # place vid_label
        self.vid_label.grid( column = 0, row = 0, rowspan = 3,
            columnspan = 3 )

        # place show_frame
        self.show_from_optionmenu.grid( column = 0, row = 4 )
        self.pause_button.grid( column = 1, row = 4)
        self.show_frame.grid( column = 0, row = 0 )

        # place entry_frame

        self.face_label.grid( column = 0 , row = 0, columnspan = 2 )
        
        self.name_label.grid(column = 0, row = 1 )
        self.name_entry.grid(column = 1 ,row = 1)

        self.DOB_label.grid(column = 0, row = 2 )
        self.DOB_entry.grid(column = 1 ,row = 2 )

        self.address_label.grid(column = 0, row = 3 )
        self.address_entry.grid(column = 1 ,row = 3 )

        self.note_label.grid(column = 0, row = 4 )
        self.note_text.grid(column = 1 ,row = 4 )
        # save_button
        self.save_button.grid( column = 1, row= 5)

        self.entry_frame.grid( column = 1, row = 0 )

        # place lang_combobox
        self.lang_combobox.grid( column = 1, row = 2 )
    
    def mainloop(self):
        self.root.mainloop()


    def locale_lang_display_names( self ):
        lang_codes = os.listdir('locale/')
        display_names = []
        for i in lang_codes:
            display_names.append( Language.make(i).display_name(i) )
            
        return display_names

