"""
| $Revision:: 283309                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-31 21:11:39 +0000 (Wed, 31 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------
"""
from ..base_source_meter import BaseSourceMeter
from ..base_source_meter import BaseSourceMeterChannel
from ..base_source_meter import BaseSourceMeterSourceParentBlock
from ..base_source_meter import BaseSourceMeterMeasureParentBlock
from ..base_source_meter import BaseSourceMeterSourceVoltageBlock
from ..base_source_meter import BaseSourceMeterSourceCurrentBlock
from ..base_source_meter import BaseSourceMeterMeasureBlock
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_exceptions import NotSupportedError
from COMMON.Utilities.custom_structures import CustomList


class Keithley24XX(BaseSourceMeter):
    """
    **Keithley 24XX Source Meter**
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
        """:type: list of Keithley24XXChannel"""


class Keithley24XXChannel(BaseSourceMeterChannel):
    """
    **Keithley24XX source meter output channel class**
    """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        **Initialize instance**

        :param channel_number: number targeting channel
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
        self.source = None

        """:type: Keithley24XXSourceParentBlock"""
        self.measure = None
        """:type: Keithley24XXMeasureParentBlock"""

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
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":SYST:BEEP:STAT?")]

    @beeper.setter
    def beeper(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 1, 'DISABLE': 0}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write(":SYST:BEEP:STAT %s" % input_dict[value])

    @property
    def output(self):
        """
        **Enable or Disable source meter output**

        **EXAMPLE:** *smu.channel[1].output = 'ENABLE'*

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read("OUTP:STAT?")]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 1, 'DISABLE': 0}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write("OUTP:STAT %s" % input_dict[value])

    @property
    def remote_sensing(self):
        """
        Enable or Disable remote sensing on source meter (2 or 4 wire sensing)

        **EXAMPLE:** *smu.channel[1].remote_sensing = 'ENABLE'*

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":SYST:RSEN?")]

    @remote_sensing.setter
    def remote_sensing(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            if value != self.remote_sensing:
                self.logger.info("Output Disabled")
            self._write(":SYST:RSEN %s" % input_dict[value])

    @property
    def terminal_select(self):
        """
        Select FRONT or REAR terminals on source meter

        **EXAMPLE:** *smu.channel[1].terminal_select = 'FRONT'*

        :value: - 'FRONT'
                - 'REAR'
        :type: str
        """
        output_dict = {'FRON': 'FRONT', 'REAR': 'REAR'}
        return str(output_dict[self._read(":ROUT:TERM?", dummy_data='FRON')])

    @terminal_select.setter
    def terminal_select(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not FRONT/REAR
        """
        value = value.upper()
        input_dict = {'FRONT': 'FRON', 'REAR': 'REAR'}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'FRONT' or 'REAR'")
        else:
            if value != self.terminal_select:
                self.logger.info("Output Disabled")
            self._write(":ROUT:TERM %s" % input_dict[value])


class Keithley24XXSourceParentBlock(BaseSourceMeterSourceParentBlock):
    """
    Keithley24XX source meter output channel class
    """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
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
        self.voltage = None
        """:type: Keithley24XXSourceVoltageBlock"""
        self.current = None
        """:type: Keithley24XXSourceCurrentBlock"""


class Keithley24XXMeasureParentBlock(BaseSourceMeterMeasureParentBlock):
    """
    Keithley24XX source meter output channel class
    """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
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
        self.voltage = None
        """:type: Keithley24XXMeasureBlock"""
        self.current = None
        """:type: Keithley24XXMeasureBlock"""
        self.resistance = None
        """:type: Keithley24XXMeasureBlock"""


