
from pony.orm import *
import os
import sys

from uuid import UUID
from datetime import date

from _ui import _
from setting import base_dir

db = Database()

data_file_p_path = base_dir + '/data'
data_file_path = data_file_p_path + '/funing.sqlite'

if not os.path.exists( data_file_p_path ):
    os.mkdir( data_file_p_path )
if not os.path.exists( data_file_path ):
    with open( data_file_path ,"w") : pass

db.bind(provider='sqlite', filename = data_file_path )

class Person( db.Entity ):
    id = PrimaryKey( UUID, auto = True )
    name = Optional( str )
    dob = Optional( date )
    note = Optional( str )
    face = Required( Json )
    
class FuningData( db.Entity ):
    id = PrimaryKey( UUID, auto = True )
    lang_code = Optional( str )

db.generate_mapping(create_tables=True)
