
from pony.orm import *
from tkinter import messagebox
import tkinter as tk
from tkinter import *
from ui.main_ui import MainUI
from langcodes import Language
import gettext
import sys,os
from models import funing_m as fm
from models.funing_m import Person
import  tkinter.filedialog as tkf
import cv2
from PIL import Image , ImageTk
import dlib
import face_recognition
from _ui.locale import _
from datetime import datetime , date
import json
from setting import setting_yml, setting_path, face_encodings_path,\
    comparison_tolerance, debug
import numpy as np
import pickle
import yaml
import uuid

class _MainUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        # vid
        self.iru =  self.video_source = \
        self.vid =  self.vid_ret_frame = None

        self.face_src_path = None
        self.iru_frame = None

        self.is_pause = False;  self.vid_fps = 30

        self.face_locations = []
        self.known_encodings = pickle.load( open(face_encodings_path , 'rb') )

        self.current_face_encoding = None
        self.comparison_tolerance = comparison_tolerance
            
        # face num for face_label
        self.face_sum = 0
        self.face_num = -1
        self.resize_rate = 0.25
        
        self.fxfy = None
        try:
            self.screenwidth = self.mainui.root.winfo_screenwidth()
            self.screenheight = self.mainui.root.winfo_screenheight()
        except:
            print(_('No desktop environment is detected! (^_^)'))
            exit()

        self.current_face_person_id = None
    
        self.set_ui_events()
        self.mainui.mainloop()
    
    def set_ui_events( self ):

        self.mainui.langcombobox.lang_combobox.bind('<<ComboboxSelected>>',
            self.change_language )
        self.mainui.showframe.ct_entry.bind('<FocusOut>', self.save_ct )
        self.mainui.showframe.rec_button['command'] = self.recognize_face
        self.mainui.entryframe.prev_f_button['command'] = self.pick_prev_face
        self.mainui.entryframe.next_f_button['command'] = self.pick_next_face
        self.mainui.entryframe.save_button['command'] = self.save_encoding
        self.mainui.showframe.show_f_optionmenu_var.trace('w', self.show_from )
        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy )
         
    def destroy( self ):
        if self.iru is not None:
            self.iru.release()
        self.mainui.root.destroy()

    def save_ct( self , event):
        if not self.mainui.showframe.values_valid():
            return
        ct_stringvar_get = float(self.mainui.showframe.ct_stringvar.get())
        self.comparison_tolerance = comparison_tolerance = ct_stringvar_get
        setting_yml['comparison_tolerance'] = ct_stringvar_get
        yaml.dump( setting_yml, open( setting_path, 'w') )

    def show_from( self, *args  ):
        keys =  self.mainui.showframe.show_from_optionmenus.keys()
        values = self.mainui.showframe.show_from_optionmenus.values()
        value = self.mainui.showframe.show_f_optionmenu_var.get()
        show_f = list(keys)[ list( values ).index( value )]

        self.video_source = 0

        image_exts = ['jpg','png']
        video_exts = ['mp4','avi','3gp','webm','mkv']
    
        if not self.is_pause:
            self.is_pause = True

        if show_f == 'file':
            if self.iru is not None:
                self.iru.release()
                self.iru = None

            self.face_src_path = tkf.askopenfilename(
                title = _('Select a file'),
                filetypes = [\
                    ( _('Image or video'), \
                    '*.'+(' *.'.join( image_exts + video_exts)))\
                ],
                initialdir = '~'
            )
            if len( self.face_src_path ) > 0:
                ext = os.path.splitext( self.face_src_path )[1][1:]
                if ext in image_exts:
                    self.pick_image()
                if ext in video_exts:
                    show_f = 'camara'
                    self.video_source = self.face_src_path

        if show_f == 'camara':
            
            if self.video_source is not None:
                if self.iru is not None:
                    self.iru.release()
                    self.iru = None
                self.iru = IRU( self.video_source )
                self.is_pause = False
                self.get_resize_fxfy()
                self.play_video()
        
    def pick_image( self ):

        face_image  = cv2.imread( self.face_src_path )
        self.iru_frame = cv2.cvtColor( face_image, cv2.COLOR_BGR2RGB)

        img = Image.fromarray( self.iru_frame )
        imgtk = ImageTk.PhotoImage( image= img )
        self.mainui.showframe.vid_img_label.imgtk = imgtk
        self.mainui.showframe.vid_img_label.configure(image=imgtk)

        self.get_face_locations( self.iru_frame )
        self.face_sum = len( self.face_locations )

        if self.face_sum > 0:
            self.face_num += 1
            self.mainui.entryframe.face_num_stringvar.set(\
                f'{ self.face_num + 1 }/{self.face_sum}')
            self.pick_face( )

    def pick_next_face(self):
        if self.face_num < self.face_sum - 1:
            self.face_num += 1
            self.mainui.entryframe.face_num_stringvar.set( \
                f'{self.face_num}/{self.face_sum}' )
            self.pick_face()

            if self.is_pause:
                self.compare_faces()
        
    
    def pick_prev_face(self):
        if self.face_num > 0:
            self.face_num -= 1
            self.mainui.entryframe.face_num_stringvar.set( \
                f'{self.face_num+1}/{self.face_sum}' )
            self.pick_face( )

            if self.is_pause:
                self.compare_faces()
        

    def recognize_face( self ):
        
        if self.iru is None:
            self.show_nfd_info()
            return

        if self.is_pause:
            self.is_pause = False
            self.play_video()
            self.mainui.showframe.rec_stringvar.set(_('Recognize'))
            self.update_entry_ui()
        else:
            self.is_pause = True
            self.compare_faces()
            self.mainui.showframe.rec_stringvar.set( _('Play') )

    def play_video( self ):
        if self.iru is not None and not self.is_pause:
            
            self.vid_ret_frame  = self.iru.get_ret_frame()
            self.iru_frame = self.vid_ret_frame[1]
            if self.vid_ret_frame[0] is not None:
                
                self.get_face_locations(  self.iru_frame )

                self.face_sum = len(self.face_locations) 
                if self.face_sum > 0:

                    if self.face_num < 0 : self.face_num = 0
                    if self.face_num > self.face_sum - 1: 
                        self.face_num = self.face_sum - 1

                    self.pick_face()
                    self.make_rect()

                vid_img = cv2.resize( self.iru_frame, (0,0) , \
                    fx = self.fxfy, fy = self.fxfy )
                vid_img = Image.fromarray( vid_img )
                imgtk = ImageTk.PhotoImage( image=vid_img )
                self.mainui.showframe.vid_img_label.imgtk = imgtk
                self.mainui.showframe.vid_img_label.configure(image=imgtk)

                self.mainui.showframe.vid_img_label.after( \
                    int(1000/self.iru.fps) , self.play_video )
            else:
                if debug:
                    print('No frame rect returned.')
                return
    
    def get_resize_fxfy( self ):
        w = self.screenwidth/2
        h = self.screenheight/2
        r = w/h 
        r0 = self.iru.width/self.iru.height
        r1= r0/r 
        h_ = w_ = 0
        self.fxfy = h/self.iru.height if r1<r else w/self.iru.width
            
    
    def get_face_locations(self, image):

        small_frame = cv2.resize( image, (0, 0), \
            fx=self.resize_rate, fy=self.resize_rate)  
        
        fs = face_recognition.face_locations( small_frame )
        self.face_locations = [ [ int(f_/self.resize_rate) for f_ in f ] \
            for f in fs]
    
    def compare_faces( self ):

        if self.iru_frame is None:
            self.show_nfd_info()
            return

        self.calc_current_face_encoding()

        if self.current_face_encoding is None:
            self.show_nfd_info()
            return

        self.current_face_person_id = None

        for _id, encodings in self.known_encodings.items():

            comparisons = face_recognition.compare_faces( \
                encodings, self.current_face_encoding , \
                self.comparison_tolerance)
                        
            if True in comparisons:
                self.current_face_person_id = _id
                break

        self.update_entry_ui()


    def calc_current_face_encoding( self ):
        
        if self.face_sum > 0 :
            self.current_face_encoding = face_recognition.face_encodings( \
                self.iru_frame, [self.face_locations[ self.face_num ]] )[0]

            
    @db_session
    def update_entry_ui(self):
        if self.is_pause and \
            self.current_face_person_id != None:
            p = select(p for p in fm.Person \
                if p.id == self.current_face_person_id ).first()
            if p != None:
                self.mainui.entryframe.clear_content()
                
                self.mainui.entryframe.uuid_entry['state'] = 'normal'
                self.mainui.entryframe.uuid_entry.insert(0 , p.id)
                self.mainui.entryframe.uuid_entry['state'] = 'disabled'
                self.mainui.entryframe.name_entry.insert(0 , p.name)
                self.mainui.entryframe.DOB_entry.insert(0 , str(p.dob) )
                self.mainui.entryframe.address_entry.insert(0 , p.address)
                self.mainui.entryframe.note_text.insert(END , p.note)

        elif (not self.is_pause) or \
            (self.is_pause and (self.current_face_person_id is None) ):
                self.mainui.entryframe.uuid_entry['state'] = 'normal'
                self.mainui.entryframe.uuid_entry.delete(0, END)
                self.mainui.entryframe.uuid_entry['state'] = 'disabled'
                self.mainui.entryframe.name_entry.delete(0, END)
                self.mainui.entryframe.DOB_entry.delete(0, END)
                self.mainui.entryframe.address_entry.delete(0, END)
                self.mainui.entryframe.note_text.delete('1.0', END)

    def make_rect( self ):

        for top, right, bottom, left in self.face_locations:
            cv2.rectangle( self.iru_frame, (left, top), \
            (right, bottom), (0, 0, 255), 2)


    def pick_face( self ):
        
        if self.face_num < 0:
            self.show_nfd_info()

        top, right, bottom, left = self.face_locations[ self.face_num ]

        b_t_sub = bottom - top
        r_l_sub = right - left
        size_add = b_t_sub if  b_t_sub > r_l_sub else r_l_sub
        frame =  self.iru_frame[top:( top + size_add ), \
            left:(left + size_add)]

        frame = cv2.resize( frame, (200, 200) )
        face_img = Image.fromarray( frame )
        faceimgtk = ImageTk.PhotoImage( image=face_img )
        self.mainui.entryframe.face_label.imgtk = faceimgtk
        self.mainui.entryframe.face_label.configure(image=faceimgtk)

        self.mainui.entryframe.face_num_stringvar.set(\
            f'{self.face_num+1}/{self.face_sum}' )


    def change_language(self, lang ):

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:
            
            lang_display_name = self.mainui.langcombobox.lang_combobox_var.get()
            lang_code = Language.find( lang_display_name ).to_tag()
            
            setting_yml['lang_code'] = lang_code
            yaml.dump( setting_yml, open( setting_path, 'w') )

            if self.iru is not None:
                self.iru.release()

            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)

        pass


    @db_session
    def save_encoding( self ):
        
        if not self.mainui.entryframe.values_valid():
            return

        # dev: face_encoding exists and person is None sometimes
        person_exists =  False if self.current_face_person_id is None else \
            fm.Person.exists( id = self.current_face_person_id )

        if self.current_face_person_id != None and \
            person_exists:

            p = select(p for p in fm.Person if \
                p.id == self.current_face_person_id ).first()

            p.name = self.mainui.entryframe.name_entry.get()
            try:
                p.dob = datetime.strptime( \
                    self.mainui.entryframe.DOB_entry.get(), "%Y-%m-%d").date()
            except:
                self.show_dob_error()
                return
            p.note = self.mainui.entryframe.note_text.get(1.0, 'end')

        else:
            p_dob = None

            try:
                p_dob = datetime.strptime( \
                    self.mainui.entryframe.DOB_entry.get(), "%Y-%m-%d").date()
            except:
                self.show_dob_error()
                return
            p = Person( \
                id = self.current_face_person_id \
                    if ( not person_exists and \
                        self.current_face_person_id !=None) \
                    else str(uuid.uuid4()),\
                name = self.mainui.entryframe.name_entry.get() ,\
                dob = p_dob,
                address = self.mainui.entryframe.address_entry.get(),
                note = self.mainui.entryframe.note_text.get(1.0, 'end') )

        commit()

        if self.current_face_encoding is None:
            messagebox.showinfo( _('Information'), _('No face is detected'))
        else:
            if len( self.known_encodings) > 0:
                if self.known_encodings.get(str(p.id)) is None:
                    self.known_encodings.setdefault(str(p.id) ,\
                        [self.current_face_encoding])
                else:
                    self.known_encodings.setdefault(str(p.id) ,\
                        [self.known_encodings.get(str(p.id))]+\
                        [self.current_face_encoding])
            else:
                self.known_encodings = { str(p.id):\
                    [self.current_face_encoding] }
            pickle.dump( self.known_encodings, open(face_encodings_path, 'wb'))
        
    def show_nfd_info( self ):
        messagebox.showinfo( _('No face detected'), \
            _('Oops.., No face detected!') )

    def show_dob_error( self ):
        messagebox.showerror( _('Error'), \
            _('Check the DOB entry please!') ) 

class IRU():
    def __init__(self, video_source = 0 ):
        self.video_source = video_source
        self.vid = cv2.VideoCapture( self.video_source )

        if not self.vid.isOpened():
            messagebox.showerror( 
                _('Unable to open video source'), 
                self.video_source )
            return
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        # 0 got when I tested it on msys.
        self.fps = 25 if self.fps == 0 else self.fps
        # self.frame_count = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_ret_frame( self ):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return (ret, frame)

            else:
               return (None, None ) 
        else:
            return (None, None)
        
    def release( self ):
        self.vid.release()
