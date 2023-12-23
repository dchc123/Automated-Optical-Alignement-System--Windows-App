"""
| $Revision:: 282442                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-09-18 17:22:41 +0100 (Tue, 18 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from ..base_source_meter import BaseSourceMeter
from ..base_source_meter import BaseSourceMeterChannel
from ..base_source_meter import BaseSourceMeterSourceParentBlock
from ..base_source_meter import BaseSourceMeterMeasureParentBlock
from ..base_source_meter import BaseSourceMeterSourceVoltageBlock
from ..base_source_meter import BaseSourceMeterSourceCurrentBlock
from ..base_source_meter import BaseSourceMeterMeasureBlock
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_exceptions import NotSupportedError
from CLI.Utilities.custom_structures import CustomList


class Keithley26XX(BaseSourceMeter):
    """
    Keithley 26XX Source Meter
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
        """:type: list of Keithley26XXChannel"""


class Keithley26XXChannel(BaseSourceMeterChannel):
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
        self.source = None
        """:type: Keithley26XXSourceParentBlock"""
        self.measure = None
        """:type: Keithley26XXMeasureParentBlock"""

    @property
    def output(self):
        """
        Disable or Enable source meter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read("OUTP%s:STAT?" % str(self._channel_number))]

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
            self._write("OUTP%s:STAT %s" % (str(self._channel_number), input_dict[value]))

    @property
    def remote_sensing(self):
        """
        Enable or Disable remote sensing on source meter (2 or 4 wire sensing)

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

        :value: - 'FRONT'
                - 'REAR'
        :type: str
        """
        output_dict = {'FRON': 'FRONT', 'REAR': 'REAR'}
        return str(output_dict[self._read(":ROUT:TERM?")])

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


class Keithley26XXSourceParentBlock(BaseSourceMeterSourceParentBlock):
    """
    Keithley26XX source meter output channel class
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
        """:type: Keithley26XXSourceVoltageBlock"""
        self.current = None
        """:type: Keithley26XXSourceVoltageBlock"""


class Keithley26XXMeasureParentBlock(BaseSourceMeterMeasureParentBlock):
    """
    Keithley26XX source meter output channel class
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
        """:type: Keithley26XXMeasureBlock"""
        self.current = None
        """:type: Keithley26XXMeasureBlock"""
        self.resistance = None
        """:type: Keithley26XXMeasureBlock"""


class Keithley26XXSourceVoltageBlock(BaseSourceMeterSourceVoltageBlock):
    """
    Keithly26XX Source sub Block
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
        Private:
        Stores which mode of operation the source meter is in

        :value: - 'VOLT'
                - 'CURR'
        :type: str
        """
        output_dict = {'VOLT': 'voltage', 'CURR': 'current'}
        return output_dict[str(self._read(":SOUR%s:FUNC?" % self._channel_number, dummy_data='VOLT'))]

    @property
    def compliance_current(self):
        """
        Voltage/Current Compliance limit
        :value: limit for voltage/current compliance
        :type: float
        """
        return float(self._read(":SENS%s:%s:PROT?" % (self._channel_number, self._type)))

    @compliance_current.setter
    def compliance_current(self, value):
        """
        :type value: float
        """

        if self._type == self._source_mode:
            raise NotSupportedError("Cannot source {0} and set {0} compliance limit".format(self._type))

        minimum = self.CAPABILITY['%s' % self._type]['source']['min']
        maximum = self.CAPABILITY['%s' % self._type]['source']['max']
        warning = self.CAPABILITY['%s' % self._type]['source']['warn']

        if (abs(value) < minimum) and (abs(value) != 0):
            raise ValueError("{0} supply minimum is limited to {1}".format(self._type, minimum))
        elif abs(value) > maximum:
            raise ValueError('Please specify a {0} between -{1} and +{1}'.format(self._type, maximum))
        elif abs(value) > warning:
            self.logger.info("Set compliance limit and source level may be exceeding calibration specification."
                             "Refer to equipment manual")

        self._write(":SENS%s:%s:PROT %s" % (self._channel_number, self._type, value))

    @property
    def range(self):
        """
        Voltage/Current setpoint range
        :value: setpoint source range
        :type: float
        """
        return float(self._read(":SENS%s:%s:RANG?" % (self._channel_number, self._type)))

    @range.setter
    def range(self, value):
        """"
        :type value: float or str
        """
        if isinstance(value, str) and value.upper() == 'AUTO':
            self._write(":SENS%s:%s:DC:RANGE:AUTO ON" % (self._channel_number, self._type))
        else:
            minimum = self.CAPABILITY['%s' % self._type]['source']['min']
            maximum = self.CAPABILITY['%s' % self._type]['source']['max']
            if minimum <= abs(value) <= maximum:
                self._write(":SOUR%s:%s:RANGE:AUTO OFF" % (self._channel_number, self._type))
                self._write(":SOUR%s:%s:RANG %s" % (self._channel_number, self._type, value))
            elif abs(value) > maximum:
                raise ValueError('Valid {0} measurement range is between -{1} and {1}'.format(self._type, maximum))
            elif abs(value) < minimum:
                raise ValueError('Valid {0} measurement range is between -{1} and {1}'.format(self._type, minimum))

    @property
    def setpoint(self):
        """
        :value: voltage/current level setting in V/A
        :type: float
        """
        mode = self._source_mode
        if mode != self._type:
            raise NotSupportedError("Cannot read {0}(object type) set point when sourcing {1}"
                                    .format(self._type, mode))
        return float(self._read(":SOUR%s:%s:LEVEL:IMM:AMPL?" % (self._channel_number, self._type)))

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
                self._write(":SENS:RES:RANGE:AUTO OFF" % self._type)
                self.logger.info("Disabling resistance auto mode to allow source changing")
            self.logger.info("Source mode changed: Output Disabled")

        self._write(":SOUR%s:FUNC %s" % (self._channel_number, self._type))
        self._write(":SOUR%s:%s:RANG %s" % (self._channel_number, self._type, value))
        self._write(":SOUR%s:%s:MODE FIXED" % (self._channel_number, self._type))
        self._write(":SOUR%s:%s:LEVEL %s" % (self._channel_number, self._type, value))


class Keithley26XXSourceCurrentBlock(BaseSourceMeterSourceCurrentBlock):
    """
    Keithly26XX Source sub Block
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
        Private:
        Stores which mode of operation the source meter is in

        :value: - 'VOLT'
                - 'CURR'
        :type: str
        """
        output_dict = {'VOLT': 'voltage', 'CURR': 'current'}
        return output_dict[str(self._read(":SOUR%s:FUNC?" % self._channel_number, dummy_data='VOLT'))]

    @property
    def compliance_voltage(self):
        """
        Voltage Compliance limit
        :value: limit for voltage compliance
        :type: float
        """
        return float(self._read(":SENS%s:%s:PROT?" % (self._channel_number, self._type)))

    @compliance_voltage.setter
    def compliance_voltage(self, value):
        """
        :type value: float
        """

        if self._type == self._source_mode:
            raise NotSupportedError("Cannot source {0} and set {0} compliance limit".format(self._type))

        minimum = self.CAPABILITY['%s' % self._type]['source']['min']
        maximum = self.CAPABILITY['%s' % self._type]['source']['max']
        warning = self.CAPABILITY['%s' % self._type]['source']['warn']

        if (abs(value) < minimum) and (abs(value) != 0):
            raise ValueError("{0} supply minimum is limited to {1}".format(self._type, minimum))
        elif abs(value) > maximum:
            raise ValueError('Please specify a {0} between -{1} and +{1}'.format(self._type, maximum))
        elif abs(value) > warning:
            self.logger.info("Set compliance limit and source level may be exceeding calibration specification."
                             "Refer to equipment manual")

        self._write(":SENS%s:%s:PROT %s" % (self._channel_number, self._type, value))

    @property
    def range(self):
        """
        Voltage/Current setpoint range
        :value: setpoint source range
        :type: float
        """
        return float(self._read(":SENS%s:%s:RANG?" % (self._channel_number, self._type)))

    @range.setter
    def range(self, value):
        """"
        :type value: float or str
        """
        if isinstance(value, str) and value.upper() == 'AUTO':
            self._write(":SENS%s:%s:DC:RANGE:AUTO ON" % (self._channel_number, self._type))
        else:
            minimum = self.CAPABILITY['%s' % self._type]['source']['min']
            maximum = self.CAPABILITY['%s' % self._type]['source']['max']
            if minimum <= abs(value) <= maximum:
                self._write(":SOUR%s:%s:RANGE:AUTO OFF" % (self._channel_number, self._type))
                self._write(":SOUR%s:%s:RANG %s" % (self._channel_number, self._type, value))
            elif abs(value) > maximum:
                raise ValueError('Valid {0} measurement range is between -{1} and {1}'.format(self._type, maximum))
            elif abs(value) < minimum:
                raise ValueError('Valid {0} measurement range is between -{1} and {1}'.format(self._type, minimum))

    @property
    def setpoint(self):
        """
        :value: voltage/current level setting in V/A
        :type: float
        """
        mode = self._source_mode
        if mode != self._type:
            raise NotSupportedError("Cannot read {0}(object type) set point when sourcing {1}"
                                    .format(self._type, mode))
        return float(self._read(":SOUR%s:%s:LEVEL:IMM:AMPL?" % (self._channel_number, self._type)))

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
                self._write(":SENS:RES:RANGE:AUTO OFF" % self._type)
                self.logger.info("Disabling resistance auto mode to allow source changing")
            self.logger.info("Source mode changed: Output Disabled")

        self._write(":SOUR%s:FUNC %s" % (self._channel_number, self._type))
        self._write(":SOUR%s:%s:RANG %s" % (self._channel_number, self._type, value))
        self._write(":SOUR%s:%s:MODE FIXED" % (self._channel_number, self._type))
        self._write(":SOUR%s:%s:LEVEL %s" % (self._channel_number, self._type, value))


class Keithley26XXMeasureBlock(BaseSourceMeterMeasureBlock):
    """
    Keithly26XX Source sub Block
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
    def _source_mode(self):
        """
        **READONLY**
        Private:
        Stores which mode of operation the source meter is in

        :value: - 'VOLT'
                - 'CURR'
        :type: str
        """
        output_dict = {'VOLT': 'voltage', 'CURR': 'current'}
        return output_dict[str(self._read(":SOUR%s:FUNC?" % self._channel_number, dummy_data='VOLT'))]

    @property
    def range(self):
        """
        Voltage/Current measurement range

        :value: - 'AUTO', measurement is determined automatically by the source meter
                - float, manual range for voltage/current measurement
        :type: float or str
        """
        if "ON" == str(self._read(":SENS:%s:DC:RANGE:AUTO?" % self._type, dummy_data='ON')):
            return "AUTO"
        else:
            return float(self._read(":SENS%s:%s:RANG?" % (self._channel_number, self._type)))

    @range.setter
    def range(self, value):
        """
        :type value: float or str
        """
        mode = self._source_mode
        if mode == self._type:
            raise NotSupportedError("Cannot configure {0} measurement range when sourcing {1}"
                                    .format(self._type, mode))

        if isinstance(value, str) and value.upper() == 'AUTO':
            self._write(":SENS{0}:{1}:DC:RANGE:AUTO ON".format(self._channel_number, self._type))
        else:
            minimum = self.CAPABILITY['%s' % self._type]['measure']['min']
            maximum = self.CAPABILITY['%s' % self._type]['measure']['max']
            if minimum <= abs(value) <= maximum:
                self._write(":SENS{0}:{1}:RANGE:AUTO OFF" .format(self._channel_number, self._type))
                self._write(":SENS{0}:{1}:RANG {2}".format(self._channel_number, self._type, value))
            elif abs(value) > maximum:
                raise ValueError('Valid {0} measurement range is between -{1} and {1}'.format(self._type, maximum))
            elif abs(value) < minimum:
                raise ValueError('Valid {0} measurement range is between -{1} and {1}'.format(self._type, minimum))

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous voltage/current/current in V/A/ohms
        :type: float
        """
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        output_check = self._read(":OUTP:STAT?", dummy_data='1')
        if output_dict[output_check] == 'DISABLE':
            raise NotSupportedError("%s does not support measurements when output is DISABLED" % self.name)
        if self._type == 'voltage':
            return float(self._read("MEAS:VOLT?").split(",")[0])  # Dummy_mode error
        elif self._type == 'current':
            return float(self._read(":MEAS:CURR?").split(",")[1])  # Dummy_mode error
        elif self._type == 'resistance':
            return float(self._read(":MEAS:RES?").split(",")[2])  # Dummy_mode error
