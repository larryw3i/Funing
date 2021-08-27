
import webbrowser
from tkinter import *
from tkinter.ttk import *

from funing import *
from funing._ui.lang import _


class AboutToplevel():
    def __init__(self):
        self.about_tl = Toplevel(borderwidth=10)
        self.about_tl.title(_('About Funing'))
        self.about_tl.resizable(0, 0)
        Label(self.about_tl, text=_('Funing'), font=("", 25)).pack()
        Label(self.about_tl, text=version).pack()
        self.source_page_label = Label(
            self.about_tl,
            text=source_page,
            foreground="blue",
            cursor="hand2")
        self.source_page_label.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new(source_page))
        self.source_page_label.pack()
        Label(self.about_tl, text=_('Licensed under the MIT license')).pack()
        Label(self.about_tl, text=_('From larryw3i & contributors')).pack()


def about_toplevel(): return AboutToplevel().about_tl
