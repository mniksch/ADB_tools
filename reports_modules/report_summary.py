#!python3
'''Module to create the two main semester by semester overview tabs'''

from ..botutils.tabletools import tabletools as tt

def create_basic_summary(con, per_stats, by_hs=False, ba_only=False):
    '''Creates a table of semester by semester performance by class
    if by_hs is true splits out by HS, otherwise one row per class year'''
    years = list(set(con.get_column('HS Class')))
    years.sort()
    ret = []
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
                year_row = [int(year), hs, len(students)]
            else:
                year_row = [int(year), len(students)]

            simple_stats = [
                  per_stats[student[0]].give_simple_persistence(ba_only) for
                            student in students]
            row_stats = [0]*len(simple_stats[0])
            for i in range(len(row_stats)):
                row_stats[i] = sum([1 for x in simple_stats if x[i] ==
                                            'In college/graduated'])

            year_row.extend(list(map(lambda x: x/len(students),row_stats)))

            ret.append(year_row)

    if by_hs:
        head = ['HS Class', 'High School', '#']
        start_col = 3
    else:
        head = ['HS Class', '#']
        start_col = 2
    for i in range(len(ret[0][start_col:])):
        head.append('Sem '+str(i+1))

    ret.insert(0,head)
    if ba_only:
        ret.insert(0,['','','% of students in college or graduated (BA)'])
    else:
        ret.insert(0,['','','% of students in college or graduated (BA/AA)'])
    ret.insert(1,['','','Status by college semester after HS (10/15 & 1/20)'])
    if by_hs:
        ret[0].insert(0,'')
        ret[1].insert(0,'')
    return ret

def basic_summary_sheet(wb,table,by_hs=False, ba_only=False):
    '''Creates and formats the basic summary sheet in the workbook'''
    ff = {'num_format': '0.0%', 'align': 'center'}
    r1f = {'bold': True, 'font_size': 16}
    r2f = {'italic': True, 'font_size': 14}
    if ba_only:
        sheet_name = 'Four yr Overview'
    else:
        sheet_name = 'Overview'
    ws = tt.table_to_exsheet(wb, sheet_name, table,
                                bold=True, header_row=2, float_format=ff,
                                space=False, first_rows_format=r1f,
                                second_row_format=r2f)
    if by_hs:
        ws.freeze_panes(3,3)
        ws.set_column('B:B',15)
    else:
        ws.freeze_panes(3,2)

