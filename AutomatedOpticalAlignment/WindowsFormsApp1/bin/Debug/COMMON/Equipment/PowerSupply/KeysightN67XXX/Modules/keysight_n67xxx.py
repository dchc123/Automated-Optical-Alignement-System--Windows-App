"""
| $Revision:: 282873                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-10-16 15:38:46 +0100 (Tue, 16 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`Equipment.PowerSupply.KeysightN67XXX.keysight_n670xx`
::

    >>> from CLI.Equipment.PowerSupply.KeysightN67XXX.keysight_n670xx import KeysightN670XX
    >>> ps = KeysightN670XX('GPIB1::23::INSTR')
    >>> ps.connect()
    >>> ps.output_coupling([1,2,3])
    >>> ps.output_coupling([])

For channel level API:
:py:class:`Equipment.PowerSupply.KeysightN67XXX.modules.keysight_n67xxx`
::

    >>> ps.channel[2].voltage.setpoint = 5
    >>> ps.channel[2].voltage.setpoint
    5
    >>> ps.channel[2].voltage.value
    5.0012
    >>> ps.channel[1].current.value
    0.102
    >>> ps.channel[1].ovp_level = 10
    >>> ps.channel[1].voltage.setpoint =11
    >>> ps.channel[1].ovp_tripped
    True
    >>> ps.channel[1].voltage.setpoint = 9
    >>> ps.channel[1].clear_protection()
"""

from COMMON.Equipment.PowerSupply.base_power_supply import BasePowerSupplyChannel
from COMMON.Equipment.PowerSupply.base_power_supply import BasePowerSupplyVoltBlock
from COMMON.Equipment.PowerSupply.base_power_supply import BasePowerSupplyCurrBlock


