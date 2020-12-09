
from pony.orm import *
import os
from  ..funing import Funing
# from uuid import UUID
# from datetime import date

f = Funing()

data_file_path = f.base_dir + '/data/funing.sqlite'
if not os.path.exists( data_file_path ):
    with open( data_file_path ,"w") as f: pass

db = Database()
db.bind(provider='sqlite', filename = data_file_path )

class FuningM( db.Entity ):
    id = PrimaryKey( UUID, auto = True )
    lang_code = Optional( str )

    person = Set('Person')

class Person( db.Entity ):
    id = PrimaryKey( UUID, auto = True )
    name = Optional( str )
    dob = Optional( date )
    note = Optional( str )
    face = Required( Json )

db.generate_mapping(create_tables=True)
