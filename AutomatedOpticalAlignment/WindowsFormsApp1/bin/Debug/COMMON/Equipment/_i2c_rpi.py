from __future__ import absolute_import, division, print_function, unicode_literals # for python 3 compatibility
import ctypes
import time
from smbus2 import SMBusWrapper

BUS_NUM = 1 # hard coded bus number

def Write(add,reg,data):
    dev_id = int(add/2)
    with SMBusWrapper(BUS_NUM) as bus:
        bus.write_byte_data(dev_id, reg, data)
        # if eeprom_backed:
        #     wait_for_ack(add)

def wait_for_ack(dev_id, timeout=1):
    """
    wait until device responds. timeout
    .dev_id, device to reach
    .timeout: amount of time to wait for
    """
    with SMBusWrapper(BUS_NUM) as bus:
        t_end = time.time()+timeout # define time period
        while time.time() < t_end:            # while we have not timed out
            try:                              # try do a single byte write
                bus.write_byte(dev_id, 0)
                ack = True                    # if we succeed, flag an ACK
                break                         # and exit the while loop
            except IOError:                   # if we get an IOerror, means a NACk was recieved
                ack = False                   # so set the ack flag false
        if not ack:                           # if the flag is not set when we exit
            # raise IOerror ourselves
            raise IOError("device 0x{0:02X} failed to ACK within 1 second".format(dev_id))


def BlockWrite(add,reg,*data):
    """
    BlockWrite: writes data to i2c device
    add is device id byte, including rd/wr bit
    """
    dev_id = int(add/2) # devide by 2 to remove read/write bit
    # check that data is an array of integers with max size = 255
    # if a list of bytes is passed to us, write block data,
    if isinstance(data[0], tuple) or isinstance(data[0], list):
        vals = data[0]
    else:
        vals = data

    # print("data ", data, data_struct)
    with SMBusWrapper(BUS_NUM) as bus:
        bus.write_i2c_block_data(dev_id, reg, vals)
        # if eeprom_backed:
        #     wait_for_ack(add)

def Read(add,reg):
    dev_id = int(add/2)
    with SMBusWrapper(BUS_NUM) as bus:
        x = bus.read_byte_data(dev_id, reg)
    return x

def BlockRead(add,reg,length):
    dev_id = int(add/2)
    with SMBusWrapper(BUS_NUM) as bus:
        value = bus.read_i2c_block_data(dev_id, reg, length) # watch out! returning a list!!
    return value
