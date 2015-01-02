#!python3
'''
Script for taking the result of intake_nsc and merging it with the alumni
database
'''

import os
from botutils.tkintertools import tktools
from datetime import date, datetime
from botutils.tabletools import tableclass as tc
from botutils.tabletools import tabletools as tt
from botutils.ADB import ContactNamespace as c
from botutils.ADB import AccountNamespace as a
from botutils.ADB import EnrollmentNamespace as e
from botutils.ADB import AlumniDatabaseInterface as aDBi
from nsc_modules import enrollment_match as em
from collections import Counter

def get_acc_dict(acc_raw):
    '''Helper function to localize the specification of fields used'''
    return acc_raw.create_dict_list(a.Id, [ a.Name,
                                            a.College_Type__c,
                                          ])
def get_con_dict(con_raw):
    '''Helper function to localize the specification of fields used'''
    return con_raw.create_dict_list(c.Id, [ c.LastName,
                                            c.FirstName,
                                            c.HS_Class__c,
                                            c.High_School__c,
                                          ])

def main(nsc, db_flag, enr, con, acc):
    '''Main control flow for merging new enrollments with old in database'''
    print('-'*40)
    print('Output file from intake_nsc.py is %s' % nsc)
    if db_flag:
        print('Grabbing data tables directly from database')
    else:
        print('Accounts file: %s' % acc)
        print('Contacts file: %s' % con)
        print('Enrollments file: %s' % enr)
    print('-'*40)

    # Load the intake_nsc file
    intake_raw = tc.Table(nsc)
    nsc_enr = em.get_enrollments_and_chg_vartype(intake_raw)
    year_range = set(intake_raw.get_column('HS Class'))
    print('Year range of %s-%s.' % (min(year_range), max(year_range)))

    # Get the database information
    if db_flag:
        restr = c.HS_Class__c + ' IN '
        restr += "('" + "','".join(year_range) + "')"
        db_res = aDBi.grabThreeMainTables_Analysis(
                                        contactRestriction=restr,
                                        mode='NSCmerge')
        con_raw = tc.Table(db_res[0])
        acc_raw = tc.Table(db_res[1])
        enr_raw = tc.Table(db_res[2])
    else:
        acc_raw = tc.Table(acc)
        con_raw = tc.Table(con)
        enr_raw = tc.Table(enr)

    # Cleanup the database info
    db_enr = em.get_enrollments_and_chg_vartype(enr_raw, True)
    acc_dict = get_acc_dict(acc_raw)
    con_dict = get_con_dict(con_raw)

    # Prior to cycling through, append an index column to the two
    # enrollment tables so we can reference the original row even
    # if we're inspecting a subset of rows
    db_enr.add_column('Index',list(range(len(db_enr))))
    nsc_enr.add_column('Index',list(range(len(nsc_enr))))

    # Do many passes through tables to find matches
    print('-'*40)
    print('Looking for matches: %d from db, %d from nsc'
            % (len(db_enr), len(nsc_enr)))

    db_enr_map, nsc_enr_map, match_table = em.find_matches(db_enr, nsc_enr)
    unmatched_db =  [x for x in db_enr.rows()  if x[-1] not in db_enr_map]
    unmatched_nsc = [x for x in nsc_enr.rows() if x[-1] not in nsc_enr_map]

    print('Still not matched: %d from db, %d from nsc' %
            (len(unmatched_db), len(unmatched_nsc)))

    # Use matching information to generate output tables
    print('-'*40)
    print('Generating output files')

    enr_update = [[e.Id, e.Start_Date__c, e.End_Date__c,
                  e.Date_Last_Verified__c, e.Status__c,
                  e.Degree_Type__c, e.Data_Source__c,
                  e.Degree_Text__c, e.Major_Text__c, ]]
    new_enr = [em.get_enr_field_list()]
    con_flag = [[c.Id, c.Needs_NSC_Review__c, c.NSC_Review_Reason__c]]

    for row in match_table:
        # row[0] is always a MatchCase subclass that will have a custom
        # function for each of these three lines if pertinent for this
        # case. Otherwise, the function will return the default None
        enr_update.append(row[0].enr_update(row[1:], acc_dict))
        new_enr.append(row[0].new_enr(row[1:]))
        con_flag.append(row[0].con_flag(row[1:], acc_dict))

    # Scrub out the empty rows if a MatchCase had nothing to say
    enr_update = [x for x in enr_update if x]
    new_enr = [x for x in new_enr if x]
    con_flag = [x for x in con_flag if x]

    #Rollup the contact flags to have a single row per student
    con_update = []
    for student in set(x[0] for x in con_flag[1:]):
        student_set = [x for x in con_flag if x[0] == student]
        new_flags = '; '.join([x[2] for x in student_set])
        con_update.append([student, True, new_flags])
    con_update.insert(0,con_flag[0])

    # Write output tables to files
    today_ending = date.today().strftime('%m_%d_%Y')
    new_enr_fn = 'new_enr_' + today_ending + '.csv'
    enr_update_fn = 'enr_update_' + today_ending + '.csv'
    con_update_fn = 'con_update_' + today_ending + '.csv'

    tt.table_to_csv(enr_update_fn, enr_update)
    tt.table_to_csv(new_enr_fn, new_enr)
    tt.table_to_csv(con_update_fn, con_update)

    # debugging lines
    case_list = Counter([x[0] for x in match_table]).most_common()
    case_table = [['Matching case','Frequency']]
    case_table.extend([[c[0], c[1]] for c in case_list])
    nsc_h = nsc_enr.get_full_table()[0]
    db_h = db_enr.get_full_table()[0]
    unmatched_nsc.insert(0,nsc_h)
    unmatched_db.insert(0,db_h)
    match_h = ['Case']
    match_h.extend(nsc_h)
    match_h.extend(db_h)
    match_table.insert(0,match_h)

    if not os.path.exists('debugging_output'):
        os.makedirs('debugging_output')
    tt.table_to_csv('debugging_output/__match_table.csv',match_table)
    tt.table_to_csv('debugging_output/__unmatched_nsc.csv',unmatched_nsc)
    tt.table_to_csv('debugging_output/__unmatched_db.csv',unmatched_db)
    tt.table_to_csv('debugging_output/__matching_cases.csv',case_table)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Merges import_nsc.py output')
    intake_help = 'Output file from import_nsc.py'
    parser.add_argument('-nsc', dest='nsc', action='store', help=intake_help)
    enr_help = 'Enrollments table from database (csv)'
    parser.add_argument('-enr', dest='enr', action='store', help=enr_help)
    acc_help = 'Accounts table from database (csv)'
    parser.add_argument('-acc', dest='acc', action='store', help=acc_help)
    con_help = 'Contacts table from database (csv)'
    parser.add_argument('-con', dest='con', action='store', help=con_help)
    flag_help = 'Ignore popup and grab data from database'
    parser.add_argument('-db', dest='db', action='store_true', help=flag_help)
    args = parser.parse_args()

    if not args.db and not (args.enr and args.con and args.acc):
        args.db = tktools.get_yes_no(
                              'Get database info directly from Salesforce?')
    arg_dict = {}
    if not args.nsc:
        arg_dict['nsc'] = [args.nsc, intake_help, 'r']
    if not args.db:
        if not args.enr: arg_dict['enr'] = [args.enr, enr_help, 'r']
        if not args.con: arg_dict['con'] = [args.con, con_help, 'r']
        if not args.acc: arg_dict['acc'] = [args.acc, acc_help, 'r']
    if arg_dict: # at least one filename needs to be queried vi GUI
        tktools.get_filenames(arg_dict)
        if 'nsc' in arg_dict: args.nsc = arg_dict['nsc'][0]
        if 'enr' in arg_dict: args.enr = arg_dict['enr'][0]
        if 'con' in arg_dict: args.con = arg_dict['con'][0]
        if 'acc' in arg_dict: args.acc = arg_dict['acc'][0]

    main(args.nsc, args.db, args.enr, args.con, args.acc)
    s = input('----(hit enter to close)----') # in case the user opens w/ icon
