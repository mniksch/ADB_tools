#!python3
'''
This file takes the contacts/accounts/enrollments data from Salesforce
(either live from Salesforce or from local CSV files) and then generates
a report or set of reports about alumni persistence
'''
from botutils.tkintertools import tktools
from botutils.tabletools import tableclass as tc
from reports_modules import get_data, reduce_tables, get_persistence
from reports_modules import create_report
from datetime import date

def main(infiles,outf,hs,by_hs,verbose):
    '''Main control flow for generating reports'''
    print('-'*40)
    if infiles:
        print('Contacts file is %s' % infiles[0])
        print('Accounts file is %s' % infiles[1])
        print('Enrollments file is %s' % infiles[2])
    else:
        print('Will load data from Salesforce')
    print('Output file is %s' % outf)
    if hs:
        print('Report will be restricted to %s' % hs)
    else:
        print('Report will be generated for all high schools')
    if not by_hs: print('Will report in summary mode')
    print('-'*40)

    # First get the raw data (this will need to be paired down):
    # raw_c_a_e is a tuple of contact/account/enrollment list of list tables
    print('Getting raw data')
    if infiles:
        raw_c_a_e = get_data.get_CSV(*infiles)
    else:
        raw_c_a_e = get_data.get_SF()

    # Next pair down into Tables with only the columns we need
    print('Reducing data into smaller tables')
    hs_list = reduce_tables.specify_high_schools(raw_c_a_e[0], hs)
    print('Working with these high schools: %s' % str(hs_list))
    c_a_e = reduce_tables.remove_extra_rows_and_columns(*raw_c_a_e,
                                                        hs_set=set(hs_list))
    print('Contacts: %d' % len(c_a_e[0]))
    print('Accounts: %d' % len(c_a_e[1]))
    #From this point on functions will use new human-readable names for columns
    reduce_tables.fix_enrollment_dates(c_a_e[2])
    reduce_tables.fix_account_percentages(c_a_e[1])
    reduce_tables.simplify_college_types(c_a_e[1])
    
    print('Enrollments: %d' % len(c_a_e[2]))
    print('-'*40)

    # Create persistence classes for each student
    print('Analyzing persistence for each student')
    end_date = date.today() # date after which enrollments assumed invalid
    per_stats = get_persistence.create_classes(*c_a_e, end_date=end_date)

    print('-'*40)

    print('Creating final output and saving to %s.' % outf)
    create_report.make_main_report(per_stats, outf, by_hs, *c_a_e,
                                   verbose=verbose)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate persistence reports')

    con_help='CSV file containing contact data'
    parser.add_argument('-con', dest='con', action='store', help=con_help,
            default='reports_inputs/contacts.csv')

    acc_help='CSV file containing account data'
    parser.add_argument('-acc', dest='acc', action='store', help=acc_help,
            default='reports_inputs/accounts.csv')

    enr_help='CSV file containing enrollment data'
    parser.add_argument('-enr', dest='enr', action='store', help=enr_help,
            default='reports_inputs/enrollments.csv')

    summary_help='Do not break out reports by HS'
    parser.add_argument('-summary', dest='summary', action='store_true',
                                                help=summary_help)

    verbose_help='Add extra detail to reports'
    parser.add_argument('-verbose', dest='verbose', action='store_true',
                                                help=verbose_help)

    hs_help='Perform report on the single HS'
    parser.add_argument('-hs', dest='hs', action='store', help=hs_help)

    db_help='Ignore popup and grab data from the database'
    parser.add_argument('-db', dest='db', action='store_true', help=db_help)

    csv_help='Ignore popu and grab data from csv files'
    parser.add_argument('-csv', dest='csv', action='store_true', help=csv_help)

    out_help='Output filename (xlsx)'
    parser.add_argument('-out', dest='out', action='store', help=out_help)

    args = parser.parse_args()

    arg_dict = {}
    if not args.out:
        arg_dict['out'] = [args.out, out_help, 'w']
    
    if not args.db:
        if args.csv:
            args.db = False
        else:
            args.db = tktools.get_yes_no(
                'Get database info directly from Salesforce?')

    if not args.out and not args.db:
        arg_dict['enr'] = [args.enr, enr_help, 'r']
        arg_dict['con'] = [args.con, con_help, 'r']
        arg_dict['acc'] = [args.acc, acc_help, 'r']
        
    if arg_dict:
        tktools.get_filenames(arg_dict)
        if 'con' in arg_dict: args.con = arg_dict['con'][0]
        if 'acc' in arg_dict: args.acc = arg_dict['acc'][0]
        if 'enr' in arg_dict: args.enr = arg_dict['enr'][0]
        if 'out' in arg_dict: args.out = arg_dict['out'][0]

    if args.summary:
        by_hs = False
    else:
        by_hs = True

    if args.db:
        infiles = None
    else:
        infiles = (args.con, args.acc, args.enr)
    main(infiles,args.out,args.hs, by_hs, args.verbose)
    #s = input('----(hit enter to close)----')
