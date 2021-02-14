
from pony.orm import *
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from tkinter import *
from fui.main_ui import MainUI
from langcodes import Language
import gettext
import sys,os
from fmodel import funing_m as fm
from fmodel.funing_m import Person, PersonInfo
import  tkinter.filedialog as tkf
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


class _MainUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()

        # vid
        self.iru =  self.video_source = \
        self.vid =  self.vid_ret_frame = None

        self.face_src_path = None
        self.iru_frame = None

        self.pause = False;  self.vid_fps = 30

        self.face_locations = []
        self.known_encodings = pickle.load( open(face_encodings_path , 'rb') )

        self.curr_f_encoding = None
        self.comparison_tolerance = comparison_tolerance
            
        # face num for face_label
        self.face_sum = 0
        self.face_num = -1
        self.resize_rate = 0.25

        self.lang_code = lang_code
        
        self.fxfy = None

        self.ins_vars = {}

        try:self.screenwidth = self.mainui.root.winfo_screenwidth();\
            self.screenheight = self.mainui.root.winfo_screenheight()
        except: print(_('No desktop environment is detected! (^_^)')); exit()

        self.curr_face_id = None
    
        self.set_ui_events()
        self.mainui.mainloop()
    
    def set_ui_events( self ):

        self.mainui.langcombobox.lang_combobox.bind('<<ComboboxSelected>>',
            self.change_language )
        self.mainui.showframe.ct_entry.bind('<FocusOut>', self.save_ct )
        self.mainui.showframe.rec_button['command'] = self.rec_now
        self.mainui.entryframe.prev_f_button['command'] = \
            lambda: self.pick_face_by_num(-1)
        self.mainui.entryframe.next_f_button['command'] = \
            lambda: self.pick_face_by_num(1)
        self.mainui.entryframe.save_button['command'] = self.save_db_encoding
        self.mainui.showframe.show_f_optionmenu_var.trace('w', self.show_from )
        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy )
        self.mainui.addinfoframe.add_rf_button['command'] = self.ins_rf 
     
    def ins_rf( self, frame_name = '', il_entry_value='',  v_value = '', \
        note_value = ''  ):
        

        frame_name = str( uuid.uuid4() ) if len( frame_name )<1 else frame_name
        row_frame = tk.Frame( self.mainui.addinfoframe.frame, \
            name = frame_name )

        info_frame = tk.Frame( row_frame )
        del_button = tk.Button( row_frame , text = _('Delete'), \
            command =lambda: self.rm_ins_rf(frame_name) )
        
        tk.Label( info_frame, text = _('Label') )\
            .grid( column =  0, row =  0 )
        il_entry_svar = StringVar( info_frame , value = il_entry_value)
        tk.Entry(info_frame, \
            textvariable= il_entry_svar)\
            .grid( column =  1,  row =  0)

        tk.Label( info_frame, text=_('Value'))\
            .grid( column = 0, row = 2)
        value_sv = StringVar( info_frame, value = v_value )
        tk.Entry( info_frame, textvariable = value_sv )\
            .grid(  column = 1 ,  row =  2 )

        tk.Label( info_frame, text=_('Note'))\
            .grid( column = 0, row = 3)
        note_sv = StringVar( info_frame, note_value )
        tk.Entry( info_frame, textvariable = note_sv )\
            .grid(  column = 1 ,  row = 3 )
        
        info_frame.grid(column = 0, row = 0)
        del_button.grid(column = 1, row = 0)
        row_frame.pack( side = TOP )

        ttk.Separator(info_frame, orient='horizontal')\
            .place(relx=0, rely=0, relwidth=1, relheight=0.01)
        
        self.ins_vars[frame_name] = [il_entry_svar, value_sv, note_sv]
        
        if debug:
            print( self.ins_vars )
            
    @db_session
    def rm_ins_rf( self , frame_name):
        # update UI
        self.mainui.addinfoframe.frame.nametowidget(frame_name).pack_forget()
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
            self.mainui.addinfoframe.frame.nametowidget(i).pack_forget()
        self.ins_vars = {}
        

         
    def destroy( self ):
        if self.iru is not None:
            self.iru.release()
        self.mainui.root.destroy()

    def save_ct( self , event):
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
    
        self.pause = True

        if show_f == 'file':
            if self.iru is not None: self.iru.release() ; self.iru = None

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
                    self.mainui.showframe.rec_button['state'] = 'disabled'
                    self.view_image()
                else: self.mainui.showframe.rec_button['state'] = 'normal'

                if ext in video_exts:
                    show_f = 'camara'
                    self.video_source = self.face_src_path

        if show_f == 'camara':
            
            if self.video_source is not None:
                if self.iru is not None:
                    self.iru.release()
                    self.iru = None
                self.iru = IRU( self.video_source )
                self.pause = False
                self.get_resize_fxfy()
                self.play_video()
           

    def rec_now( self ):
        
        if self.iru is None: self.show_nfd_info() ; return

        if self.pause:
            self.pause = False
            self.mainui.showframe.rec_stringvar.set(_('Recognize'))
            self.play_video()
            self.update_ui()
            self.curr_face_id = None
        else:
            self.pause = True
            self.mainui.showframe.rec_stringvar.set( _('Play') )

    def correct_f_num_ui( self ):

        self.face_num = 0 if self.face_num < 0 else \
            self.face_sum if self.face_num > self.face_sum \
            else self.face_num
        self.mainui.entryframe.face_num_stringvar.set( \
            f'{self.face_num+1}/{self.face_sum}' )
        

    def view_image( self ):

        face_image  = cv2.imread( self.face_src_path )
        self.iru_frame = cv2.cvtColor( face_image, cv2.COLOR_BGR2RGB)

        img = Image.fromarray( self.iru_frame )
        imgtk = ImageTk.PhotoImage( image= img )
        self.mainui.showframe.vid_frame_label.imgtk = imgtk
        self.mainui.showframe.vid_frame_label.configure(image=imgtk)

        self.get_f_loc_and_sum()
        
        if self.face_sum > 0:
            self.correct_f_num_ui()
            self.pick_face_by_num()    

    def play_video( self ):
        if self.iru is None: return
        if self.pause: 
            self.update_ui()
            return
        
        self.vid_ret_frame  = self.iru.get_ret_frame()
        self.iru_frame = self.vid_ret_frame[1]

        if self.vid_ret_frame[0] is None:
            if debug: print('No frame rect returned.'); return
        
        self.get_f_loc_and_sum()

        if self.face_sum > 0:

            self.correct_f_num_ui()
            self.pick_f_mk_rect()

        self.update_vid_frame()

        self.mainui.showframe.vid_frame_label.after( \
            int(1000/self.iru.fps) , self.play_video )
    
    def update_vid_frame( self ):
        vid_img = cv2.resize( self.iru_frame, (0,0) , \
            fx = self.fxfy, fy = self.fxfy )
        vid_img = Image.fromarray( vid_img )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        self.mainui.showframe.vid_frame_label.imgtk = imgtk
        self.mainui.showframe.vid_frame_label.configure(image=imgtk)


    def get_resize_fxfy( self ):
        w = self.screenwidth/2
        h = self.screenheight/2
        r = w/h 
        r0 = self.iru.width/self.iru.height
        r1= r0/r 
        self.fxfy = h/self.iru.height if r1<r else w/self.iru.width
    
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

            
    # @db_session
    # def update_ui(self):
    @db_session
    def update_ui(self):
        '''
        Update self.mainui.entryframe and self.mainui.addinfoframe
        '''

        if self.iru_frame is None: self.show_nfd_info() ; return
        
        self.get_curr_f_encoding_and_id()

        # update entryframe
        if self.pause and (self.curr_face_id is not None):
            p = select(p for p in fm.Person \
                if p.id == self.curr_face_id ).first()
            if p is not None:
                self.mainui.entryframe.clear_content()
                
                self.mainui.entryframe.uuid_entry['state'] = 'normal'
                self.mainui.entryframe.uuid_entry.insert(0 , p.id)
                self.mainui.entryframe.uuid_entry['state'] = 'disabled'
                self.mainui.entryframe.name_entry.insert(0 , p.name)
                self.mainui.entryframe.DOB_entry.insert(0 , p.dob )
                self.mainui.entryframe.address_entry.insert(0 , p.address)
                self.mainui.entryframe.note_text.insert(END , p.note)
        
                # update addinfoframe
                i_s = select( i for i in PersonInfo \
                    if i.person_id == self.curr_face_id )
                    
                for i in i_s:
                    self.ins_rf( il_entry_value=i.label, v_value = i.value,\
                        note_value = i.note,    frame_name  = i.id )

        else:
                self.mainui.entryframe.uuid_entry['state'] = 'normal'
                self.mainui.entryframe.uuid_entry.delete(0, END)
                self.mainui.entryframe.uuid_entry['state'] = 'disabled'
                self.mainui.entryframe.name_entry.delete(0, END)
                self.mainui.entryframe.DOB_entry.delete(0, END)
                self.mainui.entryframe.address_entry.delete(0, END)
                self.mainui.entryframe.note_text.delete('1.0', END)

                self.rm_all_ins_rfs()
    
    def get_curr_f_encoding_and_id( self ):
        self.get_curr_f_encoding()
        self.get_curr_f_id()
                
    def mk_frame_rect( self ):

        for top, right, bottom, left in self.face_locations:
            cv2.rectangle( self.iru_frame, (left, top), \
            (right, bottom), (0, 0, 255), 2)

    def pick_f_mk_rect( self ):
        '''
        Pick face image to self.entryframe.face_label and make rectangles for 
        self.showframe.vid_frame_label.
        '''
        self.pick_face_by_num()
        self.mk_frame_rect()
    
    #def pick_face( self,  ):
    def pick_face_by_num( self, p_n = 0 ):

        if not self.pause: return
        self.face_num = self.face_num + p_n

        self.correct_f_num_ui()
                   
        if self.face_num < 0:
            self.show_nfd_info()
            if debug:
                print('No face detected')
            return

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


    def change_language(self, lang ):

        lang_display_name = self.mainui.langcombobox.lang_combobox_var.get()
        new_lang_code = Language.find( lang_display_name ).to_tag()

        if new_lang_code == lang_code: return

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:
                        
            setting_yml['lang_code'] = new_lang_code
            yaml.dump( setting_yml, open( setting_path, 'w') )

            if self.iru is not None:
                self.iru.release()

            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)

        pass



