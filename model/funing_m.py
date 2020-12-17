
from pony.orm import *
import os
import sys

from uuid import UUID
from datetime import date

from _ui import _
from _ui.setting import base_dir

db = Database()

class Person( db.Entity ):
    id = PrimaryKey( UUID, auto = True )
    name = Optional( str )
    dob = Optional( date )
    note = Optional( str )
    face = Required( Json )
    
class FuningData( db.Entity ):
    id = PrimaryKey( UUID, auto = True )
    lang_code = Optional( str )



class FuningM():
    def generate_mapping(self):

        data_file_path = base_dir + '/data/funing.sqlite'

        if not os.path.exists( data_file_path ):
            with open( data_file_path ,"w") : pass

        db.bind(provider='sqlite', filename = data_file_path )
        db.generate_mapping(create_tables=True)

        print( _('generate mapping successfully!') )
