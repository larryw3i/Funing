

import os
import sys
import yaml
import json
import pickle
import numpy as np
import shutil
import cv2
from funing import settings
from funing._fui import error; 

error.lib_check()

class Enjoy():
    def __init__(self):
        if not settings.initialized:
            self.initialize()

    def start(self):
        from ._main_ui import _MainUI
        _MainUI()
    
    def msgfmt( self ):
        for d in settings.locale_langcodes:
            po_p_p =  f'{settings.locale_path}/{d}/LC_MESSAGES'
            os.system(f'msgfmt -o {po_p_p}/funing.mo {po_p_p}/funing.po')

    def pip_install_r( self ):
        os.system('pip3 install -r requirements.txt ')
        
    def initialize( self ):
        first_mo_path = os.path.join( settings.locale_path, 'en-US', \
        'LC_MESSAGES', 'funing.mo')        
        if not os.path.exists( first_mo_path ):
            try: self.msgfmt()
            except Exception as e:
                print( e );error.gettext_nf();exit()
        for d in [ settings.faces_path, settings.infos_path ]:
            if not os.path.exists( d ): os.makedirs( d, exist_ok=True )  
        settings.config_yml["initialized"] = True
        config_path = os.path.join( settings.project_path , 'config.yml') 
        yaml.safe_dump( settings.config_yml ,  open( config_path, 'w' ) )

class Iru():
    def __init__(self, video_source = 0 ):
        self.recognizer=cv2.face.EigenFaceRecognizer_create()
        self.face_casecade=cv2.CascadeClassifier( settings.hff_xml_path )    
        self.video_source = video_source
        self.vid = None
        self.ret = None
        self.frame = None
        self.width = 0
        self.height = 0
        self.fps = 0
        self.infos = []
        self.infos_len = settings.infos_len
        self.training_data_empty = False
        self.recognizer_train()

    def infos_append( self , info_id ):
        if len( self.infos ) > self.infos_len:
            del infos[ 0 ]
        self.infos.append( info_id )
    
    def open_vid_cap( self ):
        self.vid = cv2.VideoCapture( self.video_source )
        if not self.vid.isOpened(): self.show_vid_src_error(); return
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        # 0 got when I tested it on msys.
        if self.fps == 0 : 
            self.fps = 25
            print('self.pfs got 0, 25 insteaded')
        if settings.debug:
            print( 'width: ', self.width, 'height: ', \
            self.height, 'fps: ', self.fps )
   
    def show_vid_src_error( self ):
        messagebox.showerror( 
            _('Unable to open video source'), self.video_source )

    def vid_release( self ):
        if self.vid is None: return
        self.vid.release()

    def load_images( self ):
        '''
        :reference https://www.cnblogs.com/do-hardworking/p/9867708.html
        '''
        images=[]
        ids=[]
        labels=[]   
        label=0        
        subdirs = os.listdir( settings.faces_path )
        if len(subdirs) <1 : self.training_data_empty = True
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
        images,labels,ids = self.load_images()
        if self.training_data_empty: return
        self.recognizer.train( images, labels)
            
    def face_rec( self ): 
        self.ret , self.frame = self.vid.read()
        gray_img=cv2.cvtColor( self.frame , cv2.COLOR_BGR2GRAY)
        faces = self.face_casecade.detectMultiScale(gray_img,1.3,5)                
        for (x,y,w,h) in faces:
            roi_gray=gray_img[y:y+h,x:x+w]
            roi_gray=cv2.resize(roi_gray,(92,112),\
            interpolation=cv2.INTER_LINEAR)
            if not self.training_data_empty:
                params = self.recognizer.predict(roi_gray)
                id = ids[params[0]]
                if not id in self.infos:
                    self.infos_append( id )

            self.frame = cv2.rectangle( self.frame,(x,y),(x+w,y+h),(255,0,0),2)