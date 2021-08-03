
from tkinter import *




class Cui():
    def __init__(self, main_frame):
        self.main_frame = main_frame
        self.cui_frame = Frame( self.main_frame )
        self.set_ui()
        self.set_var()
    
    def set_ui(self):
        # video label
        self.vid_frame_label = Label( self.cui_frame )

        self.showf_sv = StringVar( self.cui_frame )
        self.showf_entry = Entry( \
            self.cui_frame , width = 10, textvariable = self.showf_sv)
        self.showf_go_btn = Button(self.cui_frame, text = _('GO') )

        self.showf_t_dict =  { 'file':_('File'), 'camera': _('Camera') }
        self.showf_optionmenu_sv = StringVar(self.cui_frame, value = _('Open'))
        self.showf_optionmenu = OptionMenu( self.cui_frame, \
            self.showf_optionmenu_sv , *self.showf_t_dict.values() )

        # comparison_tolerance entry
        self.ct_label = Label( \
            self.cui_frame, text = _('tolerance') + ':' )
        self.ct_stringvar = StringVar( self.cui_frame, '' )
        self.ct_entry = Entry( self.cui_frame, width = 8,\
            textvariable = self.ct_stringvar )

        # shoot
        self.pr_sv = StringVar( self.cui_frame, _('Pause'))
        self.pp_btn = Button( self.cui_frame, \
            textvariable = self.pr_sv )

        self.pick_sv = StringVar( self.cui_frame, _('Pick'))
        self.pick_btn = Button( self.cui_frame, \
            textvariable = self.pick_sv )
    
            # place vid_frame_label
        self.vid_frame_label.grid( column = 0, row = 0, rowspan = 3,
            columnspan = 7 )

        self.face_show_frame = Frame( self.cui_frame )
        self.info_enter_frame = Frame( self.cui_frame )
        self.prevf_btn = Button( self.face_show_frame, text = _('prev_symb') )
        self.curf_label = Label( self.face_show_frame )
        self.nextf_btn = Button( self.face_show_frame, text = _('next_symb') )
        self.ft_sb = Scrollbar(self.info_enter_frame, orient=VERTICAL)
        self.faces_text = Text( self.info_enter_frame,  \
        yscrollcommand = self.ft_sb.set)  
        self.save_btn = Button( self.cui_frame, text = _("Save") )
        self.ft_sb.config(command = self.faces_text.yview)          

        self.showf_entry.grid( column = 0, row = 4, sticky = E)
        self.showf_go_btn.grid( column = 1, row = 4, sticky = W)
        self.showf_optionmenu.grid( column = 2, row = 4 , sticky = W)
        self.ct_label.grid( column = 3, row = 4, sticky = E )
        self.ct_entry.grid( column = 4, row = 4, sticky = W )
        self.pp_btn.grid( column = 5, row = 4)
        self.pick_btn.grid( column = 6, row = 4 )        
        # place frame
        self.cui_frame.grid( column = 0, row = 0 )        


        self.prevf_btn.pack(side = LEFT)
        self.curf_label.pack(side = LEFT)
        self.nextf_btn.pack(side = LEFT)
        self.faces_text.pack(side=LEFT,fill=Y)
        self.ft_sb.pack(side=RIGHT,fill=Y)
        self.face_show_frame.grid( column = 0, row = 0, columnspan = 5)
        self.info_enter_frame.grid( column = 0, row = 1, columnspan = 5)
        self.save_btn.grid( column = 2, row = 2 )
        self.cui_frame.grid( column = 1, row = 0 )

    
    def show(self):
        pass

        