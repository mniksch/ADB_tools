#!python3
'''Functions for returning a tuple of contacts, accounts, and enrollments
either from the database or from a text file'''

from ..botutils.ADB import AlumniDatabaseInterface as aDBi
from ..botutils.tabletools import tabletools as tt

def get_SF():
    '''The Analysis qualifier restricts the fields only to ones we will
    likely need'''
    return aDBi.grabThreeMainTables_Analysis()

def get_CSV(c_fn, a_fn, e_fn):
    '''This will take whatever is given, but is presumably every field
    in each table (so will need to be paired down'''
    con = tt.grab_csv_table(c_fn)
    acc = tt.grab_csv_table(a_fn)
    enr = tt.grab_csv_table(e_fn)
    return (con, acc, enr)
