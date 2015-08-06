#!python3
'''
This module uses the ssf module to interface with the alumni database.
The intent is to hide much of the Salesforce implementation in this
module and let other scripts focus more on the logic of working with
tables
'''
from . import ssf
from . import ContactNamespace as c
from . import AccountNamespace as a
from . import EnrollmentNamespace as e
from ..tabletools  import tabletools as tt

def _getEnrollmentFields(sf, fields, restriction = ''):
    '''
    Helper function to be passed a custom set of fields for various purposes
    '''
    oj = sf.Enrollment__c
    return ssf.getSpecific(sf, oj, fields, restriction)


def getEnrollmentFields_Full(sf, restriction = ''):
    '''
    Get all but the database generated fields (e.g. created by)
    '''
    fields = [  e.Id,
                e.Student__c,
                e.College__c,
                e.Degree_Type__c,
                e.Start_Date__c,
                e.End_Date__c,
                e.Date_Last_Verified__c,
                e.Status__c ,
                e.Data_Source__c ,
                e.Degree_Text__c ,
                e.Major_Text__c ,
                e.Withdrawal_reason__c ,
                e.Withdrawal_code__c ,
            ]
    return _getEnrollmentFields(sf, fields, restriction)


def getEnrollmentFields_Analysis(sf, restriction = ''):
    '''
    Get the enrollment fields for the database analysis
    This function will contain hardcoded fields
    '''
    fields = [  e.Id,
                e.Student__c,
                e.College__c,
                e.Degree_Type__c,
                e.Start_Date__c,
                e.End_Date__c,
                e.Date_Last_Verified__c,
                e.Status__c ]
    return _getEnrollmentFields(sf, fields, restriction)


def getAccountFields_Analysis(sf, restriction=''):
    '''
    Get the account fields for the database analysis
    This function will contain hardcoded fields
    '''
    oj = sf.Account
    fields = [  a.Id,
                a.Name,
                a.NCESid__c,
                a.X1st_year_retention_rate__c,
                a.X6_yr_completion_rate__c,
                a.X6_yr_minority_completion_rate__c,
                a.X6_yr_transfer_rate__c,
                a.X6_yr_minority_transfer_rate__c,
                a.College_Type__c ]

    return ssf.getSpecific(sf, oj, fields, restriction)


def getContactFields_Analysis(sf, restriction=''):
    '''
    Get the contact fields for the database analysis
    This function will contain hardcoded fields
    '''
    oj = sf.Contact
    fields = [  c.Id,
                c.LastName,
                c.FirstName,
                c.Currently_Enrolled_At__c,
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
                c.Persistence_Status__c,
                c.rollupAttendingBachelors__c,
                c.rollupAttendingAssociates__c,
                c.rollupMatriculating__c,
                c.rollupGraduated4__c,
                c.rollupGraduated2__c,
                c.rollupGraduatedTrade__c,
                c.rollupAttended4__c,
                c.rollupAttended2__c,
                c.rollupAttendingTrade__c,
                c.College_Attainment__c ]
    return ssf.getSpecific(sf, oj, fields, restriction)

def getContactFields_RiskAnalysis(sf, restriction=''):
    '''
    Get the contact fields for the database analysis
    This function will contain hardcoded fields
    '''
    oj = sf.Contact
    fields = [  c.Id,
                c.LastName,
                c.FirstName,
                c.Currently_Enrolled_At__c,
                c.Ethnicity__c,
                c.HS_Class__c,
                c.Network_Student_ID__c,
                c.High_School__c,
                c.Persistence_Status__c,
                c.College_Attainment__c,
                c.MobilePhone,
                c.Email,
                c.Secondary_email__c,
                c.Campus_Email__c,
                c.Last_Successful_Contact__c,
                c.Last_Outreach__c,
                c.Risk_Variable__c,
                c.Planned_follow__c,
                ]
    return ssf.getSpecific(sf, oj, fields, restriction)

def grabAccountContactTranslations():
    '''
    Returns a tuple of 2 tables that will be used to translate the following:
    Contacts: Network Student ID-->SF ID
    Accounts: NCES ID-->SF ID
    '''
    sf = ssf.getSF()
    cfields = [c.Network_Student_ID__c, c.Id]
    crestr = c.Network_Student_ID__c + " != ''"
    contact_table = ssf.getSpecific(sf, sf.Contact, cfields, crestr)
    afields = [ a.NCESid__c, a.Id ]
    arestr = a.NCESid__c + " != ''"
    account_table = ssf.getSpecific(sf, sf.Account, afields, arestr)
    return (contact_table, account_table)

def grabThreeMainTables_Analysis(contactRestriction='',sf=None,mode='Main'):
    '''
    Returns a tuple of 3 tables based on the ...Analysis calls above
    An optional argument restricts the contacts. Enrollment and account
    tables are then restricted to contain only those related to the
    returned accounts.
    returns (contacts, accounts, enrollments)
    '''
    if not sf: sf = ssf.getSF()

    if mode=='Risk':
        contacts = getContactFields_RiskAnalysis(sf,contactRestriction)
    else:
        contacts = getContactFields_Analysis(sf,contactRestriction)
    accounts = getAccountFields_Analysis(sf)
    if mode=='NSCmerge':
        enrollments = getEnrollmentFields_Full(sf)
    else:
        enrollments = getEnrollmentFields_Analysis(sf)
    dC = tt.slice_header(contacts)
    dA = tt.slice_header(accounts)
    dE = tt.slice_header(enrollments)
    students = set([contact[dC[c.Id]] for contact in contacts])
    newEnrollments = [row for row in enrollments if
                          row[dE[e.Student__c]] in students]
    colleges = set([enroll[dE[e.College__c]] for enroll in newEnrollments])
    if mode != 'NSCmerge':
        newAccounts = [row for row in accounts if
                               row[dA[a.Id]] in colleges]
    else:
        newAccounts = [row for row in accounts]

    #Add the header back to the final tables
    tt.add_header(contacts, dC)
    tt.add_header(newAccounts, dA)
    tt.add_header(newEnrollments, dE)
    return (contacts, newAccounts, newEnrollments)
