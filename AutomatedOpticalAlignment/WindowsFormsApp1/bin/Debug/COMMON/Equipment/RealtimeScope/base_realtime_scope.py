"""
| $Revision:: 279019                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-10 14:55:58 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Equipment.Base.base_equipment import BaseEquipment
from COMMON.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseRealtimeScope(BaseEquipment):
    """
    Base Real-time Scope that all Real-time Scopes should be derived from.
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
    def mode(self):
        """
        Specify scope mode

        :value: - 'RUN'
                - 'SINGLE'
        :type: str
        """
        raise NotImplementedError

    @mode.setter
    def mode(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def serial_data(self):
        """
        **READONLY**

        :value: returns a list of Real-time Scope serial data
        :type: list
        """
        raise NotImplementedError


class BaseRealtimeScopeChannel(BaseEquipmentBlock):
    """
    Base Real-time Scope Channel that all Real-time Scopes should be derived from.
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


class BaseRealtimeScopeSubBlock(BaseEquipmentBlock):
    """
    Base Real-time Scope Probe that all Real-time Scopes should be derived from.
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

