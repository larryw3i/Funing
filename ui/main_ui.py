
from tkinter import *
import tkinter as tk
from tkinter import ttk
from _ui.locale import _, lang_code
from langcodes import Language
from setting import base_dir, locale_path
import os

class MainUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title( _('Funing') )

        # frame
        self.showframe = ShowFrame( tk.Frame( self.root ) ) 

        # entry_frame
        self.entryframe = EntryFrame( tk.Frame( self.root ) )

        # lang_combobox
        self.langcombobox = LangCombobox( self.root )

    def place(self):
        self.showframe.place()
        self.entryframe.place()
        self.langcombobox.place()

    
    def mainloop(self):
        self.root.mainloop()

class LangCombobox():
    def __init__(self, frame):

        self.frame = frame
        # language_combobox
        self.lang_combobox_var = tk.StringVar( self.frame )
        self.lang_code = lang_code
        self.lang_combobox_var.set(
            Language.make( self.lang_code ).autonym()
          )
        self.lang_combobox = ttk.Combobox( self.frame ,
            textvariable = self.lang_combobox_var,
            values = tuple( self.locale_lang_display_names() )
        )

    def place(self):

        # place lang_combobox
        self.lang_combobox.grid( column = 1, row = 2 )
    
    def locale_lang_display_names( self ):
        lang_codes = os.listdir( locale_path )
        display_names = []
        for i in lang_codes:
            display_names.append( Language.make(i).autonym() )
            
        return display_names




class ShowFrame():

    def __init__( self, frame ):

        self.frame = frame
        self.show_from_optionmenus =  {
            'file':_('File'),
            'camara': _('Camara') }
        self.show_f_optionmenu_var = tk.StringVar( self.frame )
        self.show_f_optionmenu_var.set( _('Open') )
        self.show_from_optionmenu = tk.OptionMenu( 
            self.frame,
            self.show_f_optionmenu_var , 
            *self.show_from_optionmenus.values() )

        # video label
        self.vid_img_label = tk.Label( self.frame )

        # comparison_tolerance entry
        self.comparison_tolerance_entry = tk.Entry( self.frame )

        # shoot
        self.rec_button = tk.Button( self.frame, text = _('Recognize') )
    
    def place( self ):

        # place vid_img_label
        self.vid_img_label.grid( column = 0, row = 0, rowspan = 3,
            columnspan = 3 )

        # place frame
        self.show_from_optionmenu.grid( column = 0, row = 4 )
        self.rec_button.grid( column = 1, row = 4)
        self.frame.grid( column = 0, row = 0 )

        pass

class EntryFrame():
    
    def __init__(self, frame):
        self.frame = frame

        self.face_label = tk.Label( self.frame )

        self.prev_f_button = tk.Button(self.frame , \
            text = _("prev_symb"))
        self.face_num_label = tk.Label( self.frame , text = _('*/*'))
        self.next_f_button = tk.Button(self.frame , \
            text = _('next_symb'))

        self.uuid_label = tk.Label( self.frame, text = _('id') )
        self.uuid_entry = tk.Entry( self.frame , state ='disabled')

        self.name_label = tk.Label( self.frame, text = _('Name') )
        self.name_entry = tk.Entry( self.frame )

        self.DOB_label = tk.Label( self.frame, text = _('DOB') )
        self.DOB_entry = tk.Entry( self.frame )

        self.address_label = tk.Label( self.frame, text = _('Address') )
        self.address_entry = tk.Entry( self.frame )

        self.note_label = tk.Label( self.frame, text = _('Note') )
        self.note_text = tk.Text( self.frame, height = 6, width = 20 )

        # save_button
        self.save_button = tk.Button( self.frame, text = _('Save') )

    def clear_content( self ):

        self.uuid_entry['state'] = 'normal'
        self.uuid_entry.delete(0, END)
        self.uuid_entry['state'] = 'disabled'
        self.name_entry.delete(0, END)
        self.DOB_entry.delete(0, END)
        self.address_entry.delete(0, END)
        self.note_text.delete('1.0', END)
        
    def place( self ):

        # place frame
        self.face_label.grid( column = 0 , row = 0, columnspan = 2 )
        self.prev_f_button.grid( column = 0 , row = 1)
        self.face_num_label.grid( column = 1 , row = 1)
        self.next_f_button.grid( column = 2 , row = 1)

        self.uuid_label.grid( column = 0, row = 2)
        self.uuid_entry.grid( column = 1, row = 2)
        
        self.name_label.grid(column = 0, row = 3 )
        self.name_entry.grid(column = 1 ,row = 3)

        self.DOB_label.grid(column = 0, row = 4 )
        self.DOB_entry.grid(column = 1 ,row = 4 )

        self.address_label.grid(column = 0, row = 5 )
        self.address_entry.grid(column = 1 ,row = 5 )

        self.note_label.grid(column = 0, row = 6 )
        self.note_text.grid(column = 1 ,row = 6 )
        # save_button
        self.save_button.grid( column = 1, row= 7)

        self.frame.grid( column = 1, row = 0 )
