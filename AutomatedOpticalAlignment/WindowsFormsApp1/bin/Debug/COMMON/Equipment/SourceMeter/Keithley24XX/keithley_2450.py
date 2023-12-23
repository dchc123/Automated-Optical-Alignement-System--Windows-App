"""
| $Revision:: 283308                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-31 21:10:30 +0000 (Wed, 31 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keithley2450`

::
    >>> from CLI.Equipment.SourceMeter.Keithley24XX.keithley_2450 import Keithley2450
    >>> smu = Keithley2450('GPIB0::24::INSTR')
    >>> smu.connect()

For Channel block level API:
:py:class:`.Keithley2450Channel`

::
    >>> smu.channel[1].terminal_select = "FRONT"
    >>> smu.channel[1].remote_sensing = "ENABLE"
    >>> smu.channel[1].output = "ENABLE"

    >>> smu.channel[1].source.voltage.setpoint = 3.3
    >>> smu.channel[1].source.current.compliance_voltage = 0.5
    >>> smu.channel[1].measure.current.range = "AUTO"
    >>> smu.channel[1].measure.current.range = 100e-3
    >>> smu.channel[1].measure.current.value
    0.095
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_structures import CustomList
from CLI.Utilities.custom_exceptions import NotSupportedError
from time import sleep
from .keithley_24xx import Keithley24XX
from .keithley_24xx import Keithley24XXChannel
from .keithley_24xx import Keithley24XXSourceParentBlock
from .keithley_24xx import Keithley24XXMeasureParentBlock
from .keithley_24xx import Keithley24XXSourceVoltageBlock
from .keithley_24xx import Keithley24XXSourceCurrentBlock
from .keithley_24xx import Keithley24XXMeasureBlock


class Keithley2450(Keithley24XX):
    """
    Keithley 2450 Source Meter
    """

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of Keithley2450Channel"""

        self.channel.append(Keithley2450Channel(channel_number=1, interface=interface, dummy_mode=dummy_mode))


