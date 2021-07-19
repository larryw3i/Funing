

from tkinter import messagebox
import tkinter as tk
from tkinter import *
from fui.main_ui import MainUI
from langcodes import Language
import gettext
import sys
import os
import tkinter.filedialog as tkf
import cv2
from PIL import Image , ImageTk
from funing.locale.lang import _
from datetime import datetime , date
import json
from funing import settings
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
        self.resize_rate = 0.25;    self.lang_code = settings.lang_code
        self.fxfy = None;           self.ins_vars = {}

        self.comparison_tolerance = settings.comparison_tolerance
        self.image_exts = ['jpg','png']
        self.video_exts = ['mp4','avi','3gp','webm','mkv']
        self.showf_sv = None;       self.rec_img = False
        self.showfm = self.mainui.showframe
        self.entryfm = self.mainui.entryframe
        self.infofm = self.mainui.infoframe
            
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
        # self.entryfm.prev_f_button['command'] = \
        #     lambda: self.pick_face_by_num(-1)
        # self.entryfm.next_f_button['command'] = \
        #     lambda: self.pick_face_by_num(1)
        # self.entryfm.save_button['command'] = self.save_db_encoding
        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy )
        # self.addinfofm.add_rf_button['command'] = self.ins_rf 
         
    def destroy( self ):
        if self.iru is not None: self.iru.vid_release()
        exit()

# SHOW_FRAME FUNCTIONS 
###############################################################################

    def save_ct( self , event):
        ct_stringvar_get = float(self.showfm.ct_stringvar.get())
        self.comparison_tolerance = comparison_tolerance = ct_stringvar_get
        config_yml['comparison_tolerance'] = ct_stringvar_get
        yaml.dump( config_yml, open( config_path, 'w') )
    
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
                filetypes = [ ( _('Image or video'), \
                    '*.'+(' *.'.join( self.image_exts + self.video_exts))) ],
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
            if settings.debug: print('play_video: Unable to open video source')
            return
        # Play
        self.pause = False
        self.get_resize_fxfy()
        self.refresh_frame()

        if settings.debug:
            print('fps: ', self.iru.fps)
           

    def rec_now( self ):        
        if self.rec_img: return
        if self.face_sum < 1:
            if settings.debug: print('No face detected')
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


        self.update_vid_frame()
        self.root_after = self.mainui.root.after( \
            int(1000/self.iru.fps) , self.refresh_frame )
    
    def update_vid_frame( self ):
        if self.fxfy is None: 
            if settings.debug: print('self.fxfy is None'); 
            return
        if self.iru_frame is None: 
            if settings.debug: print('self.iru_frame is None'); 
            return

        vid_img = cv2.resize( self.iru_frame, (0,0) , \
            fx = self.fxfy, fy = self.fxfy )
        vid_img = Image.fromarray( vid_img )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)

    

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
            if settings.debug: print('No face detected')
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
        
        if settings.debug:
            print( self.ins_vars )
            
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
        if settings.debug:
            print( 'new_lang_code: ', new_lang_code, \
            'lang_code: ', settings.lang_code )

        if new_lang_code == settings.lang_code: return

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:
            settings.config_yml['lang_code'] = new_lang_code
            yaml.dump( settings.config_yml, open( settings.config_path, 'w') )
            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)
        pass

###############################################################################
# LANGCOMBOBOX FUNCTIONS END

# OTHER FUNCTIONS
###############################################################################
        
###############################################################################
# OTHER FUNCTIONS END

