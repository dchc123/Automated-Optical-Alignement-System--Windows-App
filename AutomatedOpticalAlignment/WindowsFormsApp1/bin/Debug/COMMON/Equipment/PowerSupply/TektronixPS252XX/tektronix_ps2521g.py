"""
| $Revision:: 281675                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-08-17 16:11:07 +0100 (Fri, 17 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.TektronixPS2521G`
::

    >>> from CLI.Equipment.PowerSupply.TektronixPS252XX.tektronix_ps2521g import TektronixPS2521G
    >>> ps = TektronixPS2521G('GPIB1::23::INSTR')
    >>> ps.connect()

For channel level API:
:py:class:`.TektronixPS2521GChannel`
::

    >>> ps.channel[2].voltage.setpoint = 15
    >>> ps.channel[2].voltage.setpoint
    15
    >>> ps.channel[2].voltage.value
    15.0012
    >>> ps.channel[1].current.value
    0.102
"""

from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_structures import CustomList
from .tektronix_ps252xx import _TektronixPS252XXMemory
from .tektronix_ps252xx import TektronixPS252XX
from .tektronix_ps252xx import TektronixPS252XXChannel
from .tektronix_ps252xx import TektronixPS252XXVoltBlock
from .tektronix_ps252xx import TektronixPS252XXCurrBlock


class TektronixPS2521G(TektronixPS252XX):
    """
    Tektronix PS2521G power supply driver.
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
        """:type: list of TektronixPS2521GChannel"""
        self._memory = _TektronixPS252XXMemory(interface=interface, dummy_mode=dummy_mode)
        self.channel.append(TektronixPS2521GChannel(channel_number=1, memory=self._memory, interface=interface,
                                                    dummy_mode=dummy_mode))
        self.channel.append(TektronixPS2521GChannel(channel_number=2, memory=self._memory, interface=interface,
                                                    dummy_mode=dummy_mode))
        self.channel.append(TektronixPS2521GChannel(channel_number=3, memory=self._memory, interface=interface,
                                                    dummy_mode=dummy_mode))


class TektronixPS2521GChannel(TektronixPS252XXChannel):
    """
    Tektronix PS2521G Channel
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
        if channel_number == 1 or channel_number == 2:
            self.voltage = TektronixPS2521GVoltBlock20(channel_number=channel_number, memory=memory,
                                                       interface=interface, dummy_mode=dummy_mode,
                                                       name=self.name + 'VoltageMeasure')
            self.current = TektronixPS2521GCurrBlock20(channel_number=channel_number, memory=memory,
                                                       interface=interface, dummy_mode=dummy_mode,
                                                       name=self.name + 'CurrentMeasure')
        elif channel_number == 3:
            self.voltage = TektronixPS2521GVoltBlock6(channel_number=channel_number, memory=memory,
                                                      interface=interface, dummy_mode=dummy_mode,
                                                      name=self.name+'VoltageMeasure')
            self.current = TektronixPS2521GCurrBlock6(channel_number=channel_number, memory=memory,
                                                      interface=interface, dummy_mode=dummy_mode,
                                                      name=self.name+'CurrentMeasure')


class TektronixPS2521GVoltBlock6(TektronixPS252XXVoltBlock):
    """
    Tektronix PS2521G voltage sub block for 6V output
    """
    CAPABILITY = {'voltage': {'min': 0.0, 'max': 6.5}}

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


class TektronixPS2521GCurrBlock6(TektronixPS252XXCurrBlock):
    """
    Tektronix PS2521G current sub block for 6V output
    """
    CAPABILITY = {'current': {'min': 0.0, 'max': 5.1}}

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


class TektronixPS2521GVoltBlock20(TektronixPS252XXVoltBlock):
    """
    Tektronix PS2521G voltage sub block for 20V output
    """
    CAPABILITY = {'voltage': {'min': 0.0, 'max': 21.0}}

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


class TektronixPS2521GCurrBlock20(TektronixPS252XXCurrBlock):
    """
    Tektronix PS2521G current sub block for 20V output
    """
    CAPABILITY = {'current': {'min': 0.0, 'max': 2.55}}

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