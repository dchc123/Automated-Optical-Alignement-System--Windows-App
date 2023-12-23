"""
| $Revision:: 279008                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-10 14:10:01 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.Base.base_equipment import BaseEquipment


class BaseSignalGenerator(BaseEquipment):
    """
    Base Clock Generator class that all Clock Generator should be derived from.
    """
    def __init__(self, address, interface, dummy_mode, **kwargs):
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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def amplitude(self):
        """
        Signal Amplitude
        :value: amplitude in dBm
        :type: float
        """
        raise NotImplementedError

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def frequency(self):
        """
        Signal Frequency

        :value: frequency in Hz
        :type: float
        """
        raise NotImplementedError

    @frequency.setter
    def frequency(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def output(self):
        """
        Disable or Enable signal generator output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

