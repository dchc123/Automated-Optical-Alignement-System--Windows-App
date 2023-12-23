"""
| $Revision:: 279451                                   $:  Revision of last commit
| $Author:: ael-khouly@SEMNET.DOM                      $:  Author of last commit
| $Date:: 2018-07-18 15:21:19 +0100 (Wed, 18 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.Base.base_equipment import BaseEquipment
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock
from CLI.Utilities.custom_structures import CustomList


class BaseRFAttenuator(BaseEquipment):
    """
    Base RF Attenuator class that all Attenuators should be derived from.
    """
    def __init__(self, address, interface, dummy_mode, **kwargs):
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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()


class BaseFRAttenuatorChannel(BaseEquipmentBlock):
    """
    Base RF Attenuator Channel class that all attenuator channels should be derived from.
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
    def attenuation(self):
        """
        :value: attenuation level in dB
        :type: float
        """
        raise NotImplementedError

    @attenuation.setter
    def attenuation(self, value):
        """
        :type value: float
        """
        raise NotImplementedError
