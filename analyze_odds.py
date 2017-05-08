#!python3
'''
This file takes the decision results for the year and uses it to calculate
odds based on logistic regressions
'''
from botutils.tabletools import tableclass as tc
from botutils.tabletools import tabletools as tt
from odds_modules import get_data, do_analysis

def main(infile, casesfile, outfile):
    '''Main control flow for doing admissions analysis'''
    print('Loading raw data from %s' % infile)
    raw_data = get_data.get_CSV(infile) #Table Class
    print('Total of %d rows loaded' % len(raw_data))

    print('Loading analysis cases from %s' % casesfile)
    output_table=[['Case','N','GPAcoef','ACTcoef','Int','Score','Loss']]
    cases = get_data.get_cases(casesfile) #dictionary of cases
    for case in cases:
        print('Running case (%s)' % case)
        current_table = get_data.get_slice_by_case(cases[case], raw_data)
        # Huge hack: the 3 different lines below are just commented out
        # to pick the intended one of the three. School_Array is for 
        # school specific analyses, while "standard" is for Barron's
        # based general ones (ACT25 for Black/Hispanic and ACT50 for
        # White/Asian)
        school_data = do_analysis.create_school_array(current_table)
        #school_data = do_analysis.create_standard_array(current_table,'ACT25')
        #school_data = do_analysis.create_standard_array(current_table,'ACT50')
        if len(school_data)>1:
            try:
                school_results = do_analysis.run_lregression(school_data)
                new_row = [case, len(current_table)]
                new_row.extend(school_results)
                output_table.append(new_row)
            except:
                pass

    tt.table_to_csv(outfile,output_table)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Analyze admissions results')

    input_help='CSV file containing results data'
    parser.add_argument('-input', dest='infile', action='store',
                        help=input_help, default='analysis_inputs/results.csv')

    cases_help='CSV file with regression cases to run'
    parser.add_argument('-cases', dest='cases', action='store',
                        help=cases_help,
                        default='analysis_inputs/odds_cases.csv')

    output_help='CSV file to send outputs to'
    parser.add_argument('-output', dest='output', action='store',
                        help=output_help, default='odds_results.csv')

    args = parser.parse_args()

    main(args.infile, args.cases, args.output)
