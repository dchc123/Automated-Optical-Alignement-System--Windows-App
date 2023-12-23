"""
| $Revision:: 280577                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-08-01 14:23:40 +0100 (Wed, 01 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from ..base_optical_transmitter import BaseOpticalTransmitter
from CLI.Mainframes.Keysight816XX.keysight_8163x import Keysight8163X


class Keysight8149XX(BaseOpticalTransmitter):
    """
    Keysight 8149XX Transmitter driver
    """

    CAPABILITY = {'attenuation': {'min': None, 'max': None},
                  'source': [None],
                  'operating_point': {'min': None, 'max': None}
                  }

    def __init__(self, address, slot_number, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address of the mainframe controlling this module
        :type address: int or str
        :param slot_number: slot number of the module
        :type slot_number: int
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = Keysight8163X()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._slot_number = slot_number
        self._channel_number = 1

    @property
    def _current_laser(self):
        """
        ***READONLY***

        :value: index of current laser source
        :type: int
        """
        return self.CAPABILITY['source'].index(self.source)

    @property
    def attenuation(self):
        """
        :value: attenuation level in dB
        :type: float
        :raise ValueError: Exception if attenuation value is out of range
        """
        laser_index = self._current_laser
        return float(self._read("SOURce%s:CHANnel%s:POWer:ATTenuation%s?" %
                                (self._slot_number, self._channel_number, laser_index+1)))

    @attenuation.setter
    def attenuation(self, value):
        """
        :type value: float
        :raise ValueError: Exception if attenuation value is out of range
        """

        range_min = self.CAPABILITY['attenuation']['min']
        range_max = self.CAPABILITY['attenuation']['max']

        laser_index = self._current_laser

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid attenuation setpoint. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("SOURce%s:CHANnel%s:POWer:ATTenuation%s %s" %
                        (self._slot_number, self._channel_number, laser_index+1, value))

    @property
    def operating_point(self):
        """
        :value: operating point of the laser diode
        :type: float
        :raise ValueError: Exception if attenuation value is out of range
        """
        laser_index = self._current_laser
        return float(self._read("SOURce%s:CHANnel%s:TRANsmitter:OPOint%s?" %
                                (self._slot_number, self._channel_number, laser_index+1)))

    @operating_point.setter
    def operating_point(self, value):
        """
        :type value: float
        :raise ValueError: Exception if attenuation value is out of range
        """

        range_min = self.CAPABILITY['operating_point']['min']
        range_max = self.CAPABILITY['operating_point']['max']

        laser_index = self._current_laser

        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid attenuation setpoint. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write("SOURce%s:CHANnel%s:TRANsmitter:OPOint%s %s" %
                        (self._slot_number, self._channel_number, laser_index+1, value))

    @property
    def output(self):
        """
        Enable state of the output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """

        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read("SOURce%s:CHANnel%s:POWer:STATe?"
                                      % (self._slot_number, self._channel_number),
                                      dummy_data='0').strip()]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'DISABLE': '0',  'ENABLE': '1'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("SOURce%s:CHANnel%s:POWer:STATe %s"
                        % (self._slot_number, self._channel_number, input_dict[value]))

    @property
    def source(self):
        """
        Laser source of the transmitter

        :value: wavelength (nm)
        :type: float
        :raise ValueError: exception if input is not '1310' or '1550'
        """
        low = self.CAPABILITY['source'][0]
        upp = self.CAPABILITY['source'][1]
        output_dict = {'LOW': low, 'UPP': upp}
        return output_dict[self._read("SOURce%s:CHANnel%s:POWer:WAVelength?"
                                      % (self._slot_number, self._channel_number),
                                      dummy_data='LOW').strip()]

    @source.setter
    def source(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is not '1310' or '1550'
        """
        input_dict = {self.CAPABILITY['source'][0]: 'LOW',
                      self.CAPABILITY['source'][1]: 'UPP'}
        value = float(value)
        if value not in input_dict.keys():
            raise ValueError('Please specify either %s'
                             % self.CAPABILITY['source'])
        else:
            self._write("SOURce%s:CHANnel%s:POWer:WAVelength %s"
                        % (self._slot_number, self._channel_number, input_dict[value]))

    @property
    def identity(self):
        """
        Retrieve module identity.

        :return: identity
        :rtype: dict
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

    @property
    def temperature_check(self):
        """
        ***READONLY***
        Get the temperature status of the transmitter
        A value ranging from 0.0 to 1.0.
        Values near 1.0 indicate the current temperature is close to the temperature at the last recalibration.
        Values near 0.0 indicate the current temperature has drifted towards its maximum tolerance limit.

        :value: temperature status
        :type: float
        """

        return float(self._read("SOURce%s:CHANnel%s:TRANsmitter:TCHeck?" % (self._slot_number, self._channel_number)))

    def recalibrate_transmitter(self):
        """
        Re-calibrates the reference transmitter and returns status of calibration. Typically takes about 6.8 seconds.

        :returns: returns "OK" or "ERROR - <error message>"
        :rtype: str
        """
        return self._read("SOURce%s:CHANnel%s:TRANsmitter:REC?" %
                          (self._slot_number, self._channel_number), type_='stb_poll_sync', dummy_data="OK")

    def reset(self):
        """
        Perform equipment reset, to put device in known preset state
        """
        if not self.dummy_mode:
            self._write("*RST", type_='stb_poll_sync')

