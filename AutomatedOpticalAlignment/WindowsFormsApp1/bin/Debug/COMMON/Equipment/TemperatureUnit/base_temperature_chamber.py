from COMMON.Equipment.TemperatureUnit.base_temperature_unit import BaseTemperatureUnit


class BaseTemperatureChamber(BaseTemperatureUnit):
    """
    Base Temperature Chamber class that all Temperature Chamber Units (Ovens) should be derived from.
    """
    CAPABILITY = {'temperature': {'min': 0, 'max': 0}}

    def __init__(self, address, interface, dummy_mode, temp_limit, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param temp_limit: the limit type defining the limiting temperature range
        :type temp_limit: str
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, temp_limit=temp_limit, **kwargs)
