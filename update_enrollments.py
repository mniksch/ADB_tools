#!python3
'''
This module updates the named fields in an enrollments csv
'''
import datetime
import sys

import pandas as pd

from botutils.ADB import ssf

def _clean_str(x):
    """Function to give a clean string for the xml upload"""
    if isinstance(x, datetime.datetime):
        if pd.isnull(x):
            return 'null_date'
        else:
            return x.strftime('%Y-%m-%d')
    elif pd.isnull(x):
        return ''
    else:
        return x

print(len(sys.argv))
if len(sys.argv) != 2:
    print('Usage: {} enrollment_update.csv'.format(sys.argv[0]))
    print('Assumes the enrollment id has Id as header')
    sys.exit(1)

# Load the input file and convert to xml for bulk update
update_df = pd.read_csv(sys.argv[1],index_col=0,
        parse_dates=['Start_Date__c','End_Date__c','Date_Last_Verified__c'])

data = []
null_data = []
for Id, vals in update_df.iterrows():
    this_row = {'Id':Id}
    fields_to_null = []
    for x in vals.index:
        new_data = _clean_str(vals[x])
        if new_data == 'null_date':
            fields_to_null.append(x)
        else:
            this_row[x] = new_data

    if fields_to_null:
        # No fieldsToNull in sObject
        # 1) check spelling?
        # 2) push whole thing to non-bulk api?
        null_data.append([Id, {'fieldsToNull':fields_to_null}])
    data.append(this_row)
print(data)
print(null_data)

# Now push to SF
sf = ssf.getSF()
response = sf.bulk.Enrollment__c.update(data)
(pd.DataFrame(response)).to_csv('upload_response.csv')
null_response = []
for Id, null_dict in null_data:
    null_response.append(sf.Enrollment__c.update(Id, null_dict))
if null_response:
    (pd.DataFrame(null_response)).to_csv('null_response.csv')
