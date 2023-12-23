"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Equipment.Base.base_equipment import BaseEquipmentBlock
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_exceptions import NotSupportedError
from COMMON.Utilities.custom_structures import CustomList
from ..base_power_supply import BasePowerSupply
from ..base_power_supply import BasePowerSupplyChannel
from ..base_power_supply import BasePowerSupplyVoltBlock
from ..base_power_supply import BasePowerSupplyCurrBlock


class _KeysightE36XXXMemory(BaseEquipmentBlock):
    """
    Simple container for information meant to be retained Stored in a class so that it can
    be passed by reference.
    """
    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel = None

    @property
    def channel(self):
        """
        Select output channel

        :value: channel number
        :type: int
        """
        if self._channel is None:
            self._channel = int(self._read("INSTrument:NSELect?"))
        return self._channel

    @channel.setter
    def channel(self, value):
        """
        :type value: int
        """
        if value != self._channel:
            self._write("INSTrument:NSELect %d" % value)
            self._channel = value


class KeysightE36XXX(BasePowerSupply):
    """
    Keysight E36XXX common power supply driver.
    """
    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of KeysightE36XXXChannel"""

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        super()._configure_interface()
        self._interface.stb_polling_supported = False

    @property
    def global_output(self):
        """
        Enable state of the global output state. This is a single global setting that
        supersedes all output states of channel class
        :py:attr:`Equipment.base_power_supply.BasePowerSupplyChannel.output`

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read(':OUTPut?', dummy_data='0').strip()]

    @global_output.setter
    def global_output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTPut %s" % input_dict[value])


class KeysightE36XXXChannel(BasePowerSupplyChannel):
    """
    Keysight E36XXX Common Channel
    """
    CAPABILITY = {'4_wire_sensing': False, 'precision': False}

    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param memory: shared memory container for all sub-blocks
        :type memory: _KeysightE36XXXMemory
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._memory = memory
        self.voltage = None
        """:type: KeysightE36XXXVoltBlock"""
        self.current = None
        """:type: KeysightE36XXXCurrBlock"""

    @property
    def output(self):
        """
        Enable state of the channel output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        self._memory.channel = self._channel_number
        return output_dict[self._read('OUTPut?', dummy_data='0').strip()]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        self._memory.channel = self._channel_number
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("OUTPut %s" % input_dict[value])

    @property
    def power(self):
        """
        READONLY

        :value: measured power in W
        :type: float
        """
        self._memory.channel = self._channel_number
        voltage = float(self._read("MEASure:VOLTage?"))
        current = float(self._read("MEASure:CURRent?"))
        power = voltage * current
        return power


class KeysightE36XXXVoltBlock(BasePowerSupplyVoltBlock):
    """
    Keysight E36XXX voltage sub block
    """

    CAPABILITY = {'voltage': {'min': None, 'max': None}}

    def __init__(self, channel_number, range_values, range_threshold, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param range_values: range values to use for error checking and range change
        :type range_values: dict
        :param range_threshold: voltage range threshold
        :type range_threshold: float
        :param memory: shared memory container for all sub-blocks
        :type memory: _KeysightE36XXXMemory
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._memory = memory
        self._range_threshold = range_threshold
        self._range_values = range_values

    @property
    def _range(self):
        """
        :value: Voltage Range
        :type: str
        :raise ValueError:
        """

        return self._read("VOLTage:RANGe?")

    @_range.setter
    def _range(self, value):
        """
        :type value: str
        :raise ValueError: error if
        """

        value = value.upper()
        prev_range = self._range
        if value not in self._range_values["ALL"]:
            raise ValueError('Please specify either %s' % self._range_values["ALL"])
        # XOR logic to compare old and new range values
        elif (value not in self._range_values["HIGH"]) != (prev_range not in self._range_values["HIGH"]):
            self._write("VOLTage:RANGe %s" % value)
            if prev_range in self._range_values["LOW"]:
                # Changing from low voltage range to High limits the current setpoint to current threshold
                self.logger.warning("Voltage range automatically changed. Current is set to %2.3fA"
                                    % float(self._read("CURRent?")))
            else:
                self.logger.warning("Voltage range automatically changed.")
        else:
            pass

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous voltage in V
        :type: float
        """
        self._memory.channel = self._channel_number
        return float(self._read("MEAS:VOLTage?"))

    @property
    def protection_level(self):
        """
        :value: Voltage protection level
        :type: float
        """
        self._memory.channel = self._channel_number
        return float(self._read("VOLTage:PROTection:LEVel?"))

    @protection_level.setter
    def protection_level(self, value):
        """
        :type value: float
        """
        self._memory.channel = self._channel_number
        self._write("VOLTage:PROTection:LEVel %s" % value)

    @property
    def ovp(self):
        """
        Voltage protection state

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        self._memory.channel = self._channel_number
        return output_dict[self._read('VOLTage:PROTection:STATe?', dummy_data='0').strip()]

    @ovp.setter
    def ovp(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        self._memory.channel = self._channel_number
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("VOLTage:PROTection:STATe %s" % input_dict[value])

    @property
    def protection_tripped(self):
        """
        **READONLY**
        Over voltage protection. Returns True if protection is tripped

        :value: ovp tripped
        :type: bool
        """

        return bool(int(self._read("VOLTage:PROTection:TRIPped?", dummy_type="int")))

    @property
    def setpoint(self):
        """
        :value: voltage level setting in V
        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        self._memory.channel = self._channel_number
        return float(self._read("VOLTage?"))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        self._memory.channel = self._channel_number

        range_min = self.CAPABILITY['voltage']['min']
        range_max = self.CAPABILITY['voltage']['max']

        if value < range_min or value > range_max:
            raise ValueError("%s is an invalid setpoint. See supported setpoint range. (min:%s|max:%s)"
                             % (value, range_min, range_max))

        if value > self._range_threshold:
            self._range = "HIGH"
        else:
            self._range = "LOW"

        self._write("VOLTage %s" % value)

        if self.protection_tripped and not self.dummy_mode:
            self.logger.warning('Over voltage protection is tripped. Please clear condition generating the issue, '
                                'then clear protection flag.')

    def clear_protection(self):
        """
        Clears the protection status triggered by an over voltage protection.
        Condition generating the fault must be removed in order for clear to take effect.
        """

        self._write("VOLTage:PROTection:CLEar")

        if self.protection_tripped:
            self.logger.warning('Condition generating the issue has not been addressed. Please address condition, then '
                                'clear protection flag.')


