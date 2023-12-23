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
from .anritsu_mu181020a import AnritsuMU181020AChannel
from .anritsu_mu182020a import AnritsuMU182020AChannel


class AnritsuMuxedMP1800PPG(AnritsuMP1800PPG):
    """
    Abstraction layer containing an Anritsu MU182020A 1ch 25GBit/s MUX module connected to two
    Anritsu MU181020A/20B 12.5/14 Gbit/s PPGs. This class allows us to treat these three modules as
    a single PPG channel.
    """
    def __init__(self, ppg1_module_id, ppg2_module_id, mux_module_id, interface, dummy_mode, **kwargs):
        """

        :param ppg1_module_id: PPG1 module ID
        :type ppg1_module_id: int
        :param ppg2_module_id: PPG2 module ID
        :type ppg2_module_id: int
        :param mux_module_id: MUX module ID
        :type mux_module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

        self._ppg1 = AnritsuMU181020AChannel(module_id=ppg1_module_id, channel_number=1,
                                             interface=interface, dummy_mode=dummy_mode)
        self._ppg2 = AnritsuMU181020AChannel(module_id=ppg2_module_id, channel_number=1,
                                             interface=interface, dummy_mode=dummy_mode)
        self._mux = AnritsuMU182020AChannel(module_id=mux_module_id,channel_number=1,
                                            interface=interface, dummy_mode=dummy_mode)

    @property
    def amplitude(self):
        """
        Data amplitude after external attenuation

        :value: data amplitude in V
        :type: float
        """
        return self._mux.amplitude

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value:: float
        """
        self._mux.amplitude = value

    @property
    def bit_rate(self):
        """
        **READONLY**
        Gets the bit rate at the data output

        :type: int
        """
        return self._mux.bit_rate

    @property
    def clock_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        return self._mux.clock_output

    @clock_output.setter
    def clock_output(self, value):
        """
        :type value:: str
        """
        self._mux.clock_output = value

    @property
    def data_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        return self._mux.data_output

    @data_output.setter
    def data_output(self, value):
        """
        :type value:: str
        """
        self._mux.data_output = value

    @property
    def output(self):
        """
        Control both clock and data output

        :value: - 'DISABLE'
                - 'ENABLE'
        """
        return self._mux.output

    @output.setter
    def output(self, value):
        """
        :type value:: str
        """
        self._mux.output = value

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
        :type: str
        """
        return self._ppg1.pattern

    @pattern.setter
    def pattern(self, value):
        """
        :type value:: str
        """
        self._ppg1.pattern = value

    @property
    def polarity(self):
        """
        Data output polarity

        :value: - 'NORMAL'
                - 'INVERTED'
        :type: str
        """
        return self._ppg1.polarity

    @polarity.setter
    def polarity(self, value):
        """
        :type value:: str
        """
        self._ppg1.polarity = value