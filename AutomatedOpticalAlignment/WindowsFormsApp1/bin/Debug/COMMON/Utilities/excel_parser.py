"""
| $Revision:: 280254                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-30 14:54:45 +0100 (Mon, 30 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Contains methods/utilities to read data from Excel files in standard formats
including the ability to parse based on named ranges.
"""
import re
import xlrd
import collections
import openpyxl
import os


class ExcelParser(object):
    """
    Class representing an Excel file parser which can load a file, and
    extract tables and other data (in standard formats) to Python structures.

    External user interface

    | open_file(...)
    | close_file(...)
    | read_excel_table(...)
    | read_horizontal_fields(...)
    |
    """
    def __init__(self):
        """
        Initialize instance
        """
        self.workbook = None

    @staticmethod
    def _read_excel_type(cell_type, cell_data):
        """
        Internal function for converting Excel cell data
        to a Python format.
        """
        if cell_type == 1:
            if len(cell_data) >= 2 and cell_data[len(cell_data) - 1] == 'h':
                # This could be a hex number
                number = cell_data[0:len(cell_data) - 1]

                try:
                    return int(number, 16)
                except:
                    pass

            if len(cell_data) >= 3 and cell_data[0 : 2] == "0x":
                number = cell_data[2 : len(cell_data)]

                try:
                    return int(number, 16)
                except:
                    pass

            if len(cell_data) >= 2 and cell_data[len(cell_data) - 1] == 'd':
                # This could be a decimal number
                number = cell_data[0:len(cell_data) - 1]

                try:
                    return int(number)
                except:
                    pass

            try:
                return str(cell_data).strip()
            except UnicodeEncodeError:
                return "*"

        elif cell_type == 2:
            if cell_data.is_integer():
                return int(cell_data)
            else:
                return float(cell_data)

        else:
            if str(cell_data).strip() == "1":
                return True
            elif str(cell_data).strip() == "0":
                return False

        try:
            return str(cell_data).strip()
        except UnicodeEncodeError:
            return "*"

    def close_file(self):
        """
        Closes the currently loaded workbook.
        """
        self.workbook = None

    def open_file(self, fname):
        """
        Opens an Excel workbook.
        """
        self.workbook = xlrd.open_workbook(fname)

    def read_excel_table(self, key_columns=None, sheet_name=None, preserve_order=False):
        """
        Read a table from the currently loaded workbook into a python dictionary.

        :param key_columns: A string or list of strings that dictate which columns
         in the table are the 'keys' for the dictionary. If this
         is None, this function will try to find a key column by looking
         for the special token COLUMN<KEY> at the end of a column header.
        :param sheet_name: The sheet from which to extract the table.
        :param preserve_order: flag to preserve order using ordered dictionary
        :return: - If more than one key column is specified::

            { ( key1, key2, ...) : { "Col1" : data, "Col2" : data, etc...} }

         - If only one key column is specified::

            { key : { "Col1" : data, "Col2" : data, etc...} }


        **Example**

        Excel Table (sheet name: TestSheet)

        +----+-------+-------+-----------+
        |x1  |   x2  |   A   |   B       |
        +====+=======+=======+===========+
        |0   |   1   |   F   |   Example |
        +----+-------+-------+-----------+
        |1   |   2   |   Kav |   Go      |
        +----+-------+-------+-----------+

        ::

            >>> read_excel_table(['x1', 'x2'], "TestSheet")
            { (0, 1) : {'A':'F', 'B':'Example'}, (1, 2) : {'A':'Kav', 'B':'Go'} }
        """

        if self.workbook is None:
            return None

        auto_detect_key_columns = []
        if key_columns is not None:
            if not isinstance(key_columns, (list, tuple)):
                key_columns = [key_columns]
            auto_detect_key_columns = key_columns

        if sheet_name is None:
            sheet_name = self.workbook.sheet_names()[0]

        worksheet = self.workbook.sheet_by_name(sheet_name)

        if not preserve_order:
            ret_dict = {}

        else:
            ret_dict = collections.OrderedDict()

        num_rows = worksheet.nrows
        num_cols = worksheet.ncols

        found_header_row = False

        key_column_indices = []
        column_headings = {}

        current_row = 0
        while current_row < num_rows:
            dict_key = ()
            values = collections.OrderedDict()

            if not found_header_row:
                column_headings = {}
                key_column_indices = []

            found_header = False

            current_cell = 0
            while current_cell < num_cols:
                valid_cell = False

                try:
                    cell_type = worksheet.cell_type(current_row, current_cell)
                    value = worksheet.cell_value(current_row, current_cell)

                    valid_cell = True
                except:
                    # Likely an index error since the Excel Python library is unreliable when it
                    # comes to keeping track of the actual spreadsheet limits. The solution of
                    # simply ignoring these errors is not ideal but almost unavoidable.
                    pass

                if valid_cell:
                    if not found_header_row:
                        # Check for a key token
                        str_value = str(value)
                        auto_detect_check = re.match("(.+)\s+<\s*KEY\s*>\s*", str_value)
                        if auto_detect_check:
                            value = auto_detect_check.group(1)

                        column_headings[current_cell] = self._read_excel_type(cell_type, value)

                        if cell_type == 1:
                            if key_columns is not None:
                                if str(value) in key_columns:
                                    key_column_indices.append(current_cell)
                                    found_header = True
                            else:
                                if auto_detect_check:
                                    # This is a key column
                                    key_column_indices.append(current_cell)
                                    found_header = True

                    else:
                        if current_cell in key_column_indices:
                            value = self._read_excel_type(cell_type, value)
                            if (type(value) is str and len(value) > 0) or (type(value) is not str):
                                dict_key += (value,)
                            else:
                                dict_key = ()
                        elif current_cell in column_headings.keys():
                            values[column_headings[current_cell]] = self._read_excel_type(cell_type, value)

                current_cell += 1

            if found_header:
                found_header_row = found_header

            if len(dict_key) > 0:
                if len(dict_key) == 1:
                    dict_key = dict_key[0]
                ret_dict[dict_key] = values

            current_row += 1

        return ret_dict

    def read_horizontal_fields(self, field_names, sheet_name, preserve_order=False):
        """
        Read a horizontal field (or fields) from an Excel file.

        Example spreadsheet layout

        | <field 1>   |   <field 1 data>
        | <field 2>   |   <field 2 data>
        |

        This returns a dictionary with keys of field_names.
        """
        if self.workbook is None:
            return None

        # Convert a non-list to a list
        if not isinstance(field_names, (list, tuple)):
            field_names = [field_names]

        if sheet_name is None:
            sheet_name = self.workbook.sheet_names()[0]

        worksheet = self.workbook.sheet_by_name(sheet_name)

        if not preserve_order:
            ret_dict = {}

        else:
            ret_dict = collections.OrderedDict()

        num_rows = worksheet.nrows
        num_cols = worksheet.ncols

        current_row = 0
        while current_row < num_rows:
            current_cell = 0
            while current_cell < num_cols:

                try:
                    cell_type = worksheet.cell_type(current_row, current_cell)
                    value = worksheet.cell_value(current_row, current_cell)

                    python_value = self._read_excel_type(cell_type, value)

                    if python_value in field_names:

                        data_field_cell_type = worksheet.cell_type(current_row, current_cell + 1)
                        data_field_value = worksheet.cell_value(current_row, current_cell + 1)

                        data_field_python_value = self._read_excel_type(data_field_cell_type,
                                                                        data_field_value)

                        ret_dict[python_value] = data_field_python_value
                except:
                    # Likely an index error since Excel is unreliable when it comes to
                    # keeping track of the actual spreadsheet limits.
                    pass

                current_cell += 1

            current_row += 1

        return ret_dict

    def load_data_from_file(self, filename, section):
        """
        Load an entry from an arbitrary file. Supported file types: Excel spreadsheet.

        :param filename: column name for database filename
        :type filename: str
        :param section: column name for database section/sheet
        :type section: str
        """
        self.open_file(filename)
        # Do an auto key detect table read of the Excel sheet
        data = self.read_excel_table(key_columns=None, sheet_name=section)
        self.close_file()
        return data

    def load_entries_from_excel_file(self, file, sheet, tag_col="Database Tag",
                                     filename_col="Filename", section_col="Section"):
        """
        Load database entries from an Excel file.

        The spreadsheet should have a format as follows:

        Database Tag    |   Filename    |   Section         |   Comment
        ----------------+---------------+-------------------+---------------
        <Tag>           |   example.xls |   example_sheet   |   Example comment.
        ...             |   ...         |   ...             |   ...


        :param file: main source file containing database entries
        :type file: str
        :param sheet: specific sheet name where database entries are located
        :type sheet: str
        :param tag_col: (default: 'Database Tag') column name for database tags
        :type tag_col: str
        :param filename_col: (default: 'Filename') column name for database filename
        :type filename_col: str
        :param section_col: (default: 'Section') column name for database section/sheet
        :type section_col: str
        """
        database_entries = {}
        # Open an Excel file and parse the table containing the database entries
        self.open_file(file)
        entry_table = self.read_excel_table(tag_col, sheet)
        self.close_file()

        if entry_table is None:
            raise RuntimeError("Could not parse Excel sheet %s in %s" % (sheet, file))

        # Append the entries to the database
        for entry in entry_table.keys():

            values = entry_table[entry]

            tag = entry
            filename = values[filename_col]
            section = values[section_col]

            dir_name = os.path.dirname(os.path.abspath(file)) + "\\"
            data = self._load_data_from_file(dir_name + filename, section)

            if data is not None:
                database_entries[tag] = data
            else:
                raise RuntimeError("Could not open database entry: %s" % tag)

        return database_entries