class KeysightE36XXXCurrBlock(BasePowerSupplyCurrBlock):
    """
    Keysight E36XXX current sub block
    """

    CAPABILITY = {'current': {'min': None, 'max': None}}

    def __init__(self, channel_number, range_values, range_threshold, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param range_values: range values to use for error checking and range change
        :type range_values: dict
        :param range_threshold: current range threshold
        :type range_threshold: float
        :param memory: shared memory container for all sub-blocks
        :type memory: _KeysightE36XXXMemory
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._memory = memory
        self._range_threshold = range_threshold
        self._range_values = range_values

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous current in A
        :type: float
        """
        self._memory.channel = self._channel_number
        return float(self._read("MEAS:CURRent?"))

    @property
    def setpoint(self):
        """
        :value: current level setting in A
        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        self._memory.channel = self._channel_number
        return float(self._read("CURRent?"))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        self._memory.channel = self._channel_number

        range_min = self.CAPABILITY['current']['min']
        range_max = self.CAPABILITY['current']['max']

        if value < range_min or value > range_max:
            raise ValueError("%s is an invalid current setpoint. See supported setpoint range. (min:%s|max:%s)"
                             % (value, range_min, range_max))

        # Setting higher current while in High voltage range changes to Low voltage range (which limits voltage)
        if value > self._range_threshold and self._read("VOLTage:RANGe?") in self._range_values["HIGH"]:
            self._write("CURRent %s" % value)
            self.logger.warning("Voltage range automatically changed. Voltage setpoint has been limited to %sV"
                                % float(self._read("VOLTage?")))
        else:
            self._write("CURRent %s" % value)
