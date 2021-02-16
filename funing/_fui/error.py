import platform

system = platform.system()

def read_install( notfound, url ):
    return f"{notfound} can't be found, read {url} and install it. (^_^)"

def fp( content ):
    print('::::::::::::::::::::::::::::::::::::::::::::')
    print( content )
    print('::::::::::::::::::::::::::::::::::::::::::::')

def fp_r_i( notfound, url): 
    fp(self.read_install( notfound, url ))
    
def cv2_nf(self):
    fp_r_i('cv2',
'https://docs.opencv.org/master/df/d65/tutorial_table_of_content_introduction.html'
    )

def gettext_nf( ):
    fp_r_i('gettext', 'https://www.gnu.org/software/gettext/')

def dlib_nf():
    fp_r_i('dlib', 'http://dlib.net/compile.html')

def f_r_nf():
    fp_r_i('face_recognition',\
        'https://github.com/ageitgey/face_recognition#installation')

def db_no_col( db_path='' ):
    if len(db_path)>0: db_path = f'({db_path})'
    fp( f'Add specific column to database{db_path} (^_^)')

def lib_check():
    _exit = False
    try: import cv2
    except Exception as e: print(e); cv2_nf(); _exit = True
    try: import gettext
    except Exception as e: print(e); gettext_nf(); _exit = True
    try: import dlib
    except Exception as e: print(e); dlib_nf(); _exit = True
    try: import face_recognition
    except Exception as e: print(e); f_r_nf(); _exit = True
    
    if _exit: exit()
