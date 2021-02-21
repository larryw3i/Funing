
from pony.orm import *
import os
import sys

from uuid import UUID
from datetime import date

from setting import base_dir, data_file_path
from pony.orm.dbapiprovider import OperationalError
from _fui.error import db_no_col

db = Database()

# https://docs.ponyorm.org/firststeps.html#database-binding
db.bind(provider='sqlite', filename = data_file_path )

class Person( db.Entity ):
    id = PrimaryKey( str )
    name = Optional( str )
    gender = Optional( str )
    dob = Optional( str )
    address = Optional( str )
    comment = Optional( str )

# additional informations
class PersonInfo( db.Entity ):
    id = PrimaryKey( str )
    person_id = Required( str )
    label = Required( str )
    value = Required( str )
    comment = Optional( str )
    
try:
    db.generate_mapping( create_tables = True )
except OperationalError as e:
    print( e )
    db_no_col( data_file_path )