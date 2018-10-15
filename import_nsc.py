#!python3
'''
This file takes a CSV file from National Student Clearinghouse
and converts it to a table of enrollment records suitable to import
into an alumni database
'''
from botutils.tkintertools import tktools
from botutils.ADB import AlumniDatabaseInterface as aDBi
from botutils.tabletools import tableclass as tc
from botutils.tabletools import tabletools as tt
from nsc_modules import nsc_names as n
from datetime import date

def check_degrees_table_complete(nsc_data, degree_dict):
    '''performs check and if not, creates an update file and exits'''
    nsc_degrees = set(nsc_data.get_column(n.DEGREE_TITLE)) - set([''])
    missing_degrees = nsc_degrees - set(degree_dict)
    if missing_degrees:
        degree_lookup = {   'A': "Associate's",
                            'B': "Bachelor's",
                            'C': "Certificate",
                            'M': "Master's"}
        output_table = []
        for miss in missing_degrees:
            if miss:
                if miss[0] in degree_lookup:
                    output_table.append([miss, degree_lookup[miss[0]]])
                else:
                    output_table.append([miss, '?'])
        print('Some degrees from the NSC file are not included in your\n'+
              'degree list (default filename degreelist.csv). Please\n'+
              'inspect the file "missing_degrees.csv" and copy the values\n'+
              'to the bottom of degreelist.csv before running again.')
        tt.table_to_csv('missing_degrees.csv',output_table)
        exit()

def check_college_table_complete(nsc_data, college_dict):
    '''performs check and if not, creates an update file and exits'''
    nsc_colleges = set(nsc_data.get_column(
                        n.COLLEGE_CODE_BRANCH)) - set([''])
    # The OPEIDs we're comparing have follow the format '001650-01' in NSC
    # and 165001 in the IPEDS database. Also, if the two digit ending is
    # not found, '00' will specify the same school at the main branch
    opeid_missing=[] 
    for entry in nsc_colleges:
        parts = entry.split('-')
        opeid1 = str(int(parts[0]+parts[1]))
        opeid2 = str(int(parts[0]+'00'))
        if opeid1 not in college_dict and opeid2 not in college_dict:
            opeid_missing.append(entry)

    if opeid_missing:
        nsc_dict = nsc_data.create_dict_list(n.COLLEGE_CODE_BRANCH,
                                       [n.COLLEGE_NAME, n.COLLEGE_STATE,
                                        n.PUBLIC_PRIVATE])
        output = [['OPEID',  'NCESID', 'Name', 'State', 'Control']]
        for college in opeid_missing:
            data = nsc_dict[college]
            parts = college.split('-')
            opeid1 = str(int(parts[0]+parts[1]))
            row = [ opeid1, '?',      data[0], data[1], data[2]]
            output.append(row)
        print('Some colleges from the NSC file are not included in your\n'+
              'college list (default filename collegelist.csv). Please\n'+
              'inspect the file "missing_colleges.csv" and use it to\n'+
              'add new colleges to the bottom of collegelist.csv\n'+
              'before running again.')
        tt.table_to_csv('missing_colleges.csv',output)
        exit()

def grab_inputs(nsc_fn, sch_fn, deg_fn):
    '''Loads the main CSV inputs and checks to ensure the records in the
    college and degree tables cover all those given in the NSC data. (If
    not, it creates an output with the missing records and provides
    an error message.)'''
    nsc_data = tc.Table(nsc_fn)
    college_list = tc.Table(sch_fn)
    degree_list = tc.Table(deg_fn)

    college_dict = college_list.create_dict_list('OPEID',
            ['NCESID', 'Name'])
    degree_dict = degree_list.create_dict('UpdateDegree', 'DegreeType')

    # These two functions will abort the script if not complete
    check_degrees_table_complete(nsc_data, degree_dict)
    check_college_table_complete(nsc_data, college_dict)

    return (nsc_data, college_dict, degree_dict)

