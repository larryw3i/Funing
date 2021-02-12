
from pony.orm import *
import os
import sys

from uuid import UUID
from datetime import date

from setting import base_dir, data_file_path
from pony.orm.dbapiprovider import OperationalError

db = Database()



# https://docs.ponyorm.org/firststeps.html#database-binding
db.bind(provider='sqlite', filename = data_file_path )

class Person( db.Entity ):
    id = PrimaryKey( str )
    name = Optional( str )
    dob = Optional( date )
    address = Optional( str )
    note = Optional( str )

# additional informations
class PersonInfo( db.Entity ):
    id = PrimaryKey( str )
    person_id = Required( str )
    label = Required( str )
    dregex = Required( str )
    value = Required( str )
    note = Optional( str )
    
try:
    db.generate_mapping( create_tables = True )
except OperationalError as e:
    print( e )
    print('\nAdd specific column to database (^_^)\n' )