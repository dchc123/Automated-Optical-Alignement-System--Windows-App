from __future__ import absolute_import, division, print_function, unicode_literals # for python 3 compatibility
from math import ceil
from builtins import range # for python 3 compatibility
from six import string_types, iteritems # for python 3 compatibility
import storable # to access the memory map databse created from perl scripts

import platform
if platform.system() == 'Windows': # we shall assume that we use the usb to i2c converter
    from COMMON.Equipment._i2c_win32 import Write, BlockWrite, Read, BlockRead
elif platform.system() == 'Linux': # we shall assume that we are on a raspberry pi and are using the SMBusWrapper
    from COMMON.Equipment._i2c_rpi import Write, BlockWrite, Read, BlockRead
else:
    raise Exception("Sorry, no implementation for your platform ('%s') available" % platform.system())


class I2cAccess(object):
    """I2cAccess provides the mechanics for cleanly doing I2C accesses using register map stored
    as a .storable file
    .file: location of the .storable file to work with."""
    def __init__(self, file_location="MemoryMap.storable", device_id=0):
        """

        :rtype:
        """
        super(I2cAccess, self).__init__()
        self.database = storable.retrieve(file_location) # the full database
        self.current_table = 0
        self.dev_id = device_id

    def table(self, table_num):
        """set table to work in
        table_num: the table to change too.
        current table: the current table... keeps it's state accross calls...
        """
        if isinstance(table_num, string_types) or table_num < 0: # if the table is not positive int
            tab = 0 # table 0
        else:
            tab = table_num
        # print('current_table:', self.current_table, ' , table_num:', tab)
        if tab != self.current_table:
            if self.dev_id == 0:
                dev_id = self.database['memory_map']['TABLE_SEL']['deviceID']
            else:
                dev_id = self.dev_id
            reg_addr = self.database['memory_map']['TABLE_SEL']['offset']
            Write(dev_id, reg_addr, tab) #update table number
            self.current_table = tab

    def get_reg(self, register):
        """get the value of a register"""
        (dev_id, tab, reg_addr, LSbit, length) = self.get_addr(register)
        # find out how many bytes the register spans
        # (number of bits/8, rounded up to the nearest integer)
        num_bytes = int(ceil((length+LSbit)/8.0))
        mask = (((2**length)-1) << LSbit)

        #print("mask: {:X}, lsbit:".format(mask), LSbit)

        # if we want to read a byte or multiples thereoff, it's better to do a block read
        value = 0
        #if (mask%255 == 0) and  (LSbit == 0):
        #    value = BlockRead(dev_id, reg_addr, num_bytes)
        #else:
        reg = BlockRead(dev_id, reg_addr, num_bytes)
        for i in range(num_bytes):
            byte_mask = (mask >> ((num_bytes-1-i)*8)) & ((2**8)-1)
            value += ((reg[i] & byte_mask) << ((num_bytes-1-i)*8)) >> LSbit
            #print(value, reg[i], byte_mask)
        return value

    def get_addr (self, reg_or_bf):
        """
        decode a bitfield or Register into a dev_id, table, reg_addr,
        LSbit and length tuple
        """
        try:
            reg      = self.database['bit_field'][reg_or_bf]['register']
            if self.dev_id == 0:
                dev_id = self.database['memory_map'][reg]['deviceID']
            else:
                dev_id = self.dev_id
            tab      = self.database['memory_map'][reg]['table']
            reg_addr = self.database['memory_map'][reg]['offset']
            LSbit    = self.database['bit_field'][reg_or_bf]['justification']
            length   = self.database['bit_field'][reg_or_bf]['length']  # number of bits
            #print("dev_id",dev_id)
            self.table(table_num=tab)         # we change the table just to be shure
            return (dev_id, tab, reg_addr, LSbit, length)
        except KeyError: # can't find bitfield
            pass
        # won't get here if we found a bitfield
        try:
            if self.dev_id == 0:
                dev_id   = self.database['memory_map'][reg_or_bf]['deviceID']
            else:
                dev_id = self.dev_id
            tab      = self.database['memory_map'][reg_or_bf]['table']
            reg_addr = self.database['memory_map'][reg_or_bf]['offset']
            LSbit    = 0
            length   = 8  # number of bits
            self.table(table_num=tab)         # we change the table just to be shure
            return (dev_id, tab, reg_addr, LSbit, length)
        except KeyError as error:
            raise error

    def wr_bf(self, **kwargs):
        """
        set bitfield(s) to value(s)
        wr_bf(bit_field1 = 1, bit_field2 = 3, etc...)
        """
        for (key, value) in iteritems(kwargs):
            (dev_id, tab, reg_addr, LSbit, length) = self.get_addr(key)

            if isinstance(value, tuple) or isinstance(value, list):
                # assert len(value) <= ceil(length/8.0), "writing more bytes {} than bits {}".format(len(value), length)
                BlockWrite(dev_id, reg_addr, value)
            else:
                # find out how many bytes the register spans
                # (number of bits/8, rounded up to the nearest integer)
                num_bytes = int(ceil((length+LSbit)/8.0))
                max_val = (2**length)-1
                mask = (((2**length)-1) << LSbit)
                shift_val = value << LSbit
                assert value <= max_val, "you tried to set bitfield '{}' to value {} which is greater than it's maximum value {}".format(key, value, max_val)
                registers=[]
                for i in range(num_bytes): # do deal with multibyte writes
                    # if length < 8 :
                    byte_mask = (mask >> ((num_bytes-1-i)*8)) & ((2**8)-1)
                    # however, if the byte mask < 255, we will need to do a read modify write
                    if byte_mask < ((2**8)-1):
                        # read the register to be changed and record the values to be kept
                        reg = ~byte_mask & Read(dev_id, reg_addr+i)
                        # the register to write is the values to be kept
                        # added to the appropriatley shifted and masked value to be written
                        reg = reg | ((shift_val >> ((num_bytes-1-i)*8)) & byte_mask)
                    else:
                        # default is that we write the whole value, appropriatley shifted and masked
                        reg = (shift_val >> ((num_bytes-1-i)*8)) & byte_mask
                        #print("reg", reg, "dev_id", dev_id, "reg_addr", reg_addr+i)
                    registers.append(reg)

                BlockWrite(dev_id, reg_addr, registers)
