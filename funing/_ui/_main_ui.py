

from tkinter import messagebox
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from funing.ui.main_ui import MainUI
from langcodes import Language
import gettext
import sys
import os
import tkinter.filedialog as tkf
import cv2
from PIL import Image , ImageTk
from funing._ui.lang import _
from datetime import datetime , date
from funing import settings
import yaml
import uuid
import time
import re
from funing._ui import error
import numpy as np
from cv2 import haarcascades
import webbrowser

class _MainUI():
    def __init__(self):
        self.mainui = MainUI()
        self.mainui.place()
        self.source = -1
        self.root_after = -1
        # face num for face_label
        self.lang_code = settings.lang_code
        self.fxfy = None
        self.image_exts = ['jpg','png', 'jpeg', 'webp']
        self.video_exts = ['mp4','avi','3gp','webm','mkv']
        self.showf_sv = None
        self.showfm = self.mainui.showframe
        self.infofm = self.mainui.infoframe
        self.rbmixfm = self.mainui.rbmixframe
        self.about_tl = None
        # vid
        self.vid = None
        self.vid_width = 0
        self.vid_height = 0
        self.vid_fps = 0

        self.source_type = -1 # 0-> img , 1-> video

        self.cur_frame = None
        self.face_rects = []
        self.picked_face_frames = []
        self.showed_face_frames = []
        self.show_size = (200,200)
        self.zoom_in_size = (210,210)
        self.save_size = (100,100)
        self.zoomed_in_face_label = (0,0)
        
        self.doing = 'p'  # 'p'->'pick', r->'rec'

        self.pause = False
        self.face_frames = []
        self.curf_index = 0
        # rec_result
        self.rec_gray_img = None
        # rec_faces
        self.recfs = []
        # info
        self.cur_info_id = None
        self.info_ids = []
        # cv2
        self.hff_xml_path = os.path.join( haarcascades ,\
         "haarcascade_frontalface_default.xml" )
        self.recognizer=cv2.face.EigenFaceRecognizer_create()
        self.face_casecade=cv2.CascadeClassifier( self.hff_xml_path )   
        self.face_enter_count = settings.face_enter_count
        #screen
        try:self.screenwidth = self.mainui.root.winfo_screenwidth();\
            self.screenheight = self.mainui.root.winfo_screenheight()
        except: print(_('No desktop environment is detected! ')); exit()  
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
    
    def about_fn(self):
        if self.about_tl == None:
            self.about_tl = Toplevel(borderwidth = 10)
            self.about_tl.title(_('About Funing'))
            self.about_tl.resizable(0,0)
            Label( self.about_tl, text =_('Funing'), font=("", 25)).pack()
            Label(  self.about_tl, text = settings.version ).pack()
            self.source_page_label = Label(self.about_tl, text=\
            settings.source_page, foreground="blue", cursor="hand2")
            self.source_page_label.bind("<Button-1>",lambda e: \
            webbrowser.open_new(settings.source_page ))
            self.source_page_label.pack()
            Label(self.about_tl,text=_('Licensed under the MIT license') )\
            .pack()
            self.about_tl.mainloop()
        else:
            self.about_tl.destroy()
            self.about_tl = None
        pass

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
        self.rbmixfm.lang_combobox.bind('<<ComboboxSelected>>',
            self.change_language )
        self.showfm.ct_entry.bind('<FocusOut>', None )
        self.showfm.pp_btn['command'] = self.pause_play
        self.showfm.rec_btn['command'] = self.recf_v0
        self.showfm.pick_btn['command'] = self.pick_v0
        self.showfm.showf_go_btn['command'] = self.show_go
        self.showfm.showf_optionmenu_sv.trace('w', self.show_from )
        # self.infofm.prevf_btn['command'] = self.prevf
        # self.infofm.nextf_btn['command'] = self.nextf
        self.infofm.save_btn['command'] = self.savef
        self.rbmixfm.about_fn_btn['command'] = self.about_fn
        self.mainui.root.protocol("WM_DELETE_WINDOW", self.destroy )
         
    def destroy( self ):
        if self.vid is not None: self.vid.release()
        exit()

    def pause_play( self, *args ):
        if self.source_type != 1 : return
        if self.pause: 
            self.pause = False
            self.refresh_frame()
            self.showfm.pp_sv.set( _('Pause') )
            if settings.debug:
                print( 'Play. . .' )
            
        else:
            self.root_after_cancel()
            self.showfm.pp_sv.set( _('Play') )
            self.pause = True
            if settings.debug:
                print( 'Pause. . .' )

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
        
        self.infofm.face_text.delete(1.0,END)
        self.change_face_show(0)

    def pick_v0(self):
        
        if self.doing == 'r':
            self.clear_faces_frame()
            self.doing ='p'

        if (not self.pause) and self.vid :
            _, self.cur_frame = self.vid.read()
            
        if self.cur_frame is None: return

        self.clear_face_text()

        self.cur_info_id = str(uuid.uuid4())
        
        gray_img=cv2.cvtColor(self.cur_frame,cv2.COLOR_BGR2GRAY)
        self.face_rects = self.face_casecade.detectMultiScale(gray_img,1.3,5)
        
        if settings.debug:
            print( self.face_rects )
            print( type( self.face_rects ) )

        for i in range( len( self.face_rects)):
            self.add_face_label_p( i )

    def clear_face_text( self ):
        self.infofm.face_text.delete(1.0,END)

    def add_face_label_p(self, num):
        
        x,y,w,h = self.face_rects[ num ]
        _w = max( w, h )
        
        new_fl = Label( self.infofm.faces_frame )
        frame = self.cur_frame[y:y+_w, x:x+_w]
        frame = cv2.resize( frame, self.show_size )
        vid_img = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB )
        vid_img = Image.fromarray( vid_img  )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        new_fl.imgtk = imgtk
        new_fl.configure(image=imgtk)
        new_fl.bind("<Button-1>",lambda e: self.del_face_label_p(e , num) )

        new_fl.pack(side=LEFT)

        picked_face_frame = cv2.resize(self.cur_frame[y:y+h,x:x+w],self.save_size,\
        interpolation=cv2.INTER_LINEAR)
        self.picked_face_frames.append( picked_face_frame )

    def del_face_label_p( self, e, num):
        del self.picked_face_frames[ num ]
        e.widget.destroy()
        if settings.debug:
            print( len(self.picked_face_frames) )

    def show_go( self, *args ):
        self.showf_sv = self.showfm.showf_sv.get()
        if len( self.showf_sv.strip() ) < 1: return
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
            
            if self.vid is not None and self.vid.isOpened():
                _, self.cur_frame = self.vid.read()

            self.mainui.root.after_cancel( self.root_after )
            self.close_vid_cap()
            self.vid = None
        
    def play_video( self ):
        self.pause = False
        self.source_type = 1
        self.close_vid_cap()
        self.open_vid_cap()
        self.get_vid_resize_fxfy()
        self.refresh_frame()
    
    def refresh_frame(self):
        if self.source_type == 0:return
        if self.vid == None: self.vid = cv2.VideoCapture( self.source )
        if not self.vid.isOpened(): self.show_nsrc_error(); return

        _, frame = self.vid.read()

        gray_img=cv2.cvtColor( frame,cv2.COLOR_BGR2GRAY)
        rects = self.face_casecade.detectMultiScale(gray_img,1.3,5)

        for (x,y,w,h) in rects:
            frame=cv2.rectangle( frame,(x,y),(x+w,y+h),(255,0,0),2)  
        rects = None

        vid_img = cv2.resize( frame , (0,0) , \
            fx = self.fxfy, fy = self.fxfy )

        vid_img = cv2.cvtColor( vid_img, cv2.COLOR_BGR2RGB )
        vid_img = Image.fromarray( vid_img )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        self.showfm.vid_frame_label.imgtk = imgtk
        self.showfm.vid_frame_label.configure(image=imgtk)

        if not self.pause:
            self.root_after = self.mainui.root.after( \
                int(1000/self.vid_fps) , self.refresh_frame )


    def get_img_resize_fxfy( self ):
        w = self.screenwidth/2
        h = self.screenheight/2
        r = w/h 
        
        self.vid_width, self.vid_height, _ = self.cur_frame.shape

        r0 = self.vid_width/self.vid_height
        r1= r0/r 
        self.fxfy = h/self.vid_height if r1<r else w/self.vid_width
        if settings.debug:
            print('self.fxfy: ', self.fxfy)
        

    def view_image( self ):
        self.source_type = 0
        self.root_after_cancel()

        self.cur_frame  = cv2.imread( self.face_src_path )

        if settings.debug:
            print( self.cur_frame.shape,self.cur_frame.size )
            
        self.get_img_resize_fxfy()
        
        self.cur_frame = cv2.resize( self.cur_frame , (0,0) , \
            fx = self.fxfy, fy = self.fxfy )

        self.rec_gray_img=cv2.cvtColor(self.cur_frame,cv2.COLOR_BGR2GRAY)
        self.face_rects=self.face_casecade.detectMultiScale(\
        self.rec_gray_img,1.3,5)

        if len( self.face_rects ) < 1: return        
        
        for (x,y,w,h) in self.recfs:
            self.cur_frame=cv2.rectangle(\
            self.cur_frame,(x,y),(x+w,y+h),(255,0,0),2)  

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

    def get_vid_resize_fxfy( self ):
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

    def prevf( self ):
        self.change_face_show(-1)
        pass

    def nextf( self ):
        self.change_face_show(+1)
        pass
    
    def savef( self ):
        if self.cur_info_id == None: return
        info =self.infofm.face_text.get("1.0", "end-1c")
        info_file_path = os.path.join( settings.infos_path, self.cur_info_id )
        open( info_file_path, 'w+' ).write( info )
        img_path =os.path.join( settings.faces_path , self.cur_info_id )
        os.makedirs(img_path,exist_ok=True )
        count = 0
        for f in self.picked_face_frames:
            cv2.imwrite( f'{img_path}/{count}.png' , f)
            count+=1
        self.cur_info_id = None
        if settings.debug:print( 'info > ' + info )
        self.recognizer_train()
    
    def update_num_label(self):
        self.infofm.num_label['text'] = \
        f'{self.curf_index+1}/{len(self.face_frames)+len(self.recfs)-1}'
            
    def change_face_show(self, _as, rec = True):
        if len(self.face_frames) >0:
            # NEW
            self.curf_index += _as
            self.curf_index = 0 if self.curf_index < 0 else self.face_enter_count-1\
            if self.curf_index >= self.face_enter_count else self.curf_index 

            vid_img = cv2.cvtColor( self.face_frames[ self.curf_index ], \
            cv2.COLOR_BGR2RGB )
            vid_img = Image.fromarray( vid_img )
            imgtk = ImageTk.PhotoImage( image=vid_img )
            self.infofm.curf_label.imgtk = imgtk
            self.infofm.curf_label.configure(image=imgtk)
            self.update_num_label()

        elif len(self.recfs) > 0:
            # RECOGNIZE
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
            _h = h if h>w else w
            frame = self.cur_frame[y:y+_h,x:x+_h]
            frame = cv2.resize(frame, (200,200))

            vid_img = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB )
            vid_img = Image.fromarray( vid_img  )
            imgtk = ImageTk.PhotoImage( image=vid_img )
            self.infofm.curf_label.imgtk = imgtk
            self.infofm.curf_label.configure(image=imgtk)

            info_file_path = os.path.join( \
            settings.infos_path,  _id )
            self.infofm.face_text.delete(1.0,END)
            self.infofm.face_text.insert('1.0', \
            open( info_file_path, 'r' ).read() )
            self.update_num_label()
    
    def recf(self):
        self.face_frames = []
        self.recfs = []
        if settings.debug: 
            print('self.cur_frame not None')
        self.rec_gray_img=cv2.cvtColor(self.cur_frame,cv2.COLOR_BGR2GRAY)
        self.face_rects=self.face_casecade.detectMultiScale(\
        self.rec_gray_img,1.3,5)
        if len( self.recfs ) < 1: return        
        
        self.change_face_show(0)

        for (x,y,w,h) in self.recfs:
            self.cur_frame=cv2.rectangle(\
            self.cur_frame,(x,y),(x+w,y+h),(255,0,0),2)  

        self.cur_frame2label()
    
    def restore_face_label_size( self, index ):
        label, index = self.zoomed_in_face_label
        if not label.winfo_exists(): return
        
        frame =  self.showed_face_frames[ index ]
        frame = cv2.resize(frame, self.show_size )

        vid_img = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB )
        vid_img = Image.fromarray( vid_img  )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        label.imgtk = imgtk
        label.configure(image=imgtk)


    def show_info( self, label, _id, index):

        if (self.zoomed_in_face_label[0]!=0) and \
        (self.zoomed_in_face_label[0] != label) :
            self.restore_face_label_size( index )

        frame =  self.showed_face_frames[ index ]
        frame = cv2.resize(frame, self.zoom_in_size )

        vid_img = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB )
        vid_img = Image.fromarray( vid_img  )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.zoomed_in_face_label = (label, index)

        info_file_path = os.path.join( \
        settings.infos_path,  _id )
        self.infofm.face_text.delete(1.0,END)
        
        if not os.path.exists( info_file_path ): 
            self.infofm.face_text.insert('1.0', _('No informations found') )

        self.infofm.face_text.insert('1.0', \
        open( info_file_path, 'r' ).read() )


    def add_face_label_r( self, num ):

        index = len( self.showed_face_frames )

        new_fl = Label( self.infofm.faces_frame )

        x,y,w,h = self.face_rects[ num ]
        roi_gray= self.rec_gray_img[y:y+h,x:x+w]
        roi_gray= cv2.resize( roi_gray, self.save_size,\
        interpolation=cv2.INTER_LINEAR)
    
        result=self.recognizer.predict(roi_gray)

        _id = self.info_ids[result[0]]
        _h = max( h, w )
        frame = self.cur_frame[y:y+_h,x:x+_h]
        frame = cv2.resize(frame, self.show_size )

        self.showed_face_frames.append( frame )

        vid_img = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB )
        vid_img = Image.fromarray( vid_img  )
        imgtk = ImageTk.PhotoImage( image=vid_img )
        new_fl.imgtk = imgtk
        new_fl.configure(image=imgtk)

        new_fl.bind("<Double-Button-1>",lambda e: \
        self.del_face_label_r(e, index))

        new_fl.bind("<Button-1>",lambda e: self.show_info(new_fl , _id, index) )

        new_fl.pack(side=LEFT)

        self.show_info(new_fl , _id, index)

             
    def del_face_label_r( self, e, index):
        if self.zoomed_in_face_label[0] == e.widget:
            self.zoomed_in_face_label= (0,0)
        e.widget.destroy()
        self.showed_face_frames[index] = None
    
    def clear_faces_frame( self ):
        for child in self.infofm.faces_frame.winfo_children():
            child.destroy()


    def recf_v0(self):

        if self.source_type == -1:return
        if (not self.pause) and self.vid:
            _, self.cur_frame = self.vid.read()
        
        if settings.data_empty():
            self.show_data_empty()
            return
        
        if self.doing == 'p':
            self.clear_faces_frame()
            self.doing ='r'

        if self.cur_frame is None: return
        
        self.clear_face_text()

        self.rec_gray_img=cv2.cvtColor(self.cur_frame,cv2.COLOR_BGR2GRAY)
        self.face_rects=self.face_casecade.detectMultiScale(\
        self.rec_gray_img,1.3,5)

        if len( self.face_rects ) < 1: 
            if settings.debug:
                print('len( self.face_rects ) < 1 ')
            return

        for i in range( len(self.face_rects)) :
            self.add_face_label_r(i)
            
             
    def change_language(self, lang ):

        lang_display_name = self.rbmixfm.lang_combobox_var.get()
        new_lang_code = Language.find( lang_display_name ).to_tag()
        new_lang_code.replace('-','_')
        if settings.debug:
            print( 'new_lang_code: ', new_lang_code, \
            'lang_code: ', settings.lang_code )

        if new_lang_code == settings.lang_code: return

        restartapp = messagebox.askyesno(
            title = _('Restart Funing Now?')
        )
        if restartapp:
            settings.config_yml['lang_code'] = new_lang_code
            yaml.dump( settings.config_yml, open( settings._config_path, 'w') )
            sys_executable = sys.executable
            os.execl(sys_executable, sys_executable, * sys.argv)
        pass

    def show_nsrc_error( self ):
        unable_open_s = _('Unable to open video source')
        messagebox.showerror(  unable_open_s, unable_open_s+': '+self.showf_sv )
    def show_data_empty( self ):
        unable_open_s = _('Nothing enter')
        msg  = _("You haven't entered anything yet! ")
        messagebox.showerror(  unable_open_s, msg, )
        