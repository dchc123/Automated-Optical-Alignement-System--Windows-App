"""
| $Revision:: 283841                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-21 18:27:35 +0000 (Wed, 21 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.AnritsuMG3696B`
::

    >>> from CLI.Equipment.SignalGenerator.AnritsuMG369XX.anritsu_mg3696b import AnritsuMG3696B
    >>> sg = AnritsuMG3696B('GPIB1::23::INSTR')
    >>> sg.connect()
    >>> sg.amplitude
    0.0
    >>> sg.amplitude = 3.2
    >>> sg.amplitude
    3.2
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Equipment.SignalGenerator.AnritsuMG369XX.anritsu_mg369xxx import AnritsuMG369XXX


class AnritsuMG3696B(AnritsuMG369XXX):
    """
    Anritsu MG3696B Signal Generator
    """
    CAPABILITY = {'amplitude': {'min': -20, 'max': 20},
                  'frequency': {'min': 10e6, 'max': 65e9}}

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