class Keithley2450Channel(Keithley24XXChannel):
    """
    Keithly2450 Channel Sub Block
    """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)

        self._channel_number = channel_number
        self.source = Keithley2450SourceParentBlock(channel_number=channel_number, interface=interface,
                                                    dummy_mode=dummy_mode)
        self.measure = Keithley2450MeasureParentBlock(channel_number=channel_number, interface=interface,
                                                      dummy_mode=dummy_mode)

    @property
    def beeper(self):
        """
        **Enable or Disable source meter beeper**

        **EXAMPLE:** *smu.channel[1].beeper = 'ENABLE'*

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        raise NotSupportedError

    @beeper.setter
    def beeper(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        raise NotSupportedError

    def remote_sensing_state(self, mode):
        """
        The state ('ENABLE' or 'DISABLE') of the remote sensing (4-wire sense) for the specified mode

        :param mode: - 'VOLTAGE'
                      - 'CURRENT'
                      - 'RESISTANCE'
        :type mode: str
        :return: 'ENABLE' or 'DISABLE'
        :rtype: str
        """
        mode = mode.upper()
        mode_dict = {'VOLTAGE': 'VOLT', 'CURRENT': 'CURR', 'RESISTANCE': 'RES'}
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":SENS:{0}:RSEN?".format(mode_dict[mode]))]

    def remote_sensing(self, mode, toggle):
        """
        Configures the Keithley's remote sensing(4-wire sense) modes. Each mode (voltage, current, and resistance) is
        separate from one another. For example this allows 4-wire sensing on only voltage sourcing, while current
        sourcing remains on 2-wire sensing.

        :param mode: - 'VOLTAGE'
                      - 'CURRENT'
                      - 'RESISTANCE'
        :type mode: str
        :param toggle: - 'ENABLE'
                        - 'DISABLE'
        :type toggle: str
        :return: None
        :rtype: None
        """
        mode = mode.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        mode_dict = {'VOLTAGE': 'VOLT', 'CURRENT': 'CURR', 'RESISTANCE': 'RES'}
        if toggle not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            if mode != self.remote_sensing_state:
                self.logger.info("Output Disabled")
            self._write(":SENS:{0}:RSEN {1}".format(mode_dict[mode], input_dict[toggle]))


class Keithley2450SourceParentBlock(Keithley24XXSourceParentBlock):
    """
       Keithly2450 Source Mode Sub Block
       """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)

        self.voltage = Keithley2450SourceVoltageBlock(channel_number=channel_number, type_='voltage',
                                                      interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley2450SourceCurrentBlock(channel_number=channel_number, type_='current',
                                                      interface=interface, dummy_mode=dummy_mode)


class Keithley2450MeasureParentBlock(Keithley24XXMeasureParentBlock):
    """
       Keithly2450 Source Mode Sub Block
       """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)

        self.voltage = Keithley2450MeasureBlock(channel_number=channel_number, type_='voltage',
                                                interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley2450MeasureBlock(channel_number=channel_number, type_='current',
                                                interface=interface, dummy_mode=dummy_mode)
        self.resistance = Keithley2450MeasureBlock(channel_number=channel_number, type_='resistance',
                                                   interface=interface, dummy_mode=dummy_mode)


class Keithley2450SourceVoltageBlock(Keithley24XXSourceVoltageBlock):
    """
    Keithley2450 Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 500e-9, 'warn': 21, 'max': 210}},
                  'current': {'source': {'min': 500e-15, 'warn': 0.105, 'max': 1.05}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param current_type: select between AC/DC
        :type current_type: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, type_=type_,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._type = type_

    @property
    def compliance_current(self):
        """
        **Voltage/Current Compliance limit**\n

        **example:** *smu.channel[1].source.voltage.compliance_current = 0.5*

        :value: limit for voltage/current compliance
        :type: float
        """
        return float(self._read(":SOUR:VOLT:ILIM?"))

    @compliance_current.setter
    def compliance_current(self, value):
        """
        :type value: float
        """
        if not self.dummy_mode:
            if self._type != self._source_mode:
                raise NotSupportedError("Cannot source Current and set Current compliance limit simultaneously. "
                                        "Consider sourcing Voltage before using this function")

        minimum = self.CAPABILITY['current']['source']['min']
        maximum = self.CAPABILITY['current']['source']['max']
        warning = self.CAPABILITY['current']['source']['warn']

        if (abs(value) < minimum) and (abs(value) != 0):
            raise ValueError("Current supply minimum is limited to {0}".format(minimum))
        elif abs(value) > maximum:
            raise ValueError('Please specify a current between -{0} and +{0}'.format(maximum))
        elif abs(value) > warning:
            self.logger.info("Set compliance limit and source level may be exceeding calibration specification."
                             "Refer to equipment manual")

        self._write(":SOUR:VOLT:ILIM {0}".format(value))

    @property
    def setpoint(self):
        """
        **Sets the voltage level on the specified output**

        **example:** *smu.channel[1].source.voltage.setpoint = 0.8*

        :value: voltage/current level setting in V/A
        :type: float
        """
        source = str(self._source_mode)
        if source != self._type:
            raise NotSupportedError("Cannot read {0}(object type) set point when sourcing {1}"
                                    .format(self._type, source))
        return float(self._read(":SOUR:%s:LEVEL:IMM:AMPL?" % self._type))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        """
        minimum = self.CAPABILITY['voltage']['source']['min']
        maximum = self.CAPABILITY['voltage']['source']['max']
        warning = self.CAPABILITY['voltage']['source']['warn']

        if (abs(value) < minimum) and (abs(value) != 0):
                raise ValueError("Voltage supply minimum is limited to {0}".format(minimum))
        if abs(value) > maximum:
            raise ValueError('Please specify a {0} between -{0} and +{0}'.format(maximum))
        elif abs(value) > warning:
            self.logger.info("Set source and compliance limit may be out of calibration specification."
                             " Refer to equipment manual")

        if self._source_mode != self._type:
            if self._read(':SENS:RES:RANGE:AUTO?') == 'ON':
                self._write(":SENS:RES:RANGE:AUTO OFF")
                self.logger.info("Disabled resistance auto mode to allow source changing")
            self.logger.info("Source mode changed: Output Disabled")

        self._write(":SOUR:FUNC VOLT")
        self._write(":SOUR:VOLT:RANG {0}".format(value))
        self._write(":SOUR:VOLT {0}".format(value))


class Keithley2450SourceCurrentBlock(Keithley24XXSourceCurrentBlock):
    """
    Keithley2450 Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 500e-9, 'warn': 21, 'max': 210}},
                  'current': {'source': {'min': 500e-15, 'warn': 0.105, 'max': 1.05}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param current_type: select between AC/DC
        :type current_type: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, type_=type_,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._type = type_

    @property
    def compliance_voltage(self):
        """
        **VoltageCompliance limit**\n

        **example:** *smu.channel[1].source.voltage.compliance_current = 0.5*

        :value: limit for voltage/current compliance
        :type: float
        """
        return float(self._read(":SOUR:CURR:VLIM?"))

    @compliance_voltage.setter
    def compliance_voltage(self, value):
        """
        :type value: float
        """
        if not self.dummy_mode:
            if self._type != self._source_mode:
                raise NotSupportedError("Cannot source Voltage and set Coltage compliance limit simultaneously. "
                                        "Consider sourcing Current before using this function")

        minimum = self.CAPABILITY['voltage']['source']['min']
        maximum = self.CAPABILITY['voltage']['source']['max']
        warning = self.CAPABILITY['voltage']['source']['warn']

        if (abs(value) < minimum) and (abs(value) != 0):
            raise ValueError("Voltage supply minimum is limited to {0}".format(minimum))
        elif abs(value) > maximum:
            raise ValueError('Please specify a voltage between -{0} and +{0}'.format(maximum))
        elif abs(value) > warning:
            self.logger.info("Set compliance limit and source level may be exceeding calibration specification."
                             "Refer to equipment manual")

        meas_range = abs(float(self._read(":SENS:VOLT:RANG?")))
        if not (abs(meas_range)/10.0 <= abs(value) <= abs(meas_range)):
            raise ValueError("Compliance voltage must be in the same range as measurement voltage range. Set voltage "
                             "measurement range to 'AUTO' if unsure")

        self._write(":SOUR:CURR:VLIM {0}".format(value))

    @property
    def setpoint(self):
        """
        **Sets the current level on the specified output**

        **example:** *smu.channel[1].source.current.setpoint = 0.8*

        :value: voltage/current level setting in V/A
        :type: float
        """
        mode = str(self._source_mode)
        if mode != self._type:
            raise NotSupportedError("Cannot read {0} set point when sourcing {1}"
                                    .format(self._type, mode))
        return float(self._read(":SOUR:%s:LEVEL:IMM:AMPL?" % self._type))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        """
        minimum = self.CAPABILITY['current']['source']['min']
        maximum = self.CAPABILITY['current']['source']['max']
        warning = self.CAPABILITY['current']['source']['warn']

        if (abs(value) < minimum) and (abs(value) != 0):
                raise ValueError("Current supply minimum is limited to {0}".format(minimum))
        if abs(value) > maximum:
            raise ValueError('Please specify a {0} between -{0} and +{0}'.format(maximum))
        elif abs(value) > warning:
            self.logger.info("Set source and compliance limit may be out of calibration specification."
                             " Refer to equipment manual")

        if self._source_mode != self._type:
            if self._read(':SENS:RES:RANGE:AUTO?') == 'ON':
                self._write(":SENS:RES:RANGE:AUTO OFF")
                self.logger.info("Disabled resistance auto mode to allow source changing")
            self.logger.info("Source mode changed: Output Disabled")

        self._write(":SOUR:FUNC CURR")
        self._write(":SOUR:CURR:RANG {0}".format(value))
        self._write(":SOUR:CURR {0}".format(value))


class Keithley2450MeasureBlock(Keithley24XXMeasureBlock):
    """
    Keithley2450 Resistance Sub Block
    """
    CAPABILITY = {'voltage': {'measure': {'min': 10e-9, 'max': 211}},
                  'current': {'measure': {'min': 10e-15, 'max': 1.055}},
                  'resistance': {'measure': {'min': 100e-6, 'max': 211e6}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param current_type: select between AC/DC
        :type current_type: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, type_=type_,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._type = type_

    @property
    def value(self):
        """
        **READONLY**

        **Returns the measured value for the specified type of measurement**

        **example:** *smu.channel[1].measure.resistance.value*

        :value: measured instantaneous voltage/current in V/A
        :type: float
        """
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        output_check = self._read(":OUTP:STAT?", dummy_data='1')
        if output_dict[output_check] == 'DISABLE':
            raise NotSupportedError("%s does not support measurements when output is DISABLED" % self.name)
        if self._type == 'voltage':
            return float(self._read(":MEAS:VOLT?"))
        elif self._type == 'current':
            return float(self._read(":MEAS:CURR?"))
        elif self._type == 'current':
            return float(self._read(":MEAS:RES?"))
