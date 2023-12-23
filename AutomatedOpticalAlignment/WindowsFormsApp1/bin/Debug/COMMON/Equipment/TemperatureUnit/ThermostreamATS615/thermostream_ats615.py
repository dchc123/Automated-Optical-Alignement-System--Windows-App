"""
| $Revision:: 282825                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-10-12 21:24:43 +0100 (Fri, 12 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.ThermoStreamATS615`
::

    >>> from COMMON.Equipment.TemperatureUnit.ThermostreamATS615.thermostream_ats615 import ThermoStreamATS615
    >>> ts = ThermoStreamATS615('GPIB1::23::INSTR')
    >>> ts.connect()
    >>> ts.unit_temperature
    25.0
    >>> ts.set_and_soak(100)
"""
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Equipment.TemperatureUnit.base_temperature_forcer import BaseTemperatureForcer


class ThermoStreamATS615(BaseTemperatureForcer):
    """
    Driver for Temptronic Thermostream
    """
    _COLD_THRESH = 20
    _HOT_THRESH = 30
    CAPABILITY = {'temperature': {'min': -45, 'max': 225}}

    def __init__(self, address, temp_limit='high', interface=None, dummy_mode=False, **kwargs):
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
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, temp_limit=temp_limit, **kwargs)

    @property
    def unit_temperature(self):
        """
        Returns the current unit temperature reading from the unit

        :rtype: float
        """
        return float(self._read('TEMP?', dummy_data=25.0))

    @property
    def thermocouple_temperature(self):
        """
        Returns the current thermocouple temperature reading from the unit

        :rtype: float
        """
        raise NotImplementedError

    @property
    def setpoint(self):
        """
        Temperature setting of the stream

        :value: temperature in degree celsius
        :type: float
        """
        return float(self._read('SETP?', dummy_data=25.0))

    @setpoint.setter
    def setpoint(self, value):
        """
        Sets the unit temperature

        :param value: temperature value to set
        :type value: str or float or int
        """
        # Ensure temperature is within the units capability range and the lockout range
        self._check_temperature_limit(value)
        # Ensure the compressor is On
        if self._compressor == 'OFF':
            self._compressor = 'ON'
        # Write the temperature to the device
        if float(value) < ThermoStreamATS615._COLD_THRESH:
            self._temp_point = 'COLD'
        elif float(value) > ThermoStreamATS615._HOT_THRESH:
            self._temp_point = 'HOT'
        else:
            self._temp_point = 'AMBIENT'

        self._write('SETP %s' % value)

    @property
    def _compressor(self):
        """
        State of the compressor

        :value: - 'ON'
                - 'OFF'
        :type: str
        :raise ValueError: exception if input is not ON/OFF
        """
        output_dict = {'0': 'OFF', '1': 'ON', 'DUMMY_DATA': 'OFF'}

        return output_dict[self._read('COOL?').strip()]

    @_compressor.setter
    def _compressor(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ON/OFF
        """
        input_dict = {'OFF': 0, 'ON': 1}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ON' or 'OFF'")
        else:
            self._write('COOL %s' % input_dict[value])

    @property
    def _temp_point(self):
        """
        Configure temperature point to either HOT, AMBIENT or COLD

        :value: - 'AMBIENT'
                - 'COLD'
                - 'HOT'
        :type: str
        :raise ValueError: exception if input is not 'AMBIENT', 'COLD' or 'HOT'
        """
        output_dict = {'0': 'HOT', '1': 'AMBIENT', '2': 'COLD', 'DUMMY_DATA': 'HOT'}

        return output_dict[self._read('SETN?').strip()]

    @_temp_point.setter
    def _temp_point(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not 'AMBIENT', 'COLD' or 'HOT'
        """
        input_dict = {'HOT': 0, 'AMBIENT': 1, 'COLD': 2}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'AMBIENT', 'COLD' or 'HOT'")
        else:
            self._write('SETN %s' % input_dict[value.upper()])

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
            self.logger.info('Done soaking')
            return
        else:
            self.sleep(soak)

        # This recursion is different from the TE chamber recursion. This repeat was mainly
        # added due to the instrument not responding to SCPI commands some times. In some cases,
        # setting the point would not work. Therefore, this is mainly to resend the command if the
        # first command was not properly executed.
        if abs(setpoint - self.unit_temperature) > temp_error:
            self.set_and_soak(setpoint)
