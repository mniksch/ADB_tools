#!python3
'''File for performing several reduction and renaming functions'''

from botutils.ADB import ContactNamespace as c
from botutils.ADB import AccountNamespace as a
from botutils.ADB import EnrollmentNamespace as e
from botutils.tabletools import tabletools as tt
from botutils.tabletools import tableclass as tc
from botutils.tkintertools import tktools
from datetime import datetime

'''The following three pairs of lists specify the final fields we want
to keep in our main tables and their new names for all functions below
remove_extra_rows_and_columns in the main module'''

enr_fields = [  e.Id,
                e.Student__c,
                e.College__c,
                e.Degree_Type__c,
                e.Start_Date__c,
                e.End_Date__c,
                e.Status__c,
             ]
enr_names =  [  'Id',           #0
                'Student',      #1
                'College',      #2
                'Degree Type',  #3
                'Start Date',   #4
                'End Date',     #5
                'Status',       #6
             ]
acc_fields = [  a.Id,
                a.Name,
                a.NCESid__c,
                a.X1st_year_retention_rate__c,
                a.X6_yr_completion_rate__c,
                a.X6_yr_minority_completion_rate__c,
                a.X6_yr_transfer_rate__c,
                a.X6_yr_minority_transfer_rate__c,
                a.College_Type__c,
             ]
acc_names =  [  'Id',                   #0
                'Name',                 #1
                'NCESid',               #2
                '1st yr retention',     #3
                '6 yr grad',            #4
                '6 yr grad AA/H',       #5
                '6 yr transfer',        #6
                '6 yr transfer AA/H',   #7
                'College Type',         #8
             ]
                
con_fields = [  c.Id,
                c.LastName,
                c.FirstName,
                c.Ethnicity__c,
                c.First_Generation_College_Student__c,
                c.Low_Income__c,
                c.Gender__c,
                c.Highest_ACT_Score__c,
                c.HS_Final_GPA__c,
                c.HS_Class__c,
                c.Network_Student_ID__c,
                c.Special_Education__c,
                c.High_School__c,
             ]
con_names =  [  'Id',               #0
                'Last Name',        #1
                'First Name',       #2
                'Race/ Ethnicity',  #3
                'First Gen',        #4
                'Low Income',       #5
                'Gender',           #6
                'Highest ACT',      #7
                'HS GPA',           #8
                'HS Class',         #9
                'Network ID',       #10
                'SpEd',             #11
                'High School',      #12
             ]

def strYYYY_MM_DD_to_date(val):
    '''Helper function to convert a 'YYYY-MM-DD' string to a date'''
    if val: #checks for None or ''; will convert '' to None
        return datetime.strptime(val, '%Y-%m-%d').date()
    else:
        return None


def specify_high_schools(raw_con, hs):
    if hs: #User specified a single HS already
        return [hs]
    else:
        hc = tt.slice_header(raw_con) # we need to remember to add this back
        initial_hs = list(set([x[hc[c.High_School__c]] for x in raw_con]))
        initial_hs = [h for h in initial_hs if type(h) is str]
        initial_hs.sort()
        hs_list = tktools.check_pick_from_list(initial_hs,
                'Pick which High Schools to include in the report')
        tt.add_header(raw_con, hc)
        return hs_list

def remove_extra_rows_and_columns(raw_con, raw_acc, raw_enr, hs_set):
    '''Does what it says: First limits the number of entries based on the
    High Schools covered and then reduces the columns of data in each
    table prior to returning a Table class'''
    # First reduce rows in the contact table
    hc = tt.slice_header(raw_con)
    con_in_hs = [x for x in raw_con if x[hc[c.High_School__c]] in hs_set]
    student_set = set([x[hc[c.Id]] for x in con_in_hs]) # for enr
    tt.add_header(con_in_hs, hc)
    big_con = tc.Table(con_in_hs)

    # Second reduce rows in enrollment table
    he = tt.slice_header(raw_enr)
    enr_in_hs = [x for x in raw_enr if x[he[e.Student__c]] in student_set]
    college_set = set([x[he[e.College__c]] for x in enr_in_hs]) # for acc
    tt.add_header(enr_in_hs, he)
    big_enr = tc.Table(enr_in_hs)

    # Third reduce rows in the accounts table
    ha = tt.slice_header(raw_acc)
    acc_in_hs = [x for x in raw_acc if x[ha[a.Id]] in college_set]
    tt.add_header(acc_in_hs, ha)
    big_acc = tc.Table(acc_in_hs)

    # Finally, use the lists defined at the top of this file to reduce the
    # number of columns (this step is necessary so that users that supply
    # a CSV file don't need to supply the exact right columns
    little_con = big_con.new_subtable(con_fields, con_names)
    little_acc = big_acc.new_subtable(acc_fields, acc_names)
    little_enr = big_enr.new_subtable(enr_fields, enr_names)

    return (little_con, little_acc, little_enr)

def fix_enrollment_dates(enr):
    '''Just converts these dates to actual dates instead of text'''
    enr.apply_func_cols(['Start Date', 'End Date'], strYYYY_MM_DD_to_date)
 
def fix_account_percentages(acc):
    acc.apply_func_cols(['1st yr retention', '6 yr grad', '6 yr grad AA/H',
                         '6 yr transfer', '6 yr transfer AA/H'],
                        lambda x: float(x)/100.0 if x else None)

def simple_type_translation(detailed_type):
    type_tran={'< 2-year, Private for-profit':'Trade',
               'Employment':'Employment',
               'Military Enlistment':'Employment',
               'Non-accredited':'Trade',
               'Private for-profit, 2-year':'2 yr',
               'Private for-profit, 4-year or above':'4 yr',
               'Private for-profit, less than 2-year':'Trade',
               'Private not-for-profit, 2-year':'2 yr',
               'Private not-for-profit, 4-year or above':'4 yr',
               'Public, 2-year':'2 yr',
               'Public, 4-year or above':'4 yr'}
    if detailed_type in type_tran:
        return type_tran[detailed_type]
    else:
        return 'Unknown'


def simplify_college_types(acc):
    acc.apply_func('College Type', simple_type_translation)
