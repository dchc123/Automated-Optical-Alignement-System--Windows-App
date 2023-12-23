"""
| --------------------------------------------------------------------------------
| $Author:: tbrooks@semtech.com
| --------------------------------------------------------------------------------

Generates a Python DUT register map file given a register map in perl .storable format defined here:
https://collaborate.semtech.com/display/GNIDIA/Parse+Memory+Map+XLS#ParseMemoryMapXLS-Exported.storablefile
"""
# Python Standard Library Imports
import sys
import textwrap
import storable


class CSRContainer:
    """
    Container Class for CSR
    """
    def __init__(self, name):
        self.name = name
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

    def add_reg(self, reg_item):
        self._reg_items.append(reg_item)

    @property
    def text_instance(self):
        """
        ***READONLY****
        :return: Returns a string containing the code to instantiate the csr_container item
        :rtype: str
        """
        code_text = '{0}self.{1} = {2}("{1}", self.device_address, self._interface, self.dummy_mode)\n'\
            .format(self._indent, self.name, self.build_properties['ClassAssociation'])
        return code_text

    @property
    def doc_string(self):
        """
        ***READONLY****
        :return: Returns a string containing the docstring for the csr_container item
        :rtype: str
        """
        doc_text = '{0}"""\n'.format(self._indent)
        doc_text += '{0}:name: {1}\n'.format(self._indent, self.name)
        doc_text += '{0}:type: {1}\n'.format(self._indent, self.build_properties['ClassAssociation'])
        doc_text += '{0}"""\n'.format(self._indent)

        return doc_text


class GeneratorRegisterItem:
    """
    Class that represents a device register.
    """
    def __init__(self, address, name, table):
        """
        :param address: address of the register
        :type address: int
        :param name: name of the register
        """
        self.address = address
        self.name = name
        self.table = table
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
            param_text = '{0} {1} {2} {3}:{4} {5}'.format(param.name, param.table, param.addr, param.msb, param.lsb,
                                                          param.reset_value)
            param_strings.insert(0, param_text)

        code_text = '{0}self.{1} = RegisterItem('.format(self._indent, self.name)
        indent_level = code_text.find("(") + 1
        indent = ' ' * indent_level
        code_text += '"{0}", '.format(self.name)
        code_text += '{0}, '.format(self.address)
        code_text += 'self._table, '
        code_text += '{0},'.format(reset_value)
        code_text += '\n{0}"Register Contents: (Parameter Name/ Address/ Table/ Bit Slice/ Reset value)"'.format(
                indent)

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
        cell_sizes = {'Name': 0, 'Address': 0, 'Table': 0, 'Slice': 0, 'Reset': 0}
        param_col = 'Parameter Name'
        addr_col = 'Address'
        table_col = 'Table'
        slice_col = 'Bit Slice'
        reset_col = 'Reset Value'
        param_strings = []
        largest_param = 0

        # Get information relating to the parameters inside the register
        for param in self.param_items:
            param_text = dict()
            param_text['Name'] = param.name
            param_text['Address'] = '{0: 3d}|0x{0:02X}'.format(int(param.addr))
            param_text['Table'] = '0x{0:02X}'.format(param.table)
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
        cell_sizes['Address'] = len(addr_col) + 3
        cell_sizes['Table'] = len(table_col) + 2
        cell_sizes['Slice'] = len(slice_col) + 2
        cell_sizes['Reset'] = len(reset_col) + 2

        # Build the doc string table
        doc_text = '{0}"""\n'.format(self._indent)
        # Add the top of the table
        doc_text += '{0}+{1}+{2}+{3}+{4}+{5}+\n'.format(self._indent,
                                                        '-' * cell_sizes['Name'],
                                                        '-' * cell_sizes['Address'],
                                                        '-' * cell_sizes['Table'],
                                                        '-' * cell_sizes['Slice'],
                                                        '-' * cell_sizes['Reset'])
        # Add the table header
        doc_text += '{0}|{1}|{2}|{3}|{4}|{5}|\n'.format(self._indent,
                                                        param_col.center(cell_sizes['Name'], ' '),
                                                        addr_col.center(cell_sizes['Address'], ' '),
                                                        table_col.center(cell_sizes['Table']),
                                                        slice_col.center(cell_sizes['Slice']),
                                                        reset_col.center(cell_sizes['Reset']))

        # Close the tables header
        doc_text += '{0}+{1}+{2}+{3}+{4}+{5}+\n'.format(self._indent,
                                                        '=' * cell_sizes['Name'],
                                                        '=' * cell_sizes['Address'],
                                                        '=' * cell_sizes['Table'],
                                                        '=' * cell_sizes['Slice'],
                                                        '=' * cell_sizes['Reset'])

        # Add the parameter items to the table
        for param_string in param_strings:
            doc_text += '{0}|{1}|{2}|{3}|{4}|{5}|\n'.format(self._indent,
                                                            param_string['Name'].center(cell_sizes['Name']),
                                                            param_string['Address'].center(cell_sizes['Address']),
                                                            param_string['Table'].center(cell_sizes['Table']),
                                                            param_string['Slice'].center(cell_sizes['Slice']),
                                                            param_string['Reset'].center(cell_sizes['Reset']))

            doc_text += '{0}+{1}+{2}+{3}+{4}+{5}+\n'.format(self._indent,
                                                            '-' * cell_sizes['Name'],
                                                            '-' * cell_sizes['Address'],
                                                            '-' * cell_sizes['Table'],
                                                            '-' * cell_sizes['Slice'],
                                                            '-' * cell_sizes['Reset'])

        # Close the table
        doc_text += '{0}"""\n'.format(self._indent)

        return doc_text


