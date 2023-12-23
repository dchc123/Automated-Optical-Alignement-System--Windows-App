"""
| $Revision:: 283010                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-23 14:50:04 +0100 (Tue, 23 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Utilities.custom_exceptions import NotSupportedError
from CLI.Equipment.BERT.base_bert import BaseBERTJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockSJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockRJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockPJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockBUJitter
from CLI.Equipment.BERT.base_bert import BaseBERTBlockSSCJitter


class KeysightM80XXXJitter(BaseBERTJitter):
    """
    Keysight Jitter Channel
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
        self._module_id = module_id
        self._channel_number = channel_number
        self._identifier = "'M{}.DataOut{}'".format(self._module_id, self._channel_number)

        self.bu = KeysightM80XXXBUJitter(module_id, channel_number, interface, dummy_mode)
        self.pj = KeysightM80XXXPJitter(module_id, channel_number, interface, dummy_mode)
        self.rj = KeysightM80XXXRJitter(module_id, channel_number, interface, dummy_mode)
        self.lf_pj = KeysightM80XXXLFPJitter(module_id, channel_number, interface, dummy_mode)

    @property
    def global_output(self):
        """
        Enable state of the global jitter output. When this setting is toggled to enable,
        only previously enabled jitter types are re-enabled. Note that both the global_output and
        the specific jitter output must be enabled for any jitter to be outputted.

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":JITT:STAT? 'M{}.System'".format(self._module_id),
                                      dummy_data='OFF')]

    @global_output.setter
    def global_output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":JITT:STAT 'M{}.System', {}".format(self._module_id,
                                                             input_dict[value]))

    @property
    def external_jitter_output(self):
        """
        Enable state of external jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        if self._channel_number == 'clk':
            self._identifier = "'M1.ClkOut'"
        return output_dict[self._read(":JITT:HFR:EXT:STAT? {}".format(self._identifier), dummy_data='OFF')]

    @external_jitter_output.setter
    def external_jitter_output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            if self._channel_number == 'clk':
                self._identifier = "'M1.ClkOut'"
            self._write(":JITT:HFR:EXT:STAT {}, {}".format(self._identifier, input_dict[value]))


