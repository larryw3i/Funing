
import os
import cv2
from locale.locale import _
from funing import settings

class iru():
    def __init__(self, video_source = 0 ):
        self.model=cv2.face.EigenFaceRecognizer_create()
        self.face_casecade=cv2.CascadeClassifier( settings.hff_xml_path )    
        self.video_source = video_source
        self.vid = None
        self.ret = None
        self.frame = None
        self.width = 0
        self.height = 0
        self.fps = 0
        self.rec_sign = False
        self.infos = []
        self.infos_len = self.infos_len

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
        if self.fps == 0 : self.fps = 25
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
        cv2.destroyAllWindows()

    def load_images( self ):
        '''
        :reference https://www.cnblogs.com/do-hardworking/p/9867708.html
        '''
        images=[]
        ids=[]
        labels=[]   
        label=0        
        for subdir in os.listdir("faces/"):
            subpath=os.path.join("faces",subdir)            
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

    def model_train( self ):
        images,labels,ids = self.load_images()
        self.model.train( images, labels)
            
    def face_rec( self ):               
        while( rec_sign ):
            self.ret , self.frame = self.vid.read()
            gray_img=cv2.cvtColor( self.frame , cv2.COLOR_BGR2GRAY)
            faces = self.face_casecade.detectMultiScale(gray_img,1.3,5)                
            for (x,y,w,h) in faces:
                roi_gray=gray_img[y:y+h,x:x+w]
                roi_gray=cv2.resize(roi_gray,(92,112),\
                interpolation=cv2.INTER_LINEAR)
                params=model.predict(roi_gray)
                id = ids[params[0]]   
                if not id in self.infos:
                    self.infos_append( id )