class Keithley24XXSourceVoltageBlock(BaseSourceMeterSourceVoltageBlock):
    """
    Keithly24XX Source sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': None, 'warn': None, 'max': None},
                              'range': {'min': None, 'max': None}},
                  'current': {'source': {'min': None, 'warn': None, 'max': None},
                              'range': {'min': None, 'max': None}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._type = type_

    @property
    def _source_mode(self):
        """
        **READONLY**

        Stores which mode of operation the source meter is in

        :value: - 'VOLT'
                - 'CURR'
        :type: str
        """
        output_dict = {'VOLT': 'voltage', 'CURR': 'current'}
        return output_dict[str(self._read(":SOUR:FUNC?", dummy_data='VOLT'))]

    @property
    def compliance_current(self):
        """
        **Voltage/Current Compliance limit**\n

        **example:** *smu.channel[1].source.voltage.compliance_current = 0.5*

        :value: limit for voltage/current compliance
        :type: float
        """
        return float(self._read(":SENS:CURRent:PROT?"))

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

        self._write(":SENS:CURRent:PROT {0}".format(value))

    @property
    def compliance_current_tripped(self):
        """
        This command is used to determine if the source is in compliance

        :return:
        :rtype: bool
        """
        return bool(int(self._read(":VOLTage:PROTection:TRIPped?")))

    @property
    def range(self):
        """
        Voltage setpoint range

        **example:** *smu.channel[1].source.voltage.range = 1.2*

        :value: setpoint source range
        :type: float
        """
        return float(self._read(":SOUR:{0}:RANG?".format(self._type)))

    @range.setter
    def range(self, value):
        """"
        :type value: float or str
        """
        if isinstance(value, str) and value.upper() == 'AUTO':
            self._write(":SENS:%s:DC:RANGE:AUTO ON" % self._type)
        else:
            minimum = self.CAPABILITY['%s' % self._type]['source']['min']
            maximum = self.CAPABILITY['%s' % self._type]['source']['max']
            if minimum <= abs(value) <= maximum:
                self._write(":SOUR:%s:RANGE:AUTO OFF" % self._type)
                self._write(":SOUR:{0}:RANG {1}".format(self._type, value))
            elif abs(value) > maximum:
                raise ValueError('Valid {0} source range is between -{1} and {1}'.format(self._type, maximum))
            elif abs(value) < minimum:
                raise ValueError('Valid {0} source range is between -{1} and {1}'.format(self._type, minimum))

    @property
    def setpoint(self):
        """
        **Sets the voltage level on the specified output**

        **example:** *smu.channel[1].source.voltage.setpoint = 0.8*

        :value: voltage level setting in V/A
        :type: float
        """
        mode = self._source_mode
        if mode != self._type:
            raise NotSupportedError("Cannot read {0} set point when sourcing {1}"
                                    .format(self._type, mode))
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
            raise ValueError("Voltage supply minimum is limited to {1}".format(self._type, minimum))
        if abs(value) > maximum:
            raise ValueError('Please specify a {0} between -{1} and +{1}'.format(self._type, maximum))
        elif abs(value) > warning:
            self.logger.info("Set source and compliance limit may be out of calibration specification."
                             " Refer to equipment manual")

        if self._source_mode != self._type:
            if self._read(':SENS:RES:MODE?') == 'AUTO':
                self._write(":SENS:RES:RANGE:AUTO OFF")
                self.logger.info("Disabled resistance auto mode to allow source changing")
            self.logger.info("Source mode changed: Output Disabled")

        self._write(":SOUR:FUNC %s" % self._type)
        self._write(":SOUR:%s:MODE FIXED" % self._type)
        # self._write(":SOUR:{0}:RANG {1}".format(self._type, value))
        self._write(":SOUR:{0}:LEVEL {1}".format(self._type, value))


class Keithley24XXSourceCurrentBlock(BaseSourceMeterSourceCurrentBlock):
    """
    Keithly24XX Source sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': None, 'warn': None, 'max': None},
                              'range': {'min': None, 'max': None}},
                  'current': {'source': {'min': None, 'warn': None, 'max': None},
                              'range': {'min': None, 'max': None}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._type = type_

    @property
    def _source_mode(self):
        """
        **READONLY**

        **Stores which mode of operation the source meter is in**

        :value: - 'VOLT'
                - 'CURR'
        :type: str
        """
        output_dict = {'VOLT': 'voltage', 'CURR': 'current'}
        return output_dict[str(self._read(":SOUR:FUNC?", dummy_data='CURR'))]

    @property
    def compliance_voltage(self):
        """
        **Voltage/Current Compliance limit**

        **example:** *smu.channel[1].source.current.compliance_voltage = 2.6*

        :value: limit for voltage/current compliance
        :type: float
        """
        return float(self._read(":SENS:VOLTage:PROT?"))

    @compliance_voltage.setter
    def compliance_voltage(self, value):
        """
        :type value: float
        """

        if not self.dummy_mode:
            if self._type != self._source_mode:
                raise NotSupportedError("Cannot source Voltage and set Voltage compliance limit simultaneously. "
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

        self._write(":SENS:VOLTage:PROT {0}".format(value))

    @property
    def compliance_voltage_tripped(self):
        """
        This command is used to determine if the source is in compliance

        :return:
        :rtype: bool
        """
        return bool(int(self._read(":CURRent:PROTection:TRIPped?")))

    @property
    def range(self):
        """
        **Voltage/Current setpoint range**

        **example:** *smu.channel[1].source.current.range = 0.3*

        :value: setpoint source range
        :type: float
        """
        return float(self._read(":SOUR:{0}:RANG?".format(self._type)))

    @range.setter
    def range(self, value):
        """"
        :type value: float or str
        """
        if isinstance(value, str) and value.upper() == 'AUTO':
            self._write(":SENS:%s:DC:RANGE:AUTO ON" % self._type)
        else:
            minimum = self.CAPABILITY['%s' % self._type]['source']['min']
            maximum = self.CAPABILITY['%s' % self._type]['source']['max']
            if minimum <= abs(value) <= maximum:
                self._write(":SOUR:%s:RANGE:AUTO OFF" % self._type)
                self._write(":SOUR:{0}:RANG {1}".format(self._type, value))
            elif abs(value) > maximum:
                raise ValueError('Valid {0} source range is between -{1} and {1}'.format(self._type, maximum))
            elif abs(value) < minimum:
                raise ValueError('Valid {0} source range is between -{1} and {1}'.format(self._type, minimum))

    @property
    def setpoint(self):
        """
        **Sets the current level on the specified output**

        **example:** *smu.channel[1].source.current.setpoint = 0.15*

        :value: voltage/current level setting in V/A
        :type: float
        """
        mode = self._source_mode
        if mode != self._type:
            raise NotSupportedError("Cannot read {0} set point when sourcing {1}"
                                    .format(self._type, mode))
        return float(self._read(":SOUR:%s:LEVEL:IMM:AMPL?" % self._type))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        """
        minimum = self.CAPABILITY['%s' % self._type]['source']['min']
        maximum = self.CAPABILITY['%s' % self._type]['source']['max']
        warning = self.CAPABILITY['%s' % self._type]['source']['warn']

        if (abs(value) < minimum) and (abs(value) != 0):
            raise ValueError("{0} supply minimum is limited to {1}".format(self._type, minimum))
        if abs(value) > maximum:
            raise ValueError('Please specify a {0} between -{1} and +{1}'.format(self._type, maximum))
        elif abs(value) > warning:
            self.logger.info("Set source and compliance limit may be out of calibration specification."
                             " Refer to equipment manual")

        if self._source_mode != self._type:
            if self._read(':SENS:RES:MODE?') == 'AUTO':
                self._write(":SENS:RES:RANGE:AUTO OFF")
                self.logger.info("Disabling resistance auto mode to allow source changing")
            self.logger.info("Source mode changed: Output Disabled")

        self._write(":SOUR:FUNC %s" % self._type)
        self._write(":SOUR:%s:MODE FIXED" % self._type)
        # self._write(":SOUR:{0}:RANG {1}".format(self._type, value))
        self._write(":SOUR:{0}:LEVEL {1}".format(self._type, value))


class Keithley24XXMeasureBlock(BaseSourceMeterMeasureBlock):
    """
    Keithly24XX Source sub Block
    """
    CAPABILITY = {'voltage': {'measure': {'min': None, 'max': None}},
                  'current': {'measure': {'min': None, 'max': None}},
                  'resistance': {'measure': {'min': None, 'max': None}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._type = type_

    @property
    def _sense_mode(self):
        """
        **READONLY**

        **Stores which mode of operation the source meter is in**

        :value: - 'VOLT'
                - 'CURR'
        :type: str
        """
        output_dict = {'VOLT': 'voltage', 'CURR': 'current'}
        return output_dict[str(self._read(":SOUR:FUNC?",
                                          dummy_data='VOLT' if self._type == 'current' else 'CURR'))]

    @property
    def range(self):
        """
        **Voltage/Current/Resistance measurement range**

        **example1:** *smu.channel[1].measure.voltage.range = 3*

        **example2:** *smu.channel[1].measure.resistance.range = 10e3*

        :value: - 'AUTO', measurement is determined automatically by the source meter
                - float, manual range for voltage/current measurement
        :type: float or str
        """
        if "ON" == str(self._read(":SENS:%s:DC:RANGE:AUTO?" % self._type, dummy_data='ON')):
            return "AUTO"
        else:
            return float(self._read(":SENS:%s:RANG?" % self._type))

    @range.setter
    def range(self, value):
        """
        :type value: float or str
        """
        mode = self._sense_mode
        if mode == self._type:
            raise NotSupportedError("Cannot configure {0} measurement range when sourcing {1}"
                                    .format(self._type, mode))

        if isinstance(value, str) and value.upper() == 'AUTO':
            self._write(":SENS:%s:DC:RANGE:AUTO ON" % self._type)
        else:
            minimum = self.CAPABILITY['%s' % self._type]['measure']['min']
            maximum = self.CAPABILITY['%s' % self._type]['measure']['max']
            if minimum <= abs(value) <= maximum:
                self._write(":SENS:%s:RANGE:AUTO OFF" % self._type)
                self._write(":SENS:{0}:RANG {1}".format(self._type, value))
            elif abs(value) > maximum:
                raise ValueError('Valid {0} measurement range is between -{1} and {1}'.format(self._type, maximum))
            elif abs(value) < minimum:
                raise ValueError('Valid {0} measurement range is between -{1} and {1}'.format(self._type, minimum))

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
            return float(self._read("MEAS:VOLT?", dummy_data='1,2,3').split(",")[0])  # Dummy_mode error
        elif self._type == 'current':
            return float(self._read(":MEAS:CURR?", dummy_data='1,2,3').split(",")[1])  # Dummy_mode error
        elif self._type == 'resistance':
            return float(self._read(":MEAS:RES?", dummy_data='1,2,3').split(",")[2])  # Dummy_mode error
