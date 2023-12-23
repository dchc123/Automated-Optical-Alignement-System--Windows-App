"""
| $Revision:: 283908                                   $:  Revision of last commit
| $Author:: wleung@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-11-22 21:01:23 +0000 (Thu, 22 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.BERT.base_bert import BaseBERTJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockBUJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockPJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockRJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockSJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockSSCJitter
from CLI.Utilities.custom_exceptions import NotSupportedError


class AnritsuMP1800Jitter(BaseBERTJitter):
    """
    Anritsu MP1800 Jitter Module
    """
    def __init__(self, module_id, channel_number, synth_mod_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param channel_number: number targeting channel
        :type channel_number: int
        :param synth_mod_id: Synthesizer module identification string
        :type synth_mod_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._channel_number = channel_number
        self._synthesizer_module_id = synth_mod_id
        self.bu = AnritsuMP1800BUJitter(module_id=module_id, interface=interface, dummy_mode=dummy_mode)
        self.sj = AnritsuMP1800SJitter(module_id=module_id, interface=interface, dummy_mode=dummy_mode)
        self.scj = AnritsuMP1800SSCJitter(module_id=module_id, interface=interface, dummy_mode=dummy_mode)
        self.rj = AnritsuMP1800RJitter(module_id=module_id, interface=interface, dummy_mode=dummy_mode)

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)

    @property
    def global_output(self):
        """
        Enable state of the global jitter output. When this setting is toggled to enable,
        only previously enabled jitter types are re-enabled. Note that both the global_output and
        the specific jitter output must be enabled for any jitter to be outputted.

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise NotSupportedError: does not support global jitter
        """
        raise NotSupportedError('AnritsuMP1800 does not support global jitter')

    @global_output.setter
    def global_output(self, value):
        """
        :type value: str
        :raise NotSupportedError: does not support global jitter
        """
        raise NotSupportedError('AnritsuMP1800 does not support global jitter')

    @property
    def external_jitter_output(self):
        """
        Enable state of external jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(':SOURce:JITTer:EXTJitter:ENABle?')]

    @external_jitter_output.setter
    def external_jitter_output(self, value):
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
            self._write(":SOURce:JITTer:EXTJitter:ENABle %s" % input_dict[value])


class AnritsuMP1800BUJitter(BaseBERTBlockBUJitter):
    """
    AnritsuMP1800 BU Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        """
        self._select_mod()

        return float(self._read(':SOURce:JITTer:BUJ:AMPLitude?'))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        self._select_mod()

        rounded_value = round(value * 1000 / 8) * 8 / 1000
        if rounded_value != value:
            self.logger.warning('Jitter amplitude was rounded to %s '
                                'due to precision requirements' % rounded_value)
        self._write(":SOURce:JITTer:BUJ:AMPLitude %s" % rounded_value)

    @property
    def bit_rate(self):
        """
        :value: PRBS bit-rate in b/s
        :type: float
        :raise ValueError: exception if BUJ bit rate in not a valid value
        """
        self._select_mod()

        return float(self._read(':SOURce:JITTer:BUJ:BITRate?'))*1e9

    @bit_rate.setter
    def bit_rate(self, value):
        """
        :type value: float
        :raise ValueError: exception if BUJ bit rate in not a valid value
        """
        self._select_mod()

        bit_rate = float(value) / 1e9
        if 9.8 <= bit_rate <= 12.5 or 4.9 <= bit_rate <= 6.25 or 0.1 <= bit_rate <= 3.2:
            self._write(":SOURce:JITTer:BUJ:BITRate %.6f" % bit_rate)
        else:
            raise ValueError("Invalid BUJ Bitrate input: %s. Valid Range: 9.8G <= "
                             "bit_rate <= 12.5G or 4.9G <="
                             " bit_rate <= 6.25G or 0.1G <= bit_rate <= 3.2G " % bit_rate)

    @property
    def lpf(self):
        """
        :value: low-pass filter frequency in Hz
        :type: int
        :raise ValueError: exception if lpf frequency is not a valid value
        """
        self._select_mod()

        output_dict = {'M_500': 500e6, 'M_300': 300e6, 'M_200': 200e6, 'M_100': 100e6,
                       'M_50': 50e6, 'OFF': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return int(output_dict[self._read(':SOURce:JITTer:BUJ:LPF?', dummy_type='str')])

    @lpf.setter
    def lpf(self, value):
        """
        :type value: int
        :raise ValueError: exception if lpf frequency is not a valid value
        """
        self._select_mod()

        if value == 'DISABLE':
            self._write(":SOURce:JITTer:BUJ:LPF OFF")
        elif float(value) in [500e6, 300e6, 200e6, 100e6, 50e6]:
            self._write(":SOURce:JITTer:BUJ:LPF M_%d" % int(value / 1e6))
        else:
            raise ValueError("Invalid BUJ LPF input: %s" % value)

    @property
    def output(self):
        """
        Enable state of BU jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(':SOURce:JITTer:BUJ:ENABle?')]

    @output.setter
    def output(self, value):
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
            self._write(":SOURce:JITTer:BUJ:ENABle %s" % input_dict[value])

    @property
    def prbs(self):
        """
        :value: the polynomial of the PRBS pattern
        :type: int
        :raise ValueError: exception if PRBS input in not a valid value
        """
        self._select_mod()

        return int(self._read(':SOURce:JITTer:BUJ:PRBS?'))

    @prbs.setter
    def prbs(self, value):
        """
        :type value: int
        :raise ValueError: exception if PRBS input in not a valid value
        """
        self._select_mod()

        if value in [7, 9, 11, 15, 23, 31]:
            self._write(":SOURce:JITTer:BUJ:PRBS %s" % value)
        else:
            raise ValueError("Invalid BUJ PRBS input: %s."
                             " Valid inputs: [7, 9, 11, 15, 23, 31]" % value)


class AnritsuMP1800PJitter(BaseBERTBlockPJitter):
    """
    Anritsu MU181500B P Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        raise NotSupportedError('AnritsuMP1800 does not have a Periodic Jitter module')

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)


