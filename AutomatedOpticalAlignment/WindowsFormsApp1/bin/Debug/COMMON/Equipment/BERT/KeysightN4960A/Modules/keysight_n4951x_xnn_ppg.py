"""

"""

from COMMON.Utilities.custom_exceptions import NotSupportedError
from COMMON.Equipment.BERT.base_bert import BaseBERTPatternGenerator

SI_PATTERN_RE = r'([\d]+[.]?[\d]*[yzafpnumkMGTPEZY]?)'
UNITS_RE = '(V|Hz|W|dB)'


class KeysightN4951XXNNPPG(BaseBERTPatternGenerator):
    """
    Keysight N4951 PPG channel
    """
    CAPABILITY = {'amplitude': {'min': None, 'max': None},
                  'frequency': {'min': None, 'max': None}}

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
        Return the amplitude value of the data logic level.
        Example
        :PG:DATA:LLEV:AMPL?
        0.800V

        :return: volts
        :rtype: float
        """
        result = self._read(f":PG:DATA:LLEV:AMPL?")
        return float(result[:result.find('V')])

    @amplitude.setter
    def amplitude(self, value=0.5):
        """
        Adjust the amplitude of the data eye presented at the data outputs from
        0.1 V to 1 V (N4951A),
        0.3 V to 3.0 V (N4951B-H17/H32), or
        0.3 V to 1.5 V (N4951B-D17/D32) in 0.005 V increments.
        """
        if self.CAPABILITY['amplitude']['min'] <= value <= self.CAPABILITY['amplitude']['max']:
            self._write(f":PG:DATA:LLEV:AMPL {value}V")
        else:
            raise ValueError('Please specify an amplitude between {} and {}'.format(
                self.CAPABILITY['amplitude']['min'], self.CAPABILITY['amplitude']['max']))

    @property
    def amplitude_mode(self):
        raise NotSupportedError

    @property
    def clock_output(self):
        pass

    @property
    def clock_source_rate(self):
        pass

    @property
    def data_output(self):
        pass

    @property
    def data_rate(self):
        return self._read("PG:DRAT?")

    @property
    def deemphasis(self):
        pass

    @property
    def deemphasis_mode(self):
        pass

    @property
    def external_attenuation(self):
        pass

    @property
    def offset(self):
        """
        Return the DC offset value of the data logic level.
        
        :return: Voltage
        :rtype: float
        """
        result = self._read(f":PG:DATA:LLEVel:OFFSet? (@ {self._channel_number})")
        return float(result[:result.find('V')])

    @property
    def output(self):
        """
        Queries the status of the data outputs of the pattern generators connected to channel 0 (Jitter) and
        channel 1 (Delay).

        :return: ON | OFF
        :rtype: str
        """
        return self._read(f":PG:DATA:OUTP? (@ {self._channel_number})")

    @output.setter
    def output(self, value):
        """

        :param value:
        :type value:
        :return:
        :rtype:
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF',
                      'EN': 'ON', 'DIS': 'OFF',
                      'ON': 'ON', 'OFF': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError(f'Please specify one of {input_dict.keys()}')
        else:
            self._write(f":PG:DATA:OUTP {input_dict[value]} (@ {self._channel_number})")

    @property
    def pattern(self):
        """
        Return the selected data pattern name.

        :return: data pattern
        :rtype: str
        """
        return self._read(":PG:DATA:PATTern:NAME?")

    @pattern.setter
    def pattern(self, value):
        """
        Select the data pattern name.

        :return:
        :rtype:
        """
        pattern_list = self.pattern_list
        if value in pattern_list:
            self._write(f":PG:DATA:PATTern:NAME {value}", type_='srq_sync')
        else:
            raise ValueError(f"Chose a pattern from pattern_list {pattern_list}")

    @property
    def pattern_list(self):
        """
        lists all the available patterns

        :return: pattern list
        :rtype: list
        """
        patterns = self._read(":PG:DATA:PATT:LIST:PRBS?").split(", ")
        patterns.append(self._read(":PG:DATA:PATT:LIST:FACT?").split(", "))
        patterns.append(self._read(":PG:DATA:PATT:LIST:USER?").split(", "))
        return patterns

    @property
    def polarity(self):
        """
        Return the data pattern polarity. The returned string is either normal or inverted.

        :return: polarity
        :rtype: str
        """
        output_dict = {'NONI': 'NORMAL', 'INV': 'INVERTED',
                       'INVerted': 'INVERTED', 'NONInvert': 'NORMAL'}
        return output_dict[self._read(":PG:DATA:PATTern:POLarity?")]

    @polarity.setter
    def polarity(self, value):
        """
        Set the data pattern polarity to invert, to invert the data pattern presented at the data outputs, or normal.
        The default is normal.

        :param value: inverted | normal
        :type value: str
        """
        value = value.upper()
        input_dict = {'NORMAL': 'NONInvert', 'INVERTED': 'INVerted'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'NORMAL' or 'INVERTED'")
        else:
            self._write(f":PG:DATA:PATTern:POLarity {input_dict[value]}")

    @property
    def termination_mode(self):
        pass

