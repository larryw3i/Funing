
import tkinter as tk
from tkinter import ttk
from _ui import _, default_lang_code
from _ui import _main_ui
from _ui import locale_lang_display_names
from langcodes import Language

class MainUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title( _('Funing') )
        # show_frame
        self.show_frame = ttk.Frame( self.root )
        self.shoot_button = ttk.Button( self.show_frame, text = _('Shoot') )
        self.show_from_optionmenus =  {
            'file':_('File'),
            'camara': _('Camara') }
        self.optionmenu_var = tk.StringVar( self.root )
        self.optionmenu_var.set( _('Open') )
        self.show_from_optionmenu = tk.OptionMenu( 
            self.show_frame,
            self.optionmenu_var, 
            *self.show_from_optionmenus.values() )

        # entry_frame
        self.entry_frame = ttk.Frame( self.root )
        self.name_label = ttk.Label( self.entry_frame, text = _('Name') )
        self.name_entry = ttk.Entry( self.entry_frame )

        self.DOB_label = ttk.Label( self.entry_frame, text = _('DOB') )
        self.DOB_entry = ttk.Entry( self.entry_frame )

        self.address_label = ttk.Label( self.entry_frame, text = _('Address') )
        self.address_entry = ttk.Entry( self.entry_frame )

        self.note_label = ttk.Label( self.entry_frame, text = _('Note') )
        self.note_entry = ttk.Entry( self.entry_frame )

        # language_combobox
        self.lang_combobox_var = tk.StringVar( self.root )
        self.lang_code = default_lang_code
        self.lang_combobox_var.set(
            Language.make( self.lang_code ).display_name( self.lang_code)
          )
        self.lang_combobox = ttk.Combobox(
            self.root,
            textvariable = self.lang_combobox_var,
            values = tuple( locale_lang_display_names() )
        )


    def place(self):
        # place show_frame
        self.show_from_optionmenu.grid( column = 0, row = 1 )
        self.shoot_button.grid( column = 1, row = 1 )
        self.show_frame.grid( column = 0, row = 0 )

        # place entry_frame
        self.name_label.grid(column = 0, row = 0 )
        self.name_entry.grid(column = 1 ,row = 0)

        self.DOB_label.grid(column = 0, row = 1 )
        self.DOB_entry.grid(column = 1 ,row = 1 )

        self.address_label.grid(column = 0, row = 2 )
        self.address_entry.grid(column = 1 ,row = 2 )

        self.note_label.grid(column = 0, row = 3 )
        self.note_entry.grid(column = 1 ,row = 3 )

        self.entry_frame.grid( column = 1, row = 0 )

        # place lang_combobox
        self.lang_combobox.grid( column = 1, row = 2 )
    
    def mainloop(self):
        self.root.mainloop()
