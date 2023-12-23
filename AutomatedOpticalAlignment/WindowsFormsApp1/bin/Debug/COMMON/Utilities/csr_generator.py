"""
| $Revision:: 282342                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-09-12 23:02:47 +0100 (Wed, 12 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Generates a Python DUT CSR file given a Flat CSR register map in excel format
"""
# Python Standard Library Imports
import sys
import textwrap

# CLI Imports
from CLI.Utilities.excel_parser import NamedRangeParser
from CLI.Utilities.csr_hash_generator import CSRHashGenerator


class PageItem:
    """
    Class to hold device page information.
    """
    def __init__(self, name, offset):
        """
        :param name: name of the page
        :type name: str
        :param offset: offset of the page
        :type offset: int
        """
        self.name = name
        self.offset = offset
        self._reg_items = []
        self.build_properties = {'Build': False,
                                 'ClassAssociation': None}
        self._indent = 8 * ' '

    @property
    def reg_items(self):
        """
        ***READONLY***

        :return: list of register item objects
        :rtype: list of GeneratorRegisterItem
        """
        return self._reg_items

    @property
    def reg_items_flat_names(self):
        """
        Returns a list of register names that do not include the lane to which the lane belongs (i.e. (l3_register_name)

        :return: the list of register item flat names.
        :rtype: list of str
        """
        flat_names = []
        for reg_item in self.reg_items:
            flat_names.append(reg_item.flat_name)
        return flat_names

    @property
    def reg_items_full_names(self):
        """
        Returns a list of register names that include the lane to which the lane belongs (i.e. (l3_register_name).

        :return: the list of register item full names
        :rtype: list of str
        """
        full_names = []
        for reg_item in self.reg_items:
            full_names.append(reg_item.full_name)
        return full_names

    def add_reg(self, reg):
        """
        Adds a register item to the list of register items

        :param reg: the register item object to append
        :type reg: GeneratorRegisterItem
        """
        self._reg_items.append(reg)

    @property
    def text_instance(self):
        """
        ***READONLY***

        :return: Returns a string containing the code to instantiate the page item
        :rtype: str
        """
        code_text = '{0}self.{1} = {2}("{1}", {3}, self.device_address, self._interface, self.dummy_mode)\n'\
            .format(self._indent,self.name,self.build_properties['ClassAssociation'], self.offset)

        return code_text

    @property
    def doc_string(self):
        """
        ***READONLY***

        :return: returns a string containing the doc string for the PageItem object
        :rtype: str
        """
        doc_text = '{0}\"\"\"\n'.format(self._indent)
        doc_text += '{0}:lane: {1}\n'.format(self._indent, self.name)
        doc_text += '{0}:offset: {1}\n'.format(self._indent, self.offset)
        doc_text += '{0}:type: {1}\n'.format(self._indent, self.build_properties['ClassAssociation'])
        doc_text += '{0}\"\"\"\n'.format(self._indent)

        return doc_text


