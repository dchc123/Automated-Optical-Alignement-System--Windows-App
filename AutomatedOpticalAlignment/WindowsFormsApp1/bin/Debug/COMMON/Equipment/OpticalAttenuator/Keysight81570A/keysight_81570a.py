"""
| $Revision:: 283346                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-02 15:12:45 +0000 (Fri, 02 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keysight81570A`
::

    >>> from CLI.Equipment.OpticalAttenuator.Keysight81570A.keysight_81570a import Keysight81570A
    >>> Att = Keysight81570A('GPIB1::23::INSTR')
    >>> Att.connect()

For channel level API:
:py:class:`.Keysight81570AChannel`
::

    >>> Att.channel[1].attenuation = 10
    >>> Att.channel[1].attenuation
    10.0
"""
from CLI.Mainframes.Keysight816XX.keysight_8163x import Keysight8163X
from ..base_optical_attenuator import BaseOpticalAttenuatorChannel
from ..base_optical_attenuator import BaseOpticalAttenuator
from CLI.Utilities.custom_structures import CustomList


class Keysight81570A(BaseOpticalAttenuator):
    """
    Keysight 81570A optical attenuator driver
    """

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
        """:type: list of Keysight81570AChannel"""
        self.channel.append(Keysight81570AChannel(slot_number=slot_number, interface=interface, dummy_mode=dummy_mode))
        self._slot_number = slot_number


class Keysight81570AChannel(BaseOpticalAttenuatorChannel):
    """
    Keysight 81570A optical attenuator channel
    """

    # attenuation_offset_range has not been confirmed
    CAPABILITY = {'attenuation_range': {'min': 0, 'max': 60},
                  'attenuation_offset_range': {'min': -200, 'max': 200},
                  'speed_range': {'min': 0.1, 'max': 12},
                  'wavelength_range': {'min': 1200, 'max': 1700},
                  }

    def __init__(self, slot_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

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
        self._slot_number = slot_number

    @property
    def attenuation(self):
        """
        :value: attenuation level in dB
        :type: float
        :raise ValueError: Exception if attenuation value is out of range
        """
        return float(self._read("INPut%s:ATTenuation?" % self._slot_number))

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

        self._write("INPut%s:ATTenuation %s" % (self._slot_number, value))

    @property
    def attenuation_offset(self):
        """
        :value: attenuation offset in dB
        :type: float
        :raise ValueError: Exception if attenuation offset value is out of range
        """
        return float(self._read("INPut%s:OFFSet?" % self._slot_number))

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
            self._write("INPut%s:OFFSet %sdB" % (self._slot_number, value),
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
        return output_dict[self._read("OUTPut%s:STATe?" % self._slot_number,
                                      dummy_data='0')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'DISABLE': '0',  'ENABLE': '1'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("OUTPut%s:STATe %s" % (self._slot_number, input_dict[value]))

    @property
    def speed(self):
        """
        Attenuation filter speed

        :value: speed  (dB/s)
        :type: float
        :raise ValueError: Exception if speed value is out of range
        """
        return float(self._read("INPut%s:ATTenuation:SPEed?" % self._slot_number))

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
            self._write("INPut%s:ATTenuation:SPEed %s" % (self._slot_number, value))

    @property
    def wavelength(self):
        """
        Wavelength of signal

        :value: wavelength (nm)
        :type: float
        :raise ValueError: Exception if wavelength value is out of range
        """
        return float(self._read("INPut%s:WAVelength?"
                                % self._slot_number, dummy_data=1310/1e9)) * 1e9  # nm to m

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
            self._write("INPut%s:WAVelength %s" % (self._slot_number, value))

