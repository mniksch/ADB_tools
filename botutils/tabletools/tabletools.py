#!python3
'''
This file contains a number of utilities for working with tables implemented
as lists of lists (generally from imported CSV files)
This file generates some more advanced statistics for weekly odds reports
It has a students table and an applications table as inputs
'''
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

def table_to_exsheet(wb, name, table, *, sortfield=False,
                     bold=False, space=False, add_filter=True):
    '''Utility function to write to a single excel sheet after
    passed the workbook and other arguments from table_to_excel
    shown below'''
    import xlsxwriter
    ws = wb.add_worksheet(name)
    newT = table[1:]
    if sortfield:
        sortIndex = table[0].index(sortfield)
        newT.sort(key=lambda x: x[sortIndex])
    if bold:
        ws.write_row(0,0, table[0],wb.add_format({'bold': True, 
                                                  'text_wrap': True}))
        ws.set_row(0,30)
    else:
        ws.write_row(0,0, table[0])
    for i in range(len(newT)):
        ws.write_row(i+1,0,newT[i])
    if add_filter:
        ws.autofilter(0,0,len(newT),len(newT[0])-1)
#        ws.freeze_panes(1,4)#Arbitrary now--need to make an argument
    if space:
        for i in range(len(newT[0])):
            colwidth = max(max([len(str(d[i])) for d in newT]),len(table[0][i]))
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
