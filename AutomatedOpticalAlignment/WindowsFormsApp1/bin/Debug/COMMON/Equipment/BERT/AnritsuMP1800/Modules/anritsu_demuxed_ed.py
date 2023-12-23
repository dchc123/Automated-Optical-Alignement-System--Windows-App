"""
| $Revision:: 282689                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-03 22:28:11 +0100 (Wed, 03 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the Error Detector API: See :py:mod:`Equipment.BERT.AnritsuMP1800.Modules.anritsu_mp1800_ed`
::

    >>> from CLI.Equipment.BERT.AnritsuMP1800.anritsu_mp1800 import AnritsuMP1800
    >>> bert = AnritsuMP1800('GPIB1::23::INSTR')
    >>> bert.connect()
    >>> bert.ed[1].bit_count
    1000
    >>> bert.ed[1].input_mode
    'SINGLE_POSITIVE'
    >>> bert.ed[1].input_mode = 'DIFFERENTIAL'
    >>> bert.input_mode
    'DIFFERENTIAL'
"""
from .anritsu_mp1800_ed import AnritsuMP1800ED
from .anritsu_mu182040a import AnritsuMU182040AChannel
from .anritsu_mu181040a import AnritsuMU181040AChannel


class AnritsuDemuxedED(AnritsuMP1800ED):
    """
    Abstraction layer containing an Anritsu MU182040A 1ch 25GBit/s DEMUX module connected to two
    Anritsu MU181040A/40B 12.5/14 Gbit/s EDs. This class allows us to treat these three
    modules as a single ED channel.
    """
    def __init__(self, ed1_module_id, ed2_module_id, demux_module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param ed1_module_id: ED1 module identification string
        :type ed1_module_id: int
        :param ed2_module_id: ED2 module identification string
        :type ed2_module_id: int
        :param demux_module_id: DEMUX module identification string
        :type demux_module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

        self._ed1 = AnritsuMU181040AChannel(module_id=ed1_module_id, channel_number=1,
                                            interface=interface, dummy_mode=dummy_mode)
        self._ed2 = AnritsuMU181040AChannel(module_id=ed2_module_id, channel_number=1,
                                            interface=interface, dummy_mode=dummy_mode)
        self._demux = AnritsuMU182040AChannel(module_id=demux_module_id, channel_number=1,
                                              interface=interface, dummy_mode=dummy_mode)

    @property
    def bit_count(self):
        """
        **READONLY**

        :value: accumulated bit count of current or last measurement
        :type: int
        """
        return self._demux.bit_count

    @property
    def clock_delay(self):
        """
        Clock delay

        :value: clock delay in s
        :type: float
        """

        return self._demux.clock_delay

    @clock_delay.setter
    def clock_delay(self, value):
        """
        :type value: float
        """
        self._demux.clock_delay = value

    @property
    def elapsed_time(self):
        """
        **READONLY**

        :value: elapsed time for current or last measurement
        :type: int
        """
        return self._ed1.elapsed_time

    @property
    def error_count(self):
        """
        **READONLY**

        :value: error count of current or last measurement
        :type: int
        """
        return self._demux.error_count

    @property
    def error_rate(self):
        """
        **READONLY**

        :value: error rate of current or last measurement
        :type: float
        """
        return self._demux.error_rate

    @property
    def input_threshold(self):
        """
        Input threshold voltage (in Volts). To maximize compatibility with
        different BERTs, the recommended voltage range is [-0.25, 0.25] V.

        :value: threshold in V
        :type: float
        :raise ValueError: exception if threshold is not between -3.5V and 3.3V
        """
        return self._demux.input_threshold

    @input_threshold.setter
    def input_threshold(self, value):
        """
        :type value: float
        :raise ValueError: exception if threshold is not between -3.5V and 3.3V
        """
        self._demux.input_threshold = value

    @property
    def measurement_status(self):
        """
        **READONLY** BER measurement status

        :value: - 'INACTIVE'
                - 'ACTIVE'
        :type: str
        """
        return self._demux.measurement_status

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
        :raise ValueError: exception pattern is unrecognizable
        """
        return self._ed1.pattern

    @pattern.setter
    def pattern(self, value):
        """
        :type value: str
        :raise ValueError: exception pattern is unrecognizable
        """
        self._ed1.pattern = value

    @property
    def polarity(self):
        """
        Data output polarity

        :value: - 'NORMAL'
                - 'INVERTED'
        :type: str
        :raise ValueError: exception if unrecognized logic polarity returned from equipment
        """
        return self._ed1.polarity

    @polarity.setter
    def polarity(self, value):
        """
        :type value: str
        :raise ValueError: exception if invalid polarity requested
        """
        self._ed1.polarity = value

    @property
    def sync_loss(self):
        """
        **READONLY**

        :value: sync loss count for current or last measurement
        :type: int
        """
        return self._demux.sync_loss

    def start_measurement(self):
        """
        Starts a BER measurement
        """
        self._demux.start_measurement()

    def stop_measurement(self):
        """
        Stops a BER measurement
        """
        self._demux.stop_measurement()