class GeneratorParameterItem:
    """
    A class that represents a device parameter.
    """
    def __init__(self, name, table, addr, parent_name, read_access, write_access, bit_slice,
                 reset_value, lone_child, description):
        """
        :param name: name of the parameter
        :type name: str
        :param table: table of the parameter
        :type table: int
        :param addr: address of the register in which the parameter resides
        :type addr: int
        :param parent_name: name of the register in which the parameter resides
        :type parent_name: str
        :param read_access: the level of read access allowed to the parameter (pw level 0, 1, 2 or 3)
        :type read_access: str
        :param write_access: the level of write access allowed to the parameter (pw level 0, 1, 2 or 3)
        :type write_access: str
        :param bit_slice: Bit slice
        :type bit_slice: str
        :param reset_value: the value of the parameter upon device reset
        :type reset_value: int
        :param lone_child: whether or not the parameter is alone in the register
        :type lone_child: bool
        :param description: description of the parameter
        :type description: str
        """
        self.name = name
        self.table = table
        self.addr = addr
        self.parent_name = parent_name
        self.read_access = read_access
        self.write_access = write_access
        self.bit_slice = bit_slice
        self.reset_value = reset_value
        self.description = description
        self.lone_child = lone_child
        self._indent = 8 * ' '
        self._parse_bit_slice()

    def _parse_bit_slice(self):
        """
        Given a bit slice, returns the MSB, LSB and mask.
        """
        # if the bit slice is of format msb:lsb
        if ':' in str(self.bit_slice):
            split_bit_slice = self.bit_slice.split(':')
        else:  # a single bit
            split_bit_slice = [self.bit_slice, self.bit_slice]
        try:
            self.msb = int(split_bit_slice[0])
            self.lsb = int(split_bit_slice[1])
        except ValueError:
            # weird issue where a bf had bits:'0,,,,,,,,,'
            self.msb = int(split_bit_slice[0][0])
            self.lsb = int(split_bit_slice[1][0])
        self.mask = 0
        self.valid_range = 2**(self.msb-self.lsb+1)-1  # valid range is the maximum value the bit field can hold

        # Calculate the mask by taking each bit slice, raise 2 to the power of the value and add it to the overall mask
        for i in range(int(self.lsb), int(self.msb) + 1):
            self.mask += 2**i

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
        code_text += 'self._table,\n'
        code_text += indent
        code_text += '"{0}", '.format(self.read_access)
        code_text += '"{0}", '.format(self.write_access)
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

        # Add lone_child info, device address, interface and dummy mode entries
        code_text += ',\n'
        code_text += indent
        code_text += '{0}, '.format(self.lone_child)
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
        doc_text += '\n{0}:Read Access: {1}'.format(self._indent, self.read_access)
        doc_text += '\n{0}:Write Access: {1}'.format(self._indent, self.write_access)
        doc_text += '\n{0}:MSB: {1}'.format(self._indent, self.msb)
        doc_text += '\n{0}:LSB: {1}'.format(self._indent, self.lsb)
        doc_text += '\n{0}:Valid Range: {1}'.format(self._indent, str(self.valid_range))
        doc_text += '\n{0}:Mask: {1}'.format(self._indent, self.mask)

        doc_text += '\n' + self._indent + '\"\"\"\n'

        return doc_text


