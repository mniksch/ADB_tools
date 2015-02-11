#!python3
'''Main module for creating excel reports about persistence'''

from datetime import date
from ..botutils.tabletools import tabletools as tt

def safe_name_for_tab(name, length):
    '''Helper function to make sure a name works as a tab name in Excel'''
    raw_name = name[:length] if len(name) > length else name
    excluded = ('.', '?', '!', '"', "'", '*', '/', '[', ']', ':')
    new_name = ''
    for c in raw_name:
        new_name = new_name + ('_' if c in excluded else c)
    return new_name

def get_cohort_slice(students, per_stats, index, grad_only=False):
    '''Returns a single row/list with the following indices:
    0: High School
    1: HS Class
    2: Date (as referenced by the index)
    3: # (of students in the students table)
    4: % Earned a 4yr degree
    5: % Earned a 2yr degree (by default, doesn't count if working on BA)
    6: % Earned a 4 or 2 yr degree (includes Master's enrollees)
    7: % Enrolled in 4yr or 2yr on given date
    8: % Enrolled 4yr on given date
    9: % Enrolled 2yr on given date
    10: % Enrolled in a Trade/Vocational
    11: % Enrolled in a Master's program
    12: % Earned a grad degree
    13: % Earned a trade degree
    14: % No attainment

    Assumes that the students table is homogenous for 0 & 1
    '''
    ret = [students[0][12], students[0][9]] #columns 0,1
    ret.append(per_stats[students[0][0]].check_dates[index]) # column 2
    num_students = len(students)
    ret.append(num_students) # column 3

    stat_d = {}
    for student in students:
        if grad_only:
            new_status = per_stats[student[0]].grad_status_semester[index]
        else:
            new_status = per_stats[student[0]].status_semester[index]
        if not new_status: new_status = 'None'
        if new_status in stat_d:
            stat_d[new_status] += 1
        else:
            stat_d[new_status] = 1
    totals = [stat_d["4yr Degree"] if "4yr Degree" in stat_d else 0,
              stat_d["2yr Degree"] if "2yr Degree" in stat_d else 0,
              0,
              0,
              stat_d["Bachelor's"] if "Bachelor's" in stat_d else 0,
              stat_d["Associate's"] if "Associate's" in stat_d else 0,
              stat_d["Trade/Vocational"] if "Trade/Vocational" in stat_d else 0,
              stat_d["Master's"] if "Master's" in stat_d else 0,
              stat_d["Grad Degree"] if "Grad Degree" in stat_d else 0,
              stat_d["Trade Degree"] if "Trade Degree" in stat_d else 0,
              stat_d["None"] if "None" in stat_d else 0,
             ]
    totals[2] = sum([totals[i] for i in [0, 1, 7, 8]])
    totals[3] = totals[4] + totals[5]

    ret.extend(list(map(lambda x: x/num_students,totals))) #cols 4-14

    return ret

def get_short_status(status, grad_status):
    '''Helper function to combine two semester by semester status fields
    into a single text label'''
    if grad_status == 'Grad Degree':
        return 'Has grad degree'
    elif grad_status == '4yr Degree':
        if status == "Master's":
            return 'Has 4yr, persuing grad'
        else:
            return 'Has 4yr'
    elif grad_status == '2yr Degree':
        if status == "Bachelor's":
            return 'Has 2yr, pursuing 4yr'
        else:
            return 'Has 2yr'
    elif grad_status == 'Trade Degree':
        if status == "Bachelor's":
            return 'Has trade, pursuing 4yr'
        elif status == "Associate's":
            return 'Has trade, pursuing 2yr'
        else:
            return 'Has trade'
    else:
        if status == "Bachelor's":
            return 'Pursuing 4yr'
        elif status == "Associate's":
            return 'Pursuing 2yr'
        elif status == "Trade/Vocational":
            return 'Pursuing trade'
        else:
            return 'No college'