def add_columns_to_nsc_data(nsc_data, college_dict):
    '''Uses data in standard columns to add a few more useful columns to
    the main NSC data table'''
    sId = []
    hs_class = []
    NCESid = []
    colName = []
    startDate = []
    endDate = []
    gradDate = []
    grab_columns = [n.YOUR_UNIQUE_IDENTIFIER,
                    n.HIGH_SCHOOL_GRAD_DATE,
                    n.COLLEGE_CODE_BRANCH,
                    n.ENROLLMENT_BEGIN,
                    n.ENROLLMENT_END,
                    n.GRADUATION_DATE,
                   ]
    # The following will yield lists with only the above columns
    for row in nsc_data.get_columns(grab_columns):
        # NSC Unique Identifier is our ID with a '_' appended
        sId.append(row[0][:-1])

        # HS Class is the same as the year part of the grad year
        hs_class.append(row[1][0:4])

        # We can OPEID to our college database in two different ways
        opeid_raw = row[2]
        if opeid_raw:
            parts = opeid_raw.split('-')
            opeid1 = str(int(parts[0]+parts[1]))
            opeid2 = str(int(parts[0]+'00'))
            if opeid1 in college_dict: opeid = opeid1
            else: opeid = opeid2
            NCESid.append(college_dict[opeid][0])
            colName.append(college_dict[opeid][1])
        else:
            NCESid.append('')
            colName.append('')

        # These 3 date fields have the form YYYYMMDD
        startD_raw = row[3]
        if startD_raw:
            startDate.append(date(int(startD_raw[0:4]), int(startD_raw[4:6]),
                                  int(startD_raw[6:])))
        else: startDate.append('')

        endD_raw = row[4]
        if endD_raw:
            endDate.append(date(int(endD_raw[0:4]), int(endD_raw[4:6]),
                                int(endD_raw[6:])))
        else: endDate.append('')

        gradD_raw = row[5]
        if gradD_raw:
            gradDate.append(date(int(gradD_raw[0:4]), int(gradD_raw[4:6]),
                                int(gradD_raw[6:])))
        else: gradDate.append('')


    # After looping through all raw records, add the results to main table
    nsc_data.add_column('sId', sId)
    nsc_data.add_column('HS Class', hs_class)
    nsc_data.add_column('NCES ID', NCESid)
    nsc_data.add_column('College Name', colName)
    nsc_data.add_column('Start Date', startDate)
    nsc_data.add_column('End Date', endDate)
    nsc_data.add_column('Grad Date', gradDate)

def combine_s_c_enrollments(s_c_table, hd, daysgap):
    '''s_c_table is a list of lists containing all the enrollments for
    a single student at a single column (with columns defined by the header
    dictionary hd. This combines enrollments that occur within daysgap
    of each other'''

    #First, move "Grad Date" into start and end date if blank
    for row in s_c_table:
        if not row[hd['Start Date']]: #if true, always true for "End Date" also
            row[hd['Start Date']] = row[hd['Grad Date']]
            row[hd['End Date']] = row[hd['Grad Date']]

    #Second combine the enrollments that are contiguous, bringing up (as
    # (as common) the following fields: GRADUATED, DEGREE_TITLE, MAJOR
    if len(s_c_table) > 1:
        s_c_table.sort(key=lambda x: x[hd['Start Date']])

        # Now create a mapping of which records are the same
        enrollments = []
        new_enr = [0] # The current enrollment is primed with the first one
        for i in range(1,len(s_c_table)):
            last_end   = s_c_table[new_enr[-1]][hd['End Date']]
            this_start = s_c_table[i][hd['Start Date']]
            days_diff = (this_start - last_end).days
            
            if (days_diff > daysgap or #too many days apart
               (    s_c_table[i-1][hd['Grad Date']] and #continuing after
                not s_c_table[i][hd['Grad Date']])):    #graduating
                # New enrollment starting with this one
                enrollments.append(new_enr)
                new_enr = [i]
            else: # same enrollment
                new_enr.append(i)
        enrollments.append(new_enr)

        # Take the mapping of like records and create single enrollment for each
        new_s_c_table = []
        for enrollment in enrollments:
            record = s_c_table[enrollment[0]]

            # columns to copy the max value into
            for col in [hd['End Date'],     hd[n.GRADUATED],
                        hd[n.DEGREE_TITLE], hd[n.MAJOR]]:
                record[col] = max([s_c_table[enr][col] for enr in enrollment])

            # columns to copy the final value into
            for col in [hd[n.ENROLLMENT_STATUS], ]:
                record[col] = s_c_table[enrollment[-1]][col]

            new_s_c_table.append(record)   

    else: # the case if there is only a single entry for the student/college
        new_s_c_table = s_c_table

    return new_s_c_table

