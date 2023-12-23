"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.KeysightE3640A`
::

    >>> from COMMON.Equipment.PowerSupply.KeysightE36XXX.keysight_e3640a import KeysightE3640A
    >>> ps = KeysightE3640A('GPIB1::23::INSTR')
    >>> ps.connect()

For channel level API:
:py:class:`.KeysightE3640AChannel`
::

    >>> ps.channel[1].voltage.setpoint = 5
    >>> ps.channel[1].voltage.setpoint
    5
    >>> ps.channel[1].voltage.value
    5.0012
    >>> ps.channel[1].current.value
    0.102
    >>> ps.channel[1].voltage.limit = 10
    >>> ps.channel[1].voltage.setpoint =11
    >>> ps.channel[1].voltage.protection_tripped
    True
    >>> ps.channel[1].voltage.setpoint = 9
    >>> ps.channel[1].voltage.clear_protection()
"""
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_structures import CustomList
from .keysight_e36xxx import _KeysightE36XXXMemory
from .keysight_e36xxx import KeysightE36XXX
from .keysight_e36xxx import KeysightE36XXXChannel
from .keysight_e36xxx import KeysightE36XXXVoltBlock
from .keysight_e36xxx import KeysightE36XXXCurrBlock


class _KeysightE3640AMemory(_KeysightE36XXXMemory):
    """
    Simple container for information meant to be retained Stored in a class so that it can
    be passed by reference.
    """
    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def channel(self):
        return

    @channel.setter
    def channel(self, value):
        pass


class KeysightE3640A(KeysightE36XXX):
    """
    Keysight E3640A power supply driver.
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
        """:type: list of KeysightE3640AChannel"""
        self._memory = _KeysightE3640AMemory(interface=interface, dummy_mode=dummy_mode)
        self.channel.append(KeysightE3640AChannel(channel_number=1, memory=self._memory,
                                                  interface=interface, dummy_mode=dummy_mode))


class KeysightE3640AChannel(KeysightE36XXXChannel):
    """
    Keysight E3640A Channel
    """
    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param memory: shared memory container for all sub-blocks
        :type memory: _KeysightE36XXXMemory
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, memory=memory,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

        temp_range_values = {"ALL": ['P8V', 'P20V', 'LOW', 'HIGH'],
                             "LOW": ['P8V', 'LOW'], "HIGH": ['P20V', 'HIGH']}
        volt_threshold = 8.24
        curr_threshold = 3.09
        self.voltage = KeysightE3640AVoltBlock(channel_number=channel_number, range_values=temp_range_values,
                                               range_threshold=volt_threshold, memory=memory,
                                               interface=interface, dummy_mode=dummy_mode,
                                               name=self.name+'VoltageMeasure')
        self.current = KeysightE3640ACurrBlock(channel_number=channel_number, range_values=temp_range_values,
                                               range_threshold=curr_threshold, memory=memory,
                                               interface=interface, dummy_mode=dummy_mode,
                                               name=self.name+'CurrentMeasure')


class KeysightE3640AVoltBlock(KeysightE36XXXVoltBlock):
    """
    Keysight E3640A voltage sub block
    """
    CAPABILITY = {'voltage': {'min': 0.01, 'max': 20.6}}

    def __init__(self, channel_number, range_values, range_threshold, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param range_values: range values to use for error checking and range change
        :type range_values: dict
        :param range_threshold: voltage range threshold
        :type range_threshold: float
        :param memory: shared memory container for all sub-blocks
        :type memory: _KeysightE36XXXMemory
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, range_values=range_values, range_threshold=range_threshold,
                         memory=memory, interface=interface, dummy_mode=dummy_mode, **kwargs)


class KeysightE3640ACurrBlock(KeysightE36XXXCurrBlock):
    """
    Keysight E3640A current sub block
    """
    CAPABILITY = {'current': {'min': 0.01, 'max': 3.09}}

    def __init__(self, channel_number, range_values, range_threshold, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param range_values: range values to use for error checking and range change
        :type range_values: dict
        :param range_threshold: current range threshold
        :type range_threshold: float
        :param memory: shared memory container for all sub-blocks
        :type memory: _KeysightE36XXXMemory
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, range_values=range_values, range_threshold=range_threshold,
                         memory=memory, interface=interface, dummy_mode=dummy_mode, **kwargs)