class KeysightM80XXXBUJitter(BaseBERTBlockBUJitter):
    """
    This container class groups Bounded Uncorrelated Jitter functionality
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
        self._module_id = module_id
        self._channel_number = channel_number
        self._identifier = "'M{}.DataOut{}'".format(self._module_id, self._channel_number)
        if self._identifier == 'clk':
            self._identifier = "'M1.ClkOut'"

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        :raise ValueError: exception if input is less than 0 or more than max amplitude
        """
        return float(self._read(":JITT:HFR:BUNC:AMPL? {}".format(self._identifier)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is less than 0 or more than max amplitude
        """
        max_amplitude = float(self._read(":JITT:HFR:BUNC:AMPL? {}, MAX".format(self._identifier)))

        if 0 <= value <= max_amplitude:
            self._write(":JITT:HFR:BUNC:AMPL {}, {}".format(self._identifier, value))
        else:
            raise ValueError("Amplitude value must be in the range of 0 to {}".format(max_amplitude))

    @property
    def bit_rate(self):
        """
        :value: PRBS bit-rate in b/s
        :type: int
        :raise ValueError: exception if input is not 625000000, 1250000000, or 2500000000
        """
        return int(int(self._read(":JITT:HFR:BUNC:DRAT? {}".format(self._identifier),
                                  dummy_data='RATE625').strip('RATE'))*1e6)

    @bit_rate.setter
    def bit_rate(self, value):
        """
        :type value: int
        :raise ValueError: exception if input is not 625000000, 1250000000, or 2500000000
        """
        # This BERT supports 625 MBps, 1250 MBps, or 2500 MBps
        if value in [625000000, 1250000000, 2500000000]:
            self._write(":JITT:HFR:BUNC:DRAT {}, RATE{}".format(self._identifier, int(value / 1e6)))
        else:
            raise ValueError("Please specify either 625000000, 1250000000 or 2500000000 b/s")

    @property
    def lpf(self):
        """
        :value: low-pass filter frequency in Hz
        :type: int
        :raise ValueError: exception if input is not 50000000, 100000000 or 200000000 Hz
        """
        return int(int(self._read(":JITT:HFR:BUNC:FILT? {}".format(self._identifier),
                                  dummy_data='LP50').strip('LP'))*1e6)

    @lpf.setter
    def lpf(self, value):
        """
        :type value: int
        :raise ValueError: exception if input is not 50000000, 100000000 or 200000000 Hz
        """
        lpf_mhz = int(value / 1e6)

        if lpf_mhz in [50, 100, 200]:
            self._write(":JITT:HFR:BUNC:FILT {}, LP{}".format(self._identifier, lpf_mhz))
        else:
            raise ValueError("Please specify either 50000000, 100000000 or 200000000 Hz")

    @property
    def output(self):
        """
        Enable state of BU jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        if self._channel_number == 'clk':
            self._identifier = "'M1.ClkOut'"
        return output_dict[self._read(":JITT:HFR:BUNC? {}".format(self._identifier), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            if self._channel_number == 'clk':
                self._identifier = "'M1.ClkOut'"
            self._write(":JITT:HFR:BUNC {}, {}".format(self._identifier, input_dict[value]))

    @property
    def prbs(self):
        """
        :value: the polynomial of the PRBS pattern
        :type: int
        :raise ValueError: exception if input is not 7, 9, 10, 11, 15, 23, or 31
        """
        return int(self._read(":JITT:HFR:BUNC:PRBS? {}".format(self._identifier), dummy_data='PRBS7').strip('PRBS'))

    @prbs.setter
    def prbs(self, value):
        """
        :type value: int
        :raise ValueError: exception if input is not 7, 9, 10, 11, 15, 23, or 31
        """
        if value in [7, 9, 10, 11, 15, 23, 31]:
            self._write(":JITT:HFR:BUNC:PRBS {}, PRBS{}".format(self._identifier, value))
        else:
            raise ValueError("Please specify one of the following: [7, 9, 10, 11, 15, 23, 31]")


class KeysightM80XXXPJitter(BaseBERTBlockPJitter):
    """
    This container class groups Periodic Jitter functionality
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
        self._module_id = module_id
        self._channel_number = channel_number
        self._identifier = "'M{}.DataOut{}'".format(self._module_id, self._channel_number)

        self._source = None
        self.source = 1

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        :raise ValueError: exception if input is less than 0 or more than max amplitude
        """
        return float(self._read(":JITT:HFR:PER{}:AMPL? {}".format(self.source, self._identifier)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is less than 0 or more than max amplitude
        """
        max_amplitude = float(self._read(":JITT:HFR:BUNC:AMPL? {}, MAX".format(self._identifier)))

        if 0 <= value <= max_amplitude:
            self._write(":JITT:HFR:PER{}:AMPL {}, {}".format(self.source, self._identifier, value))
        else:
            raise ValueError("Amplitude value must be in the range of 0 to {}".format(max_amplitude))

    @property
    def frequency(self):
        """
        :value: jitter frequency in Hz
        :type: float
        :raise ValueError: exception if input is not between 1 kHz and 500 MHz
        """
        return float(self._read(":JITT:HFR:PER{}:FREQ?"
                                " {}".format(self.source, self._identifier)))

    @frequency.setter
    def frequency(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is not between 1 kHz and 500 MHz
        """
        if 1000.0 <= value <= 500000000.0:
            self._write(":JITT:HFR:PER{}:FREQ {}, {}".format(self.source, self._identifier, value))
        else:
            raise ValueError("Please specify a value between 1 kHz and 500 MHz")

    @property
    def output(self):
        """
        Enable state of BU jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        if self._channel_number == 'clk':
            self._identifier = "'M1.ClkOut'"
        return output_dict[self._read(":JITT:HFR:PER{}? {}".format(self.source, self._identifier), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            if self._channel_number == 'clk':
                self._identifier = "'M1.ClkOut'"
            self._write(":JITT:HFR:PER{} {}, {}".format(self.source, self._identifier, input_dict[value]))

    @property
    def source(self):
        """
        Specifies which of the two periodic sources (1 or 2) to use
        :value: 1 or 2
        :type: int
        :raise ValueError: exception if input is not 1 or 2
        """
        return self._source

    @source.setter
    def source(self, value):
        """
        :type value: int
        :raise ValueError: exception if input is not 1 or 2
        """
        if value not in [1, 2]:
            raise ValueError('Source can either be 1 or 2')
        else:
            self._source = value

    @property
    def unit(self):
        """
        Gets the unit being used for the jitter parameters (time or unit intervals)

        :value: - 'UINT' (unit intervals)
                - 'TIME' (seconds)
        :type: str
        :raise ValueError: exception if input is not UINT/TIME
        """
        return self._read(":JITT:HFR:UNIT? {}".format(self._identifier), dummy_data='TIME')

    @unit.setter
    def unit(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not UINT/TIME
        """
        if value not in ['UINT', 'TIME']:
            raise ValueError("Invalid unit specified for jitter parameters. Must be UINT or TIME.")
        else:
            self._write(":JITT:HFR:UNIT {}, {}".format(self._identifier, value))


class KeysightM80XXXLFPJitter(BaseBERTBlockPJitter):
    """
    This container class groups Low Frequency Periodic Jitter functionality
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
        self._module_id = module_id
        self._channel_number = channel_number
        self._identifier = "'M{}.DataOut{}'".format(self._module_id, self._channel_number)
        if self._identifier == 'clk':
            self._identifier = "'M1.ClkOut'"

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        :raise ValueError: exception if input is less than 0 or more than max amplitude
        """
        if self._channel_number == 'clk':
            self._identifier = "'M1.ClkOut'"
        return float(self._read(":JITT:LFR:PER:AMPL? {}".format(self._identifier)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is less than 0 or more than max amplitude
        """
        max_amplitude = 8000.0

        if 0.0 <= value <= max_amplitude:
            if self._channel_number == 'clk':
                self._identifier = "'M1.ClkOut'"
            self._write(":JITT:LFR:PER:AMPL {}, {}".format(self._identifier, value))
        else:
            raise ValueError("Amplitude value must be in the range of 0 to %s" %
                             max_amplitude)

    @property
    def frequency(self):
        """
        :value: jitter frequency in Hz
        :type: float
        :raise ValueError: exception if input is not between 1 kHz and 40 MHz
        """
        if self._channel_number == 'clk':
            self._identifier = "'M1.ClkOut'"
        return float(self._read(":JITT:LFR:PER:FREQ? {}".format(self._identifier)))

    @frequency.setter
    def frequency(self, value):
        """
        :type value: float
         :raise ValueError: exception if input is not between 1 kHz and 40 MHz
        """
        if 100.0 <= value <= 40e6:
            if self._channel_number == 'clk':
                self._identifier = "'M1.ClkOut'"
            self._write(":JITT:LFR:PER:FREQ {}, {}".format(self._identifier, value))
        else:
            raise ValueError("Please specify a value between 1 kHz and 40 MHz")

    @property
    def output(self):
        """
        Enable state of BU jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        if self._channel_number == 'clk':
            self._identifier = "'M1.ClkOut'"
        return output_dict[self._read(":JITT:LFR:PER? {}".format(self._identifier), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            if self._channel_number == 'clk':
                self._identifier = "'M1.ClkOut'"
            self._write(":JITT:LFR:PER {}, {}".format(self._identifier, input_dict[value]))

    @property
    def unit(self):
        """
        Gets the unit being used for the jitter parameters (time or unit intervals)

        :value: - 'UINT' (unit intervals)
                - 'TIME' (seconds)
        :type: str
        :raise ValueError: exception if input is not UINT/TIME
        """
        if self._channel_number == 'clk':
            self._identifier = "'M1.ClkOut'"
        return self._read(":JITT:LFR:UNIT? {}".format(self._identifier), dummy_data='TIME')

    @unit.setter
    def unit(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not UINT/TIME
        """
        if value not in ['UINT', 'TIME']:
            raise ValueError("Invalid unit specified for jitter parameters. Must be UINT or TIME.")
        else:
            if self._channel_number == 'clk':
                self._identifier = "'M1.ClkOut'"
            self._write(":JITT:LFR:UNIT {}, {}".format(self._identifier, value))


class KeysightM80XXXRJitter(BaseBERTBlockRJitter):
    """
    This container class groups Random Jitter functionality
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
        self._module_id = module_id
        self._channel_number = channel_number
        self._identifier = "'M{}.DataOut{}'".format(self._module_id, self._channel_number)
        if self._identifier == 'clk':
            self._identifier = "'M1.ClkOut'"

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        :raise ValueError: exception if input is less than 0 or more than max amplitude
        """
        return float(self._read(":JITT:HFR:RAND:AMPL? {}".format(self._identifier)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is less than 0 or more than max amplitude
        """
        max_amplitude = float(self._read(":JITT:HFR:RAND:AMPL? {}, MAX".format(self._identifier)))

        if 0 <= value <= max_amplitude:
            self._write(":JITT:HFR:RAND:AMPL {}, {}".format(self._identifier, value))
        else:
            raise ValueError("Amplitude value must be in the range of 0 to {}".format(max_amplitude))

    @property
    def hpf(self):
        """
        :value: - 10e6
                - 'DISABLE'
        :type: int
        :raise ValueError: exception if input is not 10e6/DISABLE
        """
        output_dict = {'HP10': 10000000, 'OFF': 'DISABLE'}
        return output_dict[self._read(":JITT:HFR:RAND:FILT:HPAS? {}".format(self._identifier), dummy_data='OFF')]

    @hpf.setter
    def hpf(self, value):
        """
        :type value: int
        :raise ValueError: exception if input is not 10e6/DISABLE
        """
        if isinstance(value, str) and value.upper() == 'DISABLE':
            self._write(":JITTer:HFR:RAND:FILT:HPAS {}, OFF".format(self._identifier))
        elif int(value) == 10000000:
            self._write(":JITT:HFR:RAND:FILT:HPAS {}, HP10".format(self._identifier))
        else:
            raise ValueError("Please specify either 10000000Hz or 'DISABLE'")

    @property
    def lpf(self):
        """
        :value: low-pass filter frequency in Hz
        :type: int
        :raise ValueError: exception if input is not 100000000Hz, 500000000Hz or 'DISABLE'
        """
        output_dict = {'LP100': 100000000, 'LP500': 500000000, 'OFF': 'DISABLE'}
        return output_dict[self._read(":JITT:HFR:RAND:FILT:LPAS? {}".format(self._identifier), dummy_data='OFF')]

    @lpf.setter
    def lpf(self, value):
        """
        :type value: int
        :raise ValueError: exception if input is not 100000000Hz, 500000000Hz or 'DISABLE'
        """
        # Note: Keysight BERT shows 1000MHz, but it is equivalent to 'OFF'
        if isinstance(value, str) and value.upper() == 'DISABLE':
            self._write(":JITTer:HFR:RAND:FILT:LPAS {}, OFF".format(self._identifier))
        elif int(value) in [100000000, 500000000]:
            self._write(":JITT:HFR:RAND:FILT:LPAS {}, LP{}".format(self._identifier, int(value/1e6)))
        else:
            raise ValueError("Please specify either 100000000Hz, 500000000Hz or 'DISABLE'")

    @property
    def output(self):
        """
        Enable state of R jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        if self._channel_number == 'clk':
            self._identifier = "'M1.ClkOut'"
        return output_dict[self._read(":JITT:HFR:RAND? {}".format(self._identifier), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            if self._channel_number == 'clk':
                self._identifier = "'M1.ClkOut'"
            self._write(":JITT:HFR:RAND {}, {}".format(self._identifier, input_dict[value]))