class CSRGenerator:
    """
    DUT CSR Generation Class
    """
    def __init__(self, reg_map, dut_name):
        """
        :param reg_map: File path to CSR map in .storable format
        :param dut_name: Name of the device
        """
        self._reg_map = reg_map
        self._dut_name = str(dut_name).lower()
        self.large_indent = 8 * ' '
        self.small_indent = 4 * ' '
        self._global_csr = None
        self._output_py = ''

    def _create_csr_py_file(self):
        """
        Creates the dut driver python file
        """
        # Open the file with UTF-8 encoding
        print('\nCreating python CSR file ("{0}_csr.py"):'.format(self._dut_name))
        # Add the SVN keywords to the top of the file
        print('Adding SOS version to file.')
        self._add_sos_version()
        # generate csr_container
        print('generating CSR container.')
        self._create_csr_container()
        # Add the CSR class definition code to the file
        print('Adding CSR Class definition to file.')
        self._add_csr_class_to_file()
        # Add the global lane class definition code to the file
        print('Adding Global Class definitions to file.')
        self._add_global_classes_to_file()
        # Close the file
        with open(self._dut_name + '_csr.py', 'w+', encoding='utf-8') as _output_file:
            _output_file.write(self._output_py)

    def _add_sos_version(self):
        self._output_py += '"""\n'
        self._output_py += '| :$SOS_VERSION:: {}                               $:  Revision of last ' \
                           'commit\n'.format(self.structure['SOS_VERSION'])
        self._output_py += '| --------------------------------------------------------------------------------\n'
        self._output_py += '\n"""\n\n'

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
        self._output_py += 'from CLI.Devices.Base.base_csr import {0}, {1}, {2}, {3}, {4}, {5}\n\n\n'\
            .format('BaseCSR',
                    'BaseLane',
                    'BaseRegisterList',
                    'BaseParameterList',
                    'RegisterItem',
                    'ParameterItem')

        # Add the devices CSR class definition
        self._output_py += 'class {0}CSR(BaseCSR):\n'.format(self._dut_name.upper())
        self._output_py += '{0}def __init__(self, device_address, interface, dummy_mode, **kwargs):\n'.format(self.small_indent)
        self._output_py += '{0}\"\"\"\n'.format(self.large_indent)
        self._output_py += '{0}:param device_address: address of the device\n'.format(self.large_indent)
        self._output_py += '{0}:type device_address: int or str\n'.format(self.large_indent)
        self._output_py += '{0}:param interface: communication interface\n'.format(self.large_indent)
        self._output_py += '{0}:type interface: BaseDeviceInterface\n'.format(self.large_indent)
        self._output_py += '{0}:param dummy_mode: specifies whether or not the driver is in dummy mode\n'\
                           .format(self.large_indent)
        self._output_py += '{0}:type dummy_mode: bool\n'.format(self.large_indent)
        self._output_py += '{0}:param kwargs: arbitrary keyword arguments\n'.format(self.large_indent)
        self._output_py += '{0}:type kwargs: dict\n'.format(self.large_indent)
        self._output_py += '{0}\"\"\"\n'.format(self.large_indent)

        # Add the code to make the child call the super class
        self._output_py += '{0}super(.__init__(device_address=device_address, '\
                           'interface=interface, dummy_mode=dummy_mode, **kwargs)\n'\
                           .format(self.large_indent)

        # Add the text
        self._output_py += self._global_csr.text_instance
        self._output_py += self._global_csr.doc_string
        self._output_py += '{0}self._build_lane_list()\n\n\n'.format(self.large_indent)

    def _add_global_classes_to_file(self):
        """
        Inserts the RegisterList and ParameterList code into the output python file
        """

        # Add a Class definition for the Global Page:
        class_name = self._global_csr.build_properties['ClassAssociation']
        self._output_py += 'class {0}(BaseLane):\n'.format(class_name)
        self._output_py += self._create_init_text()

        # Add the code that instantiates the RegisterList for the global lane page
        self._output_py += '{0}self.reg = {1}RegisterList(self.device_address, '\
                           'self._interface, self.dummy_mode)\n'\
                           .format(self.large_indent,
                                   class_name)

        # Add a docstring to tell pycharm that the type is of RegisterList
        self._output_py += '{0}""":type: {1}RegisterList"""\n'.format(self.large_indent, class_name)

        # Add the code that instantiates the ParameterList for the global lane page
        self._output_py += '{0}self.param = {1}ParameterList(self.device_address, '\
                           'self._interface, self.dummy_mode)\n'.format(self.large_indent,class_name)

        # Add a docstring to tell pycharm that the type if of ParameterList
        self._output_py += '{0}\"\"\":type: {1}ParameterList\"\"\"\n\n\n'.format(self.large_indent, class_name)

        # Add a class definition for the Global Pages RegisterList class:
        self._output_py += 'class {0}RegisterList(BaseRegisterList):\n'.format(class_name)
        self._output_py += self._create_init_text()
        # Add the code for the global pages registers:
        for register in self._global_csr.reg_items:
            self._output_py += register.text_instance
            self._output_py += register.doc_string

        # Add the code that causes the global lane to auto-populate its register list with register objects
        self._output_py += '{0}self._build_register_list()\n\n\n'.format(self.large_indent)

        # Add a class definition for the Global Pages ParameterList class:
        self._output_py += 'class {0}ParameterList(BaseParameterList):\n'.format(class_name)
        self._output_py += self._create_init_text()

        # Add the code for the global pages parameter items
        for register in self._global_csr.reg_items:
            for parameter in register.param_items:
                self._output_py += parameter.text_instance
                self._output_py += parameter.doc_string

        # Add the code that causes the global lane to auto-populate its parameter list with parameter objects
        self._output_py += '{0}self._build_parameter_list()\n\n\n'.format(self.large_indent)

    def _identify_lone_child_params(self):
        """
        Scans through all registers and marks the parameters that exist as lone parameters in registers
        """
        print('Identifying lone_child parameters...')
        # Identify lone_children in global pages
        for reg in self.structure['memory_map']:
            try:
                list_of_bfs = self.structure['memory_map'][reg]['list_of_bfs']
            except KeyError:
                # some LUTs don't have bitfields because the memory map doesn't have anything in the "function" column
                # so we don't bother trying to find a bf
                pass
            else:
                # if there wasn't an exception
                if len(list_of_bfs) == 1:
                    self.structure['bit_field'][list_of_bfs[0]]['lone_child'] = True
                else:
                    for b in list_of_bfs:
                        self.structure['bit_field'][b]['lone_child'] = False

        print('lone_child parameter identification completed.\n')

    def _extract_structure(self):
        """
        Extracts the 'structure' database from the .storable file to a nested dictionary
        :return: returns a dictionary containing the memory map database structure
        :rtype: dict
        """
        self.structure = storable.retrieve(self._reg_map)
        return self.structure

    def _create_csr_container(self):
        """
        Converts a storable structure into a collection of objects that contain registers and parameters.
        These are used to make output file creation easier.
        """

        csr_container = CSRContainer('csr')

        # Scan through each row by parameter
        for reg_name, register in self.structure['memory_map'].items():
            try:
                if register['table']:
                    register['table'] = int(register['table'])
            except ValueError:
                if register['table'] == 'Not Tabled':
                    register['table'] = None
                else:
                    raise ValueError('unrecognised table format: "{}". expecting "Not Tabled"'.format(register['table']))
            # Extract the page register from the structure
            reg_item = GeneratorRegisterItem(int(register['offset']), reg_name, register['table'])
            # what happens if there legitimately are no bit fields?
            # for example the lower byte of a multi-byte register
            # I feel there isn't an easy way to shoe horn this in
            try:
                lone_bf = True if len(register['list_of_bfs']) == 1 else False
                for param in register['list_of_bfs']:
                    param_item = GeneratorParameterItem(param,
                                                        register['table'],
                                                        int(register['offset']),
                                                        reg_name,
                                                        self.structure['bit_field'][param]['read_access'],
                                                        self.structure['bit_field'][param]['write_access'],
                                                        self.structure['bit_field'][param]['bits'],
                                                        self.structure['bit_field'][param]['POR'],
                                                        lone_bf,
                                                        self.structure['bit_field'][param]['description'],
                                                        )
                    # Add the parameter item to the register item
                    reg_item.add_param(param_item)
            except KeyError:
                # don't add bfs when here are none
                pass
            csr_container.add_reg(reg_item)
        self._global_csr = csr_container
        self._global_csr.name = 'gcsr'
        self._global_csr.build_properties['Build'] = True
        self._global_csr.build_properties['ClassAssociation'] = 'GlobalCSR'

    def generate(self):
        """
        Main function of the CSRGenerator class.
        This will generate a [device_name]_csr.py file given a CSR .storable file.
        """
        print('\nGenerating CSR python file for RegisterMap={0}'.format(self._reg_map))
        print('Note: Generation may take some time\n')
        self._extract_structure()
        self._identify_lone_child_params()
        self._create_csr_container()
        self._create_csr_py_file()
        print('\nCSR python file generation completed!')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Number of arguments is invalid!\n')
        print('Proper usage: python csrgenerator.py [csr_map_name.storable] '
              '[device_name]')
    else:
        # sys.argv[1] = csr map file
        # sys.argv[3] = device name >> used for output filename. i.e. GN2554 -> gn2554.py
        csr_generator = CSRGenerator(sys.argv[1], sys.argv[2])
        csr_generator.generate()
