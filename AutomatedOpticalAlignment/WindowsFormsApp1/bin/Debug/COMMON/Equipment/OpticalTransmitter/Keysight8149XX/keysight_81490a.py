"""
| $Revision:: 281713                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-20 15:03:30 +0100 (Mon, 20 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keysight81490A`
::

    >>> from CLI.Equipment.OpticalTransmitter.Keysight8149XX.keysight_81490a import Keysight81490A
    >>> trans = Keysight81490A('GPIB1::23::INSTR', 1)
    >>> trans.connect()
    >>> trans.source = 1310
    >>> trans.recalibrate_transmitter()
    >>> "OK"
    >>> trans.output = "ENABLE"
    >>> trans.attenuation = 4

"""

from CLI.Mainframes.Keysight816XX.keysight_8163x import Keysight8163X
from ..Keysight8149XX.keysight_8149xx import Keysight8149XX


class Keysight81490A(Keysight8149XX):
    """
    Keysight 81490A Transmitter driver
    """

    CAPABILITY = {'attenuation': {'min': 0, 'max': 6},
                  'source_135': [1310.0, 1550.0],
                  'source_E03': [850.0],
                  'operating_point': {'min': -50, 'max': 50}
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
        super().__init__(address=address, slot_number=slot_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._slot_number = slot_number
        self._channel_number = 1
        self.option = None
        """
        Equipment option
        
        :value: - '135'
                - 'E03'
        :type: str
        """

    def _configure(self):
        """
        Configure part depending on option
        """
        # try catch statement since there is no way to query the options remotely.
        try:
            self._write("SOURce%s:CHANnel%s:POWer:WAVelength UPP" % (self._slot_number, self._channel_number))
            self.option = '135'
        except:
            self.option = 'E03'

    @property
    def _current_laser(self):
        """
        ***READONLY***

        :value: index of current laser source
        :type: int
        """
        if self.option == 'E03':
            output = self.CAPABILITY['source_E03'].index(self.source)
        else:
            output = self.CAPABILITY['source_135'].index(self.source)

        return output

    @property
    def source(self):
        """
        Laser source of the transmitter

        :value: wavelength (nm)
        :type: float
        :raise ValueError: exception if input is not '850', '1310' or '1550' (depending on option of module)
        """
        if self.option == 'E03':
            low = self.CAPABILITY['source_E03'][0]
            output_dict = {'LOW': low}
        else:
            low = self.CAPABILITY['source_135'][0]
            upp = self.CAPABILITY['source_135'][1]
            output_dict = {'LOW': low, 'UPP': upp}

        return output_dict[self._read("SOURce%s:CHANnel%s:POWer:WAVelength?"
                                      % (self._slot_number, self._channel_number), dummy_data='LOW').strip()]

    @source.setter
    def source(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is not '850', '1310' or '1550' (depending on option of module)
        """
        if self.option == 'E03':
            input_dict = {self.CAPABILITY['source_E03'][0]: 'LOW'}
        else:
            input_dict = {self.CAPABILITY['source_135'][0]: 'LOW',
                          self.CAPABILITY['source_135'][1]: 'UPP'}
        value = float(value)
        if value not in input_dict.keys():
            raise ValueError('Please specify either %s' % list(input_dict.keys()))
        else:
            self._write("SOURce%s:CHANnel%s:POWer:WAVelength %s"
                        % (self._slot_number, self._channel_number, input_dict[value]))
