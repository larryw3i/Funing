
from tkinter import *
import tkinter as tk
from tkinter import ttk
from flocale.locale import _, lang_code
from langcodes import Language
from setting import base_dir, locale_path, debug, f_lang_codes, version
from setting import comparison_tolerance as ct
import os
import re
from datetime import datetime
import uuid

class MainUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title( _('Funing')+' ' + version )
        # frame
        self.showframe = ShowFrame( tk.Frame( self.root ) ) 
        # entry_frame
        self.entryframe = EntryFrame( tk.Frame( self.root ) )
        # lang_combobox
        self.langcombobox = LangCombobox( self.root )        
        # addinfoframe
        self.addinfoframe = AddInfoFrame( tk.Frame( self.root ) )

    def place(self):
        self.showframe.place()
        self.entryframe.place()
        self.langcombobox.place()
        self.addinfoframe.place()
    
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
            values = tuple( self.locale_lang_display_names() ),
            state = "readonly"
        )

    def place(self):
        # place lang_combobox
        self.lang_combobox.grid( column = 3, row = 2, sticky = NE )
    
    def locale_lang_display_names( self ):
        display_names = []
        for i in f_lang_codes:
            display_names.append( Language.make(i).autonym() )
            
        return display_names



class ShowFrame():

    def __init__( self, frame ):

        self.frame = frame

        # video label
        self.vid_frame_label = tk.Label( self.frame )

        self.showf_sv = tk.StringVar( self.frame )
        self.showf_entry = tk.Entry( \
            self.frame , width = 10, textvariable = self.showf_sv)
        self.showf_go_btn = tk.Button(self.frame, text = _('GO') )

        self.showf_t_dict =  { 'file':_('File'), 'camera': _('Camera') }
        self.showf_optionmenu_sv = tk.StringVar(self.frame, value = _('Open'))
        self.showf_optionmenu = tk.OptionMenu( self.frame, \
            self.showf_optionmenu_sv , *self.showf_t_dict.values() )

        # comparison_tolerance entry
        self.ct_label = tk.Label( \
            self.frame, text = _('tolerance') + ':' )
        self.ct_stringvar = StringVar( frame, ct )
        self.ct_entry = tk.Entry( self.frame, width = 8,\
            textvariable = self.ct_stringvar )

        # shoot
        self.rec_stringvar = StringVar( frame, _('Recognize'))
        self.rec_button = tk.Button( self.frame, \
            textvariable = self.rec_stringvar )
    
    def place( self ):

        # place vid_frame_label
        self.vid_frame_label.grid( column = 0, row = 0, rowspan = 3,
            columnspan = 6 )

        self.showf_entry.grid( column = 0, row = 4, sticky = E)
        self.showf_go_btn.grid( column = 1, row = 4, sticky = W)
        self.showf_optionmenu.grid( column = 2, row = 4 , sticky = W)
        self.ct_label.grid( column = 3, row = 4, sticky = E )
        self.ct_entry.grid( column = 4, row = 4, sticky = W )
        self.rec_button.grid( column = 5, row = 4)
        
        # place frame
        self.frame.grid( column = 0, row = 0 )

             

class AddInfoFrame():
    def __init__(self, frame):
        self.frame = frame
        self.ins_vars = {}
        self.add_rf_button = tk.Button( self.frame, \
            text = _('Add information') )
        
    def place( self ):
        self.add_rf_button.pack( side = BOTTOM )
        self.frame.grid( column = 3, row = 0, sticky = S )
        pass

class EntryFrame():
    
    def __init__(self, frame):
        self.frame = frame

        self.face_label = tk.Label( self.frame )

        self.prev_f_button = tk.Button(self.frame , \
            text = _("prev_symb"))
        self.face_num_stringvar = StringVar( self.frame, '*/*' )
        self.face_num_label = tk.Label( self.frame , \
            textvariable = self.face_num_stringvar  )
        self.next_f_button = tk.Button(self.frame , \
            text = _('next_symb'))

        self.uuid_label = tk.Label( self.frame, text = _('id') )
        self.uuid_entry = tk.Entry( self.frame , state ='disabled')

        self.name_label = tk.Label( self.frame, text = _('Name') )
        self.name_entry = tk.Entry( self.frame )
        
        self.gender_label = tk.Label( self.frame, text = _('Gender') )
        self.gender_entry = tk.Entry( self.frame )

        self.DOB_label = tk.Label( self.frame, text = _('DOB') )
        self.DOB_entry = tk.Entry( self.frame )

        self.address_label = tk.Label( self.frame, text = _('Address') )
        self.address_entry = tk.Entry( self.frame )

        self.cmt_label = tk.Label( self.frame, text = _('Comment') )
        self.cmt_text = tk.Text( self.frame, height = 6, width = 20 )

        # save_button
        self.save_button = tk.Button( self.frame, text = _('Save') )

    def clear_content( self ):

        self.uuid_entry['state'] = 'normal'
        self.uuid_entry.delete(0, END)
        self.uuid_entry['state'] = 'disabled'
        self.name_entry.delete(0, END)
        self.DOB_entry.delete(0, END)
        self.address_entry.delete(0, END)
        self.cmt_text.delete('1.0', END)
        
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
        
        self.gender_label.grid(column = 0, row = 4 )
        self.gender_entry.grid(column = 1 ,row = 4 )
        
        self.DOB_label.grid(column = 0, row = 5 )
        self.DOB_entry.grid(column = 1 ,row = 5 )

        self.address_label.grid(column = 0, row = 6 )
        self.address_entry.grid(column = 1 ,row = 6 )

        self.cmt_label.grid(column = 0, row = 7 )
        self.cmt_text.grid(column = 1 ,row = 7 )
        # save_button
        self.save_button.grid( column = 1, row= 8)
        self.frame.grid( column = 1, row = 0, sticky = N )
