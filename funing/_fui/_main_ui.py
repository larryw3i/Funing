

from tkinter import messagebox
import tkinter as tk
from tkinter import *
from funing.fui.main_ui import MainUI
from langcodes import Language
import gettext
import sys
import os
import tkinter.filedialog as tkf
import cv2
from PIL import Image , ImageTk
from funing.locale.lang import _
from datetime import datetime , date
from funing import settings
import yaml
import uuid
import time
import re
from funing._fui import error
import numpy as np
from cv2 import haarcascades

class _MainUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()
        self.source = 0
        self.root_after = -1        
        # face num for face_label
        self.lang_code = settings.lang_code
        self.fxfy = None        
        self.image_exts = ['jpg','png']
        self.video_exts = ['mp4','avi','3gp','webm','mkv']
        self.showf_sv = None
        self.showfm = self.mainui.showframe
        self.entryfm = self.mainui.entryframe
        self.infofm = self.mainui.infoframe   
        # vid
        self.vid = None
        self.vid_width = 0
        self.vid_height = 0
        self.vid_fps = 0
        self.cur_frame = None
        self.pause = True
        self.face_frames = []
        self.curf_index = 0
        # rec_result
        self.rec_gray_img = None
        # rec_faces
        self.recfs = []
        # info
        self.cur_info_id = None
        self.info_ids = []
        # self.rec_results = []
        # cv2
        self.hff_xml_path = os.path.join( haarcascades ,\
         "haarcascade_frontalface_default.xml" )
        self.recognizer=cv2.face.EigenFaceRecognizer_create()
        self.face_casecade=cv2.CascadeClassifier( self.hff_xml_path )   
        self.face_enter_count = settings.face_enter_count
        #screen
        try:self.screenwidth = self.mainui.root.winfo_screenwidth();\
            self.screenheight = self.mainui.root.winfo_screenheight()
        except: print(_('No desktop environment is detected! (^_^)')); exit()  
        if not settings.data_empty():
            self.recognizer_train()           
        self.set_ui_events()
        self.mainui.mainloop()    

    def load_images( self ):
        '''
        :reference https://www.cnblogs.com/do-hardworking/p/9867708.html
        '''
        images=[]
        ids=[]
        labels=[]   
        label=0        
        subdirs = os.listdir( settings.faces_path )
        for subdir in subdirs:
            subpath=os.path.join( settings.faces_path ,subdir)            
            if os.path.isdir(subpath):
                ids.append(subdir)
                for filename in os.listdir(subpath):
                    imgpath=os.path.join(subpath,filename)
                    img=cv2.imread(imgpath,cv2.IMREAD_COLOR)
                    gray_img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                    images.append(gray_img)
                    labels.append(label)
                label+=1
        images=np.asarray(images)
        labels=np.asarray(labels)
        return images,labels,ids

    def recognizer_train( self ):
        images,labels,self.info_ids = self.load_images()
        self.recognizer.train( images, labels)

    def open_vid_cap( self ):
        self.vid = cv2.VideoCapture( self.source )
        if not self.vid.isOpened(): self.show_nsrc_error(); return
        self.vid_width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.vid_height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.vid_fps = self.vid.get(cv2.CAP_PROP_FPS)
    
    def close_vid_cap( self ):
        if self.vid is None: return
        self.vid.release()  
        self.vid= None  
    
    def set_ui_events( self ):
        self.mainui.langcombobox.lang_combobox.bind('<<ComboboxSelected>>',
            self.change_language )
        self.showfm.ct_entry.bind('<FocusOut>', None )
        self.showfm.pp_btn['command'] = self.pause_play
        self.showfm.pick_btn['command'] = self.pick
        self.showfm.showf_go_btn['command'] = self.show_go
        self.showfm.showf_optionmenu_sv.trace('w', self.show_from )
        self.infofm.prevf_btn['command'] = self.prevf
        self.infofm.nextf_btn['command'] = self.nextf
        self.infofm.save_btn['command'] = self.savef
        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy )
         
    def destroy( self ):
        if self.vid is not None: self.vid.release()
        exit()

