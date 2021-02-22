
from pony.orm import *
from tkinter import messagebox
import tkinter as tk
from tkinter import *
from tkinter import ttk
from fui.main_ui import MainUI
from langcodes import Language
import gettext
import sys
import os
from fmodel.funing_m import Person, PersonInfo
import tkinter.filedialog as tkf
import cv2
from PIL import Image , ImageTk
import dlib
import face_recognition
from flocale.locale import _
from datetime import datetime , date
import json
from setting import setting_yml, setting_path, face_encodings_path,\
    comparison_tolerance, debug, lang_code
import pickle
import yaml
import uuid
import time
import re


class _MainUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        # vid
        self.iru =                  self.video_source = \
        self.vid =                  self.vid_ret_frame = None

        self.face_src_path =        self.iru_frame = None
        self.pause = False;         self.face_locations = []
        self.curr_f_encoding = None
        self.root_after = -1
        
        # face num for face_label
        self.face_sum = 0;          self.face_num = -1
        self.resize_rate = 0.25;    self.lang_code = lang_code
        self.fxfy = None;           self.ins_vars = {}

        self.known_encodings = dict(\
            pickle.load( open(face_encodings_path , 'rb') ))
        self.comparison_tolerance = comparison_tolerance
        self.image_exts = ['jpg','png']
        self.video_exts = ['mp4','avi','3gp','webm','mkv']
        self.showf_sv = None;       self.rec_img = False
        self.showfm = self.mainui.showframe
        self.entryfm = self.mainui.entryframe
        self.addinfofm = self.mainui.addinfoframe
            
        try:self.screenwidth = self.mainui.root.winfo_screenwidth();\
            self.screenheight = self.mainui.root.winfo_screenheight()
        except: print(_('No desktop environment is detected! (^_^)')); exit()

        self.curr_face_id = None
    
        self.set_ui_events()
        self.mainui.mainloop()
    
    def set_ui_events( self ):
        self.mainui.langcombobox.lang_combobox.bind('<<ComboboxSelected>>',
            self.change_language )
        self.showfm.ct_entry.bind('<FocusOut>', self.save_ct )
        self.showfm.rec_button['command'] = self.rec_now
        self.showfm.showf_go_btn['command'] = self.showf_go
        self.showfm.showf_optionmenu_sv.trace('w', self.show_from )
        self.entryfm.prev_f_button['command'] = \
            lambda: self.pick_face_by_num(-1)
        self.entryfm.next_f_button['command'] = \
            lambda: self.pick_face_by_num(1)
        self.entryfm.save_button['command'] = self.save_db_encoding
        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy )
        self.addinfofm.add_rf_button['command'] = self.ins_rf 
         
    def destroy( self ):
        if self.iru is not None: self.iru.vid_release()
        exit()

