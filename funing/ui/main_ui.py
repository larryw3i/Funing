
import os
import re
import uuid
from tkinter import *
from tkinter.ttk import *
from funing._ui.lang import _
# from langcodes import Language
from funing import settings
from datetime import datetime

class MainUI():
    def __init__(self):
        self.root = Tk()
        self.root.title( _('Funing')+'(' + settings.version+ ')' )
        # frame
        self.showframe = ShowFrame( Frame( self.root ) ) 
        # entry_frame
        self.infoframe = InfoFrame( Frame( self.root ) )
        # rbmix_frame
        self.rbmixframe = RBMixFrame( Frame( self.root ))
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
        self.vid_frame_label = Label( self.frame )

        self.showf_sv = StringVar( self.frame )
        self.showf_entry = Entry( \
            self.frame , width = 10, textvariable = self.showf_sv)
        self.showf_go_btn = Button(self.frame, text = _('GO') )

        self.showf_t_dict =  { 'file':_('File'), 'camera': _('Camera') }
        self.showf_optionmenu_sv = StringVar(self.frame, value = _('Open'))
        self.showf_optionmenu = OptionMenu( self.frame, \
            self.showf_optionmenu_sv , *self.showf_t_dict.values() )

        self.pp_sv = StringVar( frame, _('Pause'))
        self.pp_btn = Button( self.frame, \
            textvariable = self.pp_sv )

        self.rec_sv = StringVar( frame, _('Recognize'))
        self.rec_btn = Button( self.frame, \
            textvariable = self.rec_sv )

        self.pick_sv = StringVar( frame, _('Pick'))
        self.pick_btn = Button( self.frame, \
            textvariable = self.pick_sv )
    
    def place( self ):

        # place vid_frame_label
        self.vid_frame_label.grid( column = 0, row = 0, rowspan = 3,
            columnspan = 7 )

        self.showf_entry.grid( column = 0, row = 4, sticky = E)
        self.showf_go_btn.grid( column = 1, row = 4, sticky = W)
        self.showf_optionmenu.grid( column = 2, row = 4 , sticky = W)
        self.pp_btn.grid( column = 3, row = 4)
        self.rec_btn.grid( column = 4, row = 4)
        
        self.pick_btn.grid( column = 5, row = 4 )        
        # place frame
        self.frame.grid( column = 0, row = 0 )             

class InfoFrame():
    def __init__(self, frame):
        self.frame = frame
        self.face_show_frame = Frame( self.frame )
        self.info_enter_frame = Frame( self.frame )
        self.training_tip_label_is_hidden = True

        self.faces_frame = Frame( self.frame )

        self.ft_sb = Scrollbar(self.info_enter_frame, orient=VERTICAL)
        self.face_text = Text( self.info_enter_frame,  \
        yscrollcommand = self.ft_sb.set)  
        self.face_text_tip_label = Label(self.frame, text = \
        _('Write it with certain rules so that you can analyze it later'),\
        font=('', 10) )
        self.save_btn = Button( self.frame, text = _("Save") )
        self.training_tip_label = Label(self.frame, text = _('Training. . .') )
        self.ft_sb.config(command = self.face_text.yview)

    def show_or_hide_training_tip_label( self ):
        if self.training_tip_label_is_hidden:
            self.training_tip_label.grid( column = 2, row = 6 )
            self.training_tip_label_is_hidden = False
        else:
            self.training_tip_label.grid_remove()
            self.training_tip_label_is_hidden = True
        

    def place( self ):
        self.face_text.pack(side=LEFT,fill=Y)
        self.ft_sb.pack(side=RIGHT,fill=Y)
        self.faces_frame.grid( column = 0 , row = 0, columnspan = 5 )
        self.info_enter_frame.grid( column = 0, row = 3, columnspan = 5)
        self.face_text_tip_label.grid(column = 0, row = 4,  columnspan = 5)
        self.save_btn.grid( column = 2, row = 5 )
        self.frame.grid( column = 1, row = 0 )
        pass

class RBMixFrame():
    def __init__(self, frame):
        self.frame = frame
        self.about_fn_btn = Button(self.frame, text=_('About Funing') )
    def place(self):
        self.about_fn_btn.grid( column = 0, row = 0, sticky = NE )
        self.frame.grid( column = 2, row = 2, )
    