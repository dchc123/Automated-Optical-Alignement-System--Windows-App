"""
| $Revision:: 283708                                   $:  Revision of last commit
| $Author:: lagapie@SEMNET.DOM                         $:  Author of last commit
| $Date:: 2018-11-16 18:15:08 +0000 (Fri, 16 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Mainframes.YokogawaAQ221X.yokogawa_aq221x import YokogawaAQ221X
from ..base_optical_attenuator_power_control import BaseOpticalAttenuatorPowerControl
from ..base_optical_attenuator_power_control import BaseOpticalAttenuatorPowerControlChannel
from CLI.Utilities.custom_structures import CustomList


class YokogawaAQ2200_3XX(BaseOpticalAttenuatorPowerControl):
    """
    Yokogawa AQ2200 series optical attenuator with power control common driver
    """

    CAPABILITY = {'channels': None}

    def __init__(self, address, slot_number, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param slot_number: slot number of the module
        :type slot_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """

        if interface is None:
            interface = YokogawaAQ221X()
        self.interface = interface
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._slot_number = slot_number
        self.wl_range = None
        self.channel = CustomList()
        """:type: list of Yokogawa AQ2200_3XX Channel """
        self.channel.append(YokogawaAQ2200_3XXChannel(channel_number=1, slot_number=slot_number, interface=interface,
                                                      dummy_mode=dummy_mode))

    def connect(self):
        super().connect()
        slots = self.interface.slots()
        if self._slot_number > slots:
            self.disconnect()
            raise ValueError("%s is an invalid SLOT number. Choose a slot between 1 and %s. Disconnecting..."
                             % (self._slot_number, slots))
        for channel in self.channel:
            channel._module_options()

    @property
    def identity(self):
        """
        **READONLY**
        Retrieve module identity.

        :value: identity
        :type: dict
        """
        idn_data = self._read(":SLOT{}:IDN?".format(self._slot_number),
                              dummy_data='{a},{b},{b},{b}'.format(a=self.name, b='DUMMY_DATA'))
        idn_data = idn_data.split(',')

        data = {
            'manufacturer': idn_data[0],
            'model': idn_data[1],
            'serial': idn_data[2],
            'firmware': idn_data[3]
        }
        for key, value in data.items():
            self.logger.debug("{}: {}".format(key.upper(), value))
        return data

    def zero_all(self, blocking=True):
        """
        Zeros the electrical offsets of the attenuator’s integrated power meter for all channels

        :param blocking: blocking call
        :type blocking: bool
        """
        if blocking:
            self.logger.info("Zeroing started, wait for completion confirmation.")
            self._write(":OUTPut%s:CORRection:COLLect:ZERO:ALL" % self._slot_number, type_='stb_poll_sync')
            self.logger.warning("Zeroing Completed!")
        else:
            self._write(":OUTPut%s:CORRection:COLLect:ZERO:ALL" % self._slot_number)


