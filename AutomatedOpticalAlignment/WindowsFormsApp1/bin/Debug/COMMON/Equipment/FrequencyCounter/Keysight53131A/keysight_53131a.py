"""
| $Revision:: 279451                                   $:  Revision of last commit
| $Author:: ael-khouly@SEMNET.DOM                      $:  Author of last commit
| $Date:: 2018-07-18 15:21:19 +0100 (Wed, 18 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keysight53131A`
::

    >>> from CLI.Equipment.FrequencyCounter.Keysight53131A.keysight_53131a import Keysight53131A
    >>> fc = Keysight53131A('GPIB1::23::INSTR')
    >>> fc.connect()
    >>> fc.channel[1].frequency
    1000
    >>> fc.channel[2].frequency
    2000
    >>> fc.channel[3].gate_time
    0
    >>> fc.channel[3].gate_time = 20
    >>> fc.channel[3].gate_time
    20
"""
from CLI.Utilities.custom_structures import CustomList
from CLI.Equipment.FrequencyCounter.base_frequency_counter import BaseFrequencyCounter
from CLI.Equipment.FrequencyCounter.base_frequency_counter import BaseFrequencyCounterChannel
from CLI.Interfaces.VISA.cli_visa import CLIVISA


class Keysight53131A(BaseFrequencyCounter):
    """
    Keysight53131A frequency counter driver.
    """
    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of Keysight53131AChannel"""
        self.channel.append(Keysight53131AChannel(channel_number=1, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(Keysight53131AChannel(channel_number=2, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(Keysight53131AChannel(channel_number=3, interface=interface, dummy_mode=dummy_mode))


class Keysight53131AChannel(BaseFrequencyCounterChannel):
    """
    Keysight53131A frequency counter channel driver.
    """
    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number

    @property
    def frequency(self):
        """
        **READONLY**

        :value: measure frequency in Hz
        :type: float
        """
        self._write(":FUNC 'FREQ %s" % self._channel_number)
        return float(self._read("READ:FREQ?"))

    @property
    def gate_time(self):
        """
        Gate time for frequency measurement.

        :value: determines frequency resolution, the larger the gate_time, the higher the resolution
        :type: float
        """
        return float(self._read(':FREQ:ARM:STOP:TIM?'))

    @gate_time.setter
    def gate_time(self, value):
        """
        :type value: float
        """
        self._write(":FREQ:ARM:STAR:SOUR IMM")
        self._write(":FREQ:ARM:STOP:SOUR TIM")
        self._write(":FREQ:ARM:STOP:TIM %s" % value)


