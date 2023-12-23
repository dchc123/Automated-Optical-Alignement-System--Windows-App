"""
| $Revision:: 278959                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-09 15:58:04 -0400 (Mon, 09 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Top level bench functionality
"""
import logging
from COMMON.Device.Base.base_device import BaseDevice
from COMMON.Equipment.Base.base_equipment import BaseEquipment
from COMMON.Interfaces.USBtoI2C.i2c_win32 import Usb2I2c


class BaseBench:
    """
    All benches are derived from this class
    """
    def __init__(self, dummy_mode, name=None):
        """
        Initialize instance

        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param name: driver name that defaults to class name
        :type name: str
        """
        # if a name isn't supplied, use class definition name
        if name is not None:
            self._name = name
        else:
            self._name = type(self).__name__

        self._resource_connected = {}
        self.connected = False
        self.dummy_mode = dummy_mode
        self.logger = logging.getLogger(self.name)

    @property
    def identity(self):
        variables = vars(self)
        identities = {}
        for key, value in variables.items():
            if isinstance(value, (BaseDevice, BaseEquipment)):
                identities[key] = {'name': value.name, **value.identity}

        return identities

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

    def add_resource(self, name, object_):
        """
        Add resource to bench dynamically.

        :param name: handle to use when referencing inside bench instance
        :type name: str
        :param object_: object instance to be added
        :type object_: Any
        """
        setattr(self, name, object_)

    def aliases(self):
        """
        VIRTUAL FUNCTION
        Users can create aliases for resources or their sub-components.
        Automatically called by connect after all resources have been connected.
        Must be used when aliasing sub-components of dynamic resources
        """
        pass

    def connect(self):
        """
        Connect to all attached resources
        """
        dongles = {}
        equipment = {}
        devices = {}

        for key, value in vars(self).items():
            if isinstance(value, Usb2I2c):
                dongles[key] = value
            elif isinstance(value, BaseDevice):
                devices[key] = value
            elif isinstance(value, BaseEquipment):
                equipment[key] = value

        for key, value in equipment.items():
            if value not in self._resource_connected or self._resource_connected[value] is False:
                self.logger.info(f"Connecting {key}({value.name})")
                value.connect()
                self._resource_connected[value] = True

        for key, value in dongles.items():
            if value not in self._resource_connected or self._resource_connected[value] is False:
                self.logger.info(f"Opening {key}({value.name})")
                value.open()
                self._resource_connected[value] = True

        for key, value in devices.items():
            if value not in self._resource_connected or self._resource_connected[value] is False:
                self.logger.info(f"Connecting {key}({value.name})")
                try:
                    value.connect()
                    self._resource_connected[value] = True
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.warning(f"Could not connect to device '{value.name}'. It may need to be powered up")
                    self._resource_connected[value] = False

        self.connected = True
        self.aliases()

    def disconnect(self):
        """
        Disconnect all attached resources
        """
        dongles = {}
        resources = {}

        for key, value in vars(self).items():
            if isinstance(value, Usb2I2c):
                dongles[key] = value
            elif isinstance(value, (BaseDevice, BaseEquipment)):
                resources[key] = value

        for key, value in dongles.items():
            if value not in self._resource_connected or self._resource_connected[value] is True:
                self.logger.info(f"Closing {key}({value.name})")
                value.close()
                self._resource_connected[value] = False

        for key, value in resources.items():
            if value not in self._resource_connected or self._resource_connected[value] is True:
                self.logger.info(f"Disconnecting {key}({value.name})")
                value.disconnect()
                self._resource_connected[value] = False

        self.connected = False
