"""
| $Revision:: 282825                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-10-12 21:24:43 +0100 (Fri, 12 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from abc import abstractmethod
from COMMON.Equipment.Base.base_equipment import BaseEquipment


class BaseTemperatureUnit(BaseEquipment):
    """
    Base Temperature Unit class that all Temperature Units should be derived from.
    """
    CAPABILITY = {'temperature': {'min': 0, 'max': 0}}

    _TEMPERATURE_LIMITS = {
        'high': {'min': -60, 'max': 120},
        'low': {'min': -60, 'max': 60},
        'disabled': {'min': float('-inf'), 'max': float('inf')}
    }

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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._temp_limit = None
        self.temp_limit = temp_limit

    @property
    def temp_limit(self):
        """
        Returns the temp limit

        :rtype: str
        """
        return self._temp_limit

    @temp_limit.setter
    def temp_limit(self, value):
        """
        Sets the temp limit so that the proper temperature range is enforced

        :param value: the temp limit as defined by _TEMPERATURE_LIMITS
        :type value: str
        """
        if isinstance(value, str):
            value = value.lower()
            if value in BaseTemperatureUnit._TEMPERATURE_LIMITS.keys():
                self._temp_limit = value
            else:
                raise ValueError('Limit type expected one of {0} but received {1}!'.
                                 format(BaseTemperatureUnit._TEMPERATURE_LIMITS.keys(), value))
        else:
            raise TypeError('Limit type must be of type str!')

    @property
    @abstractmethod
    def setpoint(self):
        """
        Returns the temperature setpoint of the unit

        :rtype: float
        """
        raise NotImplementedError

    @setpoint.setter
    @abstractmethod
    def setpoint(self, value):
        """
        Sets the unit temperature

        :param value: temperature value to set
        :type value: str or float or int
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def unit_temperature(self):
        """
        Returns the current unit temperature reading from the unit

        :rtype: float
        """
        raise NotImplementedError

    # TODO: Change to Min & Max Temp limit
    @property
    def min_temperature_limit(self):
        """
        Returns the minimum temperature allowed in the current temperature range

        :rtype: float
        """
        return BaseTemperatureUnit._TEMPERATURE_LIMITS[self.temp_limit]['min']

    @property
    def max_temperature_limit(self):
        """
        Returns the maximum temperature allowed in the current temperature range

        :rtype: float
        """
        return BaseTemperatureUnit._TEMPERATURE_LIMITS[self.temp_limit]['max']

    def _check_temperature_limit(self, value):
        """
        Compares the value to both the units temperature range and the temperature limit being enforced

        :param value: the temperature being set
        :type value: float
        """
        # Ensure the temperature is within the units capability
        if (value < self.CAPABILITY['temperature']['min']) or (value > self.CAPABILITY['temperature']['max']):
            raise ValueError('Setpoint temperature exceeds supported range of unit! ({0}C to {1}C)'.format(
                self.CAPABILITY['temperature']['min'], self.CAPABILITY['temperature']['max']))
        # Ensure the temperature is within the allowable range of the current limit type
        if (value < BaseTemperatureUnit._TEMPERATURE_LIMITS[self.temp_limit]['min']) or \
                (value > BaseTemperatureUnit._TEMPERATURE_LIMITS[self.temp_limit]['max']):
            # TODO: Put in what range it's in
            raise ValueError('Temperature setpoint exceeds the temperature lockout range! {0} range:({1}C to {2}C)'
                             .format(self.temp_limit,
                                     BaseTemperatureUnit._TEMPERATURE_LIMITS[self.temp_limit]['min'],
                                     BaseTemperatureUnit._TEMPERATURE_LIMITS[self.temp_limit]['max']))

    @abstractmethod
    def set_and_soak(self, setpoint, soak, temp_error):
        """
        Set the temperature and wait for specified soak time to elapse.

        :param setpoint: degree celsius
        :type setpoint: float
        :param soak: soak time in seconds, usually 600s (10 minutes)
        :type soak: int
        :param temp_error: required accuracy in temperature, usually 2degC
        :type temp_error: float
        """
        raise NotImplementedError
