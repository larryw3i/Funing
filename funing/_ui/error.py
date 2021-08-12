
import platform
import webbrowser

system = platform.system()


def fp(content):
    print('::::::::::::::::::::::::::::::::::::::::::::')
    print(content)
    print('::::::::::::::::::::::::::::::::::::::::::::')


def read_install(notfound, url):
    try:
        webbrowser.open(url)
    except Exception as e:
        print(e)
        fp('The browser could not be started')

    return f"{notfound} can't be found, read {url} and install it. (^_^)"


def fp_r_i(notfound, url):
    fp(read_install(notfound, url))


def cv2_nf():
    fp_r_i('cv2', 'https://docs.opencv.org/4.5.1/da/df6/' +
           'tutorial_py_table_of_contents_setup.html'
           )


def gettext_nf():
    fp_r_i('gettext', 'https://www.gnu.org/software/gettext/')


def dlib_nf():
    fp_r_i('dlib', 'http://dlib.net/compile.html')


def f_r_nf():
    fp_r_i('face_recognition',
           'https://github.com/ageitgey/face_recognition#installation')


def db_no_col(db_path=''):
    if len(db_path) > 0:
        db_path = f'({db_path})'
    fp(f'Add specific column to database{db_path} ')


def lib_check():
    _exit = False
    try:
        import cv2
    except Exception as e:
        print(e)
        cv2_nf()
        _exit = True
    try:
        import gettext
    except Exception as e:
        print(e)
        gettext_nf()
        _exit = True
    if _exit:
        exit()
