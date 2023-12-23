"""
| $Revision:: 283744                                   $:  Revision of last commit
| $Author:: wleung@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-11-19 19:48:10 +0000 (Mon, 19 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------
"""
from CLI.Equipment.BERT.base_bert import BaseBERTPatternGenerator
from CLI.Utilities.custom_exceptions import NotSupportedError


class AnritsuMP1800PPG(BaseBERTPatternGenerator):
    """
    Anritsu MP1800 Pattern Generator Module
    """
    def __init__(self, module_id, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
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
        self._module_id = module_id
        self._min_amplitude = 0.25
        self._max_amplitude = 2.5
        self._pattern = None
        self.amplitude_mode = 'SINGLE'

    def _open_pattern_file(self, file_path):
        try:
            # If absolute path is not provided
            if file_path[1] != ':':
                file_path = "C:\\Program Files\\Anritsu\\MP1800A\\Pattern Files\\" + file_path
            self._write(':SYSTem:MMEMory:PATTern:RECall "' + file_path + '", BIN')
            self._pattern = file_path
        except RuntimeError:
            try:
                self._write(':SYSTem:MMEMory:PATTern:RECall "' + file_path + '", TXT')
                self._pattern = file_path
            except RuntimeError:
                raise ValueError("Invalid file path used. Only .ptn and .txt files allowed. "
                                 "Do not include file extension.")

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)

    @property
    def amplitude(self):
        """
        Data amplitude after external attenuation

        :value: data amplitude in V
        :type: float or dict
        :raise ValueError: exception if mode is not SINGLE or DIFFERENTIAL
        """
        self._select_mod()

        return {'DATA': float(self._read(":OUTput:DATA:AMPLitude? DATA", dummy_type='float')),
                'XDATA': float(self._read(":OUTput:DATA:AMPLitude? XDATA", dummy_type='float'))}

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value:: float or dict[str, float]
        :raise ValueError: exception if mode is not SINGLE or DIFFERENTIAL
        """

        self._select_mod()

        if not isinstance(value, dict):
            value = {'DATA': value, 'XDATA': value}

        ampl_div = 1
        if self._amplitude_mode == 'DIFFERENTIAL':
            ampl_div = 2

        for key in value.keys():
            value[key] = self._calculate_preattenuation_amplitude(value[key]) / ampl_div

            # This BERT is limited to a range of [0.5,3.5] Volts
            if self._max_amplitude < value[key] < self._min_amplitude:
                raise ValueError('Please specify an amplitude between {} and {}'.format(
                    self._max_amplitude, self._min_amplitude))

        if self.data_tracking == "DISABLE":     # set both P and N separately
            self._write(":OUTput:DATA:AMPLitude DATA, %s" % value['DATA'])
            self._write(":OUTput:DATA:AMPLitude XDATA, %s" % value['XDATA'])
        elif self.data_tracking == 'ENABLE':    # both ports share P setting
            self._write(":OUTput:DATA:AMPLitude DATA, %s" % value['DATA'])
        else:
            raise ValueError("'%s' is an invalid mode." % self.data_tracking)

    @property
    def amplitude_mode(self):
        """
        Data amplitude mode

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
        :type: str
        """
        self._select_mod()

        return self._amplitude_mode

    @amplitude_mode.setter
    def amplitude_mode(self, value):
        """
        :type value: str
        """
        self._select_mod()

        self._amplitude_mode = value

    @property
    def clock_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(':OUTPut:CLOCk:OUTPut?')]

    @clock_output.setter
    def clock_output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTPut:CLOCk:OUTPut %s" % (input_dict[value]))

    @property
    def clock_source_rate(self):
        """
        Clock recovery source rate

        :value: - 'HALF'
                - 'FULL'
        :type: str
        """
        self._select_mod()

        return self._read(':SYSTem:OUTPut:CRATe?')

    @clock_source_rate.setter
    def clock_source_rate(self, value):
        """
        :type value: str
        :raise ValueError: exception if clock source rate is neither "HALF" nor "FULL"
        """
        self._select_mod()

        if value not in ['HALF', 'FULL']:
            raise ValueError('Rate can either be "HALF" or "FULL"')
        self._write(':SYSTem:OUTPut:CRATe %s' % value)

    @property
    def data_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":OUTPut:DATA:OUTPut?")]

    @data_output.setter
    def data_output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTPut:DATA:OUTPut %s" % input_dict[value])

    @property
    def data_tracking(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":OUTPut:DATA:TRACking?")]

    @data_tracking.setter
    def data_tracking(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTPut:DATA:TRACking %s" % input_dict[value], dummy_data=input_dict[value])

    @property
    def deemphasis(self):
        """
        :value: data de-emphasis in dB
        :type: int
        """
        raise NotSupportedError('%s: Deemphasis functionalities are not supported' % self.name)

    @deemphasis.setter
    def deemphasis(self, value):
        """
        :type value: int
        """
        raise NotSupportedError('%s: Deemphasis functionalities are not supported' % self.name)

    @property
    def deemphasis_mode(self):
        """
        Data de-emphasis mode

        :value: - 'PRE'
                - 'POST'
        :type: str
        """
        raise NotSupportedError('%s: Deemphasis functionalities are not supported' % self.name)

    @deemphasis_mode.setter
    def deemphasis_mode(self, value):
        """
        :type value: str
        """
        raise NotSupportedError('%s: Deemphasis functionalities are not supported' % self.name)

    @property
    def external_attenuation(self):
        """
        External attenuation value. It is used to calculate amplitude post attenuation

        :value: external attenuation in dB. Value is the "loss", so negative values
                interpreted as amplification.
        :type: int or dict[str, int]
        """
        self._select_mod()

        return {'DATA': int(self._read(":OUTPut:DATA:ATTFactor? DATA", dummy_type='int')),
                'XDATA': int(self._read(":OUTPut:DATA:ATTFactor? XDATA", dummy_type='int'))}

    @external_attenuation.setter
    def external_attenuation(self, value):
        """
        :type value: int or dict[str, int]
        :raise ValueError: exceiption if input not between 0 and 40
        """
        self._select_mod()

        if isinstance(value, dict):
            if 40 < value['DATA'] < 0 or 40 < value['XDATA'] < 0:
                raise ValueError('External attentuation is valid for values between 0 and 40')
            else:
                self._write(":OUTPut:DATA:ATTFactor DATA, %s" % value['DATA'])
                self._write(":OUTPut:DATA:ATTFactor XDATA, %s" % value['XDATA'])
        else:
            if 40 < value < 0:
                raise ValueError('External attentuation is valid for values between 0 and 40')
            else:
                self._write(":OUTPut:DATA:ATTFactor DATA, %s" % value)
                self._write(":OUTPut:DATA:ATTFactor XDATA, %s" % value)

    @property
    def offset(self):
        """
        :value: DC offset in V
        :type: float or dict[str, float]
        """
        self._select_mod()

        return {'DATA': float(self._read(":OUTPut:DATA:OFFSet? DATA",
                                         dummy_type='float')),
                'XDATA': float(self._read(":OUTPut:DATA:OFFSet? XDATA",
                                          dummy_type='float'))}

    @offset.setter
    def offset(self, value):
        """
        :type value: float or dict[str, float]
        """
        self._select_mod()

        if not isinstance(value, dict):
            value = {'DATA': value, 'XDATA': value}

        for k, v in value.items():
            if self.offset_reference == 'VOH' and not(-2.00 < v < 3.30):
                raise ValueError('VOH offset can only be between -2.00 and 3.30')
            elif self.offset_reference == 'VTH' and not(-2.50 < v < 2.8):
                raise ValueError('VTH offset can only be between -2.50 and 2.8')
            elif self.offset_reference == 'VOL' and not(-3.00 < v < 2.30):
                raise ValueError('VOL offset can only be between -3.00 and 2.30')

        self._write(":OUTPut:DATA:OFFSet DATA, %s" % value['DATA'])
        self._write(":OUTPut:DATA:OFFSet XDATA, %s" % value['XDATA'])

    @property
    def offset_reference(self):
        """
        Offset reference value for data and clock output.
        VOH takes the top of the eye as a reference, VTH takes the
        middle of the eye as a reference and VOL takes the bottom as a reference

        :value: - 'VTH'
                - 'VOH'
                - 'VOL'
        :type: str
        :raise ValueError: exception if input is not VOH/VTH/VOL
        """
        self._select_mod()

        return self._read(":OUTPut:OFFSet?")

    @offset_reference.setter
    def offset_reference(self, value='VTH'):
        """
        :type value: float
        :raise ValueError: exception if input is not VOH/VTH/VOL
        """
        self._select_mod()

        if value not in ['VOH', 'VTH', 'VOL']:
            raise ValueError('Reference can be VOH, VTH or VOL. %s is not a defined reference' %
                             value)

        self._write(":OUTPut:OFFSet %s" % value)

    @property
    def output(self):
        """
        Control both clock and data output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str or dict[str, str]
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        return {'CLOCK': self.clock_output, 'DATA': self.data_output}

    @output.setter
    def output(self, value):
        """
        :type value: str or dict[str, str]
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        if isinstance(value, dict):
            self.data_output = value['DATA']
            self.clock_output = value['CLOCK']
        else:
            value = value.upper()
            if value not in ['ENABLE', 'DISABLE']:
                raise ValueError('Please specify either "ENABLE" or "DISABLE"')
            else:
                self.data_output = value
                self.clock_output = value

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
                - <file_path> (must be .ptn or .txt file). Default file path is
                C:\\Program Files\\Anritsu\\MP1800A\\Pattern Files\\ if absolute path isn't provided.
                Don't include file extension. .ptn files have higher priority than .txt files.
        :type: str
        :raise ValueError: exception pattern is unrecognizable
        """
        # length = self._read(":SOURce:PATTern:DATA:LENGth?")
        if self._pattern:
            return self._pattern
        else:
            return self._read(":SOURce:PATTern:TYPE?")

    @pattern.setter
    def pattern(self, value):
        """
        :type value: str
        :raise ValueError: exception pattern is unrecognizable
        """
        self._select_mod()

        # Setting the pattern to PRBS#
        if value.startswith("PRBS"):
            value = value[4:]  # strip "PRBS" off of pattern string

            self._write(":SOURce:PATTern:TYPE PRBS")
            self._write(":SOURce:PATTern:PRBS:LENGth %s" % value)
            self._pattern = value

        # Setting the pattern to a hex or binary pattern
        elif value[0] == "H" or value[0] == 'B':
            # Hex pattern
            if value[0] == "H":
                length = 4 * (len(value) - 1)
            # Binary pattern
            else:
                length = (len(value) - 1)

            self._write(":SOURce:PATTern:TYPE DATA")
            self._write(":SOURce:PATTern:DATA:LENGth %s" % length)
            try:
                self._write(':SOURce:PATTern:DATA:WHOLe #H0,#H%X, "%s"' % (length - 1, value))
                self._pattern = value
            # In case file name starts with H or B
            except RuntimeError:
                self._open_pattern_file(value)

        # Setting the pattern to a file
        else:
            self._open_pattern_file(value)

    @property
    def polarity(self):
        """
        Data output polarity

        :value: - 'NORMAL'
                - 'INVERTED'
        :type: str
        :raise ValueError: exception if unrecognized logic polarity returned from equipment
        """
        self._select_mod()

        output_dict = {'POS': 'NORMAL', 'NEG': 'INVERTED',
                       'NEGative': 'INVERTED', 'POSitive': 'NORMAL',
                       'DUMMY_DATA': 'NORMAL'}
        return output_dict[self._read(":SOURce:PATTern:LOGic?")]

    @polarity.setter
    def polarity(self, value):
        """
        :type value: str
        :raise ValueError: exception if invalid polarity requested
        """
        self._select_mod()

        value = value.upper()
        input_dict = {'NORMAL': 'POSitive', 'INVERTED': 'NEGative'}
        if value not in input_dict.keys():
            raise ValueError("Invalid polarity requested: %s" % value)
        else:
            self._write(":SOURce:PATTern:LOGic %s" % input_dict[value])

    @property
    def termination_mode(self):
        """
        Data termination mode

        :value: - 'AC'
                - 'DC'
        :type: str
        :raise ValueError: exception if mode is not AC or DC
        """
        self._select_mod()

        output_dict = {'0': 'DC', '1': 'AC',
                       'OFF': 'DC', 'ON': 'AC',
                       'DUMMY_DATA': 'DC'}
        return output_dict[self._read(':OUTPut:DATA:AOFFset?')]

    @termination_mode.setter
    def termination_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode is not AC or DC
        """
        self._select_mod()

        input_dict = {'AC': 'ON', 'DC': 'OFF'}
        value = value.upper()
        if value not in input_dict.keys():
            raise ValueError('Please specify mode either as "AC" or "DC"')

        self._write(":OUTPut:DATA:AOFFset %s" % input_dict[value])

    def _calculate_preattenuation_amplitude(self, amplitude, external_attenuation=None,
                                            signal_mode='DATA'):
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
        self._select_mod()

        if external_attenuation is None:
            external_attenuation = self.external_attenuation[signal_mode]

        attenuation_factor = 10.0 ** (-external_attenuation / 20)

        # Required amplitude (in Volts)
        amplitude = (float(amplitude) / attenuation_factor)

        return amplitude
