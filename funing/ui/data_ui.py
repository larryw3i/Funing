

import gettext
import tkinter as tk
import tkinter.filedialog as tkf
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *


class DataToplevel():
    def __init__(self):
        self.db_tl = Toplevel(borderwidth=10)
        self.db_tl.title(_('Data'))
        self.db_tl.resizable(0, 0)

    def destroy(self):
        self.db_tl.destroy()
        self.db_tl = None

    def mainloop(self):
        self.db_tl.mainloop()
    pass