# SHOW_FRAME FUNCTIONS 
###############################################################################

    def pause_play( self, *args ):
        if self.pause: 
            self.pause = False
            if self.vid is None: return
            self.root_after_cancel()
            if settings.data_empty(): 
                if settings.debug: print('data is empty!')
                self.show_data_empty_error()
                return
            if self.cur_frame is None: return
            self.recf()
            self.showfm.pp_sv.set( _('Play') )
            # self.pick()
        else:
            self.pause = True
            if self.cur_frame is None: return
            self.refresh_frame()
            self.showfm.pp_sv.set( _('Recognize') )

    def pick(self):
        if self.vid is None: return
        count = 0
        self.cur_info_id = str(uuid.uuid4())
        self.recfs = []
        self.face_frames = []
        while(True):
            ret, self.frame=self.vid.read()
            if ret:
                gray_img=cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
                faces = self.face_casecade.detectMultiScale(gray_img,1.3,5)
                if len( faces ) < 1:continue
                x,y,w,h = faces[0]
                new_frame=cv2.resize( self.frame[y:y+h,x:x+w], (92,112),\
                    interpolation=cv2.INTER_LINEAR)
                self.face_frames.append( new_frame )
                count+=1
                if count > self.face_enter_count: break
        self.change_face_show(0)
    
    def show_go( self, *args ):
        self.showf_sv = self.showfm.showf_sv.get()
        self.rec_img = False
        self.root_after_cancel()
        showf_ext = self.showf_sv.split('.')[-1]
        if showf_ext in self.video_exts:
            self.source = self.showf_sv
            self.play_video()
            return
        if re.match(r'\d+', self.showf_sv):
            self.source = int(self.showf_sv)
            self.play_video()
            return
        if showf_ext in self.image_exts:
            self.view_image()
            return 
        self.showfm.showf_sv.set('')
        self.show_nsrc_error()
    
    def get_dict_key_by_value( self , _dict, value ):
        keys =  _dict.keys()
        values = _dict.values()
        return list(keys)[ list( values ).index( value )]
            
    def show_from( self, *args  ):
        show_f = self.get_dict_key_by_value( 
            self.showfm.showf_t_dict, 
            self.showfm.showf_optionmenu_sv.get() )
        if show_f == 'file':
            self.face_src_path = tkf.askopenfilename(\
            title = _('Select a file'),\
            filetypes = [ ( _('Image or video'), \
            '*.'+(' *.'.join( self.image_exts + self.video_exts))) ],\
            initialdir = '~')
            if len( self.face_src_path ) < 1: return 
            ext = os.path.splitext( self.face_src_path )[1][1:]
            self.showfm.showf_sv.set( self.face_src_path )
            if ext in self.image_exts: 
                self.view_image()
            elif ext in self.video_exts: 
                self.source = self.face_src_path
                self.play_video()
        elif show_f == 'camera':
            self.source = 0
            self.showfm.showf_sv.set( self.source )
            self.play_video()
    
    def root_after_cancel( self ):
        if self.root_after != -1:
            self.mainui.root.after_cancel( self.root_after )
            self.close_vid_cap()
            self.vid = None
        
    def play_video( self ):
        self.close_vid_cap()
        self.open_vid_cap()
        self.get_resize_fxfy()
        self.refresh_frame()
    
    def refresh_frame(self):
        if self.vid == None: self.vid = cv2.VideoCapture( self.source )
        if not self.vid.isOpened(): self.show_nsrc_error(); return
        ret, self.cur_frame = self.vid.read()        
        self.cur_frame2label()
        self.root_after = self.mainui.root.after( \
            int(1000/self.vid_fps) , self.refresh_frame )

    def view_image( self ):
        self.cur_frame  = cv2.imread( self.face_src_path )
        frame = cv2.cvtColor( self.cur_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray( frame )
        imgtk = ImageTk.PhotoImage( image= img )
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)
           
    def cur_frame2label( self ):
        vid_img = cv2.resize( self.cur_frame , (0,0) , \
            fx = self.fxfy, fy = self.fxfy )
        vid_img = cv2.cvtColor( vid_img, cv2.COLOR_BGR2RGB )
        vid_img = Image.fromarray( vid_img )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)

    def get_resize_fxfy( self ):
        if self.vid_width == self.vid_height == 0: 
            if debug: print('self.iru is None')
            return
        w = self.screenwidth/2
        h = self.screenheight/2
        r = w/h 
        r0 = self.vid_width/self.vid_height
        r1= r0/r 
        self.fxfy = h/self.vid_height if r1<r else w/self.vid_width
        if settings.debug:
            print('self.fxfy: ', self.fxfy)

    def show_nsrc_error( self ):
        unable_open_s = _('Unable to open video source')
        messagebox.showerror( unable_open_s, unable_open_s+': '+self.showf_sv )


