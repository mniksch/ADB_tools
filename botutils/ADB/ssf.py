#!python3
'''
This module acts as a set of wrapper functions for working with the
simple_salesforce module. In general, it allows users to ignore the
OrderedDict structure of the database returns by passing database
tables as lists of lists.

A summary of modules:
    getSF() --> sf
    Returns a Salesforce connection using the ADBlogin module

    getFields(sf.Object) -->fields
    Returns a list of the fields in the object

    getQuery(sf, querytext) --> table
    Returns a list of lists based on a SOQL query with the fields as the
    header column in the first list/row

    getSpecific(sf, obj, fields, restriction='') --> table
    Returns only the specific fields implied by restriction
    
    getAll(sf, sf.Object) --> table
    Returns a list of lists of all of the fields and all of the records
    for a given object
'''
from simple_salesforce import Salesforce
import sys # for stderr

def getSF():
    try:
        from . import ssfLogin
        un = ssfLogin.user
        pw = ssfLogin.password
        st = ssfLogin.token
    except:
        un = input('Enter SF login:')
        pw = input('Enter SF password:')
        st = input('Enter SF token:')

    print('Connecting to Salesforce as user %s' % un,
            file=sys.stderr)
    sf = Salesforce(username=un, password=pw, security_token=st)
    return sf

def getFields(obj):
    '''
    Takes a Salesforce object name (e.g. Salesforce.Object) as argument
    and then returns all of the field names as a list
    Valid objects include Contact, Account, etc
    '''
    info = obj.describe()['fields']
    return [x['name'] for x in info]

def getQuery(sf, querytext):
    '''
    Returns a list of lists based on a SOQL query with the fields as the
    header column in the first list/row
    '''
    gc = sf.query(querytext)
    # will eventually need to check for empty records
    records = gc['records']
    print('Reading from %s object' % records[0]['attributes']['type'],
            file=sys.stderr)
    heads = list(records[0].keys())[1:] # get the headers (will fail if empty)
    rt = [ [record[head] for head in heads] for record in records]
    rt.insert(0,heads) # this is all we need unless the record count is high
    totalread = len(records) # will be used in the loop
    while not gc['done']: #will need to keep going if >2,000 records
        print('Progress: %d records out of %d' % (totalread, gc['totalSize']),
                file=sys.stderr)
        gc = sf.query_more(gc['nextRecordsUrl'],True)
        records = gc['records']
        totalread += len(records)
        nt = [ [record[head] for head in heads] for record in records]
        rt.extend(nt)
    return rt

def getSpecific(sf, obj, fields, restriction=''):
    '''
    Returns a list of lists of the specified fields (a list/iterable)
    for the given object given the SOQL text restriction (that follows a WHERE)
    '''
    qt = 'SELECT ' + ', '.join(fields) + ' FROM '+obj.name
    if restriction:
        qt += ' WHERE '+restriction
    return getQuery(sf,qt)

def getAll(sf, obj):
    '''
    Returns a list of lists of all of the fields and all of the records
    for a given object
    '''
    fields = getFields(obj) #returns a list of all fields in the object
    qt = 'SELECT ' + ', '.join(fields) +' FROM '+obj.name
    return getQuery(sf,qt)
