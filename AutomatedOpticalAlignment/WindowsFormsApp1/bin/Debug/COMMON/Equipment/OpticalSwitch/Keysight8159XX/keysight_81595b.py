"""
| $Revision:: 280528                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-31 13:51:18 +0100 (Tue, 31 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keysight81595B`
::

    >>> from CLI.Equipment.OpticalSwitch.Keysight8159XX.keysight_81595b import Keysight81595B
    >>> sw = Keysight81595B('GPIB1::23::INSTR', 1)
    >>> sw.connect()

For channel level API:
:py:class:`.Keysight81595BChannel`
::

    >>> sw.channel[1].close(1, 2)
    >>> sw.channel[1].current_routing()
    [[1, 2]]
    >>> sw.channel[1].add_state("state1", 1, 1)
    >>> sw.channel[1].add_state("state2", 1, 4)
    >>> sw.channel[1].states()
    {'state1': [1, 1], 'state2': [1, 4]}
    >>> sw.channel[1].close_state("state1")
    >>> sw.channel[1].current_routing()
    [[1, 1]]

"""
from CLI.Mainframes.Keysight816XX.keysight_8163x import Keysight8163X
from CLI.Utilities.custom_structures import CustomList
from ..Keysight8159XX.keysight_8159xx import Keysight8159XX
from ..Keysight8159XX.keysight_8159xx import Keysight8159XXChannel


class Keysight81595B(Keysight8159XX):
    """
    Keysight 81595B optical switch driver
    """

    CAPABILITY = {'channel': 1}

    def __init__(self, address, slot_number, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address of the mainframe controlling this module
        :type address: int or str
        :param slot_number: slot number of the module
        :type slot_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = Keysight8163X()
        super().__init__(address=address, slot_number=slot_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of Keysight81595BChannel"""
        self.channel.append(Keysight81595BChannel(channel_number=1, slot_number=slot_number, interface=interface,
                                                  dummy_mode=dummy_mode))


class Keysight81595BChannel(Keysight8159XXChannel):
    """
    Keysight 81595B optical switch channel
    """

    CAPABILITY = {'in_ports': [1], 'out_ports': [1, 2, 3, 4]}

    def __init__(self, channel_number, slot_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the switch
        :type channel_number: int
        :param slot_number: slot number of the module
        :type slot_number: int
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, slot_number=slot_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)




