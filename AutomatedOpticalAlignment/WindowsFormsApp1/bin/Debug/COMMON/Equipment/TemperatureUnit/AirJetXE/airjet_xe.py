"""
| $Revision:: 283251                                   $:  Revision of last commit
| $Author:: tobias_l@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-10-27 15:11:04 +0100 (Sat, 27 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.AirJetXE`
::

    >>> from COMMON.Equipment.TemperatureUnit.AirJetXE.airjet_xe import AirJetXE
    >>> ts = AirJetXE('GPIB1::23::INSTR')
    >>> ts.connect()
    >>> ts.unit_temperature
    25.0
    >>> ts.set_and_soak(100)
"""
from time import sleep
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Equipment.TemperatureUnit.base_temperature_forcer import BaseTemperatureForcer


class AirJetXE(BaseTemperatureForcer):
    """
    Driver for the AirJet XE
    """
    CAPABILITY = {'temperature': {'min': -75, 'max': 225}}

    def __init__(self, address, temp_limit='high', interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param temp_limit: the type of victim
        :type temp_limit: str
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

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        if isinstance(self._interface, CLIVISA):
            # AirJet does not use a read termination character
            self._interface.visa_handle.read_termination = ''
        self._interface.stb_polling_supported = False
        self._interface.error_check_supported = False

    @property
    def setpoint(self):
        """
        Returns the temperature setpoint of the unit

        :rtype: float
        """
        return float(self._read('?SP', dummy_data=25.0))

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
        self._write('SP %.1f' % value)

    @property
    def unit_temperature(self):
        """
        Returns the current unit temperature reading from the unit

        :rtype: float
        """
        for i in range(5):
            try:
                read_value = float(self._read('?TA', dummy_data=25.0))
                break
            except ValueError:  # sometimes returns 'Err 1\r'
                i += 1
                sleep(0.5)

        return read_value

    @property
    def thermocouple_temperature(self):
        """
        Returns the current thermocouple temperature reading from the unit

        :rtype: float
        """
        for i in range(5):
            try:
                read_value = float(self._read('?TD', dummy_data=25.0))
                i = 5
                break
            except ValueError:  # sometimes returns 'Err 1\r'
                self.logger.debug("ValueError GETING TC TEMPERATURE")
                i += 1
                sleep(0.5)

        return read_value

    def set_and_soak(self, setpoint, soak=150, temp_error=5):
        """
        Set the temperature and wait for specified soak time to elapse.

        :param setpoint: degree celsius
        :type setpoint: float
        :param soak: soak time in seconds
        :type soak: int
        :param temp_error: required accuracy in temperature
        :type temp_error: float
        """
        self.setpoint = setpoint

        if self.dummy_mode:
            self.logger.info('Done soaking.')
            return
        else:
            self.logger.info('Starting temperature ramp. Target range: {0} -> {1}'.format((setpoint - temp_error),
                                                                                          setpoint + temp_error))
            for ramp_time in range(1, 300, 5):
                if (setpoint - temp_error) <= self.thermocouple_temperature <= (setpoint + temp_error):
                    break
                else:
                    self.sleep(5)
            self.logger.info('Temperature within range. Starting soak.')
            soak_time = 0
            while soak_time < soak:
                if (setpoint - temp_error) <= self.thermocouple_temperature <= (setpoint + temp_error):
                    soak_time += 1  # while in range, count up to soak time
                else:
                    self.logger.info(f'Temperature {self.thermocouple_temperature}C is out of range {(setpoint - temp_error)} '
                                     f'to {(setpoint + temp_error)}. Re-starting soak.')
                    soak_time = 0
                self.sleep(1)
