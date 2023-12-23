import ctypes
import time
from smbus2 import SMBus, i2c_msg

from COMMON.Interfaces.Base.base_device_interface import BaseDeviceInterface
from COMMON.Utilities.cli_path import resolve_file_path


class RpiI2c (BaseDeviceInterface):

    connections_info = {}
    connected_dongles = {}

    CAPABILITY = {
        'buffer_size': 8,
        'gpio_number': 0,
        'gpio_voltage_level': {'min': 0.8, 'max': 5.0},
        'interface_type': ['I2C'],
        'interface_mode': {
            'I2C': ['STANDARD', 'FAST', 'FAST_PLUS', 'HIGH_SPEED'],
        },
        'interface_speed': {
            'I2C': {'min': 20, 'max': 400},
        },
    }

    def __init__(self, address=None, dummy_mode=False, eeprom_backed=False, **kwargs):
        """
        Raspberry pi i2c driver

        :param address: /dev/i2c- number
        :type address: int
        :param dummy_mode: dummy mode flag
        :type dummy_mode: bool
        """
        super().__init__(address=address, **kwargs)
        self.handle = None
        self.path = None
        self.address = address
        self.eeprom_backed = eeprom_backed
        self.dummy_mode = dummy_mode
        self.dummy_data = {}
        self.memory_address_length = 1

    @property
    def gpio_voltage_level(self):
        raise NotImplementedError

    @property
    def identity(self):
        """
        **READONLY**

        :return: interface identity details
        :rtype: str or dict
        """
        return self.connections_info

    @property
    def interface_mode(self):
        raise NotImplementedError

    @property
    def interface_type(self):
        raise NotImplementedError

    @property
    def interface_speed(self):
        raise NotImplementedError

    def close(self):
        if self.dummy_mode:
            self.interface_connected = False
            return

        self.handle.close()
        self.connections_info['handle'] = None
        self.connections_info['i2c_functions'] = None
        self.interface_connected = False

    def open(self, address=None):
        """

        :param address: /dev/i2c- number
        :type address: int
        :return: none
        :rtype: None
        """

        if self.dummy_mode:
            if self.address is None:
                self.dummy_data = {0: [range(255)]}
            self.interface_connected = True
            return

        if self.address is None:
            address = 1
        else:
            address = self.address

        self.handle = SMBus(address)
        self.connections_info['handle'] = self.handle.fd
        self.connections_info['i2c_functions'] = self.handle.funcs
        self.interface_connected = True

    def read(self, device_address, memory_address, burst_size=1):
        """
        Read data from raspberry pi I2C

        :param device_address: i2c bus address of DUT
        :type device_address: int
        :param memory_address: address to start writing to
        :type memory_address: int
        :param burst_size: number of bytes to read
        :type burst_size: int
        :return: byte(s)
        :rtype: Union(int, list)
        """
        if self.dummy_mode:
            if burst_size > 1:
                return self.dummy_data[memory_address]
            else:
                return list(self.dummy_data[memory_address:memory_address+burst_size])
        dev_id = int(device_address / 2)

        # if 2 bytes of address, burst write the 2 bytes of address, then current address read each byte
        if self.memory_address_length == 2:
            mem_array = self._create_memory_array(memory_address)
            self.handle.write_i2c_block_data(dev_id, mem_array[0], [mem_array[1]])
            if burst_size > 1:
                return_data = []
                for i in range(burst_size):
                    return_data.append(self.handle.read_byte(dev_id))
                return return_data
            else:
                return self.handle.read_byte(dev_id)
        else:
            try:
                return_data = self.handle.read_i2c_block_data(dev_id, memory_address, burst_size)  # watch out!
                # returning a list!!
            except OSError:  # occational error - wait for ack should fix it,
                self.logger.warn("OSError in i2c read")
                self.wait_for_ack(device_address)
                # now try again
                return_data = self.handle.read_i2c_block_data(dev_id, memory_address, burst_size)

            if burst_size > 1:
                return return_data
            else:
                return return_data[0]

    def reset(self):
        pass

    def write(self, device_address, memory_address, data):
        """
        Write data to raspberry pi I2C

        :param device_address: i2c bus address of DUT
        :type device_address: int
        :param memory_address: address to start writing to
        :type memory_address: int
        :param data: data to write
        :type data: Union(int, list, tuple)
        """
        if self.dummy_mode:
            self.dummy_data[device_address][memory_address] = data
            return

        dev_id = int(device_address / 2)  # divide by 2 to remove read/write bit
        # check that data is an array of integers with max size = 255
        # if a list of bytes is passed to us, write block data,
        if isinstance(data, int):
            vals = [data, ]
        elif isinstance(data[0], tuple) or isinstance(data[0], list):
            vals = data[0]
        else:
            vals = data

        # if memory address is 2 bytes long,
        # make msb of address the new "memory_adderss"
        # and lsb the first byte of data on the wire (vals)
        if self.memory_address_length == 2:
            memory_array = self._create_memory_array(memory_address)
            memory_address = memory_array[0]
            vals.insert(0, memory_array[1])

        self.handle.write_i2c_block_data(dev_id, memory_address, vals)
        if self.eeprom_backed:
            self.wait_for_ack(dev_id)

    def wait_for_ack(self, dev_id, timeout=1):
        """
        wait until device responds. timeout

        :param dev_id: device to reach (pure i2c address without read/write bit
        :type dev_id: int
        :param timeout: amount of time to wait for
        :type timeout: int
        """
        dev_id = int(dev_id/2)
        t_end = time.time()+timeout           # define time period
        ack = False
        while time.time() < t_end:            # while we have not timed out
            try:                              # try do a single byte write
                self.handle.write_byte(dev_id, 0)
                ack = True                    # if we succeed, flag an ACK
                break                         # and exit the while loop
            except IOError:                   # if we get an IOerror, means a NACk was received
                ack = False                   # so set the ack flag false
        if not ack:                           # if the flag is not set when we exit
            # raise IOerror ourselves
            raise IOError("device 0x{0:02X} failed to ACK within 1 second".format(dev_id))

    def _create_memory_array(self, memory_address):
        memory_array = []
        for i in range(self.memory_address_length):
            memory_array.append((memory_address >> ((self.memory_address_length-1-i)*8)) & 0xff)
        return memory_array
