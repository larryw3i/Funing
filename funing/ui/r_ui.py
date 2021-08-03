from tkinter import *
from funing.ui.c_ui import Cui

class Rui():
    def __init__(self, main_frame):
        self.main_frame = main_frame
        self.rui_frame = Frame( self.main_frame )
        self.create_frame = Frame( self.rui_frame )

    def set_c_ui(self):
        self.create_btn = Button( self.create_frame, text=_('Create'),\
        command = self.switch_to_c_ui )
        self.create_btn.pack()
        self.create_frame.pack()
        self.rui_frame.pack()
        pass

    def switch_to_c_ui(self):
        self.rui_frame.pack_forget()
        Cui(self.main_frame)
        pass

    def show(self):
        pass

    def hide(self):
        pass
