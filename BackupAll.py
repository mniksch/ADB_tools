#!python3
'''
This module backs up the 5 main Salesforce tables and saves to CSV
'''
from botutils.ADB import ssf
from botutils.tabletools import tabletools as tt
import botutils.fileutils.zipup as zipup #for compressing the output
import datetime
import os

ends =datetime.datetime.now().strftime('%m_%d_%Y')
os.mkdir(ends)
sf = ssf.getSF()
objects = ['Contact',
           'Account',
           'Enrollment__c',
           'Contact_Note__c',
           ]
for obj in objects:
    exec('oj = sf.' + obj)
    table = ssf.getAll(sf, oj)
    tt.table_to_csv(ends+'/'+obj+'_'+ends+'.csv', table)

zipup.compress(ends) #Compresses the output directory into a single zip file
