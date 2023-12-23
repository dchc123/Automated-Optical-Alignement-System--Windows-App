"""
| $Revision:: 279062                                   $:  Revision of last commit
| $Author:: ael-khouly@SEMNET.DOM                      $:  Author of last commit
| $Date:: 2018-07-10 19:29:10 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the PPG API: See :py:mod:`Equipment.BERT.AnritsuMP1800.Modules.anritsu_mp1800_ppg`
::

    >>> from CLI.Equipment.BERT.AnritsuMP1800.anritsu_mp1800 import AnritsuMP1800
    >>> bert = AnritsuMP1800('GPIB1::23::INSTR')
    >>> bert.connect()
    >>> bert.ppg[1].clock_output
    'DISABLE'
    >>> bert.ppg[1].clock_output = 'ENABLE'
    >>> bert.ppg[1].clock_output
    'ENABLE'
"""
from .anritsu_mp1800_ppg import AnritsuMP1800PPG


class AnritsuMU182020AChannel(AnritsuMP1800PPG):
    """
    A single channel for the Anritsu MU182020A/21A 1/2ch 25GBit/s MUX module
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
        Data amplitude after external attenuation

        :value: data amplitude in V
        :type: float
        """
        data_ampl = float(self._read(":MUX:DATA:AMPLitude? DATA, %d" % self._channel_number))
        xdata_ampl = float(self._read(":MUX:DATA:AMPLitude? XDATA, %d" % self._channel_number))
        return {"DATA": data_ampl, "XDATA": xdata_ampl}

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value:: float
        :raise ValueError: exception if amplitude mode is neither SINGLE nor DIFFERENTIAL
        """
        if not isinstance(value, dict):
            value = {'DATA': value, 'XDATA': value}

        for key in value.keys():
            value[key] = self._calculate_preattenuation_amplitude(value[key])

            # This BERT is limited to a range of [0.5,3.5] Volts
            if 1.75 < value[key] < 0.25:
                raise ValueError('Please specify an amplitude between {} and {}'.format(
                    self._max_amplitude, self._min_amplitude))

        if self.amplitude_mode == "DIFFERENTIAL":
            self._write(":MUX:DATA:AMPLitude DATA, %s, %d" % (value['DATA'], self._channel_number))
            self._write(":MUX:DATA:AMPLitude XDATA, %s, %d" % (value['XDATA'],
                                                               self._channel_number))
        elif self.amplitude_mode == 'SINGLE':
            self._write(":MUX:DATA:AMPLitude DATA, %s, %d" % (value['DATA'], self._channel_number))
        else:
            raise ValueError("'%s' is an invalid mode." % self.amplitude_mode)

    @property
    def bit_rate(self):
        """
        **READONLY**
        Gets the bit rate at the data output

        :type: int
        """
        return int(self._read(":MUX:OUTPut:BMONitor? %d" % self._channel_number) * 1e9)

    @property
    def clock_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(':MUX:CLOCk:OUTPut?')]

    @clock_output.setter
    def clock_output(self, value):
        """
        :type value:: str
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":MUX:CLOCk:OUTPut %s" % input_dict[value])

    @property
    def data_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":MUX:DATA:OUTPut?")]

    @data_output.setter
    def data_output(self, value):
        """
        :type value:: str
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":MUX:DATA:OUTPut %s" % input_dict[value])

    @property
    def output(self):
        """
        Control both clock and data output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        return {'CLOCK': self._read(':MUX:CLOCk:OUTPut?'), 'DATA': self._read(":MUX:DATA:OUTPut?")}

    @output.setter
    def output(self, value):
        """
        :type value:: str
        """
        value = value.upper()
        if value not in ['ENABLE', 'DISABLE']:
            raise ValueError('Please specify either "ENABLE" or "DISABLE')
        else:
            self.data_output = value
            self.clock_output = value

    @property
    def data_tracking(self):
        """
        Enables and disables shared settings for Data and Xdata outputs.

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {1: 'ENABLE', 0: 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":MUX:DATA:TRACking?")]

    @data_tracking.setter
    def data_tracking(self, value):
        """
        :type value:: str
        """
        value = value.upper()
        input_dict = {'ENABLE': 1, 'DISABLE': 0}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":MUX:DATA:TRACking %s" % input_dict[value])