class GeneratorRegisterItem:
    """
    Class that represents a device register.
    """
    def __init__(self, reg_type, address, full_name, flat_name):
        """
        :param reg_type: the type of register
        :type reg_type: str
        :param address: address of the register
        :type address: int
        :param full_name: name of the register including any lane prefix (i.e. lx)
        :type full_name: str
        :param flat_name: name of the register without any lane prefix
        :type flat_name: str
        """
        self.reg_type = reg_type
        self.address = address
        self.full_name = full_name
        self.flat_name = flat_name
        self._param_items = []
        self._indent = 8 * ' '

    def add_param(self, param_item):
        """
        Adds a ParameterItem object to the list of parameter items.

        :param param_item: the parameter item object to add
        :type param_item: GeneratorParameterItem
        """
        self._param_items.append(param_item)

    @property
    def param_items(self):
        """
        ***READONLY***

        :return: a list of ParameterItem objects
        :rtype: list of GeneratorParameterItem
        """
        return self._param_items

    @property
    def text_instance(self):
        """
        ***READONLY***

        :return: returns a string containing the code required to instantiate the RegisterItem
        :rtype: str
        """
        param_strings = []
        reset_value = 0

        # Get information relating to the parameters inside the register
        for param in self.param_items:
            reset_value += int(param.reset_value) << int(param.lsb)
            param_text = '{0} {1}:{2} {3}'.format(param.name, param.msb, param.lsb, param.reset_value)
            param_strings.insert(0, param_text)

        code_text = '{0}self.{1} = RegisterItem('.format(self._indent, self.flat_name)
        indent_level = code_text.find("(") + 1
        indent = ' ' * indent_level
        code_text += '"{0}", '.format(self.flat_name)
        code_text += '{0}, '.format(self.address)
        code_text += 'self._offset, '
        code_text += '{0},'.format(reset_value)
        code_text += '\n{0}"Register Contents: (Parameter Name/Bit Slice/Reset value)"'.format(indent)

        for param_string in param_strings:
            code_text += '\n{0}"\\n{1}"'.format(indent, param_string)

        code_text += ',\n{0}self.device_address, self._interface, self.dummy_mode)\n'.format(indent)

        return code_text

    @property
    def doc_string(self):
        """
        ***READONLY***

        :return: returns a string containing a docstring for the RegisterItem
        :rtype: str
        """
        cell_sizes = {'Name': 0, 'Slice': 0, 'Reset': 0}
        param_col = 'Parameter Name'
        slice_col = 'Bit Slice'
        reset_col = 'Reset Value'
        param_strings = []
        largest_param = 0

        # Get information relating to the parameters inside the register
        for param in self.param_items:
            param_text = dict()
            param_text['Name'] = param.name
            param_text['Slice'] = '{0}:{1}'.format(param.msb, param.lsb)
            param_text['Reset'] = str(param.reset_value)
            param_strings.insert(0, param_text)
            # keep track of the largest parameter name
            if len(param.name) > largest_param:
                largest_param = len(param.name)

        # ensure we make doc string table columns the proper size
        if largest_param > len(param_col):
            cell_sizes['Name'] = largest_param + 2
        else:
            cell_sizes['Name'] = len(param_col) + 2
        cell_sizes['Slice'] = len(slice_col) + 2
        cell_sizes['Reset'] = len(reset_col) + 2

        # Build the doc string table
        doc_text = '{0}\"\"\"\n'.format(self._indent)
        # Add the top of the table
        doc_text += '{0}+{1}+{2}+{3}+\n'.format(self._indent,
                                                '-' * cell_sizes['Name'],
                                                '-' * cell_sizes['Slice'],
                                                '-' * cell_sizes['Reset'])
        # Add the table header
        doc_text += '{0}|{1}|{2}|{3}|\n'.format(self._indent,
                                                param_col.center(cell_sizes['Name'], ' '),
                                                slice_col.center(cell_sizes['Slice']),
                                                reset_col.center(cell_sizes['Reset']))

        # Close the tables header
        doc_text += '{0}+{1}+{2}+{3}+\n'.format(self._indent, '=' * cell_sizes['Name'],
                                                '=' * cell_sizes['Slice'], '=' * cell_sizes['Reset'])

        # Add the parameter items to the table
        for param_string in param_strings:
            doc_text += '{0}|{1}|{2}|{3}|\n'.format(self._indent,
                                                    param_string['Name'].center(cell_sizes['Name']),
                                                    param_string['Slice'].center(cell_sizes['Slice']),
                                                    param_string['Reset'].center(cell_sizes['Reset']))

            doc_text += '{0}+{1}+{2}+{3}+\n'.format(self._indent,
                                                    '-' * cell_sizes['Name'],
                                                    '-' * cell_sizes['Slice'],
                                                    '-' * cell_sizes['Reset'])

        # Close the table
        doc_text += '{0}\"\"\"\n'.format(self._indent)

        return doc_text