def combine_contiguous_enrollments(nsc_data, daysgap):
    '''Takes the main table and combines contiguous enrollments for the
    same college and student. Enrollments are judged to be contiguous
    if the days between them is less than daysgap. Enrollments have no
    end date if the end date is after effdate.'''
    # First get a list of students with matches
    students_raw = nsc_data.get_columns(['sId', n.RECORD_FOUND_Y_N])
    students = {student[0] for student in students_raw if student[1]=='Y'}

    hd = nsc_data.get_header_dict() #So we can reference the elements
    results_table = []
    # Now process the records for each student
    print('Beginning to process %d students' % len(students))
    sCount = 0 # For screen display
    for sId in students:
        sCount += 1
        student_table = list(nsc_data.get_match_rows('sId',sId))
        colleges = {s[hd['NCES ID']] for s in student_table}
        for col in colleges:
            s_c_table = [row for row in student_table
                                 if row[hd['NCES ID']] == col
                                     and row[hd['RECORD_FOUND_Y/N']] != 'N']

            #Now need to process each college in student_table
            s_c_condensed = combine_s_c_enrollments(s_c_table, hd,
                                daysgap)

            results_table.extend(s_c_condensed)

        #if not sCount % 10: print('.', end='', flush=True)
        if not sCount %100: print('%d contacts processed.' % sCount, flush=True)

    tt.add_header(results_table, hd)

    #Also need to handle records with no date

    return tc.Table(results_table)

def add_status_fields(combined_nsc, degree_dict, daysgap, effdate):
    '''Adds a few interpreted status fields to the combined records:
    Status = Attending, Graduated, Transferred Out, Withdrew
    DegreeType = Bachelor's, Associate's, Certificate, Associate's or 
                 Certificate (TBD), Master's
    DataSource = NSC (only option
    LastVerified = Date provided by effdate
    (Note that combined_nsc is changed in place)
    '''
    # Will pass through every record to compute this into columns for each
    hd = combined_nsc.get_header_dict()
    status = []
    degree_type = []
    data_source = []
    last_verified = []
    dlv = date(int(effdate[-4:]), int(effdate[0:2]), int(effdate[3:5]))
    for row in combined_nsc.rows():
        last_verified.append(dlv) # Always the same for every record
        data_source.append('NSC') # Always the same for every record

        # Status will be based off the end date and grad/withdraw indicators
        date_gap = (dlv - row[hd['End Date']]).days
        end_status = row[hd[n.ENROLLMENT_STATUS]]
        if row[hd[n.GRADUATED]] == 'Y':
            status.append('Graduated')
        elif end_status == 'W' or date_gap > daysgap:
            status.append('T/W')
        else:
            status.append('Attending')

        # Degree type is found from "graduated" degree titles or guessed from
        # type of college
        degree_title = row[hd[n.DEGREE_TITLE]]
        if degree_title:
            degree_type.append(degree_dict[degree_title])
        else:
            if row[hd[n.TWO_YEAR_4_YEAR]][0] == '4':
                degree_type.append("Bachelor's")
            else:
                degree_type.append("Associate's or Certificate (TBD)")

    # Add new columns to table
    combined_nsc.add_column('Status', status)
    combined_nsc.add_column('Degree Type', degree_type)
    combined_nsc.add_column('Data Source', data_source)
    combined_nsc.add_column('Last Verified', last_verified)
    hd = combined_nsc.get_header_dict()
    print('Now cleaning up T/W statuses.')

    # Pass through and determine if T/W fields are T or W
    students = set(combined_nsc.get_column('sId'))
    for student in students:
        s_rows = list(combined_nsc.get_match_rows('sId', student))
        if len(s_rows) > 1:
            s_rows.sort(key=lambda x: x[hd['Start Date']])
        big_s = date(1900, 1,1) # big_s and big_e are for checking if there's
        big_e = date(1901, 1,1) # a large enrollment that encompasses small ones
        for i in range(len(s_rows)):
            sDate = s_rows[i][hd['Start Date']]
            eDate = s_rows[i][hd['End Date']]
            if sDate > big_e: # this enrollment occurs after the previous
                big_s = sDate # "big" enrollment
                big_e = eDate
            if s_rows[i][hd['Status']] == 'T/W':
                if i+1 == len(s_rows): # final row for this student
                    if eDate >= big_e: # not a summer/catchup class
                        s_rows[i][hd['Status']] = 'Withdrew'
                    else: # probably a summer/catchup class
                        s_rows[i][hd['Status']] = 'Transferred out'
                else:
                    date_gap = (s_rows[i+1][hd['Start Date']] -
                                s_rows[i][hd['End Date']]).days
                    if date_gap > daysgap:
                        if eDate >= big_e: # not a summer/catchup class
                            s_rows[i][hd['Status']] = 'Withdrew'
                        else:
                            s_rows[i][hd['Status']] = 'Transferred out'
                    else:
                        s_rows[i][hd['Status']] = 'Transferred out'

