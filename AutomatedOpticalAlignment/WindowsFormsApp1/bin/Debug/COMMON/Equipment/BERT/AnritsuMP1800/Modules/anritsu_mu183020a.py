"""
| $Revision:: 282689                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-03 22:28:11 +0100 (Wed, 03 Oct 2018) $:  Date of last commit
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
from CLI.Utilities.custom_exceptions import NotSupportedError


class AnritsuMU183020AChannel(AnritsuMP1800PPG):
    """
    A single channel for the Anritsu MU183020A/21A 1/4ch 28G/32G PPG
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
        super().__init__(module_id=module_id, channel_number=channel_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.clock_source_unit = 1
        self._synthesizer_module_id = synth_mod_id
        self._channel_number = channel_number
        self._module_id = module_id

    @property
    def bit_rate(self):
        """
        Bit_rate that the 32G PPG module outputs.

        :value: desired bit rate (in Hertz)
        :type: float
        :raise TypeError: exception if bit rate is not an int
        :raise ValueError: exception if bit rate is not in the range of 0 to 32.1 GHz
        """
        bit_rate_ghz = str(self._read(":OUTPut:DATA:BITRate?"))
        if '_' in bit_rate_ghz:
            self.logger.error('No clock source is detected')
            return
        bit_rate_hz = int(float(bit_rate_ghz.strip('"')) * 1000000000)

        return bit_rate_hz

    @bit_rate.setter
    def bit_rate(self, value):
        """
        :type value:: float
        :raise TypeError: exception if bit rate is not an int
        :raise ValueError: exception if bit rate is not in the range of 0 to 32.1 GHz
        """
        if self._synthesizer_module_id is None:
            raise NotSupportedError('Synthesizer module cannot be detected')
        else:
            if type(value) != int:
                raise TypeError("Invalid bit rate. Bit rate must be an integer.")

            # bit rate is limited to 32.1 GHz
            if value < 0 or value > 32100000000:
                raise ValueError("Invalid bit rate."
                                 " Bit rate must be in the range of 0 to 32.1 GHz")

            bit_rate_ghz = float(value) / 1000000000

            self._write(':OUTPut:DATA:STANdard "Variable"')
            self._write(":OUTPut:DATA:BITRate %f" % bit_rate_ghz)

    @property
    def clock_source_unit(self):
        """
        Bit_rate that the 32G PPG module outputs.

        :value: specifies the unit and slot numbers from the
         smallest as 1 to 7 when there is more than one built-in synthesizer.
        :type: int
        :raise TypeError: exception if slot number is not an int
        :raise ValueError: exception if slot number is not in the range of 1 to 7
        """
        return self._unit_num

    @clock_source_unit.setter
    def clock_source_unit(self, value):
        """
        :type value:: int
        :raise TypeError: exception if slot number is not an int
        :raise ValueError: exception if slot number is not in the range of 1 to 7
        """

        if type(value) != int:
            raise TypeError("Invalid slot number. Slot number must be an integer.")

        if value < 1 or value > 7:
            raise ValueError("Invalid slot number. Slot number must be in the range of [1-7")

        self._unit_num = value

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
        source = self._read(":SYSTem:INPut:CSELect?", dummy_data='EXTERNAL')
        split_source_list = source.split(',')

        if len(split_source_list) > 1:
            split_source_str = split_source_list[1].strip('"')
        else:
            split_source_str = split_source_list[0]

        if 'EXT' in split_source_str:
            return 'EXTERNAL'
        elif 'INT' in split_source_str:
            return 'INTERNAL'

    @clock_source.setter
    def clock_source(self, value):
        """
        :type value:: str
        :raise ValueError: exception if clock soruce is neither INTERNAL nor EXTERNAL
        """
        value = value.upper()
        input_dict = {'INTERNAL': 'INT%d' % self.clock_source_unit, 'EXTERNAL': 'EXT'}
        if value not in input_dict.keys():
            raise ValueError("%s is an invalid clock source."
                             " Please select 'INTERNAL' or 'EXTERNAL'." % value)
        else:
            self._write(":SYSTem:INPut:CSELect %s" % input_dict[value])