def create_cohort_detail_sheet(workbook,tab_name,students,per_stats,hs,by_hs,
                               verbose=False):
    '''Creates a tab with the detailed semester by semester stats for an
    entire cohort (all should have the same number of semesters)'''
    headline = 'Cohort detail report for '
    if by_hs:
        headline += 'All High Schools ' if hs == 'All' else (hs + ' ')
    headline += 'Class of ' + students[0][9] # HS Class
    note = 'Current status and semester by semester details of enrollment'
    note2 = 'Click on the "+" signs at the top to expand a semester'

    outtable = [['']*11+[headline],
                ['']*11+[note],
                ['']*11+[note2]]
    data_header=['Id',
                 'Race/ Ethnicity',
                 'First Gen',
                 'Low Income',
                 'Gender',
                 'Highest ACT',
                 'HS GPA',
                 'HS Class',
                 'Network ID',
                 'SpEd',
                 'High School',
                 'Last Name',
                 'First Name',
                 'Current Status',
                 'Initial PGR',
                 'Initial IRR',
                 'Initial College (10/15/'+str(students[0][9])[-2:]+')',
                 'Type']

    if verbose:
        data_header.insert(16,'Initial NCES')
        data_header.insert(17,'Persist semesters')
        data_header.insert(18,'BA semester')

    # sort the student table by HS, Class, Last, First
    students_s = sorted(students, key = lambda x: x[12]+str(x[9])+
                                                  x[1] +x[0])

    # get all the check date semesters that are not in august
    sems = [i for i in range(per_stats[students_s[0][0]].semesters) if
            per_stats[students_s[0][0]].check_dates[i].month != 8]
    
    extra_data_header = []
    if len(sems) > 1:
        sem_num = 1
        for i in sems[1:]:
            sem_num += 1
            new_date = per_stats[
                   students_s[0][0]].check_dates[i].strftime('%m/%d/%y')
            extra_data_header.extend([ 'PGR Chg',
                                       'Sem '+str(sem_num)+' '+
                                              'College (' + new_date + ')',
                                       'Type',
                                       'PGR'])
    data_header.extend(extra_data_header)
    outtable.append(data_header)
    for student in students_s:
        data_row = [student[0]] + student[3:] + student[1:3]

        #deference the performance class for this student
        per = per_stats[student[0]]
        data_row.append(get_short_status(per.status_semester[-1],
                                         per.grad_status_semester[-1]))

        cur_grad_rate = per.grad_rate_semester[0]
        cur_grad_rate = cur_grad_rate if cur_grad_rate else 0.0
        first_data = [cur_grad_rate,
                      per.ret_rate_semester[0],
                      per.col_name_semester[0],
                      per.col_type_semester[0]]
        if verbose:
            first_data.insert(2,per.col_nces_semester[0])
            first_data.insert(3,per.persist_through_sem)
            first_data.insert(4,per.earned_BA_in_sem)
        data_row.extend(first_data)
        if len(sems) > 1:
            for i in sems[1:]:
                
                new_grad_rate = per.grad_rate_semester[i]
                new_grad_rate = new_grad_rate if new_grad_rate else 0.0
                gr_change = new_grad_rate - cur_grad_rate
                cur_grad_rate = new_grad_rate
                data_row.extend([gr_change,
                                 per.col_name_semester[i],
                                 per.col_type_semester[i],
                                 per.grad_rate_semester[i]])

        outtable.append(data_row)


    # Now send it all to the sheet
    ff = {'num_format': '0.0%', 'align': 'center'}
    df = {'num_format': 'mmm d yyyy'}
    r1f = {'bold': True, 'font_size': 20}
    r2f = {'italic': True, 'font_size': 12}
    data_f = ff.copy()
    data_f['bg_color']='#D9D9D9'
    data_f_cols=(1,2,3,4,5,6,7,8,9,10)
    ws = tt.table_to_exsheet(workbook, tab_name, outtable,
                             bold=True, header_row=3, space=False,
                             float_format=ff,
                             date_format=df,
                             first_rows_format=r1f,
                             second_row_format=r2f,
                             data_format=(data_f_cols,data_f))
    ws.freeze_panes(4,14)
    ws.set_column('A:K',8, None, {'level': 1, 'hidden': True})
    ws.set_column('L:L',15, None, {'collapsed': True})
    ws.set_column('M:N',15)
    ws.set_column('O:P',7)
    if verbose:
        ws.set_column('S:S',9)
        ws.set_column('T:T',30)
        ws.set_column('U:U',6)
        bi = 21
    else:
        ws.set_column('Q:Q',30)
        ws.set_column('R:R',6)
        bi = 18
    if len(sems) > 1:
        for i in range(len(sems)-1):
            if i: #not the first one
                ws.set_column(bi+i*4,bi+i*4,6,None,{'collapsed':True})
            else:
                ws.set_column(bi+i*4,bi+i*4,6)
            ws.set_column(bi+1+i*4,bi+1+i*4,30)
            ws.set_column(bi+2+i*4,bi+2+i*4,6,None,{'level': 1, 'hidden': True})
            ws.set_column(bi+3+i*4,bi+3+i*4,7,None,{'level': 1, 'hidden': True})
        ws.set_column(bi+4+i*4,bi+4+i*4,3, None, {'collapsed':True})


