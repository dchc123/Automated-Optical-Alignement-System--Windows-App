"""
| $Revision:: 279062                                   $:  Revision of last commit
| $Author:: ael-khouly@SEMNET.DOM                      $:  Author of last commit
| $Date:: 2018-07-10 19:29:10 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
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


class AnritsuMU182040AChannel(AnritsuMP1800ED):
    """
    A single channel for the Anritsu MU182040A/41A 1/2ch 25GBit/s DEMUX module
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
                         nterface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def bit_count(self):
        """
        **READONLY**

        :value: accumulated bit count of current or last measurement
        :type: int
        """
        return int(self._read(':DEMux:CALCulate:DATA:EALarm? "CURRent:CC:TOTal"'))

    @property
    def clock_delay(self):
        """
        Clock delay

        :value: clock delay in s
        :type: float
        """
        return float(self._read(":DEMux:CLOCk:PDELay?")) / 1e12

    @clock_delay.setter
    def clock_delay(self, value):
        """
        :type value: float
        """
        delay_ps = int(value * 1e12)

        self._write(":DEMux:CLOCk:PDELay %d" % delay_ps)

    @property
    def error_count(self):
        """
        **READONLY**

        :value: error count of current or last measurement
        :type: int
        """
        return int(self._read(':DEMux:CALCulate:DATA:EALarm? "CURRent:EC:TOTal""'))

    @property
    def error_rate(self):
        """
        **READONLY**

        :value: error rate of current or last measurement
        :type: float
        """
        return float(self._read(':DEMux:CALCulate:DATA:EALarm? "CURRent:ER:TOTal"'))

    @property
    def input_threshold(self):
        """
        Input threshold voltage (in Volts). To maximize compatibility with
        different BERTs, the recommended voltage range is [-0.25, 0.25] V.

        :value: threshold in V
        :type: float
        :raise ValueError: exception if threshold is not between -3.5V and 3.3V
        """
        return float(self._read(":DEMux:DATA:THReshold? DATA"))

    @input_threshold.setter
    def input_threshold(self, value):
        """
        :type value: float
        :raise ValueError: exception if threshold is not between -3.5V and 3.3V
        """
        if value < -3.5 or value > 3.3:
            raise ValueError("Threshold out of range [-3.5, 3.3] V")

        self._write(":DEMux:DATA:THReshold DATA,%.3f" % value)
        self._write(":DEMux:DATA:THReshold XDATa,%.3f" % value)

    @property
    def measurement_status(self):
        """
        **READONLY** BER measurement status

        :value: - 'INACTIVE'
                - 'ACTIVE'
        :type: str
        """
        return self._read(":DEMux:MEASure:EALarm:STATe?")

    @property
    def sync_loss(self):
        """
        **READONLY**

        :value: sync loss count for current or last measurement
        :type: int
        """
        ret_str = self._read(':DEMux:CALCulate:DATA:MONitor? "PSLoss"')
        if ret_str == "Occur":
            return 1
        else:
            return 0

    def start_measurement(self):
        """
        Starts a BER measurement
        """
        self._write(":DEMux:MEASure:STARt")

    def stop_measurement(self):
        """
        Stops a BER measurement
        """
        self._write(":DEMux:MEASure:STOP")