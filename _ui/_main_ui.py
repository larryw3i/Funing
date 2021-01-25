
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
from PIL import Image , ImageTk
import dlib
import face_recognition

class IRU():
    def __init__(self, video_source = 0 ):
        self.video_source = video_source
        self.vid = cv2.VideoCapture( self.video_source )
        self.resize_rate = 0.25

        if not self.vid.isOpened():
            messagebox.showerror( 
                _('Unable to open video source'), 
                self.video_source )
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.f_top = 0
        self.f_right = 0
        self.f_bottom  = 0
        self.f_left = 0
        self.face_locations = []
    
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                small_frame = cv2.resize( frame, (0, 0), \
                    fx=self.resize_rate, fy=self.resize_rate)  
                
                self.face_locations = \
                    face_recognition.face_locations( small_frame )

                for top, right, bottom, left in self.face_locations:
                    self.f_top = int(top/self.resize_rate)
                    self.f_right = int(right/self.resize_rate)
                    self.f_bottom = int(bottom/self.resize_rate)
                    self.f_left = int(left/self.resize_rate)
                    cv2.rectangle( frame, \
                        (self.f_left, self.f_top), \
                        (self.f_right, self.f_bottom), (0, 0, 255), 2)

                return (ret, frame)

            else:                
               return (ret, None ) 
        else:
            return (None, None)
        
    def release( self ):
        self.vid.release()


class _MainUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy )

        self.iru = None
        self.video_source = None
        self.vid = None
        self.vid_frame = None
        self.vid_refesh = 10

        self.is_pause = False

        self.face_locations = None

        self.mainui.lang_combobox.bind(
            '<<ComboboxSelected>>',
            self.change_language )
        self.mainui.pause_button['command'] = self.pause_vid
        
        self.mainui.show_f_optionmenu_var.trace(
            'w', self.show_from )

        self.mainui.mainloop()
    
    def destroy( self ):
        if self.iru is not None:
            self.iru.release()
        self.mainui.root.destroy()

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
            

        if self.video_source is not None\
            and self.iru is None:
            self.iru = IRU( self.video_source )
        
        self.play_video()

    def pause_vid( self ):
        if self.is_pause:
            self.is_pause = False
            self.play_video()
            self.mainui.pause_button['text'] = _('Pause')
        else:
            self.is_pause = True
            self.mainui.pause_button['text'] = _('Play')

    def pick_face( self ):
        frame =  self.vid_frame[1][self.iru.f_left:self.iru.f_right,\
            self.iru.f_top:self.iru.f_bottom]
        face_img = Image.fromarray( frame )
        faceimgtk = ImageTk.PhotoImage( image=face_img )
        self.mainui.face_label.imgtk = faceimgtk
        self.mainui.face_label.configure(image=faceimgtk)

    def play_video( self ):
        if self.iru is not None and not self.is_pause:
            if len(self.iru.face_locations) > 0:
                self.pick_face()
            self.vid_frame = self.iru.get_frame()
            if self.vid_frame[0] is not None:
                vid_img = Image.fromarray( self.vid_frame[1] )
                imgtk = ImageTk.PhotoImage( image=vid_img )
                self.mainui.vid_label.imgtk = imgtk
                self.mainui.vid_label.configure(image=imgtk)
            self.mainui.vid_label.after( self.vid_refesh,  self.play_video ) 


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

            if self.iru is not None:
                self.iru.release()

            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)

        pass

