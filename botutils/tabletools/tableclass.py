#!python3
'''
This file defines a "Table" class to encapsulate a list of functions around
a lightweight table implementation as a list of lists
'''
from . import tabletools as tt

class Table():
    def __init__(self, source):
        '''
        Two modes for initialization. The first is to send a list of lists.
        The second is to send a csv filename. If neither is true, will
        raise an exception.
        '''
        errmsg = ('Table requires a list of lists or CSV file' +
                ' filename to instantiate')
        if type(source) is list:
            if type(source[0]) is list:
                fullList = tt.copy_table(source)
            else:
                raise Exception(errmsg)
        elif type(source) is str:
            try:
                fullList = tt.grab_csv_table(source)
            except:
                raise Exception(errmsg)
        else:
            raise Exception(errmsg)

        #Now make a non-full copy of the list to act as a header.
        #Because the interior lists are mutable, all of this ultimately
        #references the same interior lists in memory
        self.data = fullList[:] #still passes interior lists by ref
        self.header = tt.slice_header(self.data)

    def __len__(self):
        return len(self.data)

    def get_header_row(self):
        '''Returns the ordered header row (without changing data)'''
        hrow = []
        for i in self.header: hrow.append([self.header[i], i])
        hrow.sort()
        hrow = [j for i, j in hrow]
        return hrow

    def get_full_table(self):
        '''Pops the header row back onto the table and returns a list of lists
        '''
        fullData = self.data[:]
        tt.add_header(fullData, self.header)
        return fullData

    def new_subtable(self, column_list, new_names=None):
        '''Returns a new Table with the specified columns
        If an optional list of replacement column names exists,
        the new table will replace the current headers names with them'''
        fullData = list(self.get_columns(column_list))
        if new_names:
            fullData.insert(0, new_names)
        else:
            fullData.insert(0, column_list)
        return Table(fullData)

    def apply_func_cols(self, cols, func):
        '''applies the passed function to the given columns for each row'''
        for row in self.data:
            for column in cols:
                row[self.header[column]] = func(row[self.header[column]])

    def apply_func(self, column, func):
        '''applies the passed function to the given column for each row'''
        for row in self.data:
            row[self.header[column]] = func(row[self.header[column]])

    def create_dict(self, key_col, val_col):
        '''Returns a dictionary with a simple correspondence of one
        column containing the keys and one column containing
        the values. Columns are specified by label (in header dict)'''
        result = {}
        for row in self.data:
            result[row[self.header[key_col]]] = row[self.header[val_col]]
        return result

    def create_dict_list(self, key_col, val_cols):
        '''Returns a dictionary with key_col as the key and values
        (to be assigned as a list) specified by the val_cols list
        '''
        result = {}
        for row in self.data:
            result[row[self.header[key_col]]] = [
                row[self.header[col]] for col in val_cols]
        return result

    def get_column(self, column):
        '''Returns a simple list with only the specified column as
        specified by label (key in the header dict)'''
        return [row[self.header[column]] for row in self.data]

    def get_columns(self, column_list):
        '''Returns a generator of lists with only the specified columns.
        Columns are specified by the label (key in the header dict)
        Does not create a mutable reference back to the original'''
        for row in self.data:
            yield [row[self.header[col]] for col in column_list]

    def get_row(self, row_num):
        '''Returns a (mutable) row based on a row index'''
        return self.data[row_num]

    def __getitem__(self, key):
        '''Allows index Table[i:j] and list generators'''
        return self.data[key]

    def get_match_rows(self, column, match_value):
        '''Returns a generator of (mutable) rows where column specified by
        column matches the value in match_value'''
        for row in self.data:
            if row[self.header[column]] == match_value: yield row

    def rows(self):
        '''Returns a (mutable) generator of each row of data'''
        return (row for row in self.data)

    def get_header_dict(self):
        '''Returns a copy of the table's header dictionary'''
        return self.header.copy() #Shallow copy OK because these are immutable
    
    def c(self, header_name):
        '''short named function to enable reference to correct column'''
        return self.header[header_name]

    def add_column(self, header, col_data):
        '''tacks a new column of data onto the table'''
        if len(self.data) != len(col_data):
            raise Exception('New column not same length as existing table')
        self.header[header] = max(self.header.values())+1
        for i in range(0, len(self.data)):
            self.data[i].append(col_data[i])

    def to_csv(self, fn):
        '''sends the full table to a CSV file'''
        tt.table_to_csv(fn, self.get_full_table())
