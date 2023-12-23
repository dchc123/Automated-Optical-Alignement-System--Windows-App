"""
Author:: tbrooks@semtech.com
date::
"""

from .keysight_n4951x_xnn_ppg import KeysightN4951XXNNPPG


class KeysightN4951BD32PPG(KeysightN4951XXNNPPG):
    """
    Keysight N4951B-D32 Programmable Pattern Generator
    """
    CAPABILITY = {'amplitude': {'min': 0.3, 'max': 3.0},
                  'frequency': {'min': None, 'max': None}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
