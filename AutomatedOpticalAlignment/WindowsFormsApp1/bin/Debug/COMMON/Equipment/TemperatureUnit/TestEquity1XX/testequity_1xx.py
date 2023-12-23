"""
| $Revision:: 283616                                   $:  Revision of last commit
| $Author:: cerven@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-11-14 17:12:34 +0000 (Wed, 14 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------
"""
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_exceptions import NotSupportedError
from COMMON.Equipment.TemperatureUnit.base_temperature_chamber import BaseTemperatureChamber
from numpy import sign


class TestEquity10X(BaseTemperatureChamber):
    """
    Driver for Test Equity 10X
    """
    
    CAPABILITY = {'temperature': {'min': None, 'max': None}}

    def __init__(self, address, temp_limit='high', f4t=False, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param f4t: option to enable communication to go through the F4T controller
        :type f4t: bool
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, temp_limit=temp_limit, **kwargs)
        self.f4t = f4t

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        if isinstance(self._interface, CLIVISA):
            self._interface.visa_handle.read_termination = '\n'
        self._interface.stb_polling_supported = False
        self._interface.error_check_supported = False

    @property
    def unit_temperature(self):
        """
        Returns the current unit temperature reading from the unit

        :rtype: float
        """
        # TE returns output in hundreds (i.e 23.0C = 230C)
        if self.f4t:
            return float(self._read(":SOURCE:CLOOP1:PVALUE?", dummy_data=25.0))
        else:
            return float(self._read("R? 100,1\r", dummy_data=250.0))/10.0

    @property
    def setpoint(self):
        """
        Returns the temperature setpoint of the unit

        :rtype: float
        """
        if self.f4t:
            return float(self._read(':SOURCE:CLOOP1:SPOINT?', dummy_data=25.0))
        else:
            raise NotSupportedError

    @setpoint.setter
    def setpoint(self, value):
        """
        Sets the unit temperature

        :param value: temperature value to set
        :type value: str or float or int
        """
        # Ensure temperature is within the units capability range and the lockout range
        self._check_temperature_limit(value)
        # Write the temperature to the device
        if self.f4t:
            self._write(':SOURCE:CLOOP1:SPOINT %s' % value)
            self.sleep(1)  # Watlow F4T has issues with reading immediately after writing.
            self._read()  # Watlow temperature unit returns '\n' when written to. This clears it.
        else:
            self._write("D300 \r")
            self._write("W300, %s\r" % (value*10))

    def set_and_soak(self, setpoint, soak=300, temp_error=2.0):
        """
        Set the temperature and wait for specified soak time to elapse.

        :param setpoint: degree celsius
        :type setpoint: float
        :param soak: soak time in seconds
        :type soak: int
        :param temp_error: required accuracy in temperature
        :type temp_error: float
        """
        min_temp = self.CAPABILITY['temperature']['min']
        max_temp = self.CAPABILITY['temperature']['max']

        if self.dummy_mode:
            self.setpoint = setpoint
            self.logger.info('Done soaking.')
            return

        init_temp = self.unit_temperature
        self.setpoint = setpoint

        # The temperature chamber controller sometimes does not close the gap of the last
        # few degrees. By going to the extremes, it is forced to ramp.
        if init_temp < setpoint:
            if (setpoint + 10) < max_temp:
                self.setpoint = setpoint + 10
            else:
                self.setpoint = max_temp
        elif init_temp > setpoint:
            if (setpoint - 10) > min_temp:
                self.setpoint = setpoint - 10
            else:
                self.setpoint = min_temp

        init_error_sign = sign(init_temp - setpoint)

        # Keep tracking the delta to get the temp into the acceptable zone
        delta_temp = self.unit_temperature - setpoint

        while init_error_sign == sign(delta_temp) and abs(delta_temp) > temp_error:
            self.sleep(abs(delta_temp) * 3)
            delta_temp = self.unit_temperature - setpoint
            self.logger.info("Temperature: %4.1f, Delta to setpoint: %4.1f" %
                             (self.unit_temperature, delta_temp))

        self.setpoint = setpoint  # Set the chamber to the actual target

        # check if soaking is needed
        if abs(init_temp - setpoint) > temp_error:
            soak_inc = soak / 10  # calculate a soak increment
            for index in range(int(soak_inc)):
                self.logger.info("Remaining soak time %ds..." % (soak - index * 10))
                self.sleep(10)
            self.logger.info("Done soaking, chamber at %4.1f C" % self.unit_temperature)
        else:  # If we started close to the set_point, then skip the soak time
            self.logger.info("Initial temperature is within acceptable range, skipped soaking")
