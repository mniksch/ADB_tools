#!python3
'''
This file contains a number of utilities for working with tables implemented
as lists of lists (generally from imported CSV files)
This file generates some more advanced statistics for weekly odds reports
It has a students table and an applications table as inputs
'''
from datetime import date

def copy_table(table):
    '''Utility for returning a copy of a table that doesn't contain references
    to the inner lists'''
    new_table = []
    for row in table:
        new_row = row[:]
        new_table.append(new_row)
    return new_table

def slice_header(table):
    '''Utility function that returns a dictionary of column positions
    and slices the header row off the top of the table'''
    hrow = table.pop(0) #Note this alters the table
    hdict = {}
    for i in range(len(hrow)):
        hdict[hrow[i]]=i
    return hdict

def add_header(table, tD):
    '''Utility function that returns a reconstituted table from a
    dictionary that was created with slice_header; this changes
    the referenced table (by adding a header row), but also returns
    the same table'''
    hrow = []
    for i in tD: hrow.append([tD[i], i])
    hrow.sort()
    hrow = [j for i, j in hrow]
    return table.insert(0, hrow)

def table_to_csv(fn, table):
    '''Utility function to send a table (list of lists) to a csv file'''
    import csv
    outf = open(fn, 'wt', encoding='utf-8')
    writer = csv.writer(outf, delimiter=',', quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n')
    for row in table:
        writer.writerow(row)
    outf.close()

def create_dict(table, key_col, val_col):
    '''Returns a dictionary with a simple correspondence of one column
    containing the keys and one column containing the values. Columns
    are specified by index'''
    result = {}
    for row in table:
        result[row[key_col]] = row[val_col]
    return result

def grab_csv_table(fn):
    '''Utility function to turn a csv file into a table'''
    import csv
    with open(fn, errors='ignore') as f:
        reader = csv.reader(f)
        newTable = []
        for row in reader:
            newTable.append(row)
    return newTable

def _write_row_w_formats(ws, row, line, ff, intf, df, data_cols,dataf):
    '''Helper function to emulate a special case of ws.write_row that
    uses provided formats only for float, int, and date variables'''
    for i in range(len(line)):
        if i in data_cols:
            ws.write(row,i,line[i],dataf)
        else:
            if type(line[i]) is float:
                ws.write(row,i,line[i],ff)
            elif type(line[i]) is int:
                ws.write(row,i,line[i],intf)
            elif type(line[i]) is date:
                ws.write(row,i,line[i],df)
            else:
                ws.write(row,i,line[i])

def table_to_exsheet(wb, name, table, *, sortfield=False,
                     bold=False, space=False, add_filter=True,
                     header_row=0,
                     float_format={'num_format':'0.00'},
                     date_format={'num_format':'mm/dd/yy'},
                     int_format={'align':'center'},
                     first_rows_format={'bold':False},
                     second_row_format=False,
                     data_format=((),{'bold':False})):
    '''Utility function to write to a single excel sheet after
    passed the workbook and other arguments from table_to_excel
    shown below'''
    import xlsxwriter
    ws = wb.add_worksheet(name)
    ff = wb.add_format(float_format)
    df = wb.add_format(date_format)
    intf = wb.add_format(int_format)
    frf = wb.add_format(first_rows_format)
    dataf = wb.add_format(data_format[1])
    if second_row_format:
        srf = wb.add_format(second_row_format)
    else:
        srf = frf
    newT = table[(header_row+1):]
    if header_row > 0: #Print some preamble header fields
        for i in range((header_row)):
            if i == 0:
                ws.write_row(i,0, table[i], frf)
            else:
                ws.write_row(i,0, table[i], srf)
    if sortfield:
        sortIndex = table[header_row].index(sortfield)
        newT.sort(key=lambda x: x[sortIndex])
    if bold:
        ws.write_row(header_row,0, table[header_row],
                        wb.add_format({'bold': True, 'text_wrap': True}))
                
        ws.set_row(header_row,30)
    else:
        ws.write_row(header_row,0, table[header_row])
    for i in range(len(newT)):
        _write_row_w_formats(ws, i+1+header_row, newT[i], ff, intf,
                             df, data_format[0], dataf)
    if add_filter:
        ws.autofilter(header_row,0,len(newT) + header_row,len(newT[0])-1)
    if space:
        for i in range(len(table[header_row])):
            ranged_col = [x[i] for x in table[header_row:] if len(x) > i]
            colwidth = max([len(str(d)) for d in ranged_col])
            ws.set_column(i,i,max(colwidth,6))
    return ws #in case the user wants to do additional formatting

def table_to_excel(fn, table, *, sheetfield=False, sortfield=False,
                   bold=False, space=False, add_filter=True):
    '''Utility function to dump a table to an excel file (fn)
    if sheetfield is set to a valid (text) column header, it will
    print to a new sheet for each unique value in that field
    if sortfield is set to a valid (text) column header, it will
    sort by that in each sheet
    bold=whether to bold the first row
    space=whether to try to adjust column width
    add_filter=whether to put a filter on the data
    '''
    import xlsxwriter

    workbook = xlsxwriter.Workbook(fn)
    if sheetfield:
        #Generate a list of unique field values
        splitIndex = table[0].index(sheetfield)
        values = list({row[splitIndex] for row in table[1:]})
        values.sort()
        for value in values: # for each unique field value
            newT=[row for row in table[1:] if row[splitIndex]==value]
            newT.insert(0,table[0])
            table_to_exsheet(workbook,value, newT, sortfield=sortfield,
                             bold=bold, space=space, add_filter=add_filter)
    else:
        table_to_exsheet(workbook,'Sheet1',table, sortfield=sortfield,
                         bold=bold, space=space, add_filter=add_filter)
    workbook.close()

def convColumns(table, columns, function, skipHeader):
    '''
    Takes a table and applies a conversion function on the specified columns
    '''
    if skipHeader:
        for row in table[1:]:
            for col in columns:
                try:
                    row[col]=function(row[col])
                except ValueError: #ignoring '#N/A'
                    pass
    else:
        for row in table:
            for col in columns:
                try:
                    row[col]=function(row[col])
                except ValueError: #ignoring '#N/A'
                    pass

def conv_columns_std(table, columns, skipHeader=True):
    ''' Takes a table and applies a string to decimal conversion
    on specified columns
    '''
    convColumns(table, columns, int, skipHeader)

def conv_columns_stp(table, columns, skipHeader=True):
    ''' Takes a table and applies a string to %age conversion
    on specified columns
    '''
    convColumns(table, columns, lambda x: float(x.strip('%'))/100, skipHeader)

def conv_columns_stf(table, columns, skipHeader=True):
    ''' Takes a table and applies a string to float conversion
    on specified columns
    '''
    convColumns(table, columns, float, skipHeader)
