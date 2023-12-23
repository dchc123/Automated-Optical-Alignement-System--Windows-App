"""
| $Revision:: 283346                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-02 15:12:45 +0000 (Fri, 02 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from ..base_optical_attenuator_power_control import BaseOpticalAttenuatorPowerControl
from ..base_optical_attenuator_power_control import BaseOpticalAttenuatorPowerControlChannel


class KeysightN776XX(BaseOpticalAttenuatorPowerControl):
    """
    Keysight N776XX series optical attenuator with power control common driver
    """

    CAPABILITY = {'channels': None}

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)

    def zero_all(self, blocking=True):
        """
        Zeros the electrical offsets of the attenuator’s integrated power meter for all channels

        :param blocking: blocking call
        :type blocking: bool
        """
        if blocking:
            self.logger.info("Zeroing started, wait for completion confirmation.")
            self._write("OUTPut:CORRection:COLLect:ZERO:ALL", type_='stb_poll_sync')
            self.logger.warning("Zeroing Completed!")
        else:
            self._write("OUTPut:CORRection:COLLect:ZERO:ALL")


class KeysightN776XXChannel(BaseOpticalAttenuatorPowerControlChannel):
    """
    Keysight N776XX series optical attenuator with power control common channel
    """

    CAPABILITY = {'attenuation_range': {'min': None, 'max': None},
                  'attenuation_offset_range': {'min': None, 'max': None},
                  'opm_avg_time': {'min': None, 'max': None},
                  'power_level_dBm_range': {'min': None, 'max': None},
                  'power_level_offset_range': {'min': None, 'max': None},
                  'power_level_watt_range': {'min': None, 'max': None},
                  'speed_range': {'min': None, 'max': None},
                  'wavelength_range': {'min': None, 'max': None},
                  }

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the attenuator
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number

    @property
    def attenuation(self):
        """
        :value: attenuation level in dB
        :type: float
        :raise ValueError: Exception if attenuation value is out of range
        """
        return float(self._read("INPut%s:ATTenuation?" % self._channel_number))

    @attenuation.setter
    def attenuation(self, value):
        """
        :type value: float
        :raise ValueError: Exception if attenuation value is out of range
        """

        range_min = self.CAPABILITY['attenuation_range']['min']
        range_max = self.CAPABILITY['attenuation_range']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid attenuation setpoint. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("INPut%s:ATTenuation %s" % (self._channel_number, value))

    @property
    def attenuation_offset(self):
        """
        :value: attenuation offset in dB
        :type: float
        :raise ValueError: Exception if attenuation offset value is out of range
        """
        return float(self._read("INPut%s:OFFSet?" % self._channel_number))

    @attenuation_offset.setter
    def attenuation_offset(self, value):
        """
        :type value: float
        :raise ValueError: Exception if attenuation offset value is out of range
        """

        range_min = self.CAPABILITY['attenuation_offset_range']['min']
        range_max = self.CAPABILITY['attenuation_offset_range']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid attenuation offset. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("INPut%s:OFFSet %sdB" % (self._channel_number, value),
                        dummy_data=value)

    @property
    def output(self):
        """
        Disable or Enable attenuator output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read("OUTPut%s:STATe?" % self._channel_number,
                                      dummy_data='0')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        input_dict = {'DISABLE': '0',  'ENABLE': '1'}
        value = value.upper()
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("OUTPut%s:STATe %s" % (self._channel_number, input_dict[value]))

    @property
    def opm_avg_time(self):
        """
        :value: optical power meter averaging time (s)
        :type: float
        :raise ValueError: Exception if averaging time value is out of range
        """
        return float(self._read("OUTPut%s:ATIMe?" % self._channel_number))

    @opm_avg_time.setter
    def opm_avg_time(self, value):
        """
        :type value: float
        :raise ValueError: Exception if averaging time value is out of range
        """

        range_min = self.CAPABILITY['opm_avg_time']['min']
        range_max = self.CAPABILITY['opm_avg_time']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid averaging time. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("OUTPut%s:ATIMe %s" % (self._channel_number, value))

    @property
    def power_control(self):
        """
        Disable or Enable power control mode

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read("OUTPut%s:POWer:CONTRol?" % self._channel_number,
                                      dummy_data='0')]

    @power_control.setter
    def power_control(self, value):
        """
        :type value: str
        """
        input_dict = {'DISABLE': '0',  'ENABLE': '1'}
        value=value.upper()
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("OUTPut%s:POWer:CONTRol %s" % (self._channel_number, input_dict[value]))

    @property
    def power_offset(self):
        """
        :value: power offset in dB
        :type: float
        :raise ValueError: Exception if power offset value is out of range
        """
        return float(self._read("OUTPut%s:POWer:OFFSet?" % self._channel_number))

    @power_offset.setter
    def power_offset(self, value):
        """
        :type value: float
        :raise ValueError: Exception if power offset value is out of range
        """

        range_min = self.CAPABILITY['power_level_offset_range']['min']
        range_max = self.CAPABILITY['power_level_offset_range']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid power offset. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("OUTPut%s:POWer:OFFSet %sdB" % (self._channel_number, value),
                        dummy_data=value)

    @property
    def power_setpoint(self):
        """
        Value relies on power units
        :py:class:`.power_unit`

        :value: power level
        :type: float
        :raise ValueError: Exception if power level value is out of range
        """
        return float(self._read("OUTPut%s:POWer?" % self._channel_number))

    @power_setpoint.setter
    def power_setpoint(self, value):
        """
        :type value: float
        :raise ValueError: Exception if power level value is out of range
        """

        if self.power_unit == "Watt":
            range_min = self.CAPABILITY['power_level_watt_range']['min']
            range_max = self.CAPABILITY['power_level_watt_range']['max']
        else:
            range_min = self.CAPABILITY['power_level_dBm_range']['min']
            range_max = self.CAPABILITY['power_level_dBm_range']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid power level. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("OUTPut%s:POWer %s" % (self._channel_number, value))

    @property
    def power_unit(self):
        """
        Power unit

        :value: - 'dBm'
                - 'Watt'
        :type: str
        """
        output_dict = {'+0': 'dBm', '+1': 'Watt'}
        return output_dict[self._read("OUTPut%s:POWer:UNit?" % self._channel_number, dummy_data='+0')]

    @power_unit.setter
    def power_unit(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not dBm/Watt
        """
        value = value.upper()
        input_dict = {'DBM': '+0', 'WATT': '+1'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "dBm" or "Watt"')
        else:
            self._write("OUTPut%s:POWer:UNit %s" % (self._channel_number, input_dict[value]))

    @property
    def power_value(self):
        """
        READONLY

        Value relies on power units
        :py:class:`.power_unit`

        :value: power meter reading
        :type: float
        """

        return float(self._read("READ%s:POW?" % self._channel_number))

    @property
    def speed(self):
        """
        Attenuation filter speed

        :value: speed  (dB/s)
        :type: float
        :raise ValueError: Exception if speed value is out of range
        """
        return float(self._read("INPut%s:ATTenuation:SPEed?" % self._channel_number))

    @speed.setter
    def speed(self, value):
        """
        :type value: float
        :raise ValueError: Exception if speed value is out of range
        """

        range_min = self.CAPABILITY['speed_range']['min']
        range_max = self.CAPABILITY['speed_range']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid speed setpoint. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("INPut%s:ATTenuation:SPEed %s" % (self._channel_number, value))

    @property
    def wavelength(self):
        """
        Wavelength of signal

        :value: wavelength (nm)
        :type: float
        :raise ValueError: Exception if wavelength value is out of range
        """
        return float(self._read("INPut%s:WAVelength?"
                                % self._channel_number, dummy_data=1310/1e9))*1e9  # nm to m

    @wavelength.setter
    def wavelength(self, value):
        """
        :type value: float
        :raise ValueError: Exception if wavelength value is out of range
        """

        range_min = self.CAPABILITY['wavelength_range']['min']
        range_max = self.CAPABILITY['wavelength_range']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid wavelength setpoint. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            value /= 1e9    # To convert nm to meters
            self._write("INPut%s:WAVelength %s" % (self._channel_number, value))

    def zero_offset(self, blocking=True):
        """
        Zeros the electrical offsets of the attenuator’s integrated power meter
        """
        if blocking:
            self.logger.info("Zeroing started, wait for completion confirmation.")
            self._write("OUTPut%s:CORRection:COLLect:ZERO" % self._channel_number,
                        type_='stb_poll_sync')
            self.logger.info("Zeroing Completed!")
        else:
            self._write("OUTPut%s:CORRection:COLLect:ZERO" % self._channel_number)