def import_ids_from_salesforce():
    '''Interfaces with the Salesforce database to grab the translation from
    NCES ID->SF ID for colleges and Student Number->SF ID for alumni and
    returns the translations as a tuple of two dictionarys'''
    alumni_table, college_table = aDBi.grabAccountContactTranslations()
    alumni_dict = tt.create_dict(alumni_table[1:], 0, 1)
    college_dict = tt.create_dict(college_table[1:], 0, 1)
    return (alumni_dict, college_dict)

def add_Salesforce_indices(combined_nsc):
    ''' Adds the Salesforce names for alumni and colleges using the student
    id "YOUR UNIQUE IDENTIFIER" from NSC and using the NCES code for college.
    Will use "N/A" for any alumnus/alumnae or college not found in the lookup'''
    # First check whether the user would prefer to add from Salesforce API
    # calls directly or via file upload
    choices = ['Grab directly from Salesforce',
               'Import as CSV files (see README for details)']
    response = tktools.get_buttons_answer(choices,
              'How would you like to get the SF IDs for alumni and colleges?')

    # Once the user responds, generate a dictionary lookup for both fields
    if response == choices[0]: # user selected 'Grab directly from Salesforce'
        alumni_dict, college_dict = import_ids_from_salesforce()
    else: # user wants to enter the info as a set of CSV files
        filenames = {
         'alum':['alumniNames.csv',
                 'Alumni names file (two columns: Your ID/SF ID)', 'r'],
         'coll':['collegeNames.csv',
                 'College names file (two columns: NCES ID/ SF ID)', 'r']
        }
        tktools.get_filenames(filenames)
        alumni_table = tt.grab_csv_table(filenames['alum'][0])
        alumni_dict = tt.create_dict(alumni_table[1:], 0, 1)
        college_table = tt.grab_csv_table(filenames['coll'][0])
        college_dict = tt.create_dict(college_table[1:], 0, 1)

    # Now that we have a dictionary for both, generate the two new columns
    college_ids =[]
    alumni_ids =[]
    for row in combined_nsc.rows():
        try:
            college_ids.append(college_dict[row[combined_nsc.c('NCES ID')]])
        except:
            college_ids.append('N/A')
        try:
            alumni_ids.append(alumni_dict[row[combined_nsc.c('sId')]])
        except:
            alumni_ids.append('N/A')
    
    # Finally, add the new columns back to the master table
    combined_nsc.add_column('College__c', college_ids)
    combined_nsc.add_column('Student__c', alumni_ids)

def finalize_output_columns(combined_nsc):
    '''Takes the result of all the prior functions and reorders/renames
    columns for a slightly more user friendly/Salesforce expected set'''
    output_col = [ 'Student ID',
                   'Last Name',
                   'First Name',
                   'HS Class',
                   'College NCES ID',
                   'College Name',
                   'Student__c',
                   'College__c',
                   'Start_Date__c',
                   'End_Date__c',
                   'Status__c',
                   'Degree_Type__c',
                   'Data_Source__c',
                   'Date_Last_Verified__c',
                   'Degree_Text__c',
                   'Major_Text__c',
                  ]
    source_col = [ 'sId',
                   n.LAST_NAME,
                   n.FIRST_NAME,
                   'HS Class',
                   'NCES ID',
                   'College Name',
                   'Student__c',
                   'College__c',
                   'Start Date',
                   'End Date',
                   'Status',
                   'Degree Type',
                   'Data Source',
                   'Last Verified',
                   n.DEGREE_TITLE,
                   n.MAJOR,
                 ]
    new_table = combined_nsc.new_subtable(source_col, output_col)
    new_table.apply_func('Last Name', str.title)
    new_table.apply_func('First Name', str.title)
    for row in new_table.rows():
        if row[new_table.c('Status__c')] == 'Attending':
            row[new_table.c('End_Date__c')] = ''
    return new_table