class GeneratorParameterItem:
    """
    A class that represents a device parameter.
    """
    def __init__(self, name, addr, parent_name, access, msb, lsb, mask,
                 reset_value, valid_range, orphan, description):
        """
        :param name: name of the parameter
        :type name: str
        :param addr: address of the register in which the parameter resides
        :type addr: int
        :param parent_name: name of the register in which the parameter resides
        :type parent_name: str
        :param access: the type of access allowed by the parameter
        :type access: str
        :param msb: Most Significant Bit
        :type msb: int
        :param lsb: Least Significant Bit
        :type lsb: int
        :param mask: the mask that represents the location of the parameter in the register
        :type mask: int
        :param reset_value: the value of the parameter upon device reset
        :type reset_value: int
        :param valid_range: the range of values considered valid for the parameter
        :type valid_range: int
        :param orphan: whether or not the parameter is alone in the register
        :type orphan: bool
        :param description: description of the parameter
        :type description: str
        """
        self.name = name
        self.addr = addr
        self.parent_name = parent_name
        self.access = access
        self.msb = msb
        self.lsb = lsb
        self.mask = mask
        self.reset_value = reset_value
        self.valid_range = valid_range
        self.description = description
        self.orphan = orphan
        self._indent = 8 * ' '

    @property
    def text_instance(self):
        """
        Returns a string representing the line of code that instantiates the ParameterItem in the DUT csr file.
        """
        # Break up the descriptions into chunks of 70 characters
        wrapped_description = textwrap.wrap(self.description, 70)

        # Build the code text string for the ParameterItem instance
        code_text = '{0}self.{1} = ParameterItem('.format(self._indent, self.name)
        indent_level = code_text.find("(") + 1
        indent = ' ' * indent_level
        code_text += '"{0}", '.format(self.name)
        code_text += '{0}, '.format(self.addr)
        code_text += '"{0}", '.format(self.parent_name)
        code_text += 'self._offset,\n'
        code_text += indent
        code_text += '"{0}", '.format(self.access)
        code_text += '{0}, '.format(self.msb)
        code_text += '{0}, '.format(self.lsb)
        code_text += '{0}, '.format(self.mask)
        code_text += '{0}, '.format(self.reset_value)
        if self.valid_range is None:
            code_text += '{0}, '.format(self.valid_range)
        else:
            code_text += '"{0}", '.format(self.valid_range)

        # Insert the multi-line dut description
        for line in wrapped_description:
            code_text += '\n' + indent
            code_text += '"{0}"'.format(line)

        # Add orphan info, device address, interface and dummy mode entries
        code_text += ',\n'
        code_text += indent
        code_text += '{0}, '.format(self.orphan)
        code_text += 'self.device_address, self._interface, self.dummy_mode)\n'

        return code_text

    @property
    def doc_string(self):
        """
        Builds a docstring for the parameter and returns it.
        Note the function handles indenting to ensure each line conforms to PEP8 standards.
        """
        # split the description retrieved from the excel file into chunks of 70 characters
        wrapped_description = textwrap.wrap(self.description, 70)

        doc_text = self._indent + '\"\"\"\n'

        # Add the parameter description to the string
        for line in wrapped_description:
            doc_text += self._indent + line + '\n'

        # Add the parameter info items to the string
        doc_text += '\n{0}:Parent Name: {1}'.format(self._indent, self.parent_name)
        doc_text += '\n{0}:Register Address: {1}'.format(self._indent, self.addr)
        doc_text += '\n{0}:Reset Value: {1}'.format(self._indent, self.reset_value)
        doc_text += '\n{0}:Access: {1}'.format(self._indent, self.access)
        doc_text += '\n{0}:MSB: {1}'.format(self._indent, self.msb)
        doc_text += '\n{0}:LSB: {1}'.format(self._indent, self.lsb)
        doc_text += '\n{0}:Valid Range: {1}'.format(self._indent, str(self.valid_range))

        doc_text += '\n' + self._indent + '\"\"\"\n'

        return doc_text


