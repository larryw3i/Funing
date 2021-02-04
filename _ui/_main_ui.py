
from pony.orm import *
from tkinter import messagebox
import tkinter as tk
from tkinter import *
from ui.main_ui import MainUI
from langcodes import Language
import gettext
import sys,os
from model import funing_m as fm
from model.funing_m import Person
import  tkinter.filedialog as tkf
import cv2
from PIL import Image , ImageTk
import dlib
import face_recognition
from _ui.locale import _
from datetime import datetime , date
import json
from setting import setting_yml, setting_path, face_encodings_path
import numpy as np
import pickle
import yaml
import uuid

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

        # vid
        self.iru =  self.video_source = \
        self.vid =  self.vid_ret_frame = None

        self.face_image_path = None
        self.face_image = None

        self.is_pause = False;  self.vid_refesh = 30

        self.face_locations = []
        self.known_encodings = pickle.load( 
                open(face_encodings_path , 'rb') )

        self.current_face_encoding = None
        self.comparison_tolerance = 0.4

        # face num for face_label
        self.face_sum = 0
        self.face_num = -1
        self.resize_rate = 0.25

        self.current_face_person_id = None
    
        self.set_ui_events()
        self.mainui.mainloop()
    
    def set_ui_events( self ):

        self.mainui.langcombobox.lang_combobox.bind(
            '<<ComboboxSelected>>',
            self.change_language )
            
        self.mainui.showframe.rec_button['command'] = self.recognize_face

        self.mainui.entryframe.prev_f_button['command'] = \
            self.pick_prev_face
        self.mainui.entryframe.next_f_button['command'] = \
            self.pick_next_face
        self.mainui.entryframe.save_button['command'] = self.save_encoding
        
        self.mainui.showframe.show_f_optionmenu_var.trace(
            'w', self.show_from )

        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy )
         
    def destroy( self ):
        if self.iru is not None:
            self.iru.release()
        self.mainui.root.destroy()

    def show_from( self, *args  ):
        keys =  self.mainui.showframe.show_from_optionmenus.keys()
        values = self.mainui.showframe.show_from_optionmenus.values()
        value = self.mainui.showframe.show_f_optionmenu_var.get()
        show_f = list(keys)[ list( values ).index( value )]
        
        if show_f == 'file':
            if not self.is_pause:
                self.is_pause = True
            if self.iru is not None:
                self.iru.release()
                self.iru = None

            self.image_path = tkf.askopenfilename(
                title = _('Select a file'),
                initialdir = '~/Videos'
            )
            if len( self.image_path ) > 0:
                self.pick_image()

        if show_f == 'camara':
            self.video_source = 0
            
            if self.video_source is not None\
                and self.iru is None:
                self.is_pause = False
                self.iru = IRU( self.video_source )
            
            self.recognize_face()
        
    def pick_image( self ):

        face_image  = cv2.imread( self.image_path )
        self.face_image = cv2.cvtColor( face_image, cv2.COLOR_BGR2RGB)

        img = Image.fromarray( self.face_image )
        imgtk = ImageTk.PhotoImage( image= img )
        self.mainui.entryframe.vid_img_label.imgtk = imgtk
        self.mainui.entryframe.vid_img_label.configure(image=imgtk)

        self.get_face_locations( self.face_image )
        self.face_sum = len( self.face_locations )

        if self.face_sum > 0:
            self.face_num += 1
            self.mainui.entryframe.face_num_label['text'] = \
                f'{ self.face_num + 1 }/{self.face_sum}'
            self.pick_face( )


    def pick_next_face(self):
        if self.face_num < self.face_sum - 1:
            self.face_num += 1
            self.mainui.entryframe.face_num_label['text'] = \
                f'{self.face_num}/{self.face_sum}'
            self.pick_face()

            if self.is_pause:
                self.compare_faces()
        
    
    def pick_prev_face(self):
        if self.face_num > 0:
            self.face_num -= 1
            self.mainui.entryframe.face_num_label['text'] = \
                f'{self.face_num+1}/{self.face_sum}'
            self.pick_face( )

            if self.is_pause:
                self.compare_faces()
        

    def recognize_face( self ):

        
        if self.iru is None:
            messagebox.showinfo( _('No face detected'), \
                _('Oops.., No face detected!') )
            return

        if self.is_pause:
            self.is_pause = False
            self.play_video()
            self.mainui.showframe.rec_button['text'] = _('Recognize')
            self.update_entry_ui()
        else:
            self.is_pause = True

            self.compare_faces()
            
            self.mainui.showframe.rec_button['text'] = _('Play')

    def play_video( self ):
        if self.iru != None and not self.is_pause:
            

            self.vid_ret_frame  = self.iru.get_ret_frame()
            self.face_image = self.vid_ret_frame[1]
            if self.vid_ret_frame[0] is not None:
                
                self.get_face_locations(  self.face_image )

                self.face_sum = len(self.face_locations) 
                if self.face_sum > 0:

                    if self.face_num < 0 : self.face_num = 0
                    if self.face_num > self.face_sum - 1: 
                        self.face_num = self.face_sum - 1

                    self.pick_face()
                    self.make_rect()
                
                vid_img = Image.fromarray( self.face_image )
                imgtk = ImageTk.PhotoImage( image=vid_img )
                self.mainui.showframe.vid_img_label.imgtk = imgtk
                self.mainui.showframe.vid_img_label.configure(image=imgtk)
            self.mainui.showframe.vid_img_label.after( self.vid_refesh, self.play_video )
    
    def get_face_locations(self, image):

        small_frame = cv2.resize( image, (0, 0), \
            fx=self.resize_rate, fy=self.resize_rate)  
        
        fs = face_recognition.face_locations( small_frame )
        self.face_locations = [ [ int(f_/self.resize_rate) for f_ in f ] \
            for f in fs]
    
    def compare_faces( self ):

        if self.face_image is None:
            messagebox.showinfo( _('No face detected'), \
                _('Oops.., No face detected!') )
            return

        self.calc_current_face_encoding()

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
                self.face_image, [self.face_locations[ self.face_num ]] )[0]

            
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
            cv2.rectangle( self.face_image, (left, top), \
            (right, bottom), (0, 0, 255), 2)


    def pick_face( self ):
        
        top, right, bottom, left = self.face_locations[ self.face_num ]

        b_t_sub = bottom - top
        r_l_sub = right - left
        size_add = b_t_sub if  b_t_sub > r_l_sub else r_l_sub
        frame =  self.face_image[top:( top + size_add ), \
            left:(left + size_add)]

        frame = cv2.resize( frame, (200, 200) )
        face_img = Image.fromarray( frame )
        faceimgtk = ImageTk.PhotoImage( image=face_img )
        self.mainui.entryframe.face_label.imgtk = faceimgtk
        self.mainui.entryframe.face_label.configure(image=faceimgtk)

        self.mainui.entryframe.face_num_label['text'] = \
            f'{self.face_num+1}/{self.face_sum}'


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
        
        p = None
        
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
                messagebox.showerror( _('Error'), \
                    _('Check the DOB entry please!') ) 
            p.note = self.mainui.entryframe.note_text.get(1.0, 'end')

        else:
            p = Person( \
                id = self.current_face_person_id \
                    if ( not person_exists and \
                        self.current_face_person_id !=None) \
                    else str(uuid.uuid4()),\
                name = self.mainui.entryframe.name_entry.get() ,\
                dob =  datetime.strptime( \
                    self.mainui.entryframe.DOB_entry.get(), '%Y-%m-%d').date(),
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