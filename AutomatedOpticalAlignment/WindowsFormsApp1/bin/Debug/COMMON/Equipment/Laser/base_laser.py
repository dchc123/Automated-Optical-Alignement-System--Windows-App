"""
| $Revision:: 278910                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-06 01:01:42 +0100 (Fri, 06 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.Base.base_equipment import BaseEquipment


class BaseLaser(BaseEquipment):
    """
    Base Laser class that all Laser should be derived from.
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

    @property
    def output(self):
        """
        Enable state of the output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def power_level(self):
        """
        :value: power level
        :type: float
        """
        raise NotImplementedError

    @power_level.setter
    def power_level(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def power_unit(self):
        """
        Power unit

        :value: - 'dBm'
                - 'Watt'
        :type: str
        """
        raise NotImplementedError

    @power_unit.setter
    def power_unit(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

