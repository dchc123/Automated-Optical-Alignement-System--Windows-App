"""
| $Revision:: 281939                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-08-28 19:02:27 +0100 (Tue, 28 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.XantrexXDL35_5XX`
::

    >>> from CLI.Equipment.PowerSupply.XantrexXDL35_5XX.xantrex_xdl35_5tp import XantrexXDL35_5TP
    >>> ps = XantrexXDL35_5TP('GPIB1::23::INSTR')
    >>> ps.connect()

For channel level API:
:py:class:`.XantrexXDL35_5TPChannel`
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
from .xantrex_xdl35_5xx import _Xantrex_XDL35_5XXMemory
from .xantrex_xdl35_5xx import XantrexXDL35_5XX
from .xantrex_xdl35_5xx import XantrexXDL35_5XXChannel
from .xantrex_xdl35_5xx import XantrexXDL35_5XXVoltBlock
from .xantrex_xdl35_5xx import XantrexXDL35_5XXCurrBlock


class XantrexXDL35_5TP(XantrexXDL35_5XX):
    """
    Xantrex XDL35-5TP power supply driver.
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
        """:type: list of XantrexXDL35_5TPChannel"""
        self._memory = _Xantrex_XDL35_5XXMemory(interface=interface, dummy_mode=dummy_mode)
        self.channel.append(XantrexXDL35_5TPChannel(channel_number=1, memory=self._memory, interface=interface,
                                                    dummy_mode=dummy_mode))
        self.channel.append(XantrexXDL35_5TPChannel(channel_number=2, memory=self._memory, interface=interface,
                                                    dummy_mode=dummy_mode))
        self.channel.append(XantrexXDL35_5TPChannel(channel_number=3, memory=self._memory, interface=interface,
                                                    dummy_mode=dummy_mode))


class XantrexXDL35_5TPChannel(XantrexXDL35_5XXChannel):
    """
    Xantrex XDL35-5TP Channel
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
            self.voltage = XantrexXDL35_5TPVoltBlock(channel_number=channel_number, memory=memory,
                                                     interface=interface, dummy_mode=dummy_mode)
            self.current = XantrexXDL35_5TPCurrBlock(channel_number=channel_number, memory=memory,
                                                     interface=interface, dummy_mode=dummy_mode)


class XantrexXDL35_5TPVoltBlock(XantrexXDL35_5XXVoltBlock):
    """
    Xantrex XDL35-5TP voltage sub block
    """
    CAPABILITY = {'voltage': {'min': 0.0, 'max': 35}}

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


class XantrexXDL35_5TPCurrBlock(XantrexXDL35_5XXCurrBlock):
    """
    Xantrex XDL35-5TP current sub block
    """
    CAPABILITY = {'current': {'min': 0.0, 'max': 5}}

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
