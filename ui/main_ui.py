
from tkinter import *
import tkinter as tk
from tkinter import ttk
from _ui.locale import _, lang_code
from langcodes import Language
from setting import base_dir, locale_path, debug
from setting import comparison_tolerance as ct
import os
import re
from datetime import datetime

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
            self.frame, self.show_f_optionmenu_var , 
            *self.show_from_optionmenus.values() )

        # video label
        self.vid_img_label = tk.Label( self.frame )

        # comparison_tolerance entry
        self.ct_label = tk.Label( \
            self.frame, text = _('tolerance:') )
        self.ct_stringvar = StringVar( frame, ct )
        self.ct_entry = tk.Entry( \
            self.frame, width = 8,\
            textvariable = self.ct_stringvar )

        # shoot
        self.rec_stringvar = StringVar( frame, _('Recognize'))
        self.rec_button = tk.Button( self.frame, \
            textvariable = self.rec_stringvar )
    
    def place( self ):

        # place vid_img_label
        self.vid_img_label.grid( column = 0, row = 0, rowspan = 3,
            columnspan = 4 )

        # place frame
        self.show_from_optionmenu.grid( column = 0, row = 4 )
        self.ct_label.grid( column = 1, row = 4, sticky = E )
        self.ct_entry.grid( column = 2, row = 4, sticky = W )
        self.rec_button.grid( column = 3, row = 4)

        self.frame.grid( column = 0, row = 0 )

    def values_valid(self):
        if re.search( '^0.[0-6]\d*$', self.ct_stringvar.get() ):
            self.ct_entry['bg'] = 'white'
            is_real = True
        else:
            self.ct_entry['bg'] = 'red'
            is_real = False
        return is_real
             

class EntryFrame():
    
    def __init__(self, frame):
        self.frame = frame

        self.face_label = tk.Label( self.frame )

        self.prev_f_button = tk.Button(self.frame , \
            text = _("prev_symb"))
        self.face_num_stringvar = StringVar( frame, '*/*' )
        self.face_num_label = tk.Label( self.frame , \
            textvariable = self.face_num_stringvar  )
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

    def values_valid(self):
        is_real = True
        if len(self.name_entry.get()) < 1:\
                self.name_entry['bg'] = 'red';      is_real = False
        else:   self.name_entry['bg'] = 'white'
        
        try:    datetime.strptime( self.DOB_entry.get(), '%Y-%m-%d')
        except Exception as e: 
            self.DOB_entry['bg'] = 'red';       is_real = False
            if debug:
                print( e )

        if len(self.address_entry.get()) < 1:\
                self.address_entry['bg'] = 'red';   is_real = False
        else:   self.address_entry['bg'] = 'white'

        if len(self.note_text.get(1.0, 'end')) < 1:\
                self.note_text['bg'] = 'red';       is_real = False
        else:   self.note_text['bg'] = 'white'
        
        return is_real
