
from pony.orm import *
from tkinter import messagebox
import tkinter as tk
from ui.main_ui import MainUI
from langcodes import Language
import gettext
import sys,os
from model import funing_m as fm
from model.funing_m import FuningData as fd
import  tkinter.filedialog as tkf
import cv2

class IRU():
    def __init__(self, video_source = 0 ):
        self.vid = cv2.VideoCapture( self.video_source )
        if not self.vid.isOpened():
            messagebox.showerror( 
                _('Unable to open video source'), 
                self.video_source )
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:                
               return (ret, None ) 
        else:
            return (ret, None)


class MainUIdef():
    def __init__(self):
        self.mainui = MainUI()
        self.iru = None
        self.mainui.place()

        self.video_source = None
        self.vid = None

        self.mainui.lang_combobox.bind(
            '<<ComboboxSelected>>',
            self.change_language )
        
        self.mainui.show_f_optionmenu_var.trace(
            'w', self.show_from )

        self.mainui.mainloop()

    def show_from( self, *args  ):
        keys =  self.mainui.show_from_optionmenus.keys()
        values = self.mainui.show_from_optionmenus.values()
        value = self.mainui.show_f_optionmenu_var.get()        
        show_f = list(keys)[ list( values ).index( value )]
        
        if show_f == 'file':
            self.video_source = tkf.askopenfile(
                title = _('Select a file'),
                initialdir = '~/Videos'
            )

        if show_f == 'camara':
            self.video_source = 0
        
        self.play_video( self.video_source )

    def play_video( self , video_source ):
        self.iru = IRU( video_source )

        


    @db_session
    def change_language(self, lang ):

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:

            lang_code_exists = count( d for d in fm.FuningData ) > 0

            lang_display_name = self.mainui.lang_combobox_var.get()
            lang_code = Language.find( lang_display_name ).to_tag()

            if not lang_code_exists:
                fd( lang_code = lang_code )
            else :
                select( d for d in fm.FuningData ).first()\
                    .lang_code = lang_code
            
            commit()

            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)

        pass

