"""
| $Revision:: 279008                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-10 14:10:01 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Equipment.Base.base_equipment import BaseEquipment
from COMMON.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseAWG(BaseEquipment):
    """
    Base AWG class that all AWG should be derived from.
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
    def frequency(self):
        """
        Set clock frequency

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
        Disable or Enable AWG output

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

    @property
    def pattern(self):
        """
        Set desired custom pattern

            - Hex string i.e. H02948ACFE... (max 400 chars)
            - Bin string i.e. B010101100... (max 400 chars)

        :value: custom pattern
        :type: str
        """
        raise NotImplementedError

    @pattern.setter
    def pattern(self, value):
        """
        :type value: str
        """
        raise NotImplementedError


class BaseAWGWaveform(BaseEquipmentBlock):
    """
    Base AWG Waveform class that all AWG Waveforms should be derived from.
    """

    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.frequency = None
        """
        :value: frequency of periodic waveform in Hz
        :type: float
        """
        self.type = None
        """
        :value: - 'sine'
                - 'square'
                - 'triangle'
                - 'noise'
                - 'DC'
                - 'ramp'
                - 'pulse'
        :type: str
        """
        self.amplitude = None
        """
        :value: amplitude of the waveform
        :type: float
        """
        self.duty_cycle = None
        """
        :value: duty cycle of signal where applicable in %
        :type: int
        """
        self.rise_fall = None
        """
        :value: rise/fall time of signal where applicable in seconds
        :type: float
        """








