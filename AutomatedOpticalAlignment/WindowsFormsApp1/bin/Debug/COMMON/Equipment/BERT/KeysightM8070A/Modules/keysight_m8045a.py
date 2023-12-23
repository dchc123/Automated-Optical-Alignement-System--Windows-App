"""
| $Revision:: 282004                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-08-30 14:55:09 +0100 (Thu, 30 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from .keysight_m80xxx_ppg import KeysightM80XXXPPG


class KeysightM8045A(KeysightM80XXXPPG):
    """
    Keysight M8045A PPG Channel
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
