"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Equipment.Base.base_equipment import BaseEquipment
from COMMON.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseMultimeter(BaseEquipment):
    """
    Base Multimeter class that all Multimeter should be derived from.
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


class BaseMultimeterMeasurementBlock(BaseEquipmentBlock):
    """
    Base measurement block that all measurement blocks should be derived from.
    """
    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous voltage/current/resistance in V/A/Ohm
        :type: float
        """
        raise NotImplementedError

    @property
    def meas_mode(self):
        """
        :value: measurement mode ('AUTO' or 'MANUAL')
        :type: str
        """
        raise NotImplementedError

    @meas_mode.setter
    def meas_mode(self, value):
        """
        :type: str
        """
        raise NotImplementedError

    @property
    def nplc(self):
        """
        :value: Power line cycles per integration
        :type: float
        """
        raise NotImplementedError

    @nplc.setter
    def nplc(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def range(self):
        """
        :value: range of measurement
        :type: float
        """
        raise NotImplementedError

    @range.setter
    def range(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

