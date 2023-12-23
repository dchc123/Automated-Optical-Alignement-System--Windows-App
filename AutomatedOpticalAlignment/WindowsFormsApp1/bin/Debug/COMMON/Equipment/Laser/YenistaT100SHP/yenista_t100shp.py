"""
| $Revision:: 280392                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-31 01:14:44 +0100 (Tue, 31 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.YenistaT100SHP`
::

    >>> from CLI.Equipment.Laser.YenistaT100SHP.yenista_t100shp import YenistaT100SHP
    >>> tls = YenistaT100SHP('GPIB1::23::INSTR')
    >>> tls.connect()
    >>> tls.wavelength = 1305.11
    >>> tls.wavelength
    1305.11
    >>> tls.speed
    10
    >>> tls.control_mode('CP')

"""
from ....Interfaces.VISA.cli_visa import CLIVISA
from ..base_tunable_laser import BaseTunableLaser


class YenistaT100SHP(BaseTunableLaser):
    """
    Yenista T100SHP Tunable Laser driver
    """
    CAPABILITY = {'wavelength': {'min': 1260.0, 'max': 1360.0},
                  'current_level': {'min': 0, 'max': 400},
                  'power_level_dBm': {'min': -6.99, 'max': 14},
                  'power_level_mWatt': {'min': 0, 'max': 50},
                  'speed': {'min': 1, 'max': 100},
                  }

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address of the tunable laser
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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._control_mode = None
        self._coherence_control = None
        self._power_unit = None

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        super()._configure_interface()
        self._interface.error_check_supported = False
        self._interface.stb_event_mask = 0x01

    @property
    def control_mode(self):
        """
        Toggles between constant power and constant current modes.

        :value:     - 'CP' (Constant Power, Automatic power control)
                    - 'CC' (Constant Current)
        :type: str
        :raise ValueError: exception if input is not CP/CC
        """

        if self._control_mode:
            return self._control_mode
        else:
            self.logger.warning('Control mode has not yet been set and is in unknown state.')

    @control_mode.setter
    def control_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not CP/CC
        """

        value = value.upper()
        input_dict = {'CP': 'APCON', 'CC': 'APCOFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "CP" for constant power or "CC" for constant current')
        else:
            self._write("{}".format(input_dict[value]))
            self._control_mode = value

    @property
    def coherence_control(self):
        """
        Linewidth coherence control

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        if self._coherence_control:
            return self._coherence_control
        else:
            self.logger.warning('Coherence control has not yet been set and is in unknown state.')

    @coherence_control.setter
    def coherence_control(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """

        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("CTRL{}".format(input_dict[value]))
            self._coherence_control = value

    @property
    def current_level(self):
        """
        Current level to be used when in constant current mode

        :value: current level
        :type: float
        """
        temp = self._read("I?")
        if temp == 'DISABLED':
            self.logger.warning('Current level cannot be read when output is disabled')
        else:
            return float(temp.split('I=')[1])

    @current_level.setter
    def current_level(self, value):
        """
        :type value: float
        :raise ValueError: Exception if current level value is out of range
        """

        range_min = self.CAPABILITY['current_level']['min']
        range_max = self.CAPABILITY['current_level']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid current level. See supported range.(min:%s|max:%s)"
                             % (value, range_min, range_max))
        else:
            if self._control_mode is None or self._control_mode == 'CP':
                self.logger.warning('Setting current level changed the control mode to constant current!')
                self._control_mode = 'CC'
            self._write("I={}".format(value), dummy_data=value)

    @property
    def output(self):
        """
        Enable state of the output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """

        if self._read("P?") == 'DISABLED':
            return 'DISABLE'
        else:
            return 'ENABLE'

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_list = ['DISABLE', 'ENABLE']
        if value not in input_list:
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("{}".format(value), dummy_data=value, type_='stb_poll')

    @property
    def power_level(self):
        """
        Value depends on current power units. Currently no query commands are available for power units.
        :py:class:`.power_unit`

        :value: power level
        :type: float
        """
        temp = self._read("P?")
        if temp == 'DISABLED':
            self.logger.warning('Power level cannot be read when output is disabled')
        else:
            return float(temp.split('P=')[1])

    @power_level.setter
    def power_level(self, value):
        """
        :type value: float
        :raise ValueError: Exception if power level value is out of range
        """

        if not self._power_unit:  # Doing this since power units are monitored through code and not confirmed by command
            self.logger.warning('Power units have not yet been set and are in unknown state.'
                                'Please send power_unit command before setting power level.')
        else:
            if self._power_unit == "MW":
                range_min = self.CAPABILITY['power_level_mWatt']['min']
                range_max = self.CAPABILITY['power_level_mWatt']['max']
            else:
                range_min = self.CAPABILITY['power_level_dBm']['min']
                range_max = self.CAPABILITY['power_level_dBm']['max']

            if not (range_min <= value <= range_max):
                raise ValueError("%s is an invalid power level. See supported range.(min:%s|max:%s)"
                                 % (value, range_min, range_max))
            else:
                if self._control_mode is None or self._control_mode == 'CC':
                    self.logger.warning('Setting power level changed the control mode to constant power!')
                    self._control_mode = 'CP'
                self._write("P={}".format(value), dummy_data=value)

    @property
    def power_unit(self):
        """
        Power unit

        :value: - 'dBm'
                - 'mW'
        :type: str
        :raise ValueError: exception if input is not dBm/Watt
        """
        if not self._power_unit:
            self.logger.warning('Power units have not yet been set and is in unknown state.')
        return self._power_unit

    @power_unit.setter
    def power_unit(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not dBm/mW
        """
        value = value.upper()
        input_list = ['DBM', 'MW']
        if value not in input_list:
            raise ValueError('Please specify either "dBm" or "mW"')
        else:
            self._write("{}".format(value))
            self._power_unit = value

    @property
    def speed(self):
        """
        Motors speed. Automatically rounded to nearest operational sweep speed.

        :value: speed (nm/s)
        :type: int
        :raise ValueError: exception if input speed is out of range
        """

        return int(self._read("MOTOR_SPEED?", dummy_data=1))

    @speed.setter
    def speed(self, value):
        """
        :type value: int
        :raise ValueError: exception if input wavelength is out of range
        """
        min_speed = self.CAPABILITY['speed']['min']
        max_speed = self.CAPABILITY['speed']['max']

        if min_speed <= value <= max_speed:
            self._write("MOTOR_SPEED={}".format(value), dummy_data=value)
        else:
            raise ValueError("%s is an invalid speed entry. See valid range. (min:%s|max:%s)"
                             % (value, min_speed, max_speed))

    @property
    def wavelength(self):
        """
        Wavelength of output signal

        :value: wavelength (nm)
        :type: float
        :raise ValueError: exception if input wavelength is out of range
        """

        return float(self._read("L?", dummy_data='L=1310.001').split('L=')[1])

    @wavelength.setter
    def wavelength(self, value):
        """
        :type value: float
        :raise ValueError: exception if input wavelength is out of range
        """
        min_wl = self.CAPABILITY['wavelength']['min']
        max_wl = self.CAPABILITY['wavelength']['max']

        if min_wl <= value <= max_wl:
            self._write("L={}".format(value), dummy_data=value, timeout=120, type_='stb_poll')
        else:
            raise ValueError("%s is an invalid wavelength entry. See valid range."
                             "(min:%s|max:%s)" % (value, min_wl, max_wl))

    def auto_cal(self, blocking=True):
        """
        Performs auto calibration
        """

        self._write("AUTO_CAL")
        if not self.dummy_mode:
            if blocking:
                self.logger.info("Auto calibration started, wait for completion confirmation.")
                # Delay combined with *OPC? with polling is to bypass a bug that the unit
                # does not reply between the 5th and 10th second after AUTO_CAL is sent.
                self.sleep(12)
                self._read("*OPC?", type_='stb_poll')
                self.logger.info("Auto calibration completed!")

    def reset(self):
        """
        Perform equipment reset, to put device in known preset state
        Reset sequence as follows :
        output:             'DISABLE'
        speed:              100
        wavelength:         '1310.0'
        power_unit:         'dBm'
        power_level:        0
        control_mode:       'CP'
        coherence_control:  'DISABLE'
        """
        self.output = 'DISABLE'
        self.speed = 100
        self.wavelength = 1310
        self.power_unit = 'DBM'
        self.power_level = 0
        self.control_mode = 'CP'
        self.coherence_control = 'DISABLE'