# SHOW_FRAME FUNCTIONS 
###############################################################################

    def save_ct( self , event):
        ct_stringvar_get = float(self.showfm.ct_stringvar.get())
        self.comparison_tolerance = comparison_tolerance = ct_stringvar_get
        setting_yml['comparison_tolerance'] = ct_stringvar_get
        yaml.dump( setting_yml, open( setting_path, 'w') )
    
    def showf_go( self):
        self.showf_sv = self.showfm.showf_sv.get()
        self.rec_img = False
        self.after_cancel()

        showf_ext = self.showf_sv.split('.')[-1]

        if showf_ext in self.video_exts:
            self.video_source = self.showf_sv;  self.play_video()
            return
        if re.match(r'\d+', self.showf_sv):
            self.video_source = int(self.showf_sv);  self.play_video()
            return
        if showf_ext in self.image_exts:
            self.pause = True;  self.rec_img = True;    self.view_image()
            return 
        self.showfm.showf_sv.set('')
        self.show_nsrc_error()
            
    def show_from( self, *args  ):
        keys =  self.showfm.showf_t_dict.keys()
        values = self.showfm.showf_t_dict.values()
        value = self.showfm.showf_optionmenu_sv.get()
        show_f = list(keys)[ list( values ).index( value )]
        
        self.after_cancel()
        self.rec_img = False
    
        if show_f == 'file':
            if self.iru is not None: self.iru.vid_release() ; self.iru = None

            self.face_src_path = tkf.askopenfilename(
                title = _('Select a file'),
                filetypes = [\
                    ( _('Image or video'), \
                    '*.'+(' *.'.join( self.image_exts + self.video_exts)))\
                ],
                initialdir = '~'
            )

            if len( self.face_src_path ) > 0:
                ext = os.path.splitext( self.face_src_path )[1][1:]

                self.showfm.showf_sv.set( self.face_src_path )

                if ext in self.image_exts:
                    # Pause
                    self.pause = True
                    self.rec_img = True
                    self.view_image()
                if ext in self.video_exts:
                    self.video_source = self.face_src_path
                    self.play_video()

        elif show_f == 'camera':
            self.video_source = 0
            self.showfm.showf_sv.set( self.video_source )
            self.play_video()
    
    def after_cancel( self ):
        if self.root_after != -1:
            self.mainui.root.after_cancel( self.root_after )
        
    def play_video( self ):
        if self.iru is not None: self.iru.vid_release()
        self.iru = IRU( self.video_source )
        if not self.iru.vid.isOpened():
            self.show_nsrc_error()
            if debug: print('play_video: Unable to open video source')
            return
        # Play
        self.pause = False
        self.get_resize_fxfy()
        self.refresh_frame()

        if debug:
            print('fps: ', self.iru.fps)
           

    def rec_now( self ):        
        if self.rec_img: return
        if self.face_sum < 1:
            if debug: print('No face detected')
            return
        if self.iru is None: self.show_nfd_info() ; return
        if self.pause:
            # Play
            self.pause = False
            self.showfm.rec_stringvar.set(_('Recognize'))
            self.refresh_frame()
            self.update_ui()
            self.curr_face_id = None
        else:
            # Pause
            self.pause = True
            self.showfm.rec_stringvar.set( _('Play') )


    def view_image( self ):
        face_image  = cv2.imread( self.face_src_path )
        self.iru_frame = cv2.cvtColor( face_image, cv2.COLOR_BGR2RGB)

        img = Image.fromarray( self.iru_frame )
        imgtk = ImageTk.PhotoImage( image= img )
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)

        self.get_f_loc_and_sum()
        
        if self.face_sum < 1 : return
        self.correct_f_num_ui()
        self.pick_face_by_num()    

    def refresh_frame( self ):
        if self.iru is None: return
        self.vid_ret_frame  = self.iru.get_ret_frame()
        self.iru_frame = self.vid_ret_frame[1]

        if self.vid_ret_frame[0] is None:
            if debug: print('No frame rect returned.'); return
        
        self.get_f_loc_and_sum()
        if self.face_sum > 0:
            if self.pause:
                self.update_ui()
                self.pick_face_by_num()
                return
            else:
                self.correct_f_num_ui()
                self.mk_frame_rect()

        self.update_vid_frame()
        self.root_after = self.mainui.root.after( \
            int(1000/self.iru.fps) , self.refresh_frame )
    
    def update_vid_frame( self ):
        if self.fxfy is None: 
            if debug: print('self.fxfy is None'); 
            return
        if self.iru_frame is None: 
            if debug: print('self.iru_frame is None'); 
            return

        vid_img = cv2.resize( self.iru_frame, (0,0) , \
            fx = self.fxfy, fy = self.fxfy )
        vid_img = Image.fromarray( vid_img )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)

    def get_resize_fxfy( self ):
        if self.iru.width == self.iru.height == 0: 
            if debug: print('self.iru is None')
            return
        w = self.screenwidth/2
        h = self.screenheight/2
        r = w/h 
        r0 = self.iru.width/self.iru.height
        r1= r0/r 
        self.fxfy = h/self.iru.height if r1<r else w/self.iru.width
        if debug:
            print('self.fxfy: ', self.fxfy)
    
    def get_f_loc_and_sum( self ):
        self.get_f_loc()
        self.get_f_sum()
            
    def get_f_loc(self ):

        if self.iru_frame is None:
            if debug: print('get_f_loc: self.iru_frame is None')
            return

        small_frame = cv2.resize( self.iru_frame , (0, 0), \
            fx=self.resize_rate, fy=self.resize_rate)  
        
        fs = face_recognition.face_locations( small_frame )
        self.face_locations = [ [ int(f_/self.resize_rate) for f_ in f ] \
            for f in fs]

    def get_f_sum( self ):
        self.face_sum = len(self.face_locations) 
    
    def get_curr_f_encoding( self ):
        
        if self.face_sum > 0 :
            self.curr_f_encoding = face_recognition.face_encodings( \
                self.iru_frame, [self.face_locations[ self.face_num ]] )[0]
     
    def get_curr_f_encoding_and_id( self ):
        self.get_curr_f_encoding()
        self.get_curr_f_id()
                
    def mk_frame_rect( self ):
        for top, right, bottom, left in self.face_locations:
            cv2.rectangle( self.iru_frame, (left, top), \
            (right, bottom), (0, 0, 255), 2)

    def show_nfd_info( self ):
        messagebox.showinfo( _('No face detected'), \
            _('Oops.., No face detected!') )

    def show_dob_error( self ):
        messagebox.showerror( _('Error'), \
            _('Check the DOB entry please!') ) 

    def show_nsrc_error( self ):
        unable_open_s = _('Unable to open video source')
        messagebox.showerror(  unable_open_s, unable_open_s+': '+self.showf_sv )


