"""
| $Revision:: 282171                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-09-05 17:15:41 +0100 (Wed, 05 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""

from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_exceptions import NotSupportedError
from CLI.Utilities.custom_structures import CustomList
from ..base_power_supply import BasePowerSupply
from ..base_power_supply import BasePowerSupplyChannel
from ..base_power_supply import BasePowerSupplyVoltBlock
from ..base_power_supply import BasePowerSupplyCurrBlock


class _Xantrex_XDL35_5XXMemory(BaseEquipmentBlock):
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


class XantrexXDL35_5XX(BasePowerSupply):
    """
    Xantrex XDL35-5XX common power supply driver.
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
        """:type: list of XantrexXDL35_5XXChannel"""

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
        raise NotSupportedError("%s does not support reading Global Output Status" % self.name)

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
            if input_dict[value] == '1':
                self._write("OPALL %s" % input_dict[value])  # Only turns on CH2
                self._write("OPALL %s" % input_dict[value])  # Second command is needed to enable CH1 and AUX
            else:
                self._write("OPALL %s" % input_dict[value])  # Only need one command to disable all


class XantrexXDL35_5XXChannel(BasePowerSupplyChannel):
    """
    Xantrex XDL35-5XX Common Channel
    """
    CAPABILITY = {'4_wire_sensing': False, 'precision': False}

    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param memory: shared memory container for all sub-blocks
        :type memory: _Xantrex_XDL35_5XXMemory
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
        """:type: XantrexXDL35_5XXVoltBlock"""
        self.current = None
        """:type: XantrexXDL35_5XXCurrBlock"""

    @property
    def output(self):
        """
        Enable state of the channel output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        raise NotSupportedError("%s does not support reading Output Status" % self.name)

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
            self._write("OP{0} {1}".format(self._channel_number, input_dict[value]))

    @property
    def power(self):
        """
        READONLY

        :value: measured power in W
        :type: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support power measurements" % self.name)
        self._memory.channel = self._channel_number
        voltage = float(self._read("V%sO?" % self._channel_number).replace('V', ''))
        current = float(self._read("I%sO?" % self._channel_number).replace('A', ''))
        power = voltage * current
        return power

    @property
    def remote_sense(self):
        """
        Enables remote (4-wire) sensing on specific channel

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        raise NotSupportedError("%s does not support reading remote sensing status" % self.name)

    @remote_sense.setter
    def remote_sense(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support remote sensing" % self.name)
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        self._memory.channel = self._channel_number
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("SENSE{0} {1}".format(self._channel_number, input_dict[value]))


class XantrexXDL35_5XXVoltBlock(BasePowerSupplyVoltBlock):
    """
    Xantrex XDL35-5XX voltage sub block
    """

    CAPABILITY = {'voltage': {'min': None, 'max': None}}

    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param memory: shared memory container for all sub-blocks
        :type memory: _Xantrex_XDL35_5XXMemory
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

    @property
    def _limit_status_register(self):
        """
        **READONLY**

        :value: returns the value in the LSR
        :type: float
        """
        return float(self._read("LSR%s?" % self._channel_number))

    def clear_protection(self):
        """
        Clears the protection status triggered by and over voltage condition.
        Condition generating the fault must be removed in order for clear to take effect.
        Output it then restore to the state it was before the fault.
        """
        self._write("TRIPRST")
        self.logger.info("Clearing ALL OVP and OCP triggers")

    @property
    def protection_level(self):
        """
        :value: Voltage protection level
        :type: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support OVP" % self.name)
        self._memory.channel = self._channel_number
        return float(self._read("OVP%s?" % self._channel_number).replace('VP%s ' % self._channel_number, ''))

    @protection_level.setter
    def protection_level(self, value):
        """
        :type value: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support OVP" % self.name)
        self._memory.channel = self._channel_number
        self._write("OVP{0} {1}".format(self._channel_number, value))

    @property
    def protection_tripped(self):
        """
        **READONLY**
        Over voltage protection. Returns True if protection is tripped

        :value: ovp tripped
        :type: bool
        """
        if not self.dummy_mode:
            if self._limit_status_register == 4:
                return True
            else:
                return False
        else:
            return False

    @property
    def range(self):
        """
        Voltage protection level

        :value: - 0 = 15V (5A)
                - 1 = 35V (3A)
                - 2 = 35V (500mA)
        :type: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support voltage range" % self.name)
        self._memory.channel = self._channel_number
        return float(self._read("RANGE{0}?".format(self._channel_number)).replace('R%s ' % self._channel_number, ''))

    @range.setter
    def range(self, value):
        """
        :type value: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support range" % self.name)
        input_list = [0, 1, 2]
        if value in input_list:
            self._memory.channel = self._channel_number
            self._write("RANGE{0} {1}".format(self._channel_number, value))
        else:
            raise ValueError("%s is an invalid range. Range must be 0, 1, or 2" % value)

    @property
    def setpoint(self):
        """
        :value: voltage level setting in V

        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support voltage setpoint" % self.name)
        self._memory.channel = self._channel_number
        return float(self._read("V{0}?".format(self._channel_number)).replace('V%s ' % self._channel_number, ''))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support voltage setpoint" % self.name)
        self._memory.channel = self._channel_number

        range_min = self.CAPABILITY['voltage']['min']
        range_max = self.CAPABILITY['voltage']['max']

        if value < range_min or value > range_max:
            raise ValueError("%s is an invalid setpoint. See supported setpoint range. (min:%s|max:%s)"
                             % (value, range_min, range_max))
        try:
            self._write("V{0} {1}".format(self._channel_number, value))
            if self.protection_tripped:  # Additional check for when output is not enable, and protection not cleared
                raise RuntimeError
        except RuntimeError as e:
            if self.protection_tripped and not self.dummy_mode:
                self.logger.warning('Over voltage protection is tripped. Output is disabled. '
                                    'Please clear condition generating the issue, then clear protection '
                                    'before enabling output.')
            else:
                raise e

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous voltage in V
        :type: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support voltage measurements" % self.name)
        self._memory.channel = self._channel_number
        return float(self._read("V%sO?" % self._channel_number).replace('V', ''))


