"""

"""
from __future__ import absolute_import, division, print_function, unicode_literals  # for python 3 compatibility
import ctypes
import time

from COMMON.Interfaces.Base.base_device_interface import BaseDeviceInterface
from COMMON.Utilities.cli_path import resolve_file_path

VENDORID = 4292
PRODUCTID = 34006


class Usb2I2c(BaseDeviceInterface):
    """
    USB 2 I2C dongle driver interface
    """
    DLL_PATH = r'Interfaces\USBtoI2C\USBtoI2C.dll'
    dll = None
    connections_info = {}
    connected_dongles = {}

    ERROR_CODES = {
        -10: 'HANDLE_ERROR',
        -9:  'INVALID_BUS_SPEED',
        -8:  'INVALID_BUFFER_SIZE',
        -7:  'INVALID_ADDRESS',
        -6:  'INVALID_DEVICE',
        -5:  'NOT_CONNECTED',
        -4:  'INVALID_BUS_STATUS',
        -3:  'NOT_ACK',
        -2:  'INVALID_CMD',
        -1:  'ARBLOST_ERROR',
        0:   'TIMEDOUT',
        1:   'SUCCESS',
    }
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

    VENDORID = 4292
    PRODUCTID = 34006

    def __init__(self, address=None, dummy_mode=False, **kwargs):
        """
        Initialise instance

        :param address: communication interface address
        :type address: int
        :param dummy_mode: used for testing when there is no dongle connected
        :type dummy_mode: boolean
        """
        super().__init__(address=address, **kwargs)
        self.handle = None
        self.path = None
        self.address = address
        self.dummy_mode = dummy_mode
        self.dummy_data = {}
        self.memory_address_length = 1

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def identity(self):
        """
        **READONLY**

        :return: interface identity details
        :rtype: str or dict
        """
        return self.connections_info

    def close(self):
        if self.dummy_mode:
            self.interface_connected = False
            return

        if self.interface_connected:
            # Connected_USB seems always to return true... despite what the manual says
            if self.dll.Connected_USB(self.connections_info['handle']):
                self.dll.Disconnect_USB(self.connections_info['handle'])
                self.interface_connected = False
                self.connections_info['connected'] = False
                self.clear_dll()
            else:
                self.logger.info('Attempted to close a connection where dll reports connection closed')
        else:
            self.logger.info('Attempted to close a connection that is already closed')

    @classmethod
    def load_dll(cls):
        """
        Loads the dll
        """
        if cls.dll is None:
            cls.dll = ctypes.CDLL(resolve_file_path(cls.DLL_PATH))

    @classmethod
    def clear_dll(cls):
        """
        Destroy an instance of the DLL and free all associated memory
        """
        if cls.dll:
            if cls.connections_info['handle']:
                if cls.dll.Connected_USB(cls.connections_info['handle']):
                    raise RuntimeError('Tried to destroy DLL instance without closing the connection')
                cls.dll.DestroyMe_USB(cls.connections_info['handle'])
                cls.connections_info = {}
                cls.dll = None
            else:
                raise RuntimeError('Tried to destroy DLL instance without a handle!')
        else:
            raise RuntimeError('Tried to destroy DLL instance without loading dll!')

    @classmethod
    def scan(cls):
        """
        Scans for available usb 2 I2C dongles

        :return: connections_info
        :rtype: dict
        """
        if cls.dll is None:
            cls.load_dll()

        # clear out current connections info
        cls.connections_info = dict(number_of_dongles=0, serial_numbers=[], index=None, handle=None, connected=False)
        cls.connections_info['handle'] = cls.dll.CreateMe_USB()
        dongles = cls.dll.EnumeratesDevices_USB(cls.connections_info['handle'], cls.VENDORID, cls.PRODUCTID)
        if dongles == 0:
            raise IOError('No USBtoI2C dongles connected - Check power and USB connection?')
        if dongles > 1:
            print('{} dongles were found - using 1st dongle'.format(dongles))
        cls.connections_info.update({'number_of_dongles': dongles})
        dongle_list = range(dongles)
        l_cint = (ctypes.c_int * dongles)(*dongle_list)
        ret_val = cls.dll.ListDevices_USB(cls.connections_info['handle'], dongles, l_cint)
        if ret_val < 0:
            raise RuntimeError(f'failed to scan to dongle index {cls.connections_info["handle"]}. Returned {ret_val} - '
                               f'{cls.ERROR_CODES[ret_val]}')
        cls.connections_info.update({'serial_numbers': list(l_cint)})
        return cls.connections_info

    def open(self, address=None):
        """
        opens interface connection
        Address has no effect

        :return: None
        :rtype: NoneType
        """
        if self.dummy_mode:
            if self.address is None:
                self.dummy_data = {0: [range(255)]}
            self.interface_connected = True
            return

        if self.dll is None:
            self.load_dll()

        # If the connections dict is empty: meaning self.scan() was never called
        if not self.connections_info:
            self.scan()

        # If there are less than 1
        if not self.connections_info['number_of_dongles']:
            self.logger.info('Rescanning for available dongle connections')
            self.scan()

        if self.address is None:
            address = 0
        else:
            address = self.address

        return_val = self.dll.Connect_USB(self.connections_info['handle'], address)

        if return_val > 0:
            self.connections_info['connected'] = True
            self.connections_info['index'] = address
            # TODO record connected dongle in self.connected_dongles?
            self.interface_connected = True
        else:
            self.connections_info['connected'] = False
            self.connections_info['index'] = None
            raise RuntimeError('failed to connect to dongle index {}. Returned {} - {}'
                               .format(address, return_val, self.ERROR_CODES[return_val]))

    def read(self, device_address, memory_address, burst_size=1):
        """
        Read data from given memory address. If burst size is given then a burst read will be performed

        :param device_address: device address on the bus
        :type device_address: int
        :param memory_address: location of data to be read
        :type memory_address: int
        :param burst_size: number of bytes to be read
        :type burst_size: int
        :return: return_data: int for single read, list of int for a burst read
        :rtype: int or list of ints
        :raise ValueError: invalid memory address
        :raise RuntimeError: failed to read
        """
        if self.dummy_mode:
            return self.dummy_data

        if device_address is None:
            raise TypeError('Please specify a device_address when performing a read')

        if not self.interface_connected:
            self.logger.warning('Attempting to read without opening a connection with the dongle. '
                                'Connecting to dongle at index 0...')
            self.open()

        return_data: list = self._i2c_read(memory_address=memory_address, device_address=device_address,
                                           length=burst_size)
        if burst_size > 1:
            return return_data
        else:
            return return_data[0]

    def write(self, device_address, memory_address, data):
        """
        write data to given memory address. If data supplied is a list, then a burst
        write operation is performed

        :param device_address: device address on the bus
        :type device_address: int
        :param memory_address: location of data to be written
        :type memory_address: int
        :param data:
        :type data: int for single write, or a list of int for a burst write
        :return:
        :rtype:
        """
        if device_address is None:
            raise TypeError('Please specify a device_address when performing a write.')

        if not self.interface_connected:
            self.logger.warning('Attempting to write without opening a connection with the dongle. '
                                'Connecting to dongle at index 0...')
            self.open()

        """ 
        Use no_ack version of write because PageWrite_USB locks the driver up with a permanent timeout if it is 
        closed when device is no_ack'ing...
        """
        self._i2c_write_no_ack(device_address=device_address, memory_address=memory_address, data=data)

    def _i2c_write(self, device_address, memory_address, data):
        """
        Uses PageWrite_USB, which checks for ack after a write but can lock up if the write nacks and the device is
        closed. All calls return a timeout, even when application is fully closed then full open again...
        Requires the usb2I2C to be power cycled or physically unplugged then plugged back in.

        :param device_address: I2C device address (
        :type device_address: int
        :param memory_address: register map address
        :type memory_address: int
        :param data: data to be written to device. list if more than one byte, integer 0-255 if one byte
        :type data: list or int
        :return: Nothing
        :rtype: None
        """
        length = 1  # default to 1 byte
        if data is not None:
            if isinstance(data, int):
                data = [data]   # convert single write to simplify write logic
            length = len(data)  # update length for write

        current_memory_address = memory_address
        # initialise a ctypes C_ubyte array of length of the data passed to it, with the values pre populated
        data_to_write = (ctypes.c_ubyte * length)(*data)
        ret_val = self.dll.PageWrite_USB(self.connections_info['handle'], device_address, current_memory_address,
                                         length, ctypes.byref(data_to_write))
        if ret_val < 1:
            raise IOError('failed to write to device {}: Error number: {} - {}'.format(device_address, ret_val,
                                                                                       self.ERROR_CODES[ret_val]))

    def _i2c_write_no_ack(self, device_address, memory_address, data):
        """
        Writes to I2c device in maximum blocks of 8 bytes, with fixed time waits in the firmware between writes

        :param device_address: I2C device address (
        :type device_address: int
        :param memory_address: register map address
        :type memory_address: int
        :param data: data to be written to device. list if more than one byte, integer 0-255 if one byte
        :type data: list or int
        :return: Nothing
        :rtype: None
        """

        length = 1  # default to 1 byte
        if data is not None:
            if isinstance(data, int):
                data = [data]   # convert single write to simplify write logic
            length = len(data)  # update length for write

        if self.dummy_mode:
            self.dummy_data[device_address][memory_address] = data
            return

        current_memory_address = memory_address
        while length > 0:
            partial_length = self.CAPABILITY['buffer_size'] if length > self.CAPABILITY['buffer_size'] else length

            partial_data = data[:partial_length]

            # initialise a ctypes C_ubyte array of length of the data passed to it, with the values pre populated
            data_to_write = (ctypes.c_ubyte * partial_length)(*partial_data)
            if self.memory_address_length == 1:
                ret_val = self.dll.Write1_USB(self.connections_info['handle'], device_address, current_memory_address,
                                              partial_length, ctypes.byref(data_to_write))
            elif self.memory_address_length == 2:
                ret_val = self.dll.Write2_USB(self.connections_info['handle'], device_address, current_memory_address,
                                              partial_length, ctypes.byref(data_to_write))
            else:
                ret_val = -7

            if ret_val < 1:
                raise IOError('failed to write to device {}: Error number: {} - {}'.format(device_address, ret_val,
                                                                                           self.ERROR_CODES[ret_val]))

            # Prep for next iteration
            length = length - partial_length
            if length <= 0:
                break
            if data is not None:
                data = data[partial_length:]
            current_memory_address += partial_length

    def _i2c_read(self, device_address, memory_address, length=1):
        """

        :param device_address:
        :type device_address: int
        :param memory_address:
        :type memory_address: int
        :param length:
        :type length: int
        :return:
        :rtype: list of int
        """
        if self.dummy_mode:
            return list(self.dummy_data)
        data_out = (ctypes.c_ubyte * length)(*list())
        if self.memory_address_length == 1:
            ret_val = self.dll.Read1_USB(self.connections_info['handle'], device_address, memory_address, length,
                                         ctypes.byref(data_out))
        elif self.memory_address_length == 2:
            ret_val = self.dll.Read2_USB(self.connections_info['handle'], device_address, memory_address, length,
                                         ctypes.byref(data_out))
        else:
            ret_val = -7

        if ret_val < 1:
            raise RuntimeError('error reading from device {}. error code: {} - {}'.format(device_address, ret_val,
                                                                                          self.ERROR_CODES[ret_val]))

        return list(data_out)

    def reset(self):
        """
        This sends a bus reset signal to all the devices on the bus. This is a start signal followed by 9 clock
        pulses followed by a restart then a stop signal.s reset signal to all the devices on the bus. This is a start
        signal followed by 9 clock pulses followed by a restart then a stop signal.

        :return: USB2 I2C return status
        :rtype:  int
        """
        if self.dummy_mode:
            return 1

        ret_val = self.dll.Reset_USB()
        if ret_val < 1:
            self.logger.warning('Reset_USB returned error: {} - {}'.format(ret_val, self.ERROR_CODES[ret_val]))

        return ret_val

    @property
    def interface_speed(self):
        """

        :return:
        :rtype:
        """
        return self._interface_speed

    @interface_speed.setter
    def interface_speed(self, value=400):
        """
        The sets the bus clock speed in Hertz (Hz). The valid range of bus speeds is 20Hz to 400Hz

        :param value: clock speed value
        :type value: int
        :return:
        :rtype:
        """
        if value < 20 or value > 400:
            raise ValueError("{} is an invalid bus speed. Valid i2c bus speed is between 20(kHz) and 400(kHz)".format(
                    value))
        return_value = self.dll.SetBusSpeed_USB(self.connections_info['handle'], value)
        if return_value < 1:
            raise IOError("error {} setting bus speed: {}".format(return_value, self.ERROR_CODES[return_value]))
        else:
            self._interface_speed = value

    @property
    def gpio_voltage_level(self):
        raise NotImplementedError

    @property
    def interface_mode(self):
        raise NotImplementedError

    @property
    def interface_type(self):
        raise NotImplementedError

    def wait_for_ack(self, dev_id, timeout=1):
        """
        wait until device responds. timeout

        :param dev_id: device to reach (pure i2c address without read/write bit
        :type dev_id: int
        :param timeout: amount of time to wait for
        :type timeout: int
        """
        # dev_id = int(dev_id/2)
        t_end = time.time()+timeout           # define time period
        ack = False
        while time.time() < t_end:            # while we have not timed out
            try:                              # try do a single byte write
                self._i2c_read(dev_id, 0)
                ack = True                    # if we succeed, flag an ACK
                break                         # and exit the while loop
            except IOError:                   # if we get an IOerror, means a NACk was received
                ack = False                   # so set the ack flag false
        if not ack:                           # if the flag is not set when we exit
            # raise IOerror ourselves
            raise IOError("device 0x{0:02X} failed to ACK within 1 second".format(dev_id))