###############################################################################
# SHOW_FRAME FUNCTIONS END

# ENTRY_FRAME FUNCTIONS
###############################################################################


    def correct_f_num_ui( self ):

        self.face_num = 0 if self.face_num < 0 else \
             self.face_num if self.face_num < self.face_sum \
            else self.face_sum-1
        self.entryfm.face_num_stringvar.set( \
            f'{self.face_num+1}/{self.face_sum}' )
        
    @db_session
    def update_ui(self):
        '''
        Update self.entryfm and self.addinfofm
        '''

        if self.iru_frame is None: self.show_nfd_info() ; return
        
        self.get_curr_f_encoding_and_id()

        # update entryframe
        if self.pause:
            if self.curr_face_id is None: return

            p = Person.get(id = self.curr_face_id)

            if p is None: return
            self.entryfm.clear_content()            
            self.entryfm.uuid_entry['state'] = 'normal'
            self.entryfm.uuid_entry.insert(0 , p.id)
            self.entryfm.uuid_entry['state'] = 'disabled'
            self.entryfm.name_entry.insert(0 , p.name)
            self.entryfm.gender_entry.insert(0 , p.gender)
            self.entryfm.DOB_entry.insert(0 , p.dob )
            self.entryfm.address_entry.insert(0 , p.address)
            self.entryfm.cmt_text.insert(END , p.comment)
    
            # update addinfoframe
            i_s = select( i for i in PersonInfo \
                if i.person_id == self.curr_face_id )
                
            for i in i_s:
                self.ins_rf( il_entry_value=i.label, v_value = i.value,\
                    cmt_value = i.comment, frame_name  = i.id )

        else:
            self.entryfm.uuid_entry['state'] = 'normal'
            self.entryfm.uuid_entry.delete(0, END)
            self.entryfm.uuid_entry['state'] = 'disabled'
            self.entryfm.name_entry.delete(0, END)
            self.entryfm.gender_entry.delete(0 , END)
            self.entryfm.DOB_entry.delete(0, END)
            self.entryfm.address_entry.delete(0, END)
            self.entryfm.cmt_text.delete('1.0', END)

            self.rm_all_ins_rfs()
    
    def pick_f_mk_rect( self ):
        '''
        Pick face image to self.entryfm.face_label and make rectangles for 
        self.showfm.vid_frame_label.
        '''
        self.pick_face_by_num()
        self.mk_frame_rect()
    
    def pick_face_by_num( self, p_n = 0 ):
        '''
        Pick face image to self.entryfm.face_label
        '''
        if not self.pause: 
            print('Video is playing')
            return
        self.get_f_sum()
        if self.face_sum < 1: 
            if debug: print('No face detected')
            return
        self.face_num = self.face_num + p_n
        self.correct_f_num_ui()
        
        top, right, bottom, left = self.face_locations[ self.face_num ]
        b_t_sub = bottom - top
        r_l_sub = right - left
        size_add = b_t_sub if  b_t_sub > r_l_sub else r_l_sub
        frame =  self.iru_frame[top:( top + size_add ), \
            left:(left + size_add)]

        frame = cv2.resize( frame, (200, 200) )
        face_img = Image.fromarray( frame )
        faceimgtk = ImageTk.PhotoImage( image=face_img )
        self.entryfm.face_label.imgtk = faceimgtk
        self.entryfm.face_label.configure(image=faceimgtk)

    @db_session
    def save_db_encoding( self ):
        if not self.pause: 
            if debug: print('Video is palying');   return
        if self.curr_f_encoding is None:  
            self.show_nfd_info() ;  return

        person_exists = False if self.curr_face_id is None else \
            Person.exists( id = self.curr_face_id )

        if person_exists:
            if debug:
                print( 'Person exists')
            p = select(p for p in Person if \
                p.id == self.curr_face_id ).first()
            p.dob = self.entryfm.DOB_entry.get()
            p.name = self.entryfm.name_entry.get()
            p.gender = self.entryfm.gender_entry.get()
            p.comment = self.entryfm.cmt_text.get(1.0, 'end')

        else:
            if debug:
                print('New person')
            p = Person( id = str(uuid.uuid4()),\
                name = self.entryfm.name_entry.get() ,
                gender = self.entryfm.gender_entry.get(),
                dob = self.entryfm.DOB_entry.get(), 
                address = self.entryfm.address_entry.get(),
                comment = self.entryfm.cmt_text.get(1.0, 'end') )
        
        if debug:
            print( self.addinfofm.ins_vars )

        for frame_name, sv in self.ins_vars.items():
            label_value= sv[0].get()
            value_v = sv[1].get()
            cmt_value = sv[2].get()

            if debug:
                print( label_value,  value_v, cmt_value)

            if len(label_value+  value_v+ cmt_value )< 1: continue
            
            p_i = PersonInfo.get(person_id =p.id, label =label_value)
            if p_i:
                if debug: print( 'PersonInfo exists' )
                p_i.value = value_v;    p_i.comment = cmt_value
            else:
                if debug: print( 'New PersonInfo' )
                p_i = PersonInfo( id = frame_name,
                    comment = cmt_value,      person_id = p.id,      
                    label = label_value,    value = value_v
                )

        if len( self.known_encodings) < 1 \
            or self.known_encodings.get(p.id) is None:
                self.known_encodings.setdefault(p.id ,\
                    [self.curr_f_encoding])
        else:
            self.known_encodings.setdefault( p.id ,\
                [self.known_encodings.get(p.id)]+\
                [self.curr_f_encoding])

        pickle.dump( self.known_encodings, open(face_encodings_path, 'wb'))
        
        commit()
        
