

class DBToplevel():
    def __init__(self):
        self.db_tl = Toplevel(borderwidth=10)
        self.db_tl.title(_('Data'))
        self.db_tl.resizable(0, 0)
    pass

def db_toplevel(): return DBToplevel()