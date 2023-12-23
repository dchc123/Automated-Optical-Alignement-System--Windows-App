"""
| $Revision:: 283282                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-10-30 13:35:10 +0000 (Tue, 30 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
import logging
import time
from abc import ABC, abstractmethod
from COMMON.Utilities.custom_exceptions import NotSupportedError
from COMMON.Utilities.logging_ext import create_stream_handler
from COMMON.Interfaces.Base.base_device_interface import BaseDeviceInterface


class BaseDeviceCommon(ABC):
    """
    Common equipment attributes
    """
    def __init__(self, device_address, interface, dummy_mode, name=None, **kwargs):
        """
        Initialize instance

        :param device_address: address of the device
        :type device_address: int or str
        :param interface: communication interface
        :type interface: BaseDeviceInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param name: driver name that defaults to class name
        :type name: str
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        # error check for unused key word arguments
        if len(kwargs) > 0:
            raise RuntimeWarning("Unused keyword arguments at most base class: {}".format(kwargs))
        super().__init__()

        self._device_address = device_address
        self._interface = interface
        """:type: BaseDeviceInterface"""

        # if a name isn't supplied, use class definition name
        if name:
            self._name = name
        else:
            self._name = type(self).__name__

        self.dummy_mode = dummy_mode

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

    @property
    def device_address(self):
        """
        :return: address of the device
        :rtype: int or str
        """
        return self._device_address

    @device_address.setter
    def device_address(self, value):
        """
        :param value: address of the device
        :type value: int or str
        """
        if isinstance(value, str) or isinstance(value, int):
            self._device_address = value
        else:
            raise TypeError('device_address type must be either a str or an int!')

    def sleep(self, seconds):
        """
        Delay execution for a given number of seconds. Skipped if in dummy more.
        The argument may be a floating point number for subsecond precision

        :param seconds: time to sleep
        :type seconds: int or float
        """
        if not self.dummy_mode:
            self.logger.debug("Sleeping for {} seconds".format(seconds))
            time.sleep(seconds)
        else:
            self.logger.debug("DUMMY MODE: Skipping sleep for {} seconds".format(seconds))


class BaseDevice(BaseDeviceCommon):
    """
    All device drivers are derived from this class. It contains all base method prototypes
    that must be implemented by all device drivers
    """
    def __init__(self, device_address, interface_address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param device_address: optional address for destination device
        :type device_address: int or str
        :param interface_address: communication interface address
        :type interface_address: int
        :param interface: communication interface
        :type interface: BaseDeviceInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(device_address=device_address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._interface_address = interface_address
        self._configured = False
        self._dummy_mode_dict = {}

    @property
    @abstractmethod
    def hardware(self):
        """
        **READONLY**

        :value: hardware version
        :type: int
        """
        pass

    @property
    def identity(self):
        """
        **READONLY**
        Retrieve device identity

        :value: - serialization info: lot, wafer, row, column
                - hardware version
                - firmware version if applicable
        :type: dict
        """
        data = {}

        try:
            data['hardware'] = self.hardware
        except (NotImplementedError, NotSupportedError):
            pass

        try:
            data['serial'] = self.serial
        except (NotImplementedError, NotSupportedError):
            pass

        return data

    @property
    @abstractmethod
    def serial(self):
        """
        **READONLY**

        :value: serialization info: lot, wafer, row, column
        :type: dict
        """
        pass

    def _configure(self):
        """
        INTERNAL, VIRTUAL
        Perform driver configuration, such as selecting register map based on hardware rev
        """
        pass

    def _configure_interface(self):
        """
        INTERNAL, VIRTUAL
        Configure the interface for this driver
        """
        pass

    def connect(self):
        """
        Connect through interface
        """
        # self._unblock_setattr()
        if not self.dummy_mode and not self._interface.interface_connected:
            if self._interface is None:
                raise RuntimeError("Missing communication interface")
            self._interface.open(address=self._interface_address)
            self._configure_interface()
        if not self._configured:
            self._configure()
            self._configured = True
        # self._block_setattr()

    def disconnect(self):
        """
        Disconnect interface
        """
        if not self.dummy_mode and self._interface.interface_connected:
            self._interface.close()

    def read(self, address, length=1):
        """
        Generic method for reads form interface

        :param address: location of data to be read
        :type address: int
        :param length: number of continuous memory locations to read
        :type length: int
        :return:
        :rtype: int or list of int
        """
        if not self.dummy_mode:
            data = self._interface.read(self.device_address, address, length)
        else:
            data = []
            for key in range(address, address+length):
                if str(key) in self._dummy_mode_dict:
                    data.append(self._dummy_mode_dict[str(key)])
                else:
                    data.append(1)
            if len(data) == 1:
                data = data[0]

        return data

    def reset(self):
        """
        Hard reset of device through dongle interface
        """
        if not self.dummy_mode:
            self._interface.reset()

    def write(self, address, data):
        """
        Generic method for writes to interface

        :param address: location of data to be read
        :type address: int
        :param data: data to write; int for single write, or a list of int for a burst write
        :type data: int or list of int
        """
        if not self.dummy_mode:
                self._interface.write(self.device_address, address, data)
        else:
            if isinstance(data, int):
                data = [data]
            for key, value in zip(range(address, address+len(data)), data):
                self._dummy_mode_dict[str(key)] = value


class BaseDeviceBlock(BaseDeviceCommon):
    """
    All device driver blocks are derived from this class. It contains all base method prototypes
    that must be implemented by all device drivers
    """
    def __init__(self, interface, csr, dummy_mode, device_address=None, **kwargs):
        """
        Initialize instance

        :param interface: communication interface
        :type interface: BaseDeviceInterface
        :param csr: CSR container for named parameter/register access
        :type csr: BaseCSR
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param device_address: address of the device
        :type device_address: int or str
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(device_address=device_address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.csr = csr
