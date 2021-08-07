
import tkinter as tk
from tkinter import ttk
from tkinter import *
from funing._ui.lang import _
from langcodes import Language
from funing import settings
import os
import re
from datetime import datetime
import uuid

ct = settings.comparison_tolerance

class MainUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title( _('Funing')+'(' + settings.version+ ')' )
        # frame
        self.showframe = ShowFrame( tk.Frame( self.root ) ) 
        # entry_frame
        self.infoframe = InfoFrame( tk.Frame( self.root ) )
        # rbmix_frame
        self.rbmixframe = RBMixFrame( tk.Frame( self.root ))
    def place(self):
        self.showframe.place()
        self.infoframe.place()
        self.rbmixframe.place()
    
    def mainloop(self):
        self.root.mainloop()
    
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
        # self.ct_label = tk.Label( \
        #     self.frame, text = _('tolerance') + ':' )
        # self.ct_stringvar = tk.StringVar( frame, ct )
        # self.ct_entry = tk.Entry( self.frame, width = 8,\
        #     textvariable = self.ct_stringvar )

        # shoot
        self.pp_sv = tk.StringVar( frame, _('Pause'))
        self.pp_btn = tk.Button( self.frame, \
            textvariable = self.pp_sv )

        self.rec_sv = tk.StringVar( frame, _('Recognize'))
        self.rec_btn = tk.Button( self.frame, \
            textvariable = self.rec_sv )

        self.pick_sv = tk.StringVar( frame, _('Pick'))
        self.pick_btn = tk.Button( self.frame, \
            textvariable = self.pick_sv )
    
    def place( self ):

        # place vid_frame_label
        self.vid_frame_label.grid( column = 0, row = 0, rowspan = 3,
            columnspan = 7 )

        self.showf_entry.grid( column = 0, row = 4, sticky = E)
        self.showf_go_btn.grid( column = 1, row = 4, sticky = W)
        self.showf_optionmenu.grid( column = 2, row = 4 , sticky = W)
        # self.ct_label.grid( column = 3, row = 4, sticky = E )
        # self.ct_entry.grid( column = 4, row = 4, sticky = W )
        self.pp_btn.grid( column = 3, row = 4)
        self.rec_btn.grid( column = 4, row = 4)
        
        self.pick_btn.grid( column = 5, row = 4 )        
        # place frame
        self.frame.grid( column = 0, row = 0 )             

class InfoFrame():
    def __init__(self, frame):
        self.frame = frame
        self.face_show_frame = tk.Frame( self.frame )
        self.info_enter_frame = tk.Frame( self.frame )

        self.faces_frame = tk.Frame( self.frame )

        # self.curf_label = tk.Label( self.face_show_frame )
        # self.opt_frame =  tk.Frame( self.frame )
        # self.prevf_btn = tk.Button( self.opt_frame, text = _('prev_symb'))
        # self.num_label = tk.Label( self.opt_frame, text = _('*/*') )
        # self.nextf_btn = tk.Button( self.opt_frame, text = _('next_symb'))
        self.ft_sb = tk.Scrollbar(self.info_enter_frame, orient=VERTICAL)
        self.face_text = Text( self.info_enter_frame,  \
        yscrollcommand = self.ft_sb.set)  
        self.face_text_tip_label = Label(self.frame, text = \
        _('Write it with certain rules so that you can analyze it later'),\
        font=('', 10) )
        self.save_btn = tk.Button( self.frame, text = _("Save") )
        self.ft_sb.config(command = self.face_text.yview)      
    def place( self ):
        # self.curf_label.pack(side = LEFT)
        # self.prevf_btn.pack(side = LEFT)
        # self.num_label.pack(side=LEFT)
        # self.nextf_btn.pack(side = LEFT)
        self.face_text.pack(side=tk.LEFT,fill=tk.Y)
        self.ft_sb.pack(side=tk.RIGHT,fill=tk.Y)
        self.faces_frame.grid( column = 0 , row = 0, columnspan = 5 )
        # self.face_show_frame.grid( column = 0, row = 1, columnspan = 5)
        # self.opt_frame.grid( column = 0, row = 2, columnspan = 5)
        self.info_enter_frame.grid( column = 0, row = 3, columnspan = 5)
        self.face_text_tip_label.grid(column = 0, row = 4,  columnspan = 5)
        self.save_btn.grid( column = 2, row = 5 )
        self.frame.grid( column = 1, row = 0 )
        pass

class RBMixFrame():
    def __init__(self, frame):
        self.frame = frame
        self.about_fn_btn = Button(self.frame, text=_('About Funing') )        
        # language_combobox
        self.lang_combobox_var = tk.StringVar( self.frame )
        self.lang_code = settings.lang_code
        self.lang_combobox_var.set(
            Language.make( self.lang_code.replace('_','-') ).autonym()
          )
        self.lang_combobox = ttk.Combobox( self.frame ,
            textvariable = self.lang_combobox_var,
            values = tuple( self.locale_lang_display_names() ),
            state = "readonly"
        )
    def locale_lang_display_names( self ):
        display_names = []
        for i in settings.locale_langcodes:
            display_names.append( Language.make( i.replace('_','-')).autonym() )
        return display_names

    def place(self):
        self.about_fn_btn.grid( column = 0, row = 0, sticky = NE )
        # place lang_combobox
        self.lang_combobox.grid( column = 0, row = 1, sticky = NE )
        self.frame.grid( column = 2, row = 2, )
    