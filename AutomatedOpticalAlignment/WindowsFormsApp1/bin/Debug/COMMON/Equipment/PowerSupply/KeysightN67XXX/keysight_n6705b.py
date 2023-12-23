"""
| $Revision:: 278910                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-06 01:01:42 +0100 (Fri, 06 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from ..KeysightN67XXX.keysight_n670xx import KeysightN670XX


class KeysightN6705B(KeysightN670XX):
    """
    Keysight N6705B 4 channel power supply chassis driver.
    """
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

