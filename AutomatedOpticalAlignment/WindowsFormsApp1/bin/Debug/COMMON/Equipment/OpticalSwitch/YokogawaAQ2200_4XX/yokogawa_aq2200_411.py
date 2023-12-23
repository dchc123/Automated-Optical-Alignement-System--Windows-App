"""
| $Revision:: 283619                                   $:  Revision of last commit
| $Author:: lagapie@SEMNET.DOM                         $:  Author of last commit
| $Date:: 2018-11-14 18:37:26 +0000 (Wed, 14 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.YokogawaAQ2200_411`
::

    >>> from CLI.Equipment.OpticalSwitch.YokogawaAQ2200_4XX.yokogawa_aq2200_411 import YokogawaAQ2200_411
    >>> sw = YokogawaAQ2200_411('TCPIP0::10.2.72.29::50000::SOCKET',1)
    >>> sw.connect()

For channel level API:
:py:class:`.YokogawaAQ2200_411Channel`
::

    >>> sw.channel[1].close(1, 2)
    >>> sw.channel[1].current_routing()
    [[1, 2]]
    >>> sw.channel[1].add_state("state1", 1, 1)
    >>> sw.channel[1].add_state("state2", 1, 2)
    >>> sw.channel[1].states()
    {'state1': [1, 1], 'state2': [1, 2]}
    >>> sw.channel[1].close_state("state1")
    >>> sw.channel[1].current_routing()
    [[1, 1]]

"""
from CLI.Mainframes.YokogawaAQ221X.yokogawa_aq221x import YokogawaAQ221X
from CLI.Utilities.custom_structures import CustomList
from ..YokogawaAQ2200_4XX.yokogawa_aq2200_4xx import YokogawaAQ2200_4XX
from ..YokogawaAQ2200_4XX.yokogawa_aq2200_4xx import  YokogawaAQ2200_4XXChannel


class YokogawaAQ2200_411(YokogawaAQ2200_4XX):
    """
    Yokogawa AQ2200_411 optical switch driver
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
            interface = YokogawaAQ221X()
        super().__init__(address=address, slot_number=slot_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of YokogawaAQ2200_411Channel"""
        self.channel.append(YokogawaAQ2200_411Channel(channel_number=1, slot_number=slot_number, interface=interface,
                                                      dummy_mode=dummy_mode))


class YokogawaAQ2200_411Channel(YokogawaAQ2200_4XXChannel):
    """
    Yokogawa AQ2200-411 optical switch channel
    """
    CAPABILITY = {'in_ports': [None],
                  'out_ports': [None],
                  'optical_fiber_type': [None],
                  'wavelength_range': {'min': None, 'max': None},
                  }

    def __init__(self, channel_number, slot_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the switch
        :type channel_number: int
        :param slot_number: slot number of the module
        :type slot_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, slot_number=slot_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