class NamedRangeParser:
    """
    Takes an CSR flat map excel file, parses it and returns a list of rows
    with the cells in each row contained in a dictionary

    External user interface

    | open_file(...)
    | read_excel_table(...)
    |
    """
    def __init__(self):
        self._workbook = None
        self._csr_columns = {'ParameterType': 'AM_WS_PARAMTYPE_COL',
                             'Lane': 'AM_WS_LANE_COL',
                             'CSRModule': 'AM_WS_SUBMODULE_COL',
                             'Address': 'AM_WS_ADDRESS_DEC_COL',
                             'RegisterName': 'AM_WS_REGISTER_NAME_COL',
                             'ParameterName': 'AM_WS_PARAMETER_NAME_COL',
                             'BitSlice': 'AM_WS_BIT_SLICE_COL',
                             'RWAccess': 'AM_WS_R_W_ACCESS_COL',
                             'ResetValue': 'AM_WS_RESET_VALUE_COL',
                             'ValidRange': 'AM_WS_VALID_RANGE_COL',
                             'Description': 'AM_WS_DESCRIPTION_COL'}

    def open_file(self, excel_file):
        """
        Opens the CSR excel file and gets a reference to the
        worksheet that contains the CSR flat map
        """
        self._workbook = openpyxl.load_workbook(excel_file)

    def _get_named_ranges(self, worksheet):
        """
        Returns the named ranges for a given worksheet name. The returned value is
        a dictionary with the name of the range as the key and a dictionary as the value.

        The dictionary stored within the value contains the column (string) and the column ID (Int)
        """
        if self._workbook is not None:
            named_ranges = {}

            for name in [n for n in self._workbook.defined_names.definedName if
                         n.value.startswith(worksheet)]:
                (title, coord) = list(name.destinations)[0]
                first_cell = self._workbook[title][coord]

                while isinstance(first_cell, tuple):
                    first_cell = first_cell[0]

                named_ranges[name.name] = {'COL': first_cell.column,
                                           'COL_ID': first_cell.col_idx - 1}

            return named_ranges
        else:
            raise ValueError('Workbook must be opened!')

    def read_excel_table(self, worksheet):
        """
        Reads the entire CSR table and returns a list full of dictionaries.
        Each dictionary is the data contained within the row.

        :param worksheet: Name of the worksheet to read in
        """
        table = []
        # skip the first row, we are not interested in the header
        named_ranges = self._get_named_ranges(worksheet)
        rows = iter(self._workbook[worksheet])
        next(rows)
        for row in rows:
            row_item = {}
            for key, value in self._csr_columns.items():
                row_item[key] = row[named_ranges[value]['COL_ID']].value
            table.append(row_item)

        return table