###############################################################################
# ENTRY_FRAME FUNCTIONS END

# ADD_INFO_FRAME FUNCTIONS
###############################################################################

    def ins_rf( self, frame_name = '', il_entry_value='',  v_value = '', \
        cmt_value = ''  ):

        frame_name = str( uuid.uuid4() ) if len( frame_name )<1 else frame_name
        row_frame = tk.Frame(self.addinfofm.frame, name = frame_name )

        info_frame = tk.Frame( row_frame )
        del_button = tk.Button( row_frame , text = _('Delete'), \
            command =lambda: self.rm_ins_rf(frame_name) )
        
        il_entry_sv = StringVar( info_frame , value = il_entry_value )
        tk.Entry(info_frame, textvariable= il_entry_sv, justify = RIGHT)\
            .grid( column=1, row= 0)

        tk.Label(info_frame, text = ':').grid(column = 2, row = 0)

        value_sv = StringVar( info_frame, value = v_value)
        tk.Entry( info_frame, textvariable = value_sv).grid(\
            column = 3,row= 0)

        tk.Label(info_frame, text = f"{_('Comment')}:")\
            .grid(column = 4, row = 0)
        cmt_sv = StringVar( info_frame, cmt_value)
        tk.Entry( info_frame, textvariable = cmt_sv ).grid(column = 5 ,row= 0 )
        
        info_frame.grid(column = 0, row = 0)
        del_button.grid(column = 1, row = 0)

        row_frame.pack( side = TOP )

        ttk.Separator(info_frame, orient='horizontal')\
            .place(relx=0, rely=0, relwidth=1, relheight=0.01)
        
        self.ins_vars[frame_name] = [il_entry_sv , value_sv, cmt_sv ]
        
        if debug:
            print( self.ins_vars )
            
    @db_session
    def rm_ins_rf( self , frame_name):
        # update UI
        self.addinfofm.frame.nametowidget(frame_name).pack_forget()
        self.ins_vars.pop(frame_name)
        if debug:
            print( frame_name, self.ins_vars )
        
        # update database
        if self.curr_face_id is not None:
            if PersonInfo.exists( person_id =self.curr_face_id,\
                id = frame_name ):
                PersonInfo.get( id=frame_name ).delete()
                commit()
    
    def rm_all_ins_rfs(self):
        for i in self.ins_vars.keys():
            self.addinfofm.frame.nametowidget(i).pack_forget()
        self.ins_vars = {}
             
