#!python3
'''
Utility module to handle getting files for analyze_odds.py
'''
import csv
from botutils.tabletools import tableclass as tc

def get_CSV(infile):
    base = tc.Table(infile)
    base.apply_func_cols(['ACT25', 'ACT50', 'GPA', 'ACT', 'Y'],
            lambda x: float(x) if x and x.replace('.','').isdigit() else x)
    return base

def get_cases(casesfile):
    cases = {}
    with open(casesfile) as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                if row[0][0] != '#':
                    cases[row[0]]=list(zip(row[1::2],row[2::2]))
    return cases

def get_slice_by_case(case, full_table):
    working_table = full_table
    for item in case:
        working_table = working_table.get_match_rows_table(
                            item[0],item[1])
    return working_table