class CSRGenerator:
    """
    DUT CSR Generation Class
    """
    def __init__(self, reg_map, sheet, dut_name):
        """
        :param reg_map: File path to CSR map in excel format
        :param sheet: Name of sheet containing CSR map
        :param dut_name: Name of the device
        """
        self._reg_map = reg_map
        self._sheet = sheet
        self._dut_name = str(dut_name).lower()
        self.large_indent = 8 * ' '
        self.small_indent = 4 * ' '
        self._lane_pages = []
        """:type: list of PageItem"""
        self._global_page = None
        self._output_file = None

    def _create_csr_py_file(self):
        """
        Creates the dut driver python file
        """
        # Open the file with UTF-8 encoding
        print('\nCreating python CSR file ("{0}_csr.py"):'.format(self._dut_name))
        self._output_file = open(self._dut_name + '_csr.py', 'w+', encoding='utf-8')
        # Add the SVN keywords to the top of the file
        print('Adding SVN keywords to file.')
        self._add_svn_keywords()
        # Add the CSR class definition code to the file
        print('Adding CSR Class definition to file.')
        self._add_csr_class_to_file()
        # Add the lane class definition code to the file
        print('Adding Lane Class definitions to file.')
        self._add_lane_classes_to_file()
        # Add the global lane class definition code to the file
        print('Adding Global Class definitions to file.')
        self._add_global_classes_to_file()
        # Add the dyanmic parameters to the bottom of the file
        print('\nAdding an dynamic parameters to the file.')
        self._add_dynamic_parameters()
        # Close the file
        self._output_file.close()
        # Hash the file contents and add the digest to the bottom of the file.
        print('\nAdding a SHA3-512 hash of the file contents to the file.')
        self._add_sha3_512()

    def _add_svn_keywords(self):
        self._output_file.write('"""\n')
        self._output_file.write('| :$Revision:: 282342                                       $:  Revision of last commit\n')
        self._output_file.write('| :$Author:: sgotic@SEMNET.DOM                              $:  Author of last commit\n')
        self._output_file.write('| :$Date:: 2018-09-12 23:02:47 +0100 (Wed, 12 Sep 2018)     $:  Date of last commit\n')
        self._output_file.write('| --------------------------------------------------------------------------------\n')
        self._output_file.write('\n"""\n\n')

    def _add_dynamic_parameters(self):
        # Add the SHA3_512 hash placeholder
        self._output_file.write('{0}CSR.hash = "{1}"\n'.format(self._dut_name.upper(), ' ' * 128))
        # Add the SVN revision parameter
        self._output_file.write('{0}CSR.revision = ":$Revision:: 282342             $:"\n'
                                .format(self._dut_name.upper()))

    def _add_sha3_512(self):
        """
        Generates a SHA3_512 hash of the final csr.py file created by the generator. The generated hash is placed
        at the bottom of the file and added to the device csr object through a hash property which is accessible by
        all users.
        """
        # Create a CSRHashGenerator object
        hash_generator = CSRHashGenerator()
        # Update the hash placeholder in the file
        hash_generator.update_hash(self._dut_name + '_csr.py')

    def _create_init_text(self):
        """
        Returns a string containing code that defines __init__ and performs the super() function
        """
        init_text = '{0}def __init__(self, *args, **kwargs):\n' \
                    '{0}{0}super().__init__(*args, **kwargs)\n'.format(self.small_indent)

        return init_text

    def _add_csr_class_to_file(self):
        """
        Inserts the DUT class python code into the output python file.
        """
        # Add the code that will import the required files and classes
        self._output_file.write('from CLI.Devices.Base.base_csr import {0}, {1}, {2}, {3}, {4}, {5}\n\n\n'
                                .format('BaseCSR',
                                        'BaseLane',
                                        'BaseRegisterList',
                                        'BaseParameterList',
                                        'RegisterItem',
                                        'ParameterItem'))

        # Add the devices CSR class definition
        self._output_file.write('class {0}CSR(BaseCSR):\n'.format(self._dut_name.upper()))
        self._output_file.write('{0}def __init__(self, device_address, interface, dummy_mode, **kwargs):\n'.format(self.small_indent))
        self._output_file.write('{0}\"\"\"\n'.format(self.large_indent))
        self._output_file.write('{0}:param device_address: address of the device\n'.format(self.large_indent))
        self._output_file.write('{0}:type device_address: int or str\n'.format(self.large_indent))
        self._output_file.write('{0}:param interface: communication interface\n'.format(self.large_indent))
        self._output_file.write('{0}:type interface: BaseDeviceInterface\n'.format(self.large_indent))
        self._output_file.write('{0}:param dummy_mode: specifies whether or not the driver is in dummy mode\n'
                                .format(self.large_indent))
        self._output_file.write('{0}:type dummy_mode: bool\n'.format(self.large_indent))
        self._output_file.write('{0}:param kwargs: arbitrary keyword arguments\n'.format(self.large_indent))
        self._output_file.write('{0}:type kwargs: dict\n'.format(self.large_indent))
        self._output_file.write('{0}\"\"\"\n'.format(self.large_indent))

        # Add the code to make the child call the super class
        self._output_file.write('{0}super().__init__(device_address=device_address, '
                                'interface=interface, dummy_mode=dummy_mode, **kwargs)\n'
                                .format(self.large_indent))

        # Add the code to instantiate the lanes of the device
        for page in self._lane_pages:
            self._output_file.write(page.text_instance)
            self._output_file.write(page.doc_string)
        # Add the code to instantiate the global page of the device
        self._output_file.write(self._global_page.text_instance)
        self._output_file.write(self._global_page.doc_string)
        self._output_file.write('{0}self._build_lane_list()\n\n\n'.format(self.large_indent))

    def _add_lane_classes_to_file(self):
        """
        Inserts the LaneClass, LaneClassRegisterList and LaneClassParameterList code into the output python file
        """
        # Add a class definition for the lanes of the device:
        for page in self._lane_pages:
            class_name = page.build_properties['ClassAssociation']
            if page.build_properties['Build'] is True:
                self._output_file.write('class {0}(BaseLane):\n'.format(class_name))
                self._output_file.write(self._create_init_text())

                # Add the line of code that will instantiate the RegisterList object for the given page
                self._output_file.write('{0}self.reg = {1}RegisterList(self._offset, self.device_address, '
                                        'self._interface, self.dummy_mode)\n'
                                        .format(self.large_indent,
                                                class_name))

                # Add the doc string to let pycharm know the type is of RegisterList
                self._output_file.write('{0}\"\"\":type: {1}RegisterList\"\"\"\n'
                                        .format(self.large_indent,
                                                class_name))

                # Add the line of code that will instantiate the ParameterList object for the given page
                self._output_file.write('{0}self.param = {1}ParameterList(self._offset, self.device_address, '
                                        'self._interface, self.dummy_mode)\n'
                                        .format(self.large_indent,
                                                class_name))

                # Add the doc string to let pycharm know the type is of ParameterList
                self._output_file.write('{0}\"\"\":type: {1}ParameterList\"\"\"\n\n\n'
                                        .format(self.large_indent, class_name))

                # For the current lane, add a register list class definition:
                self._output_file.write('class {0}RegisterList(BaseRegisterList):\n'.format(class_name))
                self._output_file.write(self._create_init_text())

                # Add the code for each register item in the lane:
                for register in page.reg_items:
                    self._output_file.write(register.text_instance)
                    self._output_file.write(register.doc_string)

                # Add the line of code that will make the register list self populate with register objects
                self._output_file.write('{0}self._build_register_list()\n\n\n'.format(self.large_indent))

                # For the current lane, add a parameter list class definition:
                self._output_file.write('class {0}ParameterList(BaseParameterList):\n'.format(class_name))
                self._output_file.write(self._create_init_text())
                # Add the code for each parameter item in the lane
                for register in page.reg_items:
                    for parameter in register.param_items:
                        self._output_file.write(parameter.text_instance)
                        self._output_file.write(parameter.doc_string)
                # Add the line of code that will make the parameter list self populate wih parameter objects
                self._output_file.write('{0}self._build_parameter_list()\n\n\n'.format(self.large_indent))

    def _add_global_classes_to_file(self):
        """
        Inserts the GlobalClass, GlobalRegisterList and GlobalParameterList code into the output python file
        """
        if self._global_page is not None:
            # Add a Class definition for the Global Page:
            class_name = self._global_page.build_properties['ClassAssociation']
            self._output_file.write('class {0}(BaseLane):\n'.format(class_name))
            self._output_file.write(self._create_init_text())

            # Add the code that instantiates the RegisterList for the global lane page
            self._output_file.write('{0}self.reg = {1}RegisterList(self._offset, self.device_address, '
                                    'self._interface, self.dummy_mode)\n'
                                    .format(self.large_indent,
                                            class_name))

            # Add a docstring to tell pycharm that the type is of RegisterList
            self._output_file.write('{0}\"\"\":type: {1}RegisterList\"\"\"\n'.
                                    format(self.large_indent,
                                           class_name))

            # Add the code that instantiates the ParameterList for the global lane page
            self._output_file.write('{0}self.param = {1}ParameterList(self._offset, self.device_address, '
                                    'self._interface, self.dummy_mode)\n'
                                    .format(self.large_indent,
                                            class_name))

            # Add a docstring to tell pycharm that the type if of ParameterList
            self._output_file.write('{0}\"\"\":type: {1}ParameterList\"\"\"\n\n\n'
                                    .format(self.large_indent,
                                            class_name))

            # Add a class definition for the Global Pages RegisterList class:
            self._output_file.write('class {0}RegisterList(BaseRegisterList):\n'.format(class_name))
            self._output_file.write(self._create_init_text())
            # Add the code for the global pages registers:
            for register in self._global_page.reg_items:
                self._output_file.write(register.text_instance)
                self._output_file.write(register.doc_string)

            # Add the code that causes the global lane to auto-populate its register list with register objects
            self._output_file.write('{0}self._build_register_list()\n\n\n'.format(self.large_indent))

            # Add a class definition for the Global Pages ParameterList class:
            self._output_file.write('class {0}ParameterList(BaseParameterList):\n'.format(class_name))
            self._output_file.write(self._create_init_text())

            # Add the code for the global pages parameter items
            for register in self._global_page.reg_items:
                for parameter in register.param_items:
                    self._output_file.write(parameter.text_instance)
                    self._output_file.write(parameter.doc_string)

            # Add the code that causes the global lane to auto-populate its parameter list with parameter objects
            self._output_file.write('{0}self._build_parameter_list()\n\n\n'.format(self.large_indent))

    def _identify_orphan_params(self):
        """
        Scans through all registers and marks the parameters that exist as lone parameters in registers
        """
        print('Identifying orphan parameters...')
        # Identify orphans in lane pages
        for page in self._lane_pages:
            for reg in page.reg_items:
                for param in reg.param_items:
                    if len(reg.param_items) == 1:
                        param.orphan = True
        # Identify orphans in global pages
        for reg in self._global_page.reg_items:
            for param in reg.param_items:
                if len(reg.param_items) == 1:
                    param.orphan = True
        print('Orphan parameter identification completed.\n')

    def _create_page_associations(self):
        """
        Identifies which pages are related to each other by comparing their register lists.

        The function works by comparing the flat register names (register names without the lane indicator i.e. lx)
        in one lane to another. When a match is found, the lanes become associated as they are the same
        and are not built during the csr file creation as it is duplication of code. If a lane is not the same,
        no association is made.

        When the loop begins, the first page is automatically associated to the first LaneClass and tagged as buildable.
        As the loop iterates, any file that wasn't matched on the previous loop will also be automatically associated
        and tagged as a buildable. This continues until all pages have been checked.

        Note: The global page is not included here as it should never be associated to a lane page. Refer to the
        _extract_global_page() function to find the code that determines whether or not the global page is built.
        """
        class_number = 1
        print ('Creating page associations:')
        for i in range(0, len(self._lane_pages)):
            if self._lane_pages[i].build_properties['Build'] is False and \
                    self._lane_pages[i].build_properties['ClassAssociation'] is None:
                self._lane_pages[i].build_properties['Build'] = True
                self._lane_pages[i].build_properties['ClassAssociation'] = 'LaneClass' + str(class_number)
                class_number += 1
            for j in range(i+1, len(self._lane_pages)):
                if self._lane_pages[i].reg_items_flat_names == self._lane_pages[j].reg_items_flat_names:
                    self._lane_pages[j].build_properties['ClassAssociation'] = \
                        self._lane_pages[i].build_properties['ClassAssociation']

        # Output lane association information for the user
        for page in self._lane_pages:
            print('Page: {0}. Build: {1}. Association: {2}'
                  .format(page.name,
                          page.build_properties['Build'],
                          page.build_properties['ClassAssociation']))

        if self._global_page is not None:
            print('Page: {0}. Build: {1}. Association: {2}'
                  .format(self._global_page.name,
                          self._global_page.build_properties['Build'],
                          self._global_page.build_properties['ClassAssociation']))

    def _extract_global_page(self):
        """
        Finds the global page in the list of pages, separates it from the list and
        assigns it to the global page variable.
        """
        global_pages_found = 0
        for page in self._lane_pages:
            if page.name is None:
                global_pages_found += 1
                self._global_page = page
                self._global_page.name = 'gl'
                self._global_page.build_properties['Build'] = True
                self._global_page.build_properties['ClassAssociation'] = 'GlobalLane'
                self._lane_pages.remove(page)

        # Can make the _create_pages function smarter and remove the code below by having the
        # function first check if a page with the same name exists and switching to it instead
        # of creating a new one
        if global_pages_found > 1:
            raise ValueError('CSR Generator found more than 1 global page!')

    def _parse_bit_slice(self, bit_slice):
        """
        Given a bit slice, returns the MSB, LSB and mask.

        :param bit_slice: the bit slice of the parameter
        :type bit_slice: int
        :return: returns a dictionary containing the msb, lsb & mask of the bit slice passed in.
        :rtype: dict
        """
        split_bit_slice = bit_slice.split(':')
        msb = split_bit_slice[0]
        lsb = split_bit_slice[1]
        mask = 0

        # Calculate the mask by taking each bit slice, raise 2 to the power of the value and add it to the overall mask
        for i in range(int(lsb), int(msb) + 1):
            mask += 2**i

        return {'msb': msb, 'lsb': lsb, 'mask': mask}

    def _create_pages(self):
        """
        Converts a flat CSR map into a collection of objects that contain registers and parameters.
        These are used to make output file creation easier.
        """
        xl_parser = NamedRangeParser()

        page = PageItem(None, None)
        reg_item = GeneratorRegisterItem(None, None, None, None)
        cur_reg_name = None
        prev_reg_name = None

        print('Creating device pages:')

        xl_parser.open_file(self._reg_map)
        flat_map = xl_parser.read_excel_table(self._sheet)

        # Scan through each row by parameter
        for index, row in enumerate(flat_map):
            # Compare the lane name to that of the page name. If they are not the same, the current register
            # does not belong to this lane and a new one must be created. This will also fire in the case that
            # the iteration index is 0 (first loop) to ensure we have a page even if the device is comprised of
            # only global registers
            if page.name != row['Lane'] or index == 0:
                # If the page is not None (which only happens on the first pass through), add the final register to the
                # page and then add the page to the lane list.
                if page.name is not None:
                    page.add_reg(reg_item)
                    reg_item.reg_type = None
                    if page not in self._lane_pages:
                        self._lane_pages.append(page)
                # Create a new page item if the current register is no longer associated with the current page item
                page = PageItem(row['Lane'], row['Address'])
                for lane_page in self._lane_pages:
                    if lane_page.name == row['Lane']:
                        page = lane_page
                        break
            # Get current register name and replace any spaces with an underscore
            if row['RegisterName'] is None:
                raise ValueError('Error: CSR contains an empty row! Please remove the empty row and try again.')
            cur_reg_name = row['RegisterName'].replace(' ', '_')

            # If the register we are pulling parameters from has changed but the page it belongs to remains the same,
            # then add the previous register item to the page item before overwriting the register item contents.
            if cur_reg_name != prev_reg_name:
                prev_reg_name = cur_reg_name
                if reg_item.reg_type is not None:
                    page.add_reg(reg_item)

                # Strip the lane component from the register name if required
                if row['Lane'] is None:
                    flat_reg_name = cur_reg_name
                else:
                    flat_reg_name = cur_reg_name.replace(row['Lane'] + '_', '')

                # Extract the page register from the CSR map
                reg_item = GeneratorRegisterItem(row['ParameterType'], int(row['Address']) - int(page.offset),
                                                 cur_reg_name, flat_reg_name)

            # Strip the lane component from the parameter name if required
            if row['Lane'] is None:
                flat_param_name = row['ParameterName']
            else:
                flat_param_name = row['ParameterName'].replace(row['Lane'] + '_', '')

            # Replace any spaces with underscores
            flat_param_name = flat_param_name.replace(' ', '_').replace('-', '_')

            # Get msb, lsb & mask from bit slice
            bit_slice_info = self._parse_bit_slice(row['BitSlice'])

            # Ensure RWAccess is not empty
            if row['RWAccess'] is None:
                rw_access = 'None'
            else:
                rw_access = row['RWAccess']

            # Ensure ResetValue is not empty
            if row['ResetValue'] is None:
                reset_value = -1
            else:
                reset_value = row['ResetValue']

            # This if-else use to check to ensure ValidRange was not None
            # However, CLI checks for either a value or None. If we set valid range to a 'None' string it will
            # fail when we use it. It is now left as a None type and dealt with in the text_instance() function
            if row['ValidRange'] is None:
                valid_range = None
            else:
                valid_range = row['ValidRange']

            # Ensure the parameter description is not empty
            param_description = row['Description']
            if param_description == '' or param_description == ' ' or param_description is None:
                param_description = 'No Description provided'
            else:
                param_description = param_description.replace('"', '')
                param_description = param_description.replace('`', '')

            # Build Parameter - Note that orphan is set to false and updated later in _identify_orphans
            param_item = GeneratorParameterItem(flat_param_name,
                                                reg_item.address,
                                                flat_reg_name,
                                                rw_access,
                                                bit_slice_info['msb'],
                                                bit_slice_info['lsb'],
                                                bit_slice_info['mask'],
                                                reset_value,
                                                valid_range,
                                                False,
                                                param_description)

            # Add the parameter item to the register item
            reg_item.add_param(param_item)

        # Add the final reg item to the final page and add the final page to the list
        # This is done outside of the loop as the loop will finish when it has iterated through all of the rows in the
        # csr file without getting the opportunity add the register item to the page item and the page item to the lane
        # page list.
        page.add_reg(reg_item)
        if page not in self._lane_pages:
            self._lane_pages.append(page)

        # Check for global page(s)
        self._extract_global_page()

        # Status information for the user
        print('Created {0} lane pages.'.format(len(self._lane_pages)))
        if self._global_page is None:
            print('Created 0 global pages.\n')
        else:
            print('Created 1 global page.\n')

    def generate(self):
        """
        Main function of the CSRGenerator class.
        This will generate a [device_name]_csr.py file given a *FLAT* CSR excel file.
        """
        print('\nGenerating CSR python file for RegisterMap={0}, Sheet={1}'.format(self._reg_map,
                                                                                   self._sheet))
        print('Note: Generation may take some time due to the Azure Information Protection add-in for excel\n')
        self._create_pages()
        self._identify_orphan_params()
        self._create_page_associations()
        self._create_csr_py_file()
        print('\nCSR python file generation completed!')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Number of arguments is invalid!\n')
        print('Proper usage: python csrgenerator.py [flat_csr_map_name.xlsm] '
              '[sheet_name] [device_name]')
    else:
        # sys.argv[1] = csr map file
        # sys.argv[2] = sheet name
        # sys.argv[3] = device name >> used for output filename. i.e. GN2554 -> gn2554.py
        csr_generator = CSRGenerator(sys.argv[1], sys.argv[2], sys.argv[3])
        csr_generator.generate()