###############################################################################
# ADD_INFO_FRAME FUNCTIONS  END

# LANGCOMBOBOX FUNCTIONS
###############################################################################

    def change_language(self, lang ):

        lang_display_name = self.mainui.langcombobox.lang_combobox_var.get()
        new_lang_code = Language.find( lang_display_name ).to_tag()
        if debug:
            print( 'new_lang_code: ', new_lang_code, 'lang_code: ', lang_code )

        if new_lang_code == lang_code: return

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:
            setting_yml['lang_code'] = new_lang_code
            yaml.dump( setting_yml, open( setting_path, 'w') )
            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)
        pass

###############################################################################
# LANGCOMBOBOX FUNCTIONS END

# OTHER FUNCTIONS
###############################################################################
    def get_curr_f_id( self ):

        if self.curr_f_encoding is None: self.show_nfd_info(); return

        for _id, encodings in self.known_encodings.items():

            comparisons = face_recognition.compare_faces( \
                encodings, self.curr_f_encoding , \
                self.comparison_tolerance)
                        
            if True in comparisons: self.curr_face_id = _id ; break

        
###############################################################################
# OTHER FUNCTIONS END

class IRU():
    def __init__(self, video_source = 0 ):
        self.video_source = video_source
        self.vid = cv2.VideoCapture( video_source )        
        if not self.vid.isOpened(): self.show_vid_src_error(); return
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        # 0 got when I tested it on msys.
        if self.fps == 0 : 
            self.fps = 25
            print('self.pfs got 0, 25 insteaded')

        if debug:
            print( 'width: ', self.width, 'height: ', self.height, \
                'fps: ', self.fps )

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
    
    def show_vid_src_error( self ):
        messagebox.showerror( 
            _('Unable to open video source'), self.video_source )

    def vid_release( self ):
        if self.vid is None: return
        self.vid.release()
        cv2.destroyAllWindows()
