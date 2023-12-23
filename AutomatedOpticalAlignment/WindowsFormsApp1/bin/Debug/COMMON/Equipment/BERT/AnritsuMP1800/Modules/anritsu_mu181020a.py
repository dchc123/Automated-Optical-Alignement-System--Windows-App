"""
| $Revision:: 279062                                   $:  Revision of last commit
| $Author:: ael-khouly@SEMNET.DOM                      $:  Author of last commit
| $Date:: 2018-07-10 19:29:10 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the Error Detector API: See :py:mod:`Equipment.BERT.AnritsuMP1800.Modules.anritsu_mp1800_ppg`
::

    >>> from CLI.Equipment.BERT.AnritsuMP1800.anritsu_mp1800 import AnritsuMP1800
    >>> bert = AnritsuMP1800('GPIB1::23::INSTR')
    >>> bert.connect()
    >>> bert.ppg[1].clock_output
    'DISABLE'
    >>> bert.ppg[1].clock_output = 'ENABLE'
    >>> bert.ppg[1].clock_output
    'ENABLE'
"""
from .anritsu_mp1800_ppg import AnritsuMP1800PPG


class AnritsuMU181020AChannel(AnritsuMP1800PPG):
    """
    A single channel for the Anritsu MU181020A/20B 12.5/14 Gbit/s PPG.
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
                         interface=interface, dummy_mode=dummy_mode, **kwargs)