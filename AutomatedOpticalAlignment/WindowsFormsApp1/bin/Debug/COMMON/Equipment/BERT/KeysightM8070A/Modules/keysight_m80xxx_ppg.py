"""
| $Revision:: 283373                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-11-05 15:48:33 +0000 (Mon, 05 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
import re
from math import ceil
from COMMON.Utilities.custom_exceptions import NotSupportedError
from COMMON.Equipment.BERT.base_bert import BaseBERTPatternGenerator


class KeysightM80XXXPPG(BaseBERTPatternGenerator):
    """
    Keysight PPG Channel
    """
    def __init__(self, module_id, module_name, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification number
        :type module_id: int
        :param module_name: module identification string
        :type module_name: str
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

        self._prbs_poly_xml_string = r'<sequenceDefinition ' \
                                     r'xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
                                     r'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                                     r'xmlns="http://www.agilent.com/schemas/M8000/DataSequence">' \
                                     r'<description />' \
                                     r'<sequence>' \
                                     r'<loop>' \
                                     r'<block length="1024">' \
                                     r'<prbs polynomial="2^31-1" />' \
                                     r'</block>' \
                                     r'</loop>' \
                                     r'</sequence>' \
                                     r'</sequenceDefinition>'

        self._module_id = module_id
        self._module_name = module_name
        self._channel_number = channel_number

        self._amplitude_mode = None
        self.amplitude_mode = 'SINGLE'

        self.deemphasis_coefficient = 3

        self._external_attenuation = None
        self.external_attenuation = 0

        self._pattern = None

    @property
    def amplitude(self):
        """
        Data amplitude after external attenuation

        :value: data amplitude in V
        :type: float
        """
        mode = self.amplitude_mode

        if mode == "DIFFERENTIAL":
            return float(self._read(":VOLTage? 'M{}.DataOut{}'".format(self._module_id,
                                                                       self._channel_number)))*2
        else:
            return float(self._read(":VOLTage? 'M{}.DataOut{}'".format(self._module_id,
                                                                       self._channel_number)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        amplitude = self._calculate_preattenuation_amplitude(value)
        mode = self.amplitude_mode

        # Keysight BERT is programmed with single ended voltage
        if mode == "DIFFERENTIAL":
            self._write(":VOLTage 'M{}.DataOut{}', {}V".format(
                self._module_id, self._channel_number, float(amplitude/2.0)),
                dummy_data=amplitude/2.0)
        else:
            self._write(":VOLTage 'M{}.DataOut{}', {}V".format(
                self._module_id, self._channel_number, amplitude), dummy_data=amplitude)

    @property
    def amplitude_mode(self):
        """
        Data amplitude mode

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
        :type: str
        """
        return self._amplitude_mode

    @amplitude_mode.setter
    def amplitude_mode(self, value):
        """
        :type value: str
        """
        value = value.upper()
        if value not in ['DIFFERENTIAL', 'SINGLE']:
            raise ValueError("Please specify either 'DIFFERENTIAL' or 'SINGLE'")
        else:
            self._amplitude_mode = value

    @property
    def frequency(self):
        """
        Frequency that the 32G PPG module outputs.

        :value: desired bit rate (in Hertz)
        :type: float
        :raise ValueError: exception if bit rate is not in the range of 0 to 32.1 GHz
        """
        return float(self._read(":FREQ? 'M{}.ClkGen'".format(self._module_id)))

    @frequency.setter
    def frequency(self, value):
        """
        :type value:: float
        :raise ValueError: exception if bit rate is not in the range of 0 to 32.1 GHz
        """
        if value < 2025000000 or value > 64828000000:
            raise ValueError("Clock frequency must be in the range of 2.025 Ghz to 64.828 GHz")
        else:
            self._write(":FREQ 'M{}.ClkGen', {}".format(self._module_id, value))

    @property
    def clock_divider(self):
        """
        Channel clock divider

        :value: - 2
                - 4
                - 8
                - 16
        :type: int
        """
        return int(self._read(":OUTPut:DIVider? 'M{}.ClkOut{}'".format(
            self._module_id, self._channel_number), dummy_data='DIV2').strip('DIV'))

    @clock_divider.setter
    def clock_divider(self, value):
        """
        :type value: int
        """
        if value in [2, 4, 8, 16]:
            self._write(":OUTPut:DIVider 'M{}.ClkOut{}', DIV{}".format(self._module_id,
                                                                       self._channel_number,
                                                                       value))
        else:
            raise ValueError("Please specify a valid input: 2, 4, 8, 16")

    @property
    def clock_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":OUTPut? 'M{}.ClkOut{}'".format(
            self._module_id, self._channel_number), dummy_data='OFF')]

    @clock_output.setter
    def clock_output(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTPut 'M{}.ClkOut{}', {}".format(self._module_id, self._channel_number,
                                                            input_dict[value]))

    @property
    def clock_source_rate(self):
        """
        Clock recovery source rate

        :value: - 'HALF'
                - 'FULL'
        :type: str
        """
        raise NotSupportedError('Keysight BERT does not support clock source rate')

    @clock_source_rate.setter
    def clock_source_rate(self, value):
        """
        :type value: str
        """
        raise NotSupportedError('Keysight BERT does not support clock source rate')

    @property
    def clock_source(self):
        """
        Clock source to the PPG, whether it be a built in synthesizer/jitter generation
        source or an external synthesizer

        :value: - 'EXTERNAL'
                - 'INTERNAL'
        :type: str
        :raise ValueError: exception if clock soruce is neither INTERNAL nor EXTERNAL
        """
        output_dict = {'INT': 'INTERNAL', 'REF': 'EXTERNAL'}
        return output_dict[self._read(":TRIGger:SOURce? 'M{}.ClkGen'".format(
            self._module_id), dummy_data='INT')]

    @clock_source.setter
    def clock_source(self, value):  # TODO: [ael-khouly] add polling, current one not working
        """
        :type value:: str
        :raise ValueError: exception if clock soruce is neither INTERNAL nor EXTERNAL
        """
        value = value.upper()
        input_dict = {'INTERNAL': 'INT', 'EXTERNAL': 'REF'}
        if value not in input_dict.keys():
            raise ValueError("%s is an invalid clock source. Please select 'INTERNAL'"
                             " or 'EXTERNAL'." % value)
        else:
            self._write(":TRIGger:SOURce 'M{}.ClkGen', {}".format(self._module_id,
                                                                  input_dict[value]),
                        type_='stb_poll_sync')

    @property
    def output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":OUTPut? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTPut 'M{}.DataOut{}', {}".format(self._module_id, self._channel_number,
                                                             input_dict[value]))

    @property
    def deemphasis(self):
        """
        :value: data de-emphasis in dB
        :type: float
        """
        return float(self._read(":OUTPut:DEEM:CURS:MAGN{}? "
                                "'M{}.DataOut{}'".format(self.deemphasis_coefficient,
                                                         self._module_id,
                                                         self._channel_number)))

    @deemphasis.setter
    def deemphasis(self, value):
        """
        :type value: float
        """
        self._write(":OUTPut:DEEM:CURS:MAGN{}"
                    " 'M{}.DataOut{}', {}" .format(self.deemphasis_coefficient,
                                                   self._module_id,
                                                   self._channel_number, value))

    @property
    def deemphasis_coefficient(self):
        """
        Data de-emphasis coefficient

        :value: - 1
                - 2
                - 3
        :type: int
        """
        return self._deemphasis_coefficient

    @deemphasis_coefficient.setter
    def deemphasis_coefficient(self, value):
        """
        :type value: int
        """
        if value not in [1, 2, 3]:
            raise ValueError("Deemphasis coefficients can either be 1, 2 or 3")
        else:
            self._deemphasis_coefficient = value

    @property
    def deemphasis_mode(self):  # TODO: Masks coefficient
        """
        Data de-emphasis mode

        :value: - 'PRE'
                - 'POST'
        :type: str
        """
        output_dict = {1: 'PRE', 3: 'POST', 2: None}
        return output_dict[self.deemphasis_coefficient]

    @deemphasis_mode.setter
    def deemphasis_mode(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'PRE': 1, 'POST': 3}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'PRE' or POST'")
        else:
            self.deemphasis_coefficient = input_dict[value]

    @property
    def external_attenuation(self):
        """
        External attenuation value. It is used to calculate amplitude post attenuation

        :value: external attenuation in dB. Value is the "loss", so negative values
                interpreted as amplification.
        :type: int
        """
        return self._external_attenuation

    @external_attenuation.setter
    def external_attenuation(self, value):
        """
        :type value: int
        """
        self._external_attenuation = value

    @property
    def external_clock_frequency(self):
        """
        External clock frequency

        :value: - 10e6
                - 100e6
        :type: float
        """
        output_dict = {'REF10': 10e6, 'REF100': 100e6}
        return output_dict[self._read(":TRIGger:REFerence:FREQuency? 'M{}.ClkGen'".format(
            self._module_id), dummy_data='REF10')]

    @external_clock_frequency.setter
    def external_clock_frequency(self, value):
        """
        :type: float
        """
        if value not in [10e6, 100e6]:
            raise ValueError('External clock frequency is only valid for 10MHz and 100MHz')
        else:
            self._write(":TRIGger:REFerence:FREQuency 'M{}.ClkGen', REF{}".format(self._module_id,
                                                                                  int(value/1e6)))

    @property
    def global_clock_amplitude(self):
        """
        Data amplitude after external attenuation

        :value: data amplitude in V
        :type: float
        """
        mode = self.amplitude_mode
        if mode == "DIFFERENTIAL":
            return float(self._read(":VOLTage? 'M{}.ClkOut'".format(self._module_id)))*2
        else:
            return float(self._read(":VOLTage? 'M{}.ClkOut'".format(self._module_id)))

    @global_clock_amplitude.setter
    def global_clock_amplitude(self, value):
        """
        :type value: float
        """
        amplitude = self._calculate_preattenuation_amplitude(value)
        mode = self.amplitude_mode

        # Keysight BERT is programmed with single ended voltage
        if mode == "DIFFERENTIAL":
            self._write(":VOLTage 'M{}.ClkOut', {}V".format(
                self._module_id, float(amplitude/2.0)), dummy_data=amplitude/2.0)
        else:
            self._write(":VOLTage 'M{}.ClkOut', {}V".format(
                self._module_id, amplitude), dummy_data=amplitude)

    @property
    def global_clock_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":OUTPut? 'M{}.ClkOut'".format(
            self._module_id), dummy_data='OFF')]

    @global_clock_output.setter
    def global_clock_output(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTPut 'M{}.ClkOut', {}".format(self._module_id, input_dict[value]))

    @property
    def global_clock_divider(self):
        """
        Global clock divider

        :value: - 2
                - 4
                - 8
                - 16
        :type: int
        """
        return int(self._read(":OUTPut:DIVider? 'M{}.ClkOut'".format(
            self._module_id), dummy_data='DIV2').strip('DIV'))

    @global_clock_divider.setter
    def global_clock_divider(self, value):
        """
        :type value: int
        """
        if value in [2, 4, 8, 16]:
            self._write(":OUTPut:DIVider 'M{}.ClkOut', DIV{}".format(self._module_id, value))
        else:
            raise ValueError("Please specify a valid input: 2, 4, 8, 16")

    @property
    def offset(self):
        """
        :value: DC offset in V
        :type: float
        """
        return float(self._read(":VOLT:OFFS? 'M{}.DataOut{}'".format(self._module_id,
                                                                     self._channel_number)))

    @offset.setter
    def offset(self, value):
        """
        :type value: float
        """
        if self.termination_mode == 'DC':
            self._write(":VOLT:OFFS 'M{}.DataOut{}', {}".format(self._module_id,
                                                                self._channel_number,
                                                                value))
        else:
            self.logger.warning("Termination mode was changed to 'DC' and back to 'AC' to allow"
                                " for offset change")

            self.termination_mode = 'DC'
            self._write(":VOLT:OFFS 'M{}.DataOut{}', {}".format(self._module_id,
                                                                self._channel_number,
                                                                value))
            self.termination_mode = 'AC'

    @property
    def output_delay(self):
        """
        Sets teh time from the start of the period to the first edge of the pulse

        :value: time in seconds
        :type: float
        """
        return float(self._read(":SOUR:PULSe:DELay? 'M{0}.DataOut{1}'".format(self._module_id, self._channel_number)))

    @output_delay.setter
    def output_delay(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            capability_dict = {"M8041A": [0, 100e-9],
                               "M8195A": [-1e-9, 1e-9],
                               "M8062A": [0, 100e-9],
                               "M8045A": [0, 100e-9]}

            if self._module_name in capability_dict:
                if capability_dict[self._module_name][0] <= value <= capability_dict[self._module_name][1]:
                    self._write(":SOUR:PULSe:DELay 'M{0}.DataOut{1}', {2}".format(self._module_id, self._channel_number,
                                                                                  value))
                else:
                    raise ValueError('Valid range is between {0} and {1}'.format(capability_dict[self._module_name][0],
                                                                                 capability_dict[self._module_name][1]))
            else:
                raise NotSupportedError('Module {0} does not support this feature'.format(self._module_name))
        else:
            raise TypeError('output_delay must be a float')

    @property
    def pattern(self):
        """
        Desired PRBS or user pattern

        :value: - 'PRBS7'
                - 'PRBS9'
                - 'PRBS10'
                - 'PRBS11'
                - 'PRBS15'
                - 'PRBS20'
                - 'PRBS23'
                - 'PRBS31'
                - Hex string i.e. 'H02948ACFE'
                - Bin string i.e. 'B010101100'
                - <file_path>
        :type: str or list
        :raise ValueError: exception if option is not binary, hex,
         PRBS or a list input for saved patterns
        """
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        """
        :type value: str or list
        :raise ValueError: exception if option is not binary, hex,
         PRBS or a list input for saved patterns
        """
        self._pattern = value
        if value[0] == 'P':
            self.prbs_pattern = value
        elif value[0] == "H" or value[0] == 'B':
            self.user_pattern = value
        else:
            if isinstance(value, list):
                self.saved_pattern = value
            else:
                raise ValueError("Please specify either 'PRBSX', 'BXXXXXXX',"
                                 " 'HXXXXXXX'. If you are loading "
                                 "a saved pattern, please pass a list [file_path, pattern_length]")

    @property
    def polarity(self):
        """
        Data output polarity

        :value: - 'NORMAL'
                - 'INVERTED'
        :type: str
        """
        output_dict = {'NORM': 'NORMAL', 'INV': 'INVERTED',
                       'INVerted': 'INVERTED', 'NORMal': 'NORMAL'}
        return output_dict[self._read(":OUTPut:POLarity? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='NORM')]

    @polarity.setter
    def polarity(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'NORMAL': 'NORMal', 'INVERTED': 'INVerted'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'NORMAL' or 'INVERTED'")
        else:
            self._write(":OUTPut:POLarity 'M{}.DataOut{}', {}".format(self._module_id,
                                                                      self._channel_number,
                                                                      input_dict[value]))

    @property
    def prbs_pattern(self):
        """
        Desired PRBS pattern

        :value: - 'PRBS7'
                - 'PRBS9'
                - 'PRBS10'
                - 'PRBS11'
                - 'PRBS15'
                - 'PRBS20'
                - 'PRBS23'
                - 'PRBS31'
        :type: str
        """
        return self._pattern

    @prbs_pattern.setter
    def prbs_pattern(self, value):
        """
        :type value: str
        """
        if value[0] != 'P':
            raise ValueError("Please specify 'PRBSX'")

        pattern = value[4:]  # strip "PRBS" off of pattern string
        xml_command_string = re.sub(r'prbs polynomial="2\^31-1"',
                                    r'prbs polynomial="2^{}-1"'.format(pattern),
                                    self._prbs_poly_xml_string)

        xml_command_string = '#3%d' % len(xml_command_string) + xml_command_string

        self._write(':DATA:SEQuence:VALue "Generator",{}'.format(xml_command_string))
        self._pattern = value

    @property
    def saved_pattern(self):
        """
        Desired saved pattern

        :value: [file_path, length]
        :type: list
        """
        return self._pattern

    @saved_pattern.setter
    def saved_pattern(self, value):
        """
        :type value: list
        """
        if not isinstance(value, list):
            raise ValueError('Please enter [pattern path, pattern length] as a list')

        xlm_string_generator = r'<?xml version="1.0" encoding="utf-16"?>' \
                               r'<sequenceDefinition ' \
                               r'xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
                               r'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                               r'xmlns="http://www.agilent.com/schemas/M8000/DataSequence">' \
                               r'<version>1.0.0</version><description />' \
                               r'<sequence>' \
                               r'<loop>' \
                               r'<block length="%d">' \
                               r'<pattern source="%s"/>' \
                               r'</block>' \
                               r'</loop>' \
                               r'</sequence>' \
                               r'</sequenceDefinition>' % (value[1], value[0])

        xlm_cmd_string_generator = '#3%d' % len(xlm_string_generator) + xlm_string_generator
        self._write(':DATA:SEQuence:VALue "Generator",{}'.format(xlm_cmd_string_generator))
        self._pattern = value

    @property
    def signal_type(self):
        """
        Signal type

        :value: - 'NRZ'
                - 'PAM4'
        :type: str
        :raise ValueError: exception if type is not NRZ or PAM4
        """
        return self._read(":DATA:LINecoding? 'M{}.DataOut{}'".format(self._module_id,
                                                                     self._channel_number),
                          dummy_data='NRZ')

    @signal_type.setter
    def signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if type is not NRZ or PAM4
        """
        raise NotSupportedError('Keysight BERT does not allow you to change a signal type on a single channel/module.'
                                'Please use bert.global_ppg_signal_type instead')

    def symbol_mapping(self, value):
        """
        Symbol Mapping method which combines both symbol mapping CLI properties

        :value: - 'NONE'
                - 'GRAY'
                - 'CUST'
                -  ['11','00','01','10']
        :type: str or list of strings
        :rtype: ValueError: exception if type is not NONE or GRAY or CUST or list of symbols
        """
        if isinstance(value, list):
            if len(value) == 4:
                if all(isinstance(n, str) for n in value):  # if list of strings with length 4
                    self.symbol_mapping_mode = 'CUST'
                    self.symbol_custom_mapping = value
        elif isinstance(value, str):
            self.symbol_mapping_mode = value
        else:
            raise ValueError("Method only accepts str or list of strings. See docstring")

    @property
    def symbol_mapping_mode(self):
        """
        Symbol mapping mode

        :value: - 'NONE'
                - 'GRAY'
                - 'CUST'
        :type: str
        :raise ValueError: exception if type is not NONE or GRAY or CUST
        """
        return self._read(":DATA:LINecoding:PAM4:MAPP? 'M{}.DataOut{}'".format(self._module_id, self._channel_number),
                          dummy_data='NONE')

    @symbol_mapping_mode.setter
    def symbol_mapping_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if type is not NONE or GRAY or CUST
        """
        self._write(":DATA:LINecoding:PAM4:MAPP 'M{}.DataOut{}', {}".format(self._module_id,
                                                                            self._channel_number,
                                                                            value.upper()))

    @property
    def symbol_custom_mapping(self):
        """
        Custom symbol mapping

        :value: comma separated str of symbol encoding (i.e ['11','00','01','10'] (no spaces))
        :type: list of str
        :raise ValueError: exception if type is not list of str
        """
        return self._read(":DATA:LINecoding:PAM4:MAPP:CUST? 'M{}.DataOut{}'".format(self._module_id,
                                                                                    self._channel_number))

    @symbol_custom_mapping.setter
    def symbol_custom_mapping(self, value):
        """
        :type value: list of str
        :raise ValueError: exception if type is not list of str
        """
        if self.symbol_mapping_mode == 'CUST':
            mapping = ''
            for n in range(4):  # converts list to string
                if n != 3:
                    mapping += value[n] + ','
                else:
                    mapping += value[n]
            self._write(":DATA:LINecoding:PAM4:MAPP:CUST 'M{}.DataOut{}', {}".format(self._module_id,
                                                                                     self._channel_number,
                                                                                     mapping))
        else:
            raise NotSupportedError("{0} must be in 'custom' symbol mapping mode to define the custom symbol mapping"
                                    .format(self.name))

    @property
    def termination_mode(self):
        """
        Data termination mode

        :value: - 'AC'
                - 'DC'
        :type: str
        :raise ValueError: exception if mode is not AC or DC
        """
        return self._read(":OUTPut:COUPling? 'M{}.DataOut{}'".format(self._module_id,
                                                                     self._channel_number),
                          dummy_data='AC')

    @termination_mode.setter
    def termination_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode is not AC or DC
        """
        value = value.upper()
        if value not in ['AC', 'DC']:
            raise ValueError('Please specify mode either as "AC" or "DC"')
        self.output = 'DISABLE'
        self._write(":OUTPut:COUPling 'M{}.DataOut{}', {}".format(self._module_id,
                                                                  self._channel_number,
                                                                  value))
        self.output = 'ENABLE'

    @property
    def trigger_amplitude(self):
        """
        Trigger amplitude

        :value: data amplitude in V
        :type: float
        """
        mode = self.amplitude_mode

        if mode == "DIFFERENTIAL":
            return float(self._read(":VOLTage? 'M{}.TrigOut'".format(self._module_id,
                                                                       self._channel_number)))*2
        else:
            return float(self._read(":VOLTage? 'M{}.TrigOut'".format(self._module_id,
                                                                       self._channel_number)))

    @trigger_amplitude.setter
    def trigger_amplitude(self, value):
        """
        :type value: float
        """
        mode = self.amplitude_mode

        # Keysight BERT is programmed with single ended voltage
        if mode == "DIFFERENTIAL":
            self._write(":VOLTage 'M{}.TrigOut', {}V".format(
                self._module_id, float(value/2.0)),
                dummy_data=value/2.0)
        else:
            self._write(":VOLTage 'M{}.TrigOut', {}V".format(
                self._module_id, value), dummy_data=value)

    @property
    def trigger_divider(self):
        """
        Channel trigger divider

        :value: between 4 and 65532
        :type: int
        """
        return int(self._read(":OUTPut:TRIGger:DIVider? 'M{}.TrigOut'".format(self._module_id),
                              dummy_data=2))

    @trigger_divider.setter
    def trigger_divider(self, value):
        """
        :type value: int
        """
        if 4 <= value <= 65532:
            self._write(":OUTPut:TRIGger:DIVider 'M{}.TrigOut', {}".format(self._module_id, value))
        else:
            raise ValueError("Please specify a valid input: between 4 and 65532")

    @property
    def trigger_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":OUTPut? 'M{}.TrigOut'".format(
            self._module_id), dummy_data='OFF')]

    @trigger_output.setter
    def trigger_output(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTPut 'M{}.TrigOut', {}".format(self._module_id, input_dict[value]))

    @property
    def user_pattern(self):
        """
        Desired user pattern

        :value: - Hex string i.e. 'H02948ACFE'
                - Bin string i.e. 'B010101100'
        :type: str
        """
        return self._pattern

    @user_pattern.setter
    def user_pattern(self, value):
        """
        :type value: str
        """
        # XML string for clearing Generator pattern
        clear_xml = r'<?xml version="1.0" encoding="utf-16"?>' \
                    r'<sequenceDefinition xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
                    r'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                    r'xmlns="http://www.agilent.com/schemas/M8000/DataSequence">' \
                    r'<description />' \
                    r'<sequence />' \
                    r'</sequenceDefinition>'
        clear_xml = '#3%d' % len(clear_xml) + clear_xml

        self._write(':DATA:SEQuence:VALue "Generator",{}'.format(clear_xml))

        if value[0] == "H":
            # Convert hex string to hex number, convert to binary string, strip off "0b"
            pattern = bin(int(value[1:], 16))[2:]
        elif value[0] == "B":
            # Strip off leading "B"
            pattern = value[1:]
        else:
            raise ValueError('User patterns must start with either a "B" or an "H" ')

        command_str = ':DATA:PATTern:IDATa "shared:myGeneratorPattern",0,{}'.format(len(pattern))
        num_bytes = int(ceil(float(len(pattern)) / 8))

        for i in range(num_bytes):
            # Get a 1-byte slice from the pattern
            byte_ = pattern[i * 8:(i * 8) + 8]
            # Pad zeros to end of byte if less than 8 bits left
            if len(byte_) < 8:
                byte_ += "0" * (8 - len(byte_))
            # Convert to int
            byte_ = int(byte_, 2)
            # Append to the command string
            command_str += (",%d" % byte_)

        self._write(':DATA:PATTern:USE "shared:myGeneratorPattern",{}'.format(len(pattern)))
        self._write(command_str)

        # XML string for using new pattern
        pattern_xml = r'<?xml version="1.0" encoding="utf-16"?>' \
                      r'<sequenceDefinition xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
                      r'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                      r'xmlns="http://www.agilent.com/schemas/M8000/DataSequence">' \
                      r' <description />' \
                      r'<sequence>' \
                      r' <loop>' \
                      r'<block length="%d">' \
                      r'<pattern source="shared:myGeneratorPattern" />' \
                      r'</block>' \
                      r' </loop>' \
                      r'</sequence>' \
                      r'</sequenceDefinition>' % len(pattern)
        pattern_xml = '#3%d' % len(pattern_xml) + pattern_xml

        self._write(':DATA:SEQuence:VALue "Generator",{}'.format(pattern_xml))
        self._pattern = value

    def _calculate_preattenuation_amplitude(self, amplitude, external_attenuation=None):
        """
        Calculates the output voltage required for a given external attenuation. For example,
        if 1Vpp output swing is desired, but there is 6dB of attenuation, this method will
        calculate the required amplitude at the BERT, which in this example, is 2Vpp.

        :param amplitude: desired voltage after attenuation (in Volts)
        :type amplitude: float
        :param external_attenuation: external attenuation if different from value stored on
        object (in dB). Value is the "loss", so negative values interpreted as amplification
        :type external_attenuation: int
        :param signal_mode: select signal mode {'DATA', 'XDATA'}
        :type: str
        :return: the required output voltage at the BERT (in Volts)
        :rtype: float
        """
        if external_attenuation is None:
            external_attenuation = self.external_attenuation

        attenuation_factor = 10.0 ** (-external_attenuation / 20)

        # Required amplitude (in Volts)
        amplitude = (float(amplitude) / attenuation_factor)

        return amplitude