class XantrexXDL35_5XXCurrBlock(BasePowerSupplyCurrBlock):
    """
    Xantrex XDL35-5XX current sub block
    """

    CAPABILITY = {'current': {'min': None, 'max': None}}

    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param memory: shared memory container for all sub-blocks
        :type memory: _Xantrex_XDL35_5XXMemory
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

    @property
    def _limit_status_register(self):
        """
        **READONLY**

        :value: returns the value in the LSR
        :type: float
        """
        return float(self._read("LSR%s?" % self._channel_number))

    def clear_protection(self):
        """
        Clears the protection status triggered by and over voltage condition.
        Condition generating the fault must be removed in order for clear to take effect.
        Output it then restore to the state it was before the fault.
        """
        self._write("TRIPRST")
        self.logger.info("Clearing ALL OVP and OCP triggers")

    @property
    def protection_level(self):
        """
        :value: Current protection level
        :type: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support OCP" % self.name)
        self._memory.channel = self._channel_number
        return float(self._read("OCP%s?" % self._channel_number).replace('CP%s ' % self._channel_number, ''))

    @protection_level.setter
    def protection_level(self, value):
        """
        :type value: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support OCP" % self.name)
        self._memory.channel = self._channel_number
        self._write("OCP{0} {1}".format(self._channel_number, value))

    @property
    def protection_tripped(self):
        """
        **READONLY**
        Over voltage protection. Returns True if protection is tripped

        :value: ovp tripped
        :type: bool
        """
        if not self.dummy_mode:
            if self._limit_status_register == 11:
                return True
            else:
                return False
        else:
            return False

    @property
    def range(self):
        """
        :value: Voltage protection level
        :type: float
        """
        raise NotSupportedError("%s does not support current range. See voltage range function for more info"
                                % self.name)

    @range.setter
    def range(self, value):
        """
        :type value: float
        """
        raise NotSupportedError("%s does not support current range. See voltage range function for more info"
                                % self.name)

    @property
    def setpoint(self):
        """
        :value: current level setting in A
        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support current setpoint" % self.name)
        self._memory.channel = self._channel_number
        return float(self._read("I{0}?".format(self._channel_number)).replace('I%s ' % self._channel_number, ''))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support current setpoint" % self.name)
        self._memory.channel = self._channel_number

        range_min = self.CAPABILITY['current']['min']
        range_max = self.CAPABILITY['current']['max']

        if value < range_min or value > range_max:
            raise ValueError("%s is an invalid setpoint. See supported setpoint range. (min:%s|max:%s)"
                             % (value, range_min, range_max))
        try:
            self._write("I{0} {1}".format(self._channel_number, value))
            if self.protection_tripped:  # Additional check for when output is not enable, and protection not cleared
                raise RuntimeError
        except RuntimeError as e:
            if self.protection_tripped and not self.dummy_mode:
                self.logger.warning('Over current protection is tripped. Output is disabled. '
                                    'Please clear condition generating the issue, then clear protection '
                                    'before enabling output.')
            else:
                raise e

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous current in A
        :type: float
        """
        if self._channel_number == 3:
            raise NotSupportedError("%s Channel 3 (Aux) does not support current measurements" % self.name)
        self._memory.channel = self._channel_number
        return float(self._read("I%sO?" % self._channel_number).replace('A', ''))
