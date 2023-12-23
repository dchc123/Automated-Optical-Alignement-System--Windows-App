"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.KeysightE3631A`
::

    >>> from CLI.Equipment.PowerSupply.KeysightE36XXX.keysight_e3631a import KeysightE3631A
    >>> ps = KeysightE3631A('GPIB1::23::INSTR')
    >>> ps.connect()

For channel level API:
:py:class:`.KeysightE3631AChannel`
::

    >>> ps.channel[2].voltage.setpoint = 5
    >>> ps.channel[2].voltage.setpoint
    5
    >>> ps.channel[2].voltage.value
    5.0012
    >>> ps.channel[1].current.value
    0.102
"""
from CLI.Utilities.custom_exceptions import NotSupportedError
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_structures import CustomList
from .keysight_e36xxx import _KeysightE36XXXMemory
from .keysight_e36xxx import KeysightE36XXX
from .keysight_e36xxx import KeysightE36XXXChannel
from .keysight_e36xxx import KeysightE36XXXVoltBlock
from .keysight_e36xxx import KeysightE36XXXCurrBlock


class KeysightE3631A(KeysightE36XXX):
    """
    Keysight E3631A power supply driver.
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
        """:type: list of KeysightE3631AChannel"""
        self._memory = _KeysightE36XXXMemory(interface=interface, dummy_mode=dummy_mode)
        self.channel.append(KeysightE3631AChannel(channel_number=1, memory=self._memory, interface=interface,
                                                  dummy_mode=dummy_mode))
        self.channel.append(KeysightE3631AChannel(channel_number=2, memory=self._memory, interface=interface,
                                                  dummy_mode=dummy_mode))
        self.channel.append(KeysightE3631AChannel(channel_number=3, memory=self._memory, interface=interface,
                                                  dummy_mode=dummy_mode))


class KeysightE3631AChannel(KeysightE36XXXChannel):
    """
    Keysight E3631A Channel
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
        # if statement is to allow the blocks for 3 channels to have its own CAPABILITY, working just like other PSUs
        if channel_number == 1:
            self.voltage = KeysightE3631AVoltBlockP6(channel_number=channel_number, memory=memory, interface=interface,
                                                     dummy_mode=dummy_mode, name=self.name+'VoltageMeasure')
            self.current = KeysightE3631AVoltBlockP6(channel_number=channel_number, memory=memory, interface=interface,
                                                     dummy_mode=dummy_mode, name=self.name+'CurrentMeasure')
        elif channel_number == 2:
            self.voltage = KeysightE3631AVoltBlockP25(channel_number=channel_number, memory=memory, interface=interface,
                                                      dummy_mode=dummy_mode, name=self.name+'VoltageMeasure')
            self.current = KeysightE3631ACurrBlockP25(channel_number=channel_number, memory=memory, interface=interface,
                                                      dummy_mode=dummy_mode, name=self.name+'CurrentMeasure')
        elif channel_number == 3:
            self.voltage = KeysightE3631AVoltBlockM25(channel_number=channel_number, memory=memory, interface=interface,
                                                      dummy_mode=dummy_mode, name=self.name+'VoltageMeasure')
            self.current = KeysightE3631ACurrBlockM25(channel_number=channel_number, memory=memory, interface=interface,
                                                      dummy_mode=dummy_mode, name=self.name+'CurrentMeasure')


class KeysightE3631AVoltBlockP6(KeysightE36XXXVoltBlock):
    """
    Keysight E3631A voltage +6 sub block
    """
    CAPABILITY = {'voltage': {'min': 0.01, 'max': 6.18}}

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
        super().__init__(channel_number=channel_number, range_values=None, range_threshold=None, memory=memory,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    def ovp(self):
        """
        :raise NotSupportedError: Over voltage protection is not supported
        """
        raise NotSupportedError("%s does not support over voltage protection" % self.name)

    @property
    def protection_level(self):
        """
        :raise NotSupportedError: Over protection level is not supported
        """
        raise NotSupportedError("%s does not support over voltage protection" % self.name)

    @protection_level.setter
    def protection_level(self, value):
        """
        :raise NotSupportedError: Over protection level is not supported
        """
        raise NotSupportedError("%s does not support over voltage protection" % self.name)

    @property
    def _range(self):
        """
        :raise NotSupportedError: Range is not supported
        """
        raise NotSupportedError("%s does not support voltage range" % self.name)

    @_range.setter
    def _range(self, value):
        """
        :raise NotSupportedError: Range is not supported
        """
        raise NotSupportedError("%s does not support voltage range" % self.name)

    @property
    def setpoint(self):
        """
        :value: voltage level setting in V
        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        self._memory.channel = self._channel_number
        return float(self._read("VOLTage?"))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        self._memory.channel = self._channel_number

        range_min = self.CAPABILITY['voltage']['min']
        range_max = self.CAPABILITY['voltage']['max']

        if value < range_min or value > range_max:
            raise ValueError("%s is an invalid voltage setpoint. See supported setpoint range. (min:%s|max:%s)"
                             % (value, range_min, range_max))

        self._write("VOLTage %s" % value)

    def clear_protection(self):
        """
        :raise NotSupportedError: protection level is not supported
        """
        raise NotSupportedError("%s does not support over voltage protection" % self.name)

    @property
    def protection_tripped(self):
        """
        :raise NotSupportedError: protection level is not supported
        """
        raise NotSupportedError("%s does not support over voltage protection" % self.name)


