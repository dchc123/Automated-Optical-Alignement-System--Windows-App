"""
| $Revision:: 282333                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-09-12 20:40:14 +0100 (Wed, 12 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from abc import ABC
from abc import abstractmethod
import logging
from COMMON.Utilities.logging_ext import create_stream_handler


class _InterfaceCommon(ABC):
    """
    Base Equipment Interface from which all equipment interface should be derived from
    """
    def __init__(self, name=None, **kwargs):
        """
        Initialize instance

        :param name: communication interface name
        :type name: str
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        # error check for unused key word arguments
        if len(kwargs) > 0:
            raise RuntimeWarning("Unused keyword arguments at most base class: {}".format(kwargs))
        super().__init__()

        # if a name isn't supplied, use class definition name
        if name:
            self._name = name
        else:
            self._name = type(self).__name__

        # assign a standard logger to each item using device name
        # TODO: [sfarsi] multiple objects with same name, will tunnel to same logger!
        self.logger = logging.getLogger(self.name)
        create_stream_handler()

    @property
    def name(self):
        """
        :value: object name
        :type: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        :type value: str
        """
        self._name = value
        self.logger.name = value  # Update object's logger name to match object name


class InterfaceGPIO(_InterfaceCommon):
    """
    Small container class for a single GPIO and its properties
    """
    def __init__(self, index, **kwargs):
        """
        Initialize instance

        :param index: GPIO index
        :type index: int
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super(_InterfaceCommon).__init__(**kwargs)
        self.index = index

    @property
    @abstractmethod
    def mode(self):
        """
        :value: - 'INPUT'
                - 'OUTPUT'
                - 'OPEN_DRAIN'
        :type: str
        """
        pass

    @mode.setter
    @abstractmethod
    def mode(self, value):
        """
        :type value: str
        """
        pass

    @property
    @abstractmethod
    def value(self):
        """
        :value: - 'LOW'
                - 'HIGH'
        :type: str
        :raise RuntimeError: if setting value while not in output mode
        :raise RuntimeError: if reading value while not in input mode
        """
        pass

    @value.setter
    @abstractmethod
    def value(self, value):
        """
        :type value: str
        """
        pass


class BaseDeviceInterface(_InterfaceCommon):
    """
    Base Device Interface from which all device interface should be derived from
    """
    CAPABILITY = {
        'buffer_size': 32,
        'gpio_number': 10,
        'gpio_voltage_level': {'min': 0.8, 'max': 5.0},
        'interface_type': ['I2C', 'SPI'],
        'interface_mode': {
            'I2C': ['STANDARD', 'FAST', 'FAST_PLUS','HIGH_SPEED'],
            'SPI': ['CPOL0_CPHA0', 'CPOL0_CPHA1', 'CPOL1_CPHA0', 'CPOL1_CPHA1']
        },
        'interface_speed': {
            'I2C': {'min': 100, 'max': 400},
            'SPI': {'min': 1000, 'max': 10000}
        },
    }

    def __init__(self, address=None, **kwargs):
        """
        Initialize instance

        :param address: communication interface address
        :type address: int
        :param gpio_voltage_level: GPIO voltage level
        :type gpio_voltage_level: float
        :param interface_type: see :py:attr:`BaseDeviceInterface.interface_type` for description
        :type interface_type: str
        :param interface_mode: see :py:attr:`BaseDeviceInterface.interface_mode` for description
        :type interface_mode: str
        :param interface_speed: interface speed in kHz (independent of type)
        :type interface_speed: int
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(**kwargs)
        self.address = address
        self.interface_connected = False
        self._interface_type = None
        self._interface_speed = None

    @property
    @abstractmethod
    def gpio_voltage_level(self):
        """
        :value: GPIO voltage level
        :type: float
        :raise ValueError: for out of range voltage level
        """
        pass

    @gpio_voltage_level.setter
    @abstractmethod
    def gpio_voltage_level(self, value):
        """
        :type value: float
        """
        pass

    @property
    @abstractmethod
    def identity(self):
        """
        READONLY

        :return: interface identity details
        :rtype: str or dict
        """
        pass

    @property
    @abstractmethod
    def interface_mode(self):
        """
        Interface mode is dependant on type. See
        :py:attr:`BaseDeviceInterface.interface_type`

        :value: For I2C interface

         - 'STANDARD'
         - 'FAST'
         - 'FAST_PLUS'
         - 'HIGH_SPEED'

         For SPI interface

         - 'CPOL0_CPHA0'
         - 'CPOL0_CPHA1'
         - 'CPOL1_CPHA0'
         - 'CPOL1_CPHA1'
        :type: str
        :raise ValueError: invalid interface type
        """
        return

    @interface_mode.setter
    @abstractmethod
    def interface_mode(self, value):
        """
        :type value: str
        :raise ValueError: invalid interface type
        """
        pass

    @property
    @abstractmethod
    def interface_type(self):
        """
        Interface type if options available

        :value: - 'I2C'
                - 'SPI'
        :type: str
        :raise ValueError: invalid interface type
        """
        pass

    @interface_type.setter
    @abstractmethod
    def interface_type(self, value):
        """
        :type value: str
        :raise ValueError: invalid interface type
        """
        pass

    @property
    @abstractmethod
    def interface_speed(self):
        """
        :value: interface speed in kHz (independent of type)
        :type: int
        :raise ValueError: invalid interface speed value
        """
        pass

    @interface_speed.setter
    @abstractmethod
    def interface_speed(self, value):
        """
        :type value: int
        :raise ValueError: invalid interface speed value
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close interface connection.
        """
        pass

    @abstractmethod
    def open(self, address=None):
        """
        Opens interface connection.
        """
        pass

    @abstractmethod
    def read(self, device_address, memory_address, burst_size=None):
        """
        Read data form given memory address. If burst size is given, then a burst
        read will be performed.

        :param device_address: device address on the bus
        :type device_address: int or str
        :param memory_address: location of data to be read
        :type memory_address: int
        :param burst_size: number of continuous memory locations to read
        :type burst_size: int
        :return: read data; int for single read, or a list of int for a burst read
        :rtype: int or list of int
        :raise ValueError: invalid memory address
        :raise RuntimeError: failed to read
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Perform hard reset of connected device
        """
        pass

    @abstractmethod
    def write(self, device_address, memory_address, data):
        """
        Write data to given memory address. If data supplied is a list, then a burst
        write operation is performed

        :param device_address: device address on the bus
        :type device_address: int or str
        :param memory_address: location of data to be written
        :type memory_address: int
        :param data: data to write; int for single write, or a list of int for a burst write
        :type data: int or list of int
        :raise ValueError: invalid memory address
        :raise RuntimeError: failed to write
        """
        pass
