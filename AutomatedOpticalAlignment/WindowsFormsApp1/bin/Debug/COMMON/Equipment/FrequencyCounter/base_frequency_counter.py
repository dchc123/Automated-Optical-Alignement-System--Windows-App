"""
| $Revision:: 279019                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-10 14:55:58 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.Base.base_equipment import BaseEquipment
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseFrequencyCounter(BaseEquipment):
    """
    Base Frequency Counter class that all Frequency Counter should be derived from.
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


class BaseFrequencyCounterChannel(BaseEquipmentBlock):
    """
    Base frequency counter output channel class that all channels should be derived from.
    """
    def __init__(self, interface, dummy_mode=False, **kwargs):
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
    def frequency(self):
        """
        **READONLY**

        :value: measure frequency in Hz
        :type: float
        """
        raise NotImplementedError

    @property
    def gate_time(self):
        """
        Gate time for frequency measurement.

        :value: determines frequency resolution, the larger the gate_time, the higher the resolution
        :type: float
        """
        raise NotImplementedError

    @gate_time.setter
    def gate_time(self, value):
        """
        :type value: float
        """
        raise NotImplementedError
