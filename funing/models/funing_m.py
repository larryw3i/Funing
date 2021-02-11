
from pony.orm import *
import os
import sys

from uuid import UUID
from datetime import date

from setting import base_dir
from pony.orm.dbapiprovider import OperationalError

db = Database()

data_file_p_path = base_dir + '/data'
data_file_path = data_file_p_path + '/funing.sqlite'

if not os.path.exists( data_file_p_path ):
    os.mkdir( data_file_p_path )
if not os.path.exists( data_file_path ):
    with open( data_file_path ,"w") : pass

# https://docs.ponyorm.org/firststeps.html#database-binding
db.bind(provider='sqlite', filename = data_file_path )

class Person( db.Entity ):
    id = PrimaryKey( str )
    name = Optional( str )
    dob = Optional( date )
    address = Optional( str )
    note = Optional( str )
    
try:
    db.generate_mapping( create_tables = True )
except OperationalError as e:
    print( e )
    print('\nAdd specific column to database (^_^)\n' )