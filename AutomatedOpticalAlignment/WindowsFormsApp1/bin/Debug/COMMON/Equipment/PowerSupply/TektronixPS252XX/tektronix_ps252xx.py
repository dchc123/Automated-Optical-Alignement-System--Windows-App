"""
| $Revision:: 281675                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-08-17 16:11:07 +0100 (Fri, 17 Aug 2018) $:  Date of last commit
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


class _TektronixPS252XXMemory(BaseEquipmentBlock):
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


class TektronixPS252XX(BasePowerSupply):
    """
    Tektronix PS252XX common power supply driver.
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
        """:type: list of TektronixPS252XXChannel"""

    @property
    def global_output(self):
        """
        :raise NotSupportedError: Global output is not supported
        """
        raise NotSupportedError("%s does not support over Global Output" % self.name)

    @global_output.setter
    def global_output(self, value):
        """
        :raise NotSupportedError: Global output is not supported
        """
        raise NotSupportedError("%s does not support over Global Output" % self.name)

    def reset(self):
        super().reset()
        self._write("CURRent:PROTection:STATe 0")


class TektronixPS252XXChannel(BasePowerSupplyChannel):
    """
    Tektronix PS252XX Common Channel
    """
    CAPABILITY = {'4_wire_sensing': False, 'precision': False}

    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param memory: shared memory container for all sub-blocks
        :type memory: _TektronixPS252XXMemory
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
        """:type: TektronixPS252XXVoltBlock"""
        self.current = None
        """:type: TektronixPS252XXCurrBlock"""

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


class TektronixPS252XXVoltBlock(BasePowerSupplyVoltBlock):
    """
    Tektronix PS252XX voltage sub block
    """

    CAPABILITY = {'voltage': {'min': None, 'max': None}}

    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param memory: shared memory container for all sub-blocks
        :type memory: _TektronixPS252XXMemory
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
    def _stat_ques_cond(self):
        """
        **READONLY**
        Reads the Status:Questionable:Condition Register. Returns decimal value.

        :value: Decimal register value
        :type: int
        """
        return int(self._read("STATus:QUEStionable:CONDition?"))

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
    def protection_tripped(self):
        """
        **READONLY**
        Over voltage protection. Returns True if protection is tripped

        :value: ovp tripped
        :type: bool
        """
        if not self.dummy_mode:
            tripped = self._stat_ques_cond & 0x200

            if tripped:
                return True
            else:
                return False
        else:
            return False

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
        try:
            self._write("VOLTage %s" % value)
            if self.protection_tripped:  # Additional check for when output is not enable, and protection not cleared
                raise RuntimeError
        except RuntimeError as e:
            if self.protection_tripped and not self.dummy_mode:
                self.logger.warning('Over voltage protection is tripped. Output is disabled. '
                                    'Please clear condition generating the issue, then clear protection '
                                    'before enabling output.')
            else:
                raise e

    def clear_protection(self):
        """
        Clears the protection status triggered by an over voltage protection. Also resets all values to default.
        If possible, reset from the front panel instead.
        """

        self._write("OUTput:PROTection:CLEar")
        self._write("CURRent:PROTection:STATe 0")
        self.logger.warning('All power supply settings have been reset to default, for all channels!')


class TektronixPS252XXCurrBlock(BasePowerSupplyCurrBlock):
    """
    Tektronix PS252XX current sub block
    """

    CAPABILITY = {'current': {'min': None, 'max': None}}

    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param memory: shared memory container for all sub-blocks
        :type memory: _TektronixPS252XXMemory
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
    def _stat_ques_cond(self):
        """
        **READONLY**
        Reads the Status:Questionable:Condition Register. Returns decimal value.

        :value: Decimal register value
        :type: int
        """
        return int(self._read("STATus:QUEStionable:CONDition?"))

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

        self._write("CURRent %s" % value)

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous current in A
        :type: float
        """
        self._memory.channel = self._channel_number
        return float(self._read("MEAS:CURRent?"))
