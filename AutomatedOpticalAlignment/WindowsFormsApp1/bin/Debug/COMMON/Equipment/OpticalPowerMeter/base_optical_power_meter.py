"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.Base.base_equipment import BaseEquipment
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseOpticalPowerMeter(BaseEquipment):
    """
    Base Optical Power Meter class that all Optical Power Meter should be derived from.
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


class BaseOpticalPowerMeterChannel(BaseEquipmentBlock):
    """
    Base power meter channel class that all optical power meter channels should be derived from.
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
    def avg_time(self):
        """
        :value: optical power meter averaging time (s)
        :type: float
        """
        raise NotImplementedError

    @avg_time.setter
    def avg_time(self, value):
        """
        :type: float
        """
        raise NotImplementedError

    @property
    def value(self):
        """
        READONLY
        Value relies on power units
        :py:class:`.power_unit`

        :value: measured instantaneous power level dBm/W
        :type: float
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

    @property
    def wavelength(self):
        """
        Wavelength of signal

        :value: wavelength (nm)
        :type: float
        """
        raise NotImplementedError

    @wavelength.setter
    def wavelength(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    def zero_offset(self):
        """
        Zeros the electrical offsets of the power meter
        """
        raise NotImplementedError
