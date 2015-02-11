#!python3
'''Main module for creating excel reports about persistence'''

import xlsxwriter
from . import report_summary as rs
from . import report_grads

def make_main_report(per_stats, outf, by_hs, con, acc, enr, verbose):
    '''con, acc, and enr are Tables of basic Salesforce data
    per_stats is a dictionary with keys contact_id and values
    Persistence objects, and outf is the name of the filename'''
    workbook = xlsxwriter.Workbook(outf)

    if len(set(con.get_column('High School'))) == 1:
        by_hs = False

    basic = rs.create_basic_summary(con, per_stats, by_hs)
    rs.basic_summary_sheet(workbook, basic, by_hs)

    ba_basic = rs.create_basic_summary(con, per_stats, by_hs, ba_only=True)
    rs.basic_summary_sheet(workbook, ba_basic, by_hs, ba_only=True)

    report_grads.create_cohort_grads(workbook, con, per_stats, by_hs)

    report_grads.create_cohort_overviews(workbook, con, per_stats,
                                         by_hs, verbose, details=True)

    workbook.close()