class AnritsuMP1800SSCJitter(BaseBERTBlockSSCJitter):
    """
    Anritsu MU181500B SSC Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)

    @property
    def frequency(self):
        """
        :value: modulation frequency in Hz
        :type: int
        :raise ValueError: exception if frequency out of range 28000Hz to 37000Hz
        """
        self._select_mod()

        return int(float(self._read(':SOURce:JITTer:SSC:FREQuency?')))

    @frequency.setter
    def frequency(self, value):
        """
        :type value: int
        :raise ValueError: exception if frequency out of range 28000Hz to 37000Hz
        """
        self._select_mod()

        if value < 28000 or value > 37000:
            raise ValueError('Modulation frequency must be in the range 28000Hz to 37000Hz')
        self._write(':SOURce:JITTer:SSC:FREQuency %s' % value)

    @property
    def output(self):
        """
        Enable state of SSC jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'1': 'ENABLE', 'ON': 'ENABLE', '0': 'DISABLE', 'OFF': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(':SOURce:JITTer:SSC:ENABle?')]

    @output.setter
    def output(self, value):
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
            self._write(":SOURce:JITTer:SSC:ENABle %s" % input_dict[value])

    @property
    def type(self):
        """
        SSC jitter type

        :value: - 'CENTER'
                - 'DOWN'
                - 'UP'
        :type: str
        :raise ValueError: exception if input is not 'CENTER', 'DOWN' or 'UP'
        """
        self._select_mod()

        output_dict = {'CENT': 'CENTER', 'UP': 'UP', 'DOWN': 'DOWN', 'DUMMY_DATA': 'CENTER'}
        return output_dict[self._read(':SOURce:JITTer:SSC:TYPE?')]

    @type.setter
    def type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not 'CENTER', 'DOWN' or 'UP'
        """
        self._select_mod()

        value = value.upper()
        if value not in ['CENTER', 'DOWN', 'UP']:
            raise ValueError('Please specify either "CENTER", "DOWN" or "UP"')
        self._write(':SOURce:JITTer:SSC:TYPE %s' % value)

    @property
    def deviation(self):
        """
        :value: SSC frequency deviation in ppm
        :type: int
        :raise ValueError: exception if frequency deviation is out of range 0ppm to 5300ppm
        """
        self._select_mod()

        return int(float(self._read(':SOURce:JITTer:SSC:DEViation?')))

    @deviation.setter
    def deviation(self, value):
        """
        :type value: int
        :raise ValueError: exception if frequency deviation is out of range 0ppm to 5300ppm
        """
        self._select_mod()

        if value < 0 or value > 5300:
            raise ValueError('Frequency deviation must be in the range 0ppm to 5300ppm')
        self._write(':SOURce:JITTer:SSC:DEViation %s' % value)


class AnritsuMP1800RJitter(BaseBERTBlockRJitter):
    """
    Anritsu MU181500B R Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        """
        self._select_mod()

        return float(self._read(":SOURce:JITTer:RJ:AMPLitude?"))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        self._select_mod()

        rounded_value = round(value * 1000 / 8) * 8 / 1000
        if rounded_value != value:
            self.logger.warning('Jitter amplitude was rounded to %s'
                                ' due to precision requirements' % rounded_value)
        self._write(":SOURce:JITTer:RJ:AMPLitude %s" % rounded_value)

    @property
    def hpf(self):
        """
        :value: high-pass filter frequency in Hz
        :type: int
        :raise ValueError: exception if frequency is not a valid value
        """
        self._select_mod()

        output_dict = {'M_20': 20e6, 'M_10': 10e6, 'OFF': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":SOURce:JITTer:RJ:HPF?", dummy_type='str')]

    @hpf.setter
    def hpf(self, value):
        """
        :type value: int/str
        :raise ValueError: exception if frequency is not a valid value
        """
        self._select_mod()

        if value == "DISABLE":
            self._write(":SOURce:JITTer:RJ:HPF OFF")
        elif float(value) in [10e6, 20e6]:
            self._write(":SOURce:JITTer:RJ:HPF M_%d" % (int(value / 1e6)))
        else:
            raise ValueError("Invalid RJ HPF input: %s. Valid inputs are: [10e6, 20e6, DISABLE]" % value)

    @property
    def lpf(self):
        """
        :value: low-pass filter frequency in Hz
        :type: int
        """
        self._select_mod()

        output_dict = {'M_100': 100e6, 'OFF': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":SOURce:JITTer:RJ:LPF?", dummy_type='str')]

    @lpf.setter
    def lpf(self, value):
        """
        :type value: int/str
        """
        self._select_mod()

        if value == "DISABLE":
            self._write(":SOURce:JITTer:RJ:LPF OFF")
        elif float(value) == 100e6:
            self._write(":SOURce:JITTer:RJ:LPF M_100")
        else:
            raise ValueError("Invalid RJ LPF input: %s. Valid inputs are: [100e6, DISABLE]" % value)

    @property
    def output(self):
        """
        Enable state of R jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'1': 'ENABLE', 'ON': 'ENABLE', '0': 'DISABLE', 'OFF': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(':SOURce:JITTer:RJ:ENABle?')]

    @output.setter
    def output(self, value):
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
            self._write(":SOURce:JITTer:RJ:ENABle %s" % input_dict[value])


