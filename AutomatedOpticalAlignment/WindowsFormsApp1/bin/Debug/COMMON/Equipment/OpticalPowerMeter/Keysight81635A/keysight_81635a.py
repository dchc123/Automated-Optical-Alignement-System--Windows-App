"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keysight81635A`
::

    >>> from CLI.Equipment.OpticalPowerMeter.Keysight81635A.keysight_81635a import Keysight81635A
    >>> OPM = Keysight81635A('GPIB1::23::INSTR')
    >>> OPM.connect()

For channel level API:
:py:class:`.Keysight81635AChannel`
::

    >>> OPM.channel[1].power_units = "dBm"
    >>> OPM.channel[1].value
    -4.44

"""
from CLI.Utilities.custom_structures import CustomList
from CLI.Mainframes.Keysight816XX.keysight_8163x import Keysight8163X
from ..base_optical_power_meter import BaseOpticalPowerMeter
from ..base_optical_power_meter import BaseOpticalPowerMeterChannel


class Keysight81635A(BaseOpticalPowerMeter):
    """
    Keysight 81635A optical power meter driver
    """

    CAPABILITY = {'channels': 2}

    def __init__(self, address, slot_number, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address of the mainframe controlling this module
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
            interface = Keysight8163X()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of Keysight81635AChannel"""
        self._slot_number = slot_number
        self.channel.append(Keysight81635AChannel(channel_number=1, slot_number=slot_number,
                                                  interface=interface, dummy_mode=dummy_mode))
        self.channel.append(Keysight81635AChannel(channel_number=2, slot_number=slot_number,
                                                  interface=interface, dummy_mode=dummy_mode))

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
        data = {
            'manufacturer': idn_data[0],
            'model': idn_data[1],
            'serial': idn_data[2],
            'firmware': idn_data[3]
        }

        for key, value in data.items():
            self.logger.debug("{}: {}".format(key.upper(), value))

        return data


class Keysight81635AChannel(BaseOpticalPowerMeterChannel):
    """
    Keysight 81635A optical power meter channel
    """

    CAPABILITY = {'avg_time': {'min': 0.0001, 'max': 1},
                  'power_range': {'min': -80, 'max': 10},
                  'wavelength_range': {'min': 800, 'max': 1650},
                  }

    def __init__(self, channel_number, slot_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the attenuator
        :type channel_number: int
        :param slot_number: slot number of the module
        :type slot_number: int
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
    def avg_time(self):
        """
        :value: optical power meter averaging time (s)
        :type: float
        :raise ValueError: Exception if averaging time value is out of range
        """
        return float(self._read("SENSe%s:CHANnel%s:POWer:ATIMe?"
                                % (self._slot_number, self._channel_number)))

    @avg_time.setter
    def avg_time(self, value):
        """
        :type value:  float
        :raise ValueError: Exception if averaging time value is out of range
        """

        range_min = self.CAPABILITY['avg_time']['min']
        range_max = self.CAPABILITY['avg_time']['max']

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid averaging time. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("SENSe%s:CHANnel%s:POWer:ATIMe %s"
                        % (self._slot_number, self._channel_number, value))

    @property
    def value(self):
        """
        READONLY

        Value relies on power units
        :py:class:`.power_unit`

        :value: power level
        :type: float
        """
        if not self.dummy_mode:
            self._write("INITiate%s:CHANnel%s:IMMediate"
                        % (self._slot_number, self._channel_number))
        else:
            return float(self._read("FETCh%s:CHANnel%s:POW?"
                                    % (self._slot_number, self._channel_number)))

    @property
    def power_unit(self):
        """
        Power unit

        :value: - 'dBm'
                - 'Watt'
        :type: str
        :raise ValueError: exception if input is not dBm/Watt
        """
        output_dict = {'+0': 'dBm', '+1': 'Watt'}
        return output_dict[self._read("OUTPut%s:CHANnel%s:POWer:UNit?" %
                                      (self._slot_number, self._channel_number), dummy_data='+0')]

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
            self._write("OUTPut%s:CHANnel%s:POWer:UNit %s"
                        % (self._slot_number, self._channel_number, input_dict[value]))

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

