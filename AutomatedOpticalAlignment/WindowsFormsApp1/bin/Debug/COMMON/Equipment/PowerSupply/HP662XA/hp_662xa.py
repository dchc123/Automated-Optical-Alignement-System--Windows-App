"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: tbrooks@semtech.com                        $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_exceptions import NotSupportedError
from COMMON.Utilities.custom_structures import CustomList
from ..base_power_supply import BasePowerSupply
from ..base_power_supply import BasePowerSupplyChannel
from ..base_power_supply import BasePowerSupplyVoltBlock
from ..base_power_supply import BasePowerSupplyCurrBlock


class HP662XA(BasePowerSupply):
    """
    HP 662XA common power supply driver.
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
        """:type: list of HP662XAChannel"""

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        super()._configure_interface()
        self._interface.stb_polling_supported = False
        self._interface.error_check_supported = False

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
        """
        :raise NotSupportedError: Global output is not supported
        """
        raise NotSupportedError("%s does not support over Global Output" % self.name)

    @property
    def identity(self):
        """
        **READONLY**
        Very old equipment not conforming to modern standards - gathers data manually
        :return: itentity
        :rtype: dict
        """
        data = {
            'manufacturer': "HP",
            'model': self._read("ID?"),
            'serial': None,
            'firmware': self._read("ROM?")
        }
        for key, value in data.items():
            self.logger.debug("{}: {}".format(key.upper(), value))
        return data


class HP662XAChannel(BasePowerSupplyChannel):
    """
    HP common channel
    """

    CAPABILITY = {'4_wire_sensing': False, 'precision': False}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number

        self.voltage = HP662XAVoltageBlock(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode,
                                           name=self.name+'VoltageMeasure')
        self.current = HP662XACurrBlock(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode,
                                        name=self.name+'CurrentMeasure')

    @property
    def output(self):
        """
        Enable state of the channel output

        :return: returns the state of the channel ouput
        :rtype: str
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read(f"OUT? {self._channel_number}", dummy_data='0').strip()]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0',
                      'EN': '1', 'DIS': '0'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(f"OUT {self._channel_number}, {input_dict[value]}")

    @property
    def power(self):
        """
        **READONLY**

        :return: measured power in W
        :rtype: float
        """
        power = self.voltage.value * self.current.value
        return power


class HP662XAVoltageBlock(BasePowerSupplyVoltBlock):
    """
    HP 662xA power supply voltage sub block
    """

    CAPABILITY = {'voltage': {'min': None, 'max': None}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number

    @property
    def _status_register(self):
        """
        **READONLY**
        Reads the Status Register. Returns decimal value.

        :return: 8 bit status register
        :rtype: int
        """
        return int(self._read(f"STS? {self._channel_number}"))

    @property
    def value(self):
        """
        **READONLY**

        :return: measured voltage output
        :rtype: float
        """
        return float(self._read(f"VOUT? {self._channel_number}"))

    @property
    def protection_level(self):
        """
        **READONLY**

        :return: measured voltage output
        :rtype: float
        """
        return float(self._read(f"OVSET? {self._channel_number}"))

    @protection_level.setter
    def protection_level(self, value):
        """
        :type value: float
        """
        self._write(f"OVSET {self._channel_number}, {float(value)}", dummy_data=value)

    @property
    def protection_tripped(self):
        """
        **READONLY**
        Over voltage protection. Returns True if protection is tripped

        :value: ovp tripped
        :type: bool
        """
        if not self.dummy_mode:
            if self._status_register & 0x08:
                return True
            else:
                return False
        else:
            return False

    @property
    def setpoint(self):
        """
        sets the target voltage

        :return: voltage
        :rtype: float
        """
        return float(self._read(f"VSET? {self._channel_number}"))

    @setpoint.setter
    def setpoint(self, value):
        """
        :param value: Voltage set point in Volts
        :type value: float
        """

        r_max = self.CAPABILITY['voltage']['max']
        r_min = self.CAPABILITY['voltage']['min']

        if value < r_min or value > r_max:
            raise ValueError(f"{value} is an invalid voltage setpoint. See supported setpoint range. (min:"
                             f"{r_min}|max:{r_max}")

        self._write(f"VSET {self._channel_number}, {value}")

        if self.protection_tripped:
            self.logger.warning('Over voltage protection is tripped. Please clear condition generating the issue, '
                                'then clear protection flag.')

    def clear_protection(self):
        """
        Clears the protection status triggered by and over voltage condition.
        Condition generating the fault must be removed in order for clear to take effect.
        Output it then restore to the state it was before th fault.
        """
        self._write(f"OVRST {self._channel_number}")

        if self.protection_tripped:
            self.logger.warning('Condition generating the issue has not been addressed. Please address condition, then '
                                'clear protection flag.')


class HP662XACurrBlock(BasePowerSupplyCurrBlock):
    """
    HP 662xA power supply current sub block
    """

    CAPABILITY = {'current': {'min': None, 'max': None}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialise instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param interface:
        :type interface:
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number

    @property
    def _status_register(self):
        """
        **READONLY**
        :value: Decimal register value
        :type: int
        """
        return int(self._read(f"STS? {self._channel_number}"))

    @property
    def value(self):
        return float(self._read(f"IOUT? {self._channel_number}"))

    @property
    def setpoint(self):
        """
        Voltage set point

        :return: Current level setting in A
        :rtype: float
        """
        return float(self._read(f"ISET? {self._channel_number}"))

    @setpoint.setter
    def setpoint(self, value):
        """

        :param value: current set point
        :type value: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        r_max = self.CAPABILITY['current']['max']
        r_min = self.CAPABILITY['current']['min']

        if value < r_min or value > r_max:
            raise ValueError(f"{value} is an invalid current setpoint. See supported setpoint range. (min:"
                             f"{r_min}|max:{r_max}")

        self._write(f"ISET {self._channel_number}, {value}")

        if self.protection_tripped:
            self.logger.warning('Over voltage protection is tripped. Please clear condition generating the issue, '
                                'then clear protection flag.')

    @property
    def ocp(self):
        """
        Enable state of the over current protection.
        Value of OCP is the current setpoint (which is shared with limit)

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read(f'OCP? {self._channel_number}', dummy_data='0').strip()]

    @ocp.setter
    def ocp(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(f"OCP {self._channel_number}, {input_dict[value]}", dummy_data=input_dict[value])

    @property
    def protection_level(self):
        """
        **READONLY**

        :return: protection current level
        :rtype: float
        """
        return self.setpoint

    @protection_level.setter
    def protection_level(self, value):
        """
        :type value: float
        """
        self.setpoint = value

    @property
    def protection_tripped(self):
        """
        **READONLY**
        Over voltage protection. Returns True if protection is tripped

        :value: ovp tripped
        :type: bool
        """
        if not self.dummy_mode:
            if self._status_register & 0x40:
                return True
            else:
                return False
        else:
            return False

    def clear_protection(self):
        """
        Clears the protection status triggered by and over current condition.
        Condition generating the fault must be removed in order for clear to take effect.
        Output it then restore to the state it was before th fault.
        """
        self._write(f"OCRST {self._channel_number}")

        if self.protection_tripped:
            self.logger.warning('Condition generating the issue has not been addressed. Please address condition, then '
                                'clear protection flag.')