class YokogawaAQ2200_3XXChannel(BaseOpticalAttenuatorPowerControlChannel):
    """
    Yokogawa AQ2200-3XX series optical attenuator with power control common channel
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

    def __init__(self, slot_number, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param slot_number: slot number of the module
        :type slot_number: int
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
        self._slot_number = slot_number

    @property
    def attenuation(self):
        """
        :value: attenuation level in dB
        :type: float
        :raise ValueError: Exception if attenuation value is out of range
        """
        return float(self._read(":INPut%s:CHANnel%s:ATTenuation?" % (self._slot_number, self._channel_number)))

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
            self._write(":INPut%s:CHANnel%s:ATTenuation %s" % (self._slot_number, self._channel_number, value))

    @property
    def attenuation_offset(self):
        """
        :value: attenuation offset in dB
        :type: float
        :raise ValueError: Exception if attenuation offset value is out of range
        """
        return float(self._read(":INPut%s:CHANnel%s:OFFSet?" % (self._slot_number, self._channel_number)))

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
            self._write(":INPut%s:CHANnel%s:OFFSet %s" % (self._slot_number, self._channel_number, value),
                        dummy_data=value)

    @property
    def output(self):
        """
        Disable or Enable attenuator output
        Warning: Toggling ON and OFF within 4 seconds might damage the instrument.

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0\r': 'DISABLE', '1\r': 'ENABLE'}
        return output_dict[self._read(":OUTPut%s:CHANnel%s:STATe?" % (self._slot_number, self._channel_number),
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
            self._write(":OUTPut%s:CHANnel%s:STATe %s" % (self._slot_number,
                                                          self._channel_number, input_dict[value]))

    @property
    def opm_avg_time(self):
        """
        :value: optical power meter averaging time (s)
        :type: float
        :raise ValueError: Exception if averaging time value is out of range
        """
        return float(self._read("OUTPut%s:CHANnel%s:ATIMe?" % (self._slot_number, self._channel_number)))

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
            self._write(":OUTPut%s:CHANnel%s:ATIMe %sS" % (self._slot_number, self._channel_number, value))

    @property
    def power_control(self):
        """
        Disable or Enable power control mode

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        power_control = self._read(":OUTPut%s:CHANnel%s:POWer:CONTRol?" % (self._slot_number,
                                   self._channel_number), dummy_data='0').strip("\r")
        return output_dict[power_control]

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
            self._write(":OUTPut%s:CHANnel%s:POWer:CONTRol %s" % (self._slot_number, self._channel_number,
                                                                  input_dict[value]))

    @property
    def power_offset(self):
        """
        :value: power offset in dB
        :type: float
        :raise ValueError: Exception if power offset value is out of range
        """
        return float(self._read(":OUTPut%s:CHANnel%s:POWer:OFFSet?" %(self._slot_number,self._channel_number)))

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
            self._write(":OUTPut%s:CHANnel%s:POWer:OFFSet %sdB" % (self._slot_number, self._channel_number, value),
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
        return float(self._read("OUTPut%s:CHANnel%s:POWer?" % (self._slot_number, self._channel_number)))

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
            self._write(":OUTPut%s:CHANnel%s:POWer %s" % (self._slot_number, self._channel_number, value))

    @property
    def power_unit(self):
        """
        Power unit

        :value: - 'dBm'
                - 'Watt'
        :type: str
        """
        output_dict = {'+0': 'dBm', '+1': 'Watt'}
        power_units = self._read(":OUTPut%s:CHANnel%s:POWer:UNit?" % (self._slot_number, self._channel_number),
                                 dummy_data='+0')
        return output_dict[power_units.strip("\r")]

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
            self._write(":OUTPut%s:CHANnel%s:POWer:UNit %s" % (self._slot_number, self._channel_number, input_dict[value]))

    @property
    def power_value(self):
        """
        READONLY

        Value relies on power units
        :py:class:`.power_unit`

        :value: power meter reading
        :type: float
        """
        return float(self._read(":READ%s:CHANnel%s:POW?" % (self._slot_number, self._channel_number)))

    @property
    def speed(self):
        """
        Attenuation filter speed

        :value: speed  (dB/s)
        :type: float
        :raise ValueError: Exception if speed value is out of range
        """
        return float(self._read(":INPut%s:CHANnel%s:ATTenuation:SPEed?" % (self._slot_number, self._channel_number)))

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
            self._write(":INPut%s:CHANnel%s:ATTenuation:SPEed %s" % (self._slot_number, self._channel_number, value))

    @property
    def wavelength(self):
        """
        Wavelength of signal

        :value: wavelength (nm)
        :type: float
        :raise ValueError: Exception if wavelength value is out of range
        """
        return float(self._read(":INPut%s:CHANnel%s:WAVelength?"
                                % (self._slot_number, self._channel_number), dummy_data=1310/1e9))*1e9  # m to nm

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
            self._write(":INPut%s:CHANnel%s:WAVelength %sNM" % (self._slot_number, self._channel_number, value))

    def zero_offset(self, blocking=True):
        """
        Zeros the electrical offsets of the attenuator’s integrated power meter
        """
        if blocking:
            self.logger.info("Zeroing started, wait for completion confirmation.")
            self._write(":OUTPut%s:CHANnel%s:CORRection:COLLect:ZERO" % (self._slot_number, self._channel_number),
                        type_='stb_poll_sync')
            self.logger.info("Zeroing Completed!")
        else:
            self._write(":OUTPut%s:CHANnel%s:CORRection:COLLect:ZERO" % (self._slot_number, self._channel_number),
                        type_='basic')

    def _module_options(self):
        """
        Retrieve the module options and populate some of the capability fields.
        """
        module_opt = str(self._read(":SLOT%s:OPT?" % self._slot_number, dummy_data="800NM-1370NM")).split(",")
        wl_range = module_opt[6].split("-")

        self.CAPABILITY['wavelength_range']['min'] = float(wl_range[0].rstrip("NM"))
        self.CAPABILITY['wavelength_range']['max'] = float(wl_range[1].rstrip("NM"))