def main(nsc, sch, deg, out, daysgap, effdate):
    '''Main control flow for processing NSC files'''
    print('-'*40)
    print('NSC file is %s' % nsc)
    print('Schools file is %s' % sch)
    print('Degrees file is %s' % deg)
    print('Output file will be %s' % out)
    print('Allowed days gap is %d' % int(daysgap))
    print('NSC report produced on %s' % effdate)
    print('-'*40)

    # Load input files (aborts with error if college/degree incomplete)
    nsc_data, college_dict, degree_dict = grab_inputs(nsc, sch, deg)

    # Add a few interpreted columns to the nsc table
    print('Beginning to process NSC file.')
    add_columns_to_nsc_data(nsc_data, college_dict)

    # Combine records that reflect contiguous enrollments
    print('Beginning to combine contiguous records.')
    combined_nsc = combine_contiguous_enrollments(nsc_data, daysgap)
    print('-'*40)

    # Add Status, DegreeType, Date Verified, DataSource fields
    print('Enrollments combined, now adding status fields.')
    # had previously forced daysgap=40 in the below; not sure why?
    add_status_fields(combined_nsc, degree_dict, daysgap, effdate)

    # Add in Salesforce names for students and for colleges
    # ToDo: Pass a "silent" variable to this function based on a to-be-added
    # command line option to supress the query for SF/files
    print('-'*40)
    print('Adding Salesforce IDs for alumni and colleges')
    add_Salesforce_indices(combined_nsc)
    
    # Throw out the columns we don't need anymore and reorder others
    print('-'*40)
    print('Creating final output and saving to %s.' % out)

    final_output_table = finalize_output_columns(combined_nsc)

    #Finally, save the output file
    final_output_table.to_csv(out)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process new NSC detail file')
    nsc_help='Detailed CSV file from Clearinghouse'
    parser.add_argument('-nsc', dest='nsc', action='store', help=nsc_help)
    sch_help='Colleges table (provided with this file)'
    parser.add_argument('-sch', dest='sch', action='store', help=sch_help,
            default='nsc_inputs/collegelist.csv')
    deg_help='Degrees table (provided with this file)'
    parser.add_argument('-deg', dest='deg', action='store', help=deg_help,
            default='nsc_inputs/degreelist.csv')
    out_help='Output filename (csv)'
    parser.add_argument('-out', dest='out', action='store', help=out_help,
            default='import_nsc_output.csv')
    days_help='Number of days allowed between enrollments'
    parser.add_argument('-days', dest='daysgap', type=int, help=days_help)
    effdate_help='Date to use for NSC file run (MM/DD/YYYY)'
    parser.add_argument('-date', dest='effdate', help=effdate_help)
    args = parser.parse_args()
    # The following dict format is expected by tktools.get_filenames
    arg_dict = {    'nsc':  [args.nsc, nsc_help, 'r'],
                    'sch':  [args.sch, sch_help, 'r'],
                    'deg':  [args.deg, deg_help, 'r'],
                    'out':  [args.out, out_help, 'w'],
                    }
    if args.nsc is None: #Assume the user needs to be queried with a window
        tktools.get_filenames(arg_dict)
    if args.daysgap is None:
        args.daysgap=131
    if args.effdate is None:
        #args.effdate='08/10/2016'
        #args.effdate='11/18/2016'
        args.effdate='08/30/2018'
    main(   arg_dict['nsc'][0],
            arg_dict['sch'][0],
            arg_dict['deg'][0],
            arg_dict['out'][0],
            args.daysgap,
            args.effdate
            )
    s = input('----(hit enter to close)----')