def create_cohort_sheet(workbook,tab_name,students,per_stats,hs,by_hs):
    '''Actually creates the tab with overview stats for a cohort (one
    row per check date)'''
    headline = 'Cohort summary report for '
    if by_hs:
        headline += 'All High Schools ' if hs == 'All' else (hs + ' ')
    headline += 'Class of ' + students[0][9] # HS Class
    note = '% of class with given status on specified date'
    note += ' (students pursuing higher degrees show as "enrolled")'
    note2 = 'Shaded columns add to 100%. First two shaded columns '
    note2 += 'add to "in college or graduated" on Overview'

    outtable = [['','',headline],
                ['','',note],
                ['','',note2],
                ['Date', '#', 'Grad 4yr', 'Grad 2yr', 'Grad 2 or 4yr',
                 'Enrolled 2 or 4yr', 'Enrolled 4yr', 'Enrolled 2yr',
                 'Enrolled Trade', 'Enrolled Grad Degree',
                 'Grad Grad Degree', 'Grad Trade/Vocational','No College']]

    for i in range(per_stats[students[0][0]].semesters):
        date_snapshot = get_cohort_slice(students, per_stats, i)
        outtable.append(date_snapshot[2:])

    # New send it all to the sheet
    ff = {'num_format': '0.0%', 'align': 'center'}
    df = {'num_format': 'mmm d yyyy'}
    r1f = {'bold': True, 'font_size': 20}
    r2f = {'italic': True, 'font_size': 12}
    data_f = ff.copy()
    data_f['bg_color']='#D9D9D9'
    ws = tt.table_to_exsheet(workbook, tab_name, outtable,
                             bold=True, header_row=3, space=False,
                             float_format=ff,
                             date_format=df,
                             first_rows_format=r1f,
                             second_row_format=r2f,
                             data_format=((4,5,8,11,12),data_f))
    ws.freeze_panes(4,2)
    ws.set_column('A:A',12)
    ws.set_column('E:F',15)

