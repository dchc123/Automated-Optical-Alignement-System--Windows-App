"""
| $Revision:: 279036                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-10 17:01:00 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.AgilentE4422B`
::

    >>> from CLI.Equipment.SignalGenerator.AgilentE44XXX.agilent_e4422b import AgilentE4422B
    >>> sg = AgilentE4422B('GPIB1::23::INSTR')
    >>> sg.connect()
    >>> sg.amplitude
    0.0
    >>> sg.amplitude = 3.2
    >>> sg.amplitude
    3.2
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Equipment.SignalGenerator.AgilentE44XXX.agilent_e44xxx import AgilentE44XXX


class AgilentE4422B(AgilentE44XXX):
    """
    AgilentE4422B Signal Generator
    """
    CAPABILITY = {'amplitude': {'min': -135, 'max': 20},
                  'frequency': {'min': 100e3, 'max': 4e9}}

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
        self._frequency = None
        self._amplitude = None
        self._output = None