###############################################################################
# SHOW_FRAME FUNCTIONS END

# ENTRY_FRAME FUNCTIONS
###############################################################################

        
###############################################################################
# ENTRY_FRAME FUNCTIONS END

# INFO_FRAME FUNCTIONS
###############################################################################

    def prevf( self ):
        self.change_face_show(-1)
        pass

    def nextf( self ):
        self.change_face_show(+1)
        pass
    
    def savef( self ):
        if self.cur_info_id == None: return
        info =self.infofm.faces_text.get("1.0", "end-1c")
        info_file_path = os.path.join( settings.infos_path, self.cur_info_id )
        open( info_file_path, 'w+' ).write( info )
        img_path =os.path.join( settings.faces_path , self.cur_info_id )
        os.makedirs(img_path,exist_ok=True )
        count = 0
        for f in self.face_frames:
            cv2.imwrite( f'{img_path}/{count}.png' , f)
            count+=1
        self.cur_info_id = None
        if settings.debug:print( 'info > ' + info )
        self.recognizer_train()
            
    def change_face_show(self, _as):
        if len(self.face_frames) >0:
            self.curf_index += _as
            self.curf_index = 0 if self.curf_index < 0 else self.face_enter_count-1\
            if self.curf_index >= self.face_enter_count else self.curf_index 
            vid_img = cv2.cvtColor( self.face_frames[ self.curf_index ], \
            cv2.COLOR_BGR2RGB )
            vid_img = Image.fromarray( vid_img )
            imgtk = ImageTk.PhotoImage( image=vid_img )
            self.infofm.curf_label.imgtk = imgtk
            self.infofm.curf_label.configure(image=imgtk)
        elif len(self.recfs) > 0:
            _len = len( self.recfs )
            self.curf_index+=_as
            self.curf_index = 0 if self.curf_index < 0 else _len - 1\
            if self.curf_index >= _len else self.curf_index 

            x,y,w,h = self.recfs[ self.curf_index ]
            roi_gray= self.rec_gray_img[y:y+h,x:x+w]
            roi_gray= cv2.resize( roi_gray, (92,112),\
            interpolation=cv2.INTER_LINEAR)
            result=self.recognizer.predict(roi_gray)
            _id = self.info_ids[result[0]]
            frame = self.cur_frame[y:y+h,x:x+w] 

            vid_img = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB )
            vid_img = Image.fromarray( vid_img  )
            imgtk = ImageTk.PhotoImage( image=vid_img )
            self.infofm.curf_label.imgtk = imgtk
            self.infofm.curf_label.configure(image=imgtk)

            info_file_path = os.path.join( \
            settings.infos_path,  _id )
            self.infofm.faces_text.delete(1.0,tk.END)
            self.infofm.faces_text.insert('1.0', \
            open( info_file_path, 'r' ).read() )
    
    def recf(self):
        self.face_frames = []
        self.recfs = []
        if settings.debug: 
            print('self.cur_frame not None')
        self.rec_gray_img=cv2.cvtColor(self.cur_frame,cv2.COLOR_BGR2GRAY)
        self.recfs=self.face_casecade.detectMultiScale(self.rec_gray_img,1.3,5)
        if len( self.recfs ) < 1: return
        self.change_face_show(0)
        for (x,y,w,h) in self.recfs:
            self.cur_frame=cv2.rectangle(\
            self.cur_frame,(x,y),(x+w,y+h),(255,0,0),2)  
        self.cur_frame2label()




             
###############################################################################
# INFO_FRAME FUNCTIONS  END

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
    def show_nsrc_error( self ):
        unable_open_s = _('Unable to open video source')
        messagebox.showerror(  unable_open_s, unable_open_s+': '+self.showf_sv )
    def show_data_empty_error( self ):
        unable_open_s = _('Nothing enter')
        msg  = _("You haven't entered anything yet! ")
        messagebox.showerror(  unable_open_s, msg, )

###############################################################################
# OTHER FUNCTIONS END