def create_cohort_grads(workbook, con, per_stats, by_hs=False):
    '''Creates a single tab with summary data at 3, 4, 5, 6 yrs, and "6+"'''
    years = list(set(con.get_column('HS Class')))
    years.sort()
    if date(int(min(years))+3,8,31) > date.today(): return #too early

    headline = 'Graduation summary report at 3, 4, 5, 6 and 6+ years'
    note = '% of class with given status a number of years after high school'

    out_table = [['','','',headline],
                 ['','','',note],
                 ['HS Class','Years out', '#',
                  'Grad 4yr', 'Grad 2yr',
                  'Grad Grad Degree', '4yr or Grad Degree',
                  'Grad Trade/Vocational','No Degree']]
    if by_hs:
        out_table[0].insert(0,'')
        out_table[1].insert(0,'')
        out_table[2].insert(0,'High School')

    for sem in [8, 11, 14, 17, 18]: #indices for Aug 31 3,4,5,6 years, then +
        for year in years:
            # Get yr data & check if this year has results that are old enough
            yr_students = list(con.get_match_rows('HS Class', year))
            num_semesters = per_stats[yr_students[0][0]].semesters
            if num_semesters <= sem: break # no more years apply

            if by_hs:
                high_schools = list(set([student[12] for
                                         student in yr_students]))
                high_schools.sort()
            else:
                high_schools = []
            if len(high_schools) != 1: high_schools.append('All')

            if sem == 18: #6+ (greatest semester out)
                sem_check = num_semesters - 1
            else: #3-6 years out
                sem_check = sem

            for hs in high_schools:
                if hs == 'All':
                    students = yr_students
                else:
                    students = [s for s in yr_students if s[12] == hs]

                # call the slice function
                snapshot = get_cohort_slice(students, per_stats,
                                            sem_check, grad_only=True)

                # take result and add to the output table
                if by_hs:
                    next_row = [hs, int(year)]
                else:
                    next_row = [int(year)]
                sem_cases = {   8:'3 years',
                                11:'4 years',
                                14:'5 years',
                                17:'6 years',
                                18:'6+ years'}

                next_row.append(sem_cases[sem])

                next_row.extend(snapshot[3:6])
                next_row.append(snapshot[12])
                next_row.append(snapshot[4]+snapshot[12])
                next_row.extend(snapshot[13:])
                out_table.append(next_row)

    # New send it all to the sheet
    ff = {'num_format': '0.0%', 'align': 'center'}
    df = {'num_format': 'mmm d yyyy'}
    r1f = {'bold': True, 'font_size': 20}
    r2f = {'italic': True, 'font_size': 12}
    data_f = ff.copy()
    data_f['bg_color']='#D9D9D9'
    data_col = 7 if by_hs else 6
    ws = tt.table_to_exsheet(workbook, 'Graduation Summary', out_table,
                             bold=True, header_row=2, space=False,
                             float_format=ff,
                             date_format=df,
                             first_rows_format=r1f,
                             second_row_format=r2f,
                             data_format=((data_col,),data_f))
    if by_hs:
        ws.freeze_panes(3,4)
        ws.set_column('H:H',12)
    else:
        ws.freeze_panes(3,3)
        ws.set_column('G:G',12)



def create_cohort_overviews(workbook, con, per_stats, by_hs=False,
                            verbose=False, details=False):
    '''Creates one tab for each cohort with a row per check date on status
    creates HS specific tabs if by_hs is True. If details is True, will
    also create a student by student summary tab'''

    years = list(set(con.get_column('HS Class')))
    years.sort()
    for year in years:
        yr_students = list(con.get_match_rows('HS Class', year))
        if by_hs:
            high_schools = list(set([student[12] for student in yr_students]))
            high_schools.sort()
        else:
            high_schools = []
        if len(high_schools) != 1: high_schools.append('All')

        for hs in high_schools:
            if hs == 'All':
                students = yr_students
            else:
                students = [s for s in yr_students if s[12] == hs]
            if by_hs:
                tab_root = str(year)+' '+safe_name_for_tab(hs, 18)
            else:
                tab_root = str(year)
            tab_name = tab_root+' Summary'
            create_cohort_sheet(workbook,tab_name,students,per_stats,hs,by_hs)
        if details:
            detail_tab = tab_root+' Details'
            create_cohort_detail_sheet(workbook,detail_tab,students,per_stats,
                    hs, by_hs, verbose)
