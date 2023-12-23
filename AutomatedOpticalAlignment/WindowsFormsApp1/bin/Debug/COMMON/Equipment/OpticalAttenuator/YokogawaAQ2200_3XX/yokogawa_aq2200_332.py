"""
| $Revision:: 283708                                   $:  Revision of last commit
| $Author:: lagapie@SEMNET.DOM                         $:  Author of last commit
| $Date:: 2018-11-16 18:15:08 +0000 (Fri, 16 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.YokogawaAQ2200_332`
::

    >>> from CLI.Equipment.OpticalAttenuator.YokogawaAQ2200_3XX.yokogawa_aq2200_332 import YokogawaAQ2200_332
    >>> Att = YokogawaAQ2200_332('TCPIP0::10.2.72.29::50000::SOCKET',9)
    >>> Att.connect()
    >>> Att.zero_all()

For channel level API: See :py:class:`.YokogawaAQ2200_332Channel`
::

    >>> Att.channel[1].power_unit = "dBm"
    >>> Att.channel[1].attenuation = 10
    >>> Att.channel[1].attenuation
    10.0
"""

from CLI.Mainframes.YokogawaAQ221X.yokogawa_aq221x import YokogawaAQ221X
from .yokogawa_aq2200_3xx import YokogawaAQ2200_3XX
from .yokogawa_aq2200_3xx import YokogawaAQ2200_3XXChannel
from CLI.Utilities.custom_exceptions import NotSupportedError
from CLI.Utilities.custom_structures import CustomList

class YokogawaAQ2200_332(YokogawaAQ2200_3XX):
    """
    Yokogawa AQ2200-332 optical attenuator (SMF or MMF) with power control driver
    """

    CAPABILITY = {'channels': None}

    def __init__(self, address, slot_number, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param slot_number: the physical slot within the main frame
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
        """:type: list of  YokogawaAQ2200_332Channel"""
        self.channel.append(YokogawaAQ2200_332Channel(slot_number=slot_number, channel_number=1, interface=interface,
                                                      dummy_mode=dummy_mode))


class YokogawaAQ2200_332Channel(YokogawaAQ2200_3XXChannel):
    """
    Yokogawa AQ2200-332 (MMF or SMF) optical attenuator with power control channel
    """

    CAPABILITY = {'attenuation_range': {'min': 0, 'max': 45},
                  'attenuation_offset_range': {'min': -200, 'max': 200},
                  'opm_avg_time': {'min': 0.01, 'max': 10},
                  'power_level_dBm_range': {'min': -50, 'max': 19},
                  'power_level_offset_range': {'min': -60, 'max': 60},
                  'power_level_watt_range': {'min': 0.00000001, 'max': 0.1},
                  'speed_range': {'min': 4, 'max': 80},
                  'wavelength_range': {'min': None, 'max': None},
                  }

    def __init__(self, slot_number, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param slot_number: the physical slot within the main frame
        :type slot_number: int
        :param channel_number: channel number of the attenuator
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(slot_number=slot_number, channel_number=channel_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def power_control(self):
        """
        Disable or Enable power control mode --NOT SUPPORTED
        """
        raise NotSupportedError

    @power_control.setter
    def power_control(self, value):
        """
        Disable or Enable power control mode --NOT SUPPORTED
        """
        raise NotSupportedError

    @property
    def speed(self):
        """
        Attenuation filter speed- NOT SUPPORTED
        """
        raise NotSupportedError

    @speed.setter
    def speed(self, value):
        """
        Attenuation filter speed- NOT SUPPORTED
        """
        raise NotSupportedError