class KeysightN67XXXChannel(BasePowerSupplyChannel):
    """
    Keysight N67XXX power supply common Channel
    """
    CAPABILITY = {'4_wire_sensing': None, 'precision': None}

    def __init__(self, channel_number, channel_options, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param channel_options: options on the power supply module
        :type channel_options: str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._channel_options = channel_options

        self.voltage = KeysightN67XXXVoltBlock(channel_number=channel_number, channel_options=channel_options,
                                               interface=interface, dummy_mode=dummy_mode,
                                               name=self.name+'VoltageMeasure')
        self.current = KeysightN67XXXCurrBlock(channel_number=channel_number, channel_options=channel_options,
                                               interface=interface, dummy_mode=dummy_mode,
                                               name=self.name+'CurrentMeasure')

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
        return output_dict[self._read('OUTPut:STATe? (@ %s)' % self._channel_number, dummy_data='0').strip()]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("OUTPut:STATe %s, (@%s)"
                        % (input_dict[value], self._channel_number), dummy_data=input_dict[value])

    @property
    def power(self):
        """
        **READONLY**

        :value: measured power in W
        :type: float
        """
        voltage = float(self._read("MEASure:VOLTage? (@%s)" % self._channel_number))
        current = float(self._read("MEASure:CURRent? (@%s)" % self._channel_number))
        power = voltage * current
        return power

    @property
    def remote_sensing(self):
        """
        Enable or Disable remote sensing (2 or 4 wire sensing)

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        if self.CAPABILITY['4_wire_sensing']:
            output_dict = {'EXT': 'ENABLE', 'INT': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
            return output_dict[self._read(":SOUR:VOLT:SENS:SOUR? (@ {0})".format(self._channel_number),
                                          dummy_data='EXT')]
        else:
            raise NotImplementedError('{0} does not support 4-wire sensing'.format(self.name))

    @remote_sensing.setter
    def remote_sensing(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        if self.CAPABILITY['4_wire_sensing']:
            value = value.upper()
            input_dict = {'ENABLE': 'EXT', 'DISABLE': 'INT'}

            if value not in input_dict.keys():
                raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
            else:
                self._write(":SOUR:VOLT:SENS:SOUR {0}, (@ {1})".format(input_dict[value], self._channel_number),
                            dummy_data=input_dict[value])
        else:
            raise NotImplementedError('{0} does not support 4-wire sensing'.format(self.name))


class KeysightN67XXXVoltBlock(BasePowerSupplyVoltBlock):
    """
    Keysight N67XXX power supply voltage sub block
    """

    CAPABILITY = {'voltage': {'min': None, 'max': None}}

    def __init__(self, channel_number, channel_options, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param channel_options: options on the power supply module
        :type channel_options: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._channel_options = channel_options
        self._range = "AUTO"

    @property
    def _stat_ques_cond(self):
        """
        **READONLY**
        Reads the Status:Questionable:Condition Register. Returns decimal value.

        :value: Decimal register value
        :type: int
        """
        return int(self._read("STATus:QUEStionable:CONDition? (@%s)" % self._channel_number))

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous voltage in V
        :type: float
        """
        return float(self._read("MEASure:VOLTage? (@%s)" % self._channel_number))

    @property
    def protection_level(self):
        """
        Voltage protection level.

        :value: limit for voltage protection
        :type: float
        """
        return float(self._read(":SOURce:VOLTage:PROTection:LEVel? (@%s)" % self._channel_number))

    @protection_level.setter
    def protection_level(self, value):
        """
        :type value: float
        """
        self._write(":SOURce:VOLTage:PROTection:LEVel %s, (@%s)" % (value, self._channel_number), dummy_data=value)

    @property
    def protection_tripped(self):
        """
        **READONLY**
        Over voltage protection. Returns True if protection is tripped

        :value: ovp tripped
        :type: bool
        """
        if not self.dummy_mode:
            tripped = self._stat_ques_cond & 0x01

            if tripped:
                return True
            else:
                return False
        else:
            return False

    @property
    def range(self):
        """
        Equipment will select optimal range for the value being sent.
        If range is 'AUTO', power supply will use the setpoint as range input. If range
        is a float/int value, power supply will use the range value as range input.

        :value: 'AUTO', Voltage
        :type: str or float
        """
        return self._range

    @range.setter
    def range(self, value):
        """
        :type value: str or float
        """

        range_min = self.CAPABILITY['voltage']['min']
        range_max = self.CAPABILITY['voltage']['max']

        if isinstance(value, str) and value.upper() == "AUTO":
            self._range = value.upper()
        elif not isinstance(value, str) and range_min <= value <= range_max:
            self._range = value
        else:
            raise ValueError("Voltage range is invalid. See valid entries/range. ('AUTO'|min:%s|max:%s)"
                             % (range_min, range_max))

    @property
    def setpoint(self):
        """
        If range is 'AUTO', unit will select optimal range for value.

        :value: voltage level setting in V
        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        return float(self._read(":SOURce:VOLTage? (@%s)" % self._channel_number))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        :raise ValueError: Exception if setpoint value is out of range
        """

        range_min = self.CAPABILITY['voltage']['min']
        range_max = self.CAPABILITY['voltage']['max']

        if value < range_min or value > range_max:
            raise ValueError("%s is an invalid voltage setpoint. See supported setpoint range. (min:%s|max:%s)"
                             % (value, range_min, range_max))

        if self.range == "AUTO":
            # Manual suggest sending those commands in same mesage to avoid errors.
            self._write(":SOURce:{type} {val}, (@{chan});{type}:RANGe {val}, (@{chan});"
                        ":SENSe:{type}:RANGe {val}, (@{chan})"
                        .format(type='VOLTage', val=value, chan=self._channel_number),
                        dummy_data=value)
            self.logger.info("Power supply will choose optimal range for a '{setpoint}V' setpoint."
                             .format(setpoint=value))
        else:
            self._write(":SOURce:{type} {val}, (@{chan});{type}:RANGe {range}, (@{chan});"
                        ":SENSe:{type}:RANGe {range}, (@{chan})"
                        .format(type='VOLTage', val=value, range=self.range,
                                chan=self._channel_number), dummy_data=value)
            self.logger.info("Power supply will choose optimal range for a '{range}V' range setting."
                             .format(range=self.range))

        if self.protection_tripped:
            self.logger.warning('Over voltage protection is tripped. Please clear condition generating the issue, '
                                'then clear protection flag.')

    @property
    def slew_rate(self):
        """
        Voltage slew rate. Sending 'max' or 'min' will set it to the maximum or minimum values

        :value: voltage slew rate V/s
        :type: float
        """
        return float(self._read(":SOURce:VOLTage:SLEW? (@%s)" % self._channel_number))

    @slew_rate.setter
    def slew_rate(self, value):
        """
        :type value: float
        """
        self._write(":SOURce:VOLTage:SLEW %s, (@%s)" % (value, self._channel_number),
                    dummy_data=value)

    def clear_protection(self):
        """
        Clears the protection status triggered by and over voltage condition.
        Condition generating the fault must be removed in order for clear to take effect.
        Output it then restore to the state it was before th fault.
        """
        self._write(":OUTPut:PROTection:CLEar (@%s)" % self._channel_number)

        if self.protection_tripped:
            self.logger.warning('Condition generating the issue has not been addressed. Please address condition, then '
                                'clear protection flag.')


class KeysightN67XXXCurrBlock(BasePowerSupplyCurrBlock):
    """
    Keysight N67XXX power supply current sub block
    """

    CAPABILITY = {'current': {'min': None, 'max': None}}

    def __init__(self, channel_number, channel_options, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param channel_options: options on the power supply module
        :type channel_options: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._channel_options = channel_options
        self._range = "AUTO"

    @property
    def _stat_ques_cond(self):
        """
        **READONLY**
        Reads the Status:Questionable:Condition Register. Returns decimal value.

        :value: Decimal register value
        :type: int
        """
        return int(self._read("STATus:QUEStionable:CONDition? (@%s)" % self._channel_number))

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous current in A
        :type: float
        """
        return float(self._read("MEASure:CURRent? (@%s)" % self._channel_number))

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
        return output_dict[self._read(':SOURce:CURRent:PROTection:STATe? (@ %s)'
                                      % self._channel_number, dummy_data='0').strip()]

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
            self._write(":SOURce:CURRent:PROTection:STATe %s, (@%s)"
                        % (input_dict[value], self._channel_number), dummy_data=input_dict[value])

    @property
    def protection_level(self):
        """
        Current protection level is shared with current setpoint.

        :value: limit for current protection
        :type: float
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

        Over voltage or over current protection. Returns True if protection is tripped

        :value: ovp or ocp tripped
        :type: bool
        """
        if not self.dummy_mode:
            tripped = self._stat_ques_cond & 0x02

            if tripped:
                return True
            else:
                return False
        else:
            return False

    @property
    def range(self):
        """
        Equipment will select optimal range for the value being sent.
        If range is 'AUTO', power supply will use the setpoint as range input. If range
        is a float/int value, power supply will use the range value as range input.

        :value: 'AUTO', Current
        :type: str or float
        """
        return self._range

    @range.setter
    def range(self, value):
        """
        :type value: str or float
        """

        range_min = self.CAPABILITY['current']['min']
        range_max = self.CAPABILITY['current']['max']
        if "Opt 2UA" in self._channel_options:
            range_min = 0.000004
        if isinstance(value, str) and value.upper() == "AUTO":
            self._range = value.upper()
        elif not isinstance(value, str) and range_min <= value <= range_max:
            self._range = value
        else:
            raise ValueError("Current range is invalid. See valid entries/range. ('AUTO'|min:%s|max:%s)"
                             % (range_min, range_max))

    @property
    def setpoint(self):
        """
        If range is 'AUTO', unit will select optimal range for value.

        :value: current level setting in A
        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        return float(self._read(":SOURce:CURRent? (@%s)" % self._channel_number))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        :raise ValueError: Exception if setpoint value is out of range
        """

        range_min = self.CAPABILITY['current']['min']
        range_max = self.CAPABILITY['current']['max']

        if value < range_min or value > range_max:
            raise ValueError("%s is an invalid current setpoint. See supported setpoint range. (min:%s|max:%s)"
                             % (value, range_min, range_max))

        if self.range == "AUTO":
            # Manual suggest sending those commands in same message to avoid errors.
            self._write(":SOURce:{type} {val}, (@{chan});{type}:RANGe {val}, (@{chan});"
                        ":SENSe:{type}:RANGe {val}, (@{chan})"
                        .format(type='CURRent', val=value, chan=self._channel_number), dummy_data=value)
            self.logger.info("Power supply will choose optimal range for a '{setpoint}A' setpoint."
                             .format(setpoint=value))
        else:
            self._write(":SOURce:{type} {val}, (@{chan});{type}:RANGe {range}, (@{chan});"
                        ":SENSe:{type}:RANGe {range}, (@{chan})"
                        .format(type='CURRent', val=value, range=self.range,
                                chan=self._channel_number), dummy_data=value)
            self.logger.info("Power supply will choose optimal range for a '{range}A' range setting."
                             .format(range=self.range))

        if self.protection_tripped:
            self.logger.warning('Over current protection is tripped. Please clear condition generating the issue, '
                                'then clear protection flag.')

    def clear_protection(self):
        """
        Clears the protection status triggered by and over over current condition.
        Condition generating the fault must be removed in order for clear to take effect.
        Output it then restore to the state it was before th fault.
        """
        self._write(":OUTPut:PROTection:CLEar (@%s)" % self._channel_number)

        if self.protection_tripped:
            self.logger.warning('Condition generating the issue has not been addressed. Please address condition, then '
                                'clear protection flag.')