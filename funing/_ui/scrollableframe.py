from  tkinter import  *
from tkinter.ttk import *


class ScrollableFrame(Frame):
    
    def __init__(self, container, orient = 0,*args, **kwargs):
        super().__init__(container, *args, **kwargs)
        top_frame =Frame( self)
        bottom_frame = Frame( self )
        canvas = Canvas(top_frame)
        self.scrollable_frame =Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        scrollbar = Scrollbar(top_frame if orient==0 else bottom_frame, \
        command=canvas.yview if orient==0 else canvas.xview, orient=VERTICAL \
        if orient== 0 else HORIZONTAL)
        if orient == 0:
            canvas.configure(yscrollcommand=scrollbar.set)
        else:
            canvas.configure(xscrollcommand=scrollbar.set)
        if orient == 2:
            _scrollbar = Scrollbar(self,  command=canvas.yview, orient=VERTICAL)
            canvas.configure(yscrollcommand=_scrollbar.set)
            _scrollbar.pack(side=RIGHT, fill=Y  )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=NW)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT if orient==0 else BOTTOM, \
        fill=Y if orient==0 else X )
        top_frame.pack(side=TOP)
        bottom_frame.pack(side=BOTTOM, fill=X)
