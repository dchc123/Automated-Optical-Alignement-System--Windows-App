"""
| $Revision:: 282647                                   $:  Revision of last commit
| $Author:: tobias_l@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-10-02 03:03:54 +0100 (Tue, 02 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from .keysight_m80xxx_jitter import KeysightM80XXXJitter
from.keysight_m80xxx_jitter import KeysightM80XXXBUJitter
from.keysight_m80xxx_jitter import KeysightM80XXXLFPJitter
from.keysight_m80xxx_jitter import KeysightM80XXXPJitter
from.keysight_m80xxx_jitter import KeysightM80XXXRJitter


class KeysightM8045AJitter(KeysightM80XXXJitter):
    """
    Keysight M8045A Jitter Channel
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
        super().__init__(module_id=module_id, channel_number=channel_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.bu = KeysightM8045ABUJitter(module_id, channel_number, interface, dummy_mode)
        self.pj = KeysightM8045APJitter(module_id, channel_number, interface, dummy_mode)
        self.rj = KeysightM8045ARJitter(module_id, channel_number, interface, dummy_mode)
        self.lf_pj = KeysightM8045ALFPJitter(module_id, channel_number, interface, dummy_mode)


class KeysightM8045ABUJitter(KeysightM80XXXBUJitter):
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
        super().__init__(module_id=module_id, channel_number=channel_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        :raise ValueError: exception if amplitude is not between 0 and maximum module amplitude
        """
        return float(self._read(":JITT:HFR:BUNC:AMPL?"
                                " 'M{}.DataOut{}'".format(self._module_id, self._channel_number)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if amplitude is not between 0 and maximum module amplitude
        """
        max_amplitude = float(self._read(":JITT:HFR:BUNC:AMPL?"
                                         " 'M%d.DataOut%d', MAX" % (self._module_id, self._channel_number)))

        if 0 <= value <= max_amplitude:
            self._write(":JITT:HFR:BUNC:AMPL 'M{}.DataOut{}', {}".format(self._module_id, self._channel_number, value))
        else:
            raise ValueError("Amplitude value must be in the range of 0 to %f" % max_amplitude)

    @property
    def bit_rate(self):
        """
        :value: PRBS bit-rate in b/s
        :type: int
        :raise ValueError: exception if bit rate is not 625000000, 1250000000 or 2500000000 b/s
        """
        return int(int(self._read(":JITT:HFR:BUNC:DRAT? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='RATE625').strip('RATE'))*1e6)

    @bit_rate.setter
    def bit_rate(self, value):
        """
        :type value: int
        :raise ValueError: exception if bit rate is not 625000000, 1250000000 or 2500000000 b/s
        """
        # This BERT supports 625 MBps, 1250 MBps, or 2500 MBps
        if value in [625000000, 1250000000, 2500000000]:
            self._write(":JITT:HFR:BUNC:DRAT 'M{}.DataOut{}',"
                        " RATE{}".format(self._module_id, self._channel_number, int(value / 1e6)))
        else:
            raise ValueError("Please specify either 625000000, 1250000000 or 2500000000 b/s")

    @property
    def lpf(self):
        """
        :value: low-pass filter frequency in Hz
        :type: int
        """
        return int(int(self._read(":JITT:HFR:BUNC:FILT? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='LP50').strip('LP'))*1e6)

    @lpf.setter
    def lpf(self, value):
        """
        :type value: int
        :raise ValueError: exception if filter is not 50000000, 100000000 or 200000000 Hz
        """
        lpf_mhz = int(value / 1e6)

        if lpf_mhz in [50, 100, 200]:
            self._write(":JITT:HFR:BUNC:FILT 'M{}.DataOut{}',"
                        " LP{}".format(self._module_id, self._channel_number, lpf_mhz))
        else:
            raise ValueError("Please specify either 50000000, 100000000 or 200000000 Hz")

    @property
    def output(self):
        """
        Enable state of BU jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if value is not 'ENABLE' or 'DISABLE'
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":JITT:HFR:BUNC? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not 'ENABLE' or 'DISABLE'
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":JITT:HFR:BUNC 'M{}.DataOut{}', {}".format(self._module_id,
                                                                    self._channel_number, input_dict[value]))

    @property
    def prbs(self):
        """
        :value: the polynomial of the PRBS pattern
        :type: int
        :raise ValueError: exception if filter is not 50000000, 100000000 or 200000000 Hz
        """
        return int(self._read(":JITT:HFR:BUNC:PRBS? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='PRBS7').strip('PRBS'))

    @prbs.setter
    def prbs(self, value):
        """
        :type value: int
        :raise ValueError: exception if filter is not [7, 9, 10, 11, 15, 23, 31]
        """
        if value in [7, 9, 10, 11, 15, 23, 31]:
            self._write(":JITT:HFR:BUNC:PRBS 'M{}.DataOut{}',"
                        " PRBS{}".format(self._module_id, self._channel_number, value))
        else:
            raise ValueError("Please specify one of the following: [7, 9, 10, 11, 15, 23, 31]")


class KeysightM8045APJitter(KeysightM80XXXPJitter):
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
        super().__init__(module_id=module_id, channel_number=channel_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

        self._source = None
        self.source = 1

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        :raise ValueError: exception if amplitude is not between 0 and maximum module amplitude
        """
        return float(self._read(":JITT:HFR:PER{}:AMPL?"
                                " 'M{}.DataOut{}'".format(self.source, self._module_id,
                                                          self._channel_number)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if amplitude is not between 0 and maximum module amplitude
        """
        max_amplitude = float(self._read(":JITT:HFR:PER:AMPL?"
                                         " 'M%d.DataOut%d', MAX" % (self._module_id, self._channel_number)))

        if 0 <= value <= max_amplitude:
            self._write(":JITT:HFR:PER{}:AMPL 'M{}.DataOut{}', {}".format(self.source, self._module_id,
                                                                          self._channel_number, value))
        else:
            raise ValueError("Amplitude value must be in the range of 0 to %f" % max_amplitude)

    @property
    def frequency(self):
        """
        :value: jitter frequency in Hz
        :type: float
        :raise ValueError: exception if frequency is not between 1 kHz and 500 MHz
        """
        return float(self._read(":JITT:HFR:PER{}:FREQ?"
                                " 'M{}.DataOut{}'".format(self.source, self._module_id, self._channel_number)))

    @frequency.setter
    def frequency(self, value):
        """
        :type value: float
        :raise ValueError: exception if frequency is not between 1 kHz and 500 MHz
        """
        if 1000.0 <= value <= 500000000.0:
            self._write(":JITT:HFR:PER{}:FREQ 'M{}.DataOut{}', {}".format(self.source, self._module_id,
                                                                          self._channel_number, value))
        else:
            raise ValueError("Please specify a value between 1 kHz and 500 MHz")

    @property
    def output(self):
        """
        Enable state of BU jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if value is not 'ENABLE' or 'DISABLE'
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":JITT:HFR:PER{}? 'M{}.DataOut{}'".format(
            self.source, self._module_id, self._channel_number), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not 'ENABLE' or 'DISABLE'
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":JITT:HFR:PER{} 'M{}.DataOut{}', {}".format(self.source, self._module_id, self._channel_number,
                                                                     input_dict[value]))

    @property
    def source(self):
        """
        Specifies which of the two periodic sources (1 or 2) to use
        :value: 1 or 2
        :type: int
        :raise ValueError: exception if source is not 1 or 2
        """
        return self._source

    @source.setter
    def source(self, value):
        """
        :type value: int
        :raise ValueError: exception if source is not 1 or 2
        """
        if value not in [1, 2]:
            raise ValueError('Source can either be 1 or 2')
        else:
            self._source = value


class KeysightM8045ALFPJitter(KeysightM80XXXLFPJitter):
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
        super().__init__(module_id=module_id, channel_number=channel_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        :raise ValueError: exception if amplitude is not between 0 and maximum module amplitude
        """
        return float(self._read(":JITT:LFR:PER:AMPL? 'M{}.DataOut{}'".format(self._module_id, self._channel_number)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if amplitude is not between 0 and maximum module amplitude
        """
        max_amplitude = 8000.0

        if 0.0 <= value <= max_amplitude:
            self._write(":JITT:LFR:PER:AMPL 'M{}.DataOut{}', {}".format(self._module_id, self._channel_number, value))
        else:
            raise ValueError("Amplitude value must be in the range of 0 to %s" % max_amplitude)

    @property
    def frequency(self):
        """
        :value: jitter frequency in Hz
        :type: float
        :raise ValueError: exception if frequency is not between 1 kHz and 40 MHz
        """
        return float(self._read(":JITT:LFR:PER:FREQ? 'M{}.DataOut{}'".format(self._module_id, self._channel_number)))

    @frequency.setter
    def frequency(self, value):
        """
        :type value: float
        :raise ValueError: exception if frequency is not between 1 kHz and 40 MHz
        """
        if 100.0 <= value <= 40e6:
            self._write(":JITT:LFR:PER:FREQ 'M{}.DataOut{}', {}".format(self._module_id, self._channel_number, value))
        else:
            raise ValueError("Please specify a value between 1 kHz and 40 MHz")

    @property
    def output(self):
        """
        Enable state of BU jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if value is not 'ENABLE' or 'DISABLE'
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":JITT:LFR:PER? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not 'ENABLE' or 'DISABLE'
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":JITT:LFR:PER 'M{}.DataOut{}', {}".format(self._module_id, self._channel_number,
                                                                   input_dict[value]))


class KeysightM8045ARJitter(KeysightM80XXXRJitter):
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
        super().__init__(module_id=module_id, channel_number=channel_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        :raise ValueError: exception if amplitude is not between 0 and maximum module amplitude
        """
        return float(self._read(":JITT:HFR:RAND:AMPL?"
                                " 'M{}.DataOut{}'".format(self._module_id, self._channel_number)))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if amplitude is not between 0 and maximum module amplitude
        """
        max_amplitude = float(self._read(":JITT:HFR:RAND:AMPL?"
                                         " 'M%d.DataOut%d', MAX" % (self._module_id, self._channel_number)))

        if 0 <= value <= max_amplitude:
            self._write(":JITT:HFR:RAND:AMPL 'M{}.DataOut{}', {}".format(self._module_id, self._channel_number, value))
        else:
            raise ValueError("Amplitude value must be in the range of 0 to %f" % max_amplitude)

    @property
    def hpf(self):
        """
        :value: - 10e6
                - 'DISABLE'
        :type: int
        :raise ValueError: exception if filter is not 'DISABLE' or 10000000Hz
        """
        output_dict = {'HP10': 10000000, 'OFF': 'DISABLE'}
        return output_dict[self._read(":JITT:HFR:RAND:FILT:HPAS? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='OFF')]

    @hpf.setter
    def hpf(self, value):
        """
        :type value: int
        :raise ValueError: exception if filter is not 'DISABLE' or 10000000Hz
        """
        if isinstance(value, str) and value.upper() == 'DISABLE':
            self._write(":JITTer:HFR:RAND:FILT:HPAS 'M{}.DataOut{}', OFF".format(self._module_id, self._channel_number))
        elif int(value) == 10000000:
            self._write(":JITT:HFR:RAND:FILT:HPAS 'M{}.DataOut{}', HP10".format(self._module_id, self._channel_number))
        else:
            raise ValueError("Please specify either 10000000Hz or 'DISABLE'")

    @property
    def lpf(self):
        """
        :value: low-pass filter frequency in Hz
        :type: int
        :raise ValueError: exception if filter is not 100000000Hz, 500000000Hz or 'DISABLE'
        """
        output_dict = {'LP100': 100000000, 'LP500': 500000000, 'OFF': 'DISABLE'}
        return output_dict[self._read(":JITT:HFR:RAND:FILT:LPAS? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='OFF')]

    @lpf.setter
    def lpf(self, value):
        """
        :type value: int
        :raise ValueError: exception if filter is not 100000000Hz, 500000000Hz or 'DISABLE'
        """
        # Note: Keysight BERT shows 1000MHz, but it is equivalent to 'OFF'
        if isinstance(value, str) and value.upper() == 'DISABLE':
            self._write(":JITTer:HFR:RAND:FILT:LPAS 'M{}.DataOut{}', OFF".format(self._module_id, self._channel_number))
        elif int(value) in [100000000, 500000000]:
            self._write(":JITT:HFR:RAND:FILT:LPAS 'M{}.DataOut{}', LP{}".format(
                self._module_id, self._channel_number, int(value/1e6)))
        else:
            raise ValueError("Please specify either 100000000Hz, 500000000Hz or 'DISABLE'")

    @property
    def output(self):
        """
        Enable state of R jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if value is not 'ENABLE' or 'DISABLE'
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":JITT:HFR:RAND? 'M{}.DataOut{}'".format(
            self._module_id, self._channel_number), dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not 'ENABLE' or 'DISABLE'
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":JITT:HFR:RAND 'M{}.DataOut{}', {}".format(self._module_id, self._channel_number,
                                                                    input_dict[value]))

