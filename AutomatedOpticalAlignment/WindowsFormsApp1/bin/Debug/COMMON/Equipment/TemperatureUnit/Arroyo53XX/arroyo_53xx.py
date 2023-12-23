from COMMON.Equipment.TemperatureUnit.base_temperature_forcer import BaseTemperatureForcer
from COMMON.Interfaces.VISA.cli_visa import CLIVISA


class Arroyo53XX(BaseTemperatureForcer):
    """
    Driver for Arroyo 5300 series TEC controller
    """

    CAPABILITY = {}

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
            self._interface.visa_handle.baud_rate = 38400
            self._interface.visa_handle.read_termination = '\n'
        self._interface.write('*CLS')
        self._interface.write('*ESE 1')

    @property
    def identity(self):
        """
        **READONLY**
        Retrieve equipment identity. Also retrieve modules and options properties
        if available

        :value: identity
        :type: dict
        """
        idn_data = self._read("*IDN?", dummy_data='{a},{b},{b},{b}'.format(a=self.name, b='DUMMY_DATA'))
        idn_data = idn_data.split(' ')

        data = {
            'manufacturer': idn_data[0].strip(),
            'model': idn_data[1].strip(),
            'serial': idn_data[2].strip(),
            'firmware': idn_data[3].strip()
        }

        if hasattr(self, 'modules'):
            data['modules'] = self.modules
        if hasattr(self, 'options'):
            data['options'] = self.options

        for key, value in data.items():
            self.logger.debug("{}: {}".format(key.upper(), value))

        return data


    @property
    def thermocouple_temperature(self):
        """
        Returns the temperature from the thermistor
        :return: Temperature in celsius
        :rtype: float
        """
        return float(self._read('TEC:T?', dummy_data=25.0))

    @property
    def setpoint(self):
        """
        Query temperature set point
        :return: TEC set point
        :rtype: float
        """
        return float(self._read('TEC:SET:T?', dummy_data=25.0))

    @setpoint.setter
    def setpoint(self, value):
        """
        Set the temperature set point

        :param value: The temperature to target in C
        :type value: float
        """
        self._check_temperature_limit(value)
        self._write(f'TEC:T {round(value,2)}')

    @property
    def output(self):
        """
        Query the TEC output state

        :return: state of output: ENBALE|DISABLE
        :rtype: str
        """
        output_dict = {0: "DISABLE", 1: "ENABLE"}
        return output_dict[int(self._read('TEC:OUTput?'))]

    @output.setter
    def output(self, value):
        """
        Set the TEC output state

        :param value: ENABLE or DISABLE
        :type value: str
        :return:
        :rtype:
        """
        value = value.upper()
        input_dict = {"DISABLE": 0, "ENABLE": 1}
        self._write(f'TEC:OUTput {input_dict[value]}')

    @property
    def unit_temperature(self):
        pass

    @property
    def pid(self):
        """
        Queries the TEC PID parameters

        :return: PID factors
        :rtype: list of floats, [p, i, d]
        """
        return list(map(float, self._read('TEC:PID?').split(',')))

    @pid.setter
    def pid(self, value):
        """
        Sets the PID parameters

        :param value: [P, I, D], floats 0->10
        :type value: list
        """
        if type(value) not in (list, tuple):
            raise TypeError("expecting a list or tuple of P, I, D value.")
        d = dict(zip(['P', 'I', 'D'], value))
        for k, v in d.items():
            if 0 > v > 10:
                raise ValueError(f"PID terms should be floats between 0 and 10. {k} value was {v}")
        # print(f'TEC:PID {str(value)[1:-1].replace(" ", "")}')
        self._write(f'TEC:PID {str(value)[1:-1].replace(" ", "")}')

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
        if self.output == 'DISABLE':
            self.output = 'ENABLE'
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
