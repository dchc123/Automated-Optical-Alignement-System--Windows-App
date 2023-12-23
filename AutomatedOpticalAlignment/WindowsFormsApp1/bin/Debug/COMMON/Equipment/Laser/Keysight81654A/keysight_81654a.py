"""
| $Revision:: 280528                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-31 13:51:18 +0100 (Tue, 31 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keysight81654A`
::

    >>> from CLI.Equipment.Laser.Keysight81654A.keysight_81654a import Keysight81654A
    >>> laser = Keysight81654A('GPIB1::23::INSTR', 1)
    >>> laser.connect()
    >>> laser.source = 1310

"""
from CLI.Equipment.Laser.base_laser import BaseLaser
from CLI.Mainframes.Keysight816XX.keysight_8163x import Keysight8163X


class Keysight81654A(BaseLaser):
    """
    Keysight 81654A Laser driver
    """
    CAPABILITY = {'source': [1310.0, 1550.0]}

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
        self._slot_number = slot_number
        self._channel_number = 1

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
        Laser source of output signal

        :value: wavelength (nm)
        :type: float
        :raise ValueError: exception if input is not '1310' or '1550'
        """
        output_dict = {'LOW': 1310.0, 'UPP': 1550.0}
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
