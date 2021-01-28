
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

        if not self.vid.isOpened():
            messagebox.showerror( 
                _('Unable to open video source'), 
                self.video_source )
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_ret_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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
         
        # vid
        self.iru =  self.video_source = self.vid =  self.vid_ret_frame = None

        self.is_pause = False;  self.vid_refesh = 30

        self.face_locations = []
        # face num for face_label
        self.face_sum = self.face_num = 0
        self.resize_rate = 0.25

    
        self.mainui.lang_combobox.bind(
            '<<ComboboxSelected>>',
            self.change_language )
            
        self.mainui.pause_button['command'] = self.pause_vid
        self.mainui.prev_f_button['command'] = self.pick_prev_face
        self.mainui.next_f_button['command'] = self.pick_next_face
        
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

    def pick_next_face():
        if self.face_num < self.face_sum - 1:
            self.mainui.face_num_label = f'{self.face_num}/{self.face_sum}'
            self.face_num += 1
            self.pick_face(self.face_num)
    
    def pick_prev_face():
        if self.face_num > -1:
            self.mainui.face_num_label = f'{self.face_num}/{self.face_sum}'
            self.face_num -= 1
            self.pick_face(self.face_num)

    def pause_vid( self ):
        if self.is_pause:
            self.is_pause = False
            self.play_video()
            self.mainui.pause_button['text'] = _('Pause')
        else:
            self.is_pause = True
            self.mainui.pause_button['text'] = _('Play')

    def play_video( self ):
        if self.iru is not None and not self.is_pause:
            

            self.vid_ret_frame = self.iru.get_ret_frame()
            if self.vid_ret_frame[0] is not None:
                
                self.get_face_locations()

                self.face_sum = len(self.face_locations) 
                if self.face_sum > 0:

                    self.pick_face()
                    self.make_rect()
                
                vid_img = Image.fromarray( self.vid_ret_frame[1] )
                imgtk = ImageTk.PhotoImage( image=vid_img )
                self.mainui.vid_label.imgtk = imgtk
                self.mainui.vid_label.configure(image=imgtk)
            self.mainui.vid_label.after( self.vid_refesh,  self.play_video ) 
    
    def get_face_locations(self):

        small_frame = cv2.resize( self.vid_ret_frame[1], (0, 0), \
            fx=self.resize_rate, fy=self.resize_rate)  
        
        fs = face_recognition.face_locations( small_frame )
        self.face_locations = [ [ int(f_/self.resize_rate) for f_ in f ] \
            for f in fs]
        
    def make_rect( self ):

        for top, right, bottom, left in self.face_locations:
            cv2.rectangle( self.vid_ret_frame[1], (left, top), \
            (right, bottom), (0, 0, 255), 2)


    def pick_face( self ):
        
        top, right, bottom, left = self.face_locations[ self.face_num ]

        b_t_sub = bottom - top
        r_l_sub = right - left
        size_add = b_t_sub if  b_t_sub > r_l_sub else r_l_sub
        frame =  self.vid_ret_frame[1][top:( top + size_add ), \
            left:(left + size_add)]

        frame = cv2.resize( frame, (200, 200) )
        face_img = Image.fromarray( frame )
        faceimgtk = ImageTk.PhotoImage( image=face_img )
        self.mainui.face_label.imgtk = faceimgtk
        self.mainui.face_label.configure(image=faceimgtk)

        self.mainui.face_num_label['text'] = \
            f'{self.face_num+1}/{(self.face_sum )}'


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

