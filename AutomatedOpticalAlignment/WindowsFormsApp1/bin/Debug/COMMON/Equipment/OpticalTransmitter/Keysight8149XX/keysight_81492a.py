"""
| $Revision:: 280528                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-31 13:51:18 +0100 (Tue, 31 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keysight81492A`
::

    >>> from CLI.Equipment.OpticalTransmitter.Keysight8149XX.keysight_81492a import Keysight81492A
    >>> trans = Keysight81492A('GPIB1::23::INSTR', 1)
    >>> trans.connect()
    >>> trans.source = 1310
    >>> trans.recalibrate_transmitter()
    >>> "OK"
    >>> trans.output = "ENABLE"
    >>> trans.attenuation = 4

"""

from CLI.Mainframes.Keysight816XX.keysight_8163x import Keysight8163X
from ..Keysight8149XX.keysight_8149xx import Keysight8149XX


class Keysight81492A(Keysight8149XX):
    """
    Keysight 81492A Transmitter driver
    """

    CAPABILITY = {'attenuation': {'min': 0, 'max': 6},
                  'source': [1310.0, 1550.0],
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
