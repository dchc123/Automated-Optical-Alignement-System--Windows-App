from __future__ import absolute_import, division, print_function, unicode_literals # for python 3 compatibility
import re
from math import ceil
from builtins import range  # for python 3 compatibility
from six import string_types, iteritems  # for python 3 compatibility
import storable  # to access the memory map database created from perl scripts
from collections import OrderedDict
from pathlib import Path


class MemoryMapAccess:
    """
    MemoryMapAccess provides the mechanics for cleanly doing I2C accesses using register map stored
    as a .storable file
    """
    def __init__(self, interface, file_location="MemoryMap.storable", device_id=0,
                 dummy_mode=False,  dummy_data=None):
        """

        :param interface: an instance of an interface (USB to I2C, raspberry pi i2c, other I2C interaface, SPI interface...
        :type interface: interface class instance
        :param file_location: MemoryMap file location
        :type file_location: Path
        :param device_id: i2c device address, if it is different from that defined in the Memory map file. otherwise leave it a t0 default
        :type device_id: int
        :param dummy_mode: dummy mode to work without i2c device connected
        :type dummy_mode: Bool
        :param kwargs:
        :type kwargs:
        """
        # super().__init__(**kwargs)
        self.dummy_mode = dummy_mode
        self.dummy_data = dummy_data
        file_location = file_location
        self.database = storable.retrieve(file_location)  # the full database
        self.current_table = 0
        self.dev_id = device_id
        self.interface = interface
        self.dig_debug = self._get_dig_debug_signals()
        if 'NUM_I2C_ADDR_BYTES' in self.database:
            self.interface.memory_address_length = self.database['NUM_I2C_ADDR_BYTES']
        else:
            self.interface.memory_address_length = 1

    def __enter__(self):
        if not self.dummy_mode:
            self.interface.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.dummy_mode:
            self.interface.close()

    def table(self, table_num):
        """
        set table to work in - This is automatically set when invoking set_reg or get_reg

        :param table_num: the table to change too.
        :type table_num: int or string
        """
        if isinstance(table_num, string_types) or table_num < 0:   # if the table is not positive int
            tab = 0   # table 0
        else:
            tab = table_num
        # print('current_table:', self.current_table, ' , table_num:', tab)
        if tab != self.current_table:
            if self.dev_id:
                dev_id = self.dev_id
            else:
                dev_id = self.database['memory_map']['TABLE_SEL']['deviceID']
            reg_addr = self.database['memory_map']['TABLE_SEL']['offset']
            if not self.dummy_mode:
                self.interface.write(dev_id, reg_addr, tab)  # update table number
            self.current_table = tab

    def get_reg(self, register):
        """
        get the value of a register (UPPERCASE) or bitfield (lowercase)

        :param register: the register or bitfield to access
        :type register: str
        :returns value: the value of the register or shifted and masked bit field
        :return type: int
        """
        (dev_id, tab, reg_addr, LSbit, length) = self._get_addr(register)
        # find out how many bytes the register spans
        # (number of bits/8, rounded up to the nearest integer)
        num_bytes = int(ceil((length+LSbit)/8.0))
        mask = (((2**length)-1) << LSbit)

        # print("mask: {:X}, lsbit:".format(mask), LSbit)

        # if we want to read a byte or multiples thereoff, it's better to do a block read
        value = 0
        # if (mask%255 == 0) and  (LSbit == 0):
        #     value = BlockRead(dev_id, reg_addr, num_bytes)
        # else:
        if not self.dummy_mode:
            reg = self.interface.read(dev_id, reg_addr, num_bytes)
        else:
            reg = self.dummy_data
        if type(reg) is int:
            reg = [reg]

        for i in range(num_bytes):
            byte_mask = (mask >> ((num_bytes-1-i)*8)) & ((2**8)-1)

            if not self.dummy_mode:
                value += ((reg[i] & byte_mask) << ((num_bytes-1-i)*8)) >> LSbit
            else:
                value=0
            # print(value, reg[i], byte_mask)
        return value

    def _get_addr(self, reg_or_bf):
        """
        decode a bitfield or Register into a dev_id, table, reg_addr,
        LSbit and length tuple
        """
        try:
            reg      = self.database['bit_field'][reg_or_bf]['register']
            if self.dev_id:
                dev_id = self.dev_id
            else:
                dev_id = self.database['memory_map'][reg]['deviceID']
            tab      = self.database['memory_map'][reg]['table']
            reg_addr = self.database['memory_map'][reg]['offset']
            LSbit    = self.database['bit_field'][reg_or_bf]['justification']
            length   = self.database['bit_field'][reg_or_bf]['length']  # number of bits
            # print("dev_id",dev_id)
            self.table(table_num=tab)         # we change the table just to be sure
            return dev_id, tab, reg_addr, LSbit, length
        except KeyError:  # can't find bitfield
            pass
        # won't get here if we found a bitfield
        try:
            if self.dev_id:
                dev_id = self.dev_id
            else:
                dev_id = self.database['memory_map'][reg_or_bf]['deviceID']
            tab      = self.database['memory_map'][reg_or_bf]['table']
            reg_addr = self.database['memory_map'][reg_or_bf]['offset']
            LSbit    = 0
            length   = 8  # number of bits
            self.table(table_num=tab)         # we change the table just to be sure
            return dev_id, tab, reg_addr, LSbit, length
        except KeyError as error:
            raise error

    def set_reg(self, **kwargs):
        """
        set register(s) to value(s)
        set_reg(bit_field1 = 1, bit_field2 = 3, etc...)
        or
        registers = {'reg_1': 1, 'reg_2':2)
        bit fields (function column in the memory map spreadsheet)are in lowercase - use for multiple byte bit fields and if you want to access a specific
        bit.
        Byte registers (Name column in the memory map spreadsheet) are in UPPERCASE - Use for setting multiple related
        bits in a register

        :param kwargs: Dictionary of register-value pairs
        :type kwargs: dict
        """
        for (key, value) in iteritems(kwargs):
            (dev_id, tab, reg_addr, LSbit, length) = self._get_addr(key)

            if isinstance(value, tuple) or isinstance(value, list):
                assert len(value) <= ceil(length/8.0), "writing more bytes {} than bits {}".format(len(value), length)
                if not self.dummy_mode:
                    self.interface.write(dev_id, reg_addr, value)
            else:
                # find out how many bytes the register spans
                # (number of bits/8, rounded up to the nearest integer)
                num_bytes = int(ceil((length+LSbit)/8.0))
                max_val = (2**length)-1
                mask = (((2**length)-1) << LSbit)
                shift_val = value << LSbit
                assert value <= max_val, "you tried to set bitfield '{}' to value {} which is greater than it's " \
                                         "maximum value {}".format(key, value, max_val)
                registers = []
                for i in range(num_bytes):  # do deal with multibyte writes
                    # if length < 8 :
                    byte_mask = (mask >> ((num_bytes-1-i)*8)) & ((2**8)-1)
                    # however, if the byte mask < 255, we will need to do a read modify write
                    if byte_mask < ((2**8)-1):
                        # read the register to be changed and record the values to be kept
                        if not self.dummy_mode:
                            reg = ~byte_mask & self.interface.read(dev_id, reg_addr+i)
                        else:
                            reg = 0
                        # the register to write is the values to be kept
                        # added to the appropriatley shifted and masked value to be written
                        reg = reg | ((shift_val >> ((num_bytes-1-i)*8)) & byte_mask)
                    else:
                        # default is that we write the whole value, appropriatley shifted and masked
                        reg = (shift_val >> ((num_bytes-1-i)*8)) & byte_mask
                        # print("reg", reg, "dev_id", dev_id, "reg_addr", reg_addr+i)
                    registers.append(reg)

                if not self.dummy_mode:
                    self.interface.write(dev_id, reg_addr, registers)

    @property
    def pw3(self):
        """
        **READONLY**

        :return: pwe value to enter Password level 3
        :rtype: dict
        """
        return dict(OrderedDict(self.database['chip_sequences']['PASSWORD_LEVEL_3']))

    @property
    def soft_reset(self):
        """
        **READONLY**

        :return: sequence for soft reset
        :rtype: dict
        """
        soft_reset_list = self.database['chip_sequences']['SOFT_RESET']
        od = OrderedDict(soft_reset_list)
        return dict(od)

    def save_settings(self, file_location, registers_to_record=()):
        """
        Save settings to file. If a list of registers to record is supplied, only those registers will be read back
        and written to file.

        :param registers_to_record: list of bitfields or registers to save in the settings file
        :type registers_to_record: list or dict
        :param file_location: location of settings file to write
        :type file_location: str
        """
        with open(file_location, 'w') as h:
            for reg_name in registers_to_record or self.database['memory_map']:
                string_to_write = '{}: 0x{:02X}\n'.format(reg_name, self.get_reg(reg_name))
                h.write(string_to_write)

    def load_settings(self, file_location):
        """
        Read a settings file, returning a dictionary of settings that can then be written to the device using set_reg

        :param file_location: location of settings file to read
        :type file_location: str
        :return: dictionary of settings from the file
        :rtype: dict
        """
        settings = {}
        with open(file_location, 'r') as h:
            for line in h:
                k, v = line.strip().split(': ')
                if k in {**self.database['bit_field'], **self.database['memory_map']}:
                    settings.update({k: int(v, 0)})
                else:
                    # this should be a log entry really
                    print("could not find register {} in memory map".format(k))
        return settings

    def get_non_default_values(self, tables=()):
        """
        run through all writable registers and return a dictionary of all values that differ from default values

        :param tables: list of tables to save
        :type tables: list
        :return: non default registers
        :rtype: dict
        """
        writable = ['cond', 'all', 'pw0', 'pw1', 'pw2', 'pw3']
        non_default_values = {}
        for bf_name, bf_attr in self.database['bit_field'].items():
            if len(tables) == 0 or self.database['memory_map'][bf_attr['register']]['table'] in tables:
                if not re.search('(^tb_)|(^fsc_)', bf_name):
                    if bf_attr['write_access']:  # ignore if not specified
                        if bf_attr['write_access'].lower() in writable:
                            bf_val = self.get_reg(bf_name)
                            print('.', end='', flush=True)
                            if bf_attr['POR'] != bf_val:
                                non_default_values.update({bf_name: bf_val})
        print('\n{} non default writable register{}'.format(len(non_default_values),
                                                            's' if len(non_default_values) > 1 else ''))
        return non_default_values

    def _get_dig_debug_signals(self):
        """
        Iterate through the database['test_signals'] structure and returns a dictionary of debug signal / value
        Entries are of the form:
        * database['test_signals']['<test_signal_name_entry>']['address'] = <integer>
        * database['test_signals']['<test_signal_name_entry>']['fromXLS'] = <signal_name>
        where <integer> is the value that needs to be written to the DEBUG register so that <signal_name> comes out
        on the selected digital debug output.
        So <test_signal_name_entry> would be of the form: DIG_DEBUG_TX_ENABLE_SEL ...
        and is the text that would be used in the RTL.

        :return: key: test signal name value: address to write to dig_debug_bus
        :rtype: dict
        """
        test_signals = {}
        for test_signal in self.database['test_signals']:
            key = self.database['test_signals'][test_signal]['fromXLS']
            test_signals.update({key: self.database['test_signals'][test_signal]['address']})
        return test_signals