# SHOW_FRAME FUNCTIONS 
###############################################################################

    def show_nfd_info( self ):
        messagebox.showinfo( _('No face detected'), \
            _('Oops.., No face detected!') )

    def show_dob_error( self ):
        messagebox.showerror( _('Error'), \
            _('Check the DOB entry please!') ) 

###############################################################################
# SHOW_FRAME FUNCTIONS END

# ENTRY_FRAME FUNCTIONS
###############################################################################

    @db_session
    def save_db_encoding( self ):
        if self.pause: 
            if self.debug: print('Video is palying');   return
        if self.curr_f_encoding is None:  
            self.show_nfd_info() ;  return

        person_exists = Person.exists( id = self.curr_face_id )
        if person_exists:
            if self.debug:
                print( 'Person exists')
            p = select(p for p in fm.Person if \
                p.id == self.curr_face_id ).first()
            p.dob = self.mainui.entryframe.DOB_entry.get()
            p.name = self.mainui.entryframe.name_entry.get()
            p.note = self.mainui.entryframe.note_text.get(1.0, 'end')

        else:
            print('New person')
            p = Person( id = str(uuid.uuid4()),\
                name = self.mainui.entryframe.name_entry.get() ,\
                dob = self.mainui.entryframe.DOB_entry.get(), 
                address = self.mainui.entryframe.address_entry.get(),
                note = self.mainui.entryframe.note_text.get(1.0, 'end') )
        
        if self.debug:
            print( self.mainui.addinfoframe.ins_vars )

        for frame_name, info_widgets in self.ins_vars.items():
            label_value = info_widgets[0].get()
            value_v = info_widgets[1].get()
            note_value = info_widgets[2].get()

            if self.debug:
                print( label_value,  value_v, note_value)

            if len(label_value+  value_v+ note_value )< 1: continue
            
            if PersonInfo.exists(person_id =p.id, label =label_value):
                p_i = select( p for p in PersonInfo \
                    if p.person_id == p.id and p.label == label_value)\
                    .first()

                if self.debug: print( 'PersonInfo exists' )
                p_i.value = value_v;    p_i.note = note_value
            else:
                if self.debug: print( 'New PersonInfo' )
                PersonInfo( id = frame_name,
                    note = note_value,      person_id = person_id,      
                    label = label_value,    value = value_v
                )
        commit()

        self.known_encodings[ person_id] = self.known_encodings[ person_id] +\
            [ self.curr_f_encoding ]
        pickle.dump( self.known_encodings, open(face_encodings_path, 'wb'))
        
###############################################################################
# ENTRY_FRAME FUNCTIONS END

# ADD_INFO_FRAME FUNCTIONS
###############################################################################

###############################################################################
# ADD_INFO_FRAME FUNCTIONS  END

# LANGCOMBOBOX FUNCTIONS
###############################################################################

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
        self.vid = cv2.VideoCapture( self.video_source )

        if not self.vid.isOpened():
            messagebox.showerror( 
                _('Unable to open video source'), self.video_source )
            return
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        # 0 got when I tested it on msys.
        if debug and self.fps == 0 :
            print('self.pfs got 0, 25 insteaded')
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
