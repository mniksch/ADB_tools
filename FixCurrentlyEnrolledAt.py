#!python3
'''
This module fixes errors in the "Currently Enrolled At" field in the alumni
database
'''
from botutils.ADB import AlumniDatabaseInterface as aDBi
from botutils.ADB import ContactNamespace as c
from botutils.ADB import AccountNamespace as a
from botutils.ADB import EnrollmentNamespace as e
from botutils.tabletools import tabletools as tt
from botutils.ADB import ssf

#Grab the data tables
restriction = ''
sf = ssf.getSF()
contacts, accounts, enrollments = aDBi.grabThreeMainTables_Analysis(
                                                    restriction,sf)

#Lop off headers
dC = tt.slice_header(contacts)
dA = tt.slice_header(accounts)
dE = tt.slice_header(enrollments)

print('Beginning to parse %d contacts.' % len(contacts))
soFar = 0 #index of number of contacts covered
for student in contacts:
    soFar+=1
    if not soFar % 10: print('.', end='')
    if not soFar % 100: print('%d contacts processed.' % soFar)
    records = [row for row in enrollments if row[dE[e.Student__c]] ==
                                                  student[dC[c.Id]] and
                                                  row[dE[e.Status__c]] ==
                                                  'Attending']

    enrolled_at = None
    for record in records:
        matchcols = [sch for sch in accounts if sch[dA[a.Id]] ==
                                                record[dE[e.College__c]]]
        for school in matchcols:
            if enrolled_at:
                enrolled_at += '; ' + school[dA[a.Name]]
            else:
                enrolled_at = school[dA[a.Name]]
    student.append(len(records))
    student.append(enrolled_at)
    if enrolled_at == student[dC[c.Currently_Enrolled_At__c]]:
        student.append('NO CHANGE')
    else:
        student.append('CHANGE')
        sf.Contact.update(student[dC[c.Id]],
                          {c.Currently_Enrolled_At__c: enrolled_at})
dC['EnrollmentCount']=max(dC.values())+1
dC['NewEnrolledAt']=max(dC.values())+1
dC['EnrollChangeStatus']=max(dC.values())+1

#Reconstitute headers
tt.add_header(contacts, dC)
tt.add_header(accounts, dA)
tt.add_header(enrollments, dE)

#Now write everything to the file
import xlsxwriter
workbook = xlsxwriter.Workbook('FixCurrentlyEnrolledAtReport.xlsx')
ws =tt.table_to_exsheet(workbook, 'Contacts', contacts, bold=True, space=True)
ws.freeze_panes(1,3)
ws = tt.table_to_exsheet(workbook, 'Accounts', accounts, bold=True, space=True)
ws.freeze_panes(1,2)
ws = tt.table_to_exsheet(workbook, 'Enrollments', enrollments,
                         bold=True, space=True)
ws.freeze_panes(1,3)
workbook.close()