class KeysightE3631ACurrBlockP6(KeysightE36XXXCurrBlock):
    """
    Keysight E3631A current +6 sub block
    """
    CAPABILITY = {'current': {'min': 0.01, 'max': 5.15}}

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
        super().__init__(channel_number=channel_number,  range_values=None, range_threshold=None, memory=memory,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def setpoint(self):
        """
        :value: current level setting in A
        :type: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        self._memory.channel = self._channel_number
        return float(self._read("CURRent?"))

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        :raise ValueError: Exception if setpoint value is out of range
        """
        self._memory.channel = self._channel_number

        range_min = self.CAPABILITY['current']['min']
        range_max = self.CAPABILITY['current']['max']

        if value < range_min or value > range_max:
            raise ValueError("%s is an invalid current setpoint. See supported setpoint range. (min:%s|max:%s)"
                             % (value, range_min, range_max))

        self._write("CURRent %s" % value)


class KeysightE3631AVoltBlockP25(KeysightE3631AVoltBlockP6):
    """
    Keysight E3631A voltage +25 sub block
    """
    CAPABILITY = {'voltage': {'min': 0.0, 'max': 25.75}}

    def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
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
        super().__init__(channel_number=channel_number, memory=memory, interface=interface,
                         dummy_mode=dummy_mode, **kwargs)


class KeysightE3631ACurrBlockP25(KeysightE3631ACurrBlockP6):
    """
    Keysight E3631A current +25 sub block
    """
    CAPABILITY = {'current': {'min': 0.0, 'max': 1.03}}

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
        super().__init__(channel_number=channel_number, memory=memory, interface=interface,
                         dummy_mode=dummy_mode, **kwargs)


class KeysightE3631AVoltBlockM25(KeysightE3631AVoltBlockP6):
    """
    Keysight E3631A voltage -25 sub block
    """
    CAPABILITY = {'voltage': {'min': -25.75, 'max': 0.0}}

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
        super().__init__(channel_number=channel_number, memory=memory, interface=interface,
                         dummy_mode=dummy_mode, **kwargs)


class KeysightE3631ACurrBlockM25(KeysightE3631ACurrBlockP6):
    """
    Keysight E3631A current -25 sub block
    """
    CAPABILITY = {'current': {'min': 0.0, 'max': 1.03}}

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
        super().__init__(channel_number=channel_number, memory=memory, interface=interface,
                         dummy_mode=dummy_mode, **kwargs)