class AnritsuMP1800SJitter(BaseBERTBlockSJitter):
    """
    Anritsu MU181500B S Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._source = 1
        self.source = 1

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        """
        self._select_mod()

        return float(self._read(":SOURce:JITTer:SJ:AMPLitude?"))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        self._select_mod()

        rounded_value = round(value * 1000 / 4) * 4 / 1000
        if rounded_value != value:
            self.logger.warning('Jitter amplitude was rounded to %s'
                                ' due to precision requirements' % rounded_value)
        self._write(":SOURce:JITTer:SJ:AMPLitude %s" % rounded_value)

    @property
    def frequency(self):
        """
        :value: jitter frequency in Hz
        :type: int
        :raise ValueError: exception if freqency value not in valid range
        """
        self._select_mod()

        return int(float(self._read(":SOURce:JITTer:SJ:FREQuency?")))

    @frequency.setter
    def frequency(self, value):
        """
        :type value: int
        :raise ValueError: exception if freqency value not in valid range
        """
        self._select_mod()

        if 10 < value <= 150000000:
            self._write(":SOURce:JITTer:SJ:FREQuency %s " % value)
        else:
            raise ValueError("Invalid frequency value: %s. Valid range:"
                             " 10 < frequency <= 150000000" % value)

    @property
    def output(self):
        """
        Enable state of S jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'1': 'ENABLE', 'ON': 'ENABLE', '0': 'DISABLE', 'OFF': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":SOURce:JITTer:SJ:ENABle?")]

    @output.setter
    def output(self, value):
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
            self._write(":SOURce:JITTer:SJ:ENABle %s" % input_dict[value])

    @property
    def source(self):
        self._select_mod()
        return self._source

    @source.setter
    def source(self, value):
        self._select_mod()
        self._source = value
