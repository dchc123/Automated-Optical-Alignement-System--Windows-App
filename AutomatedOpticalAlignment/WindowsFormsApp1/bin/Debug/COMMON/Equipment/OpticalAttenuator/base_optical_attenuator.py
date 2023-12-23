"""
| $Revision:: 283346                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-02 15:12:45 +0000 (Fri, 02 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.Base.base_equipment import BaseEquipment
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseOpticalAttenuator(BaseEquipment):
    """
    Base Optical Attenuator class that all Optical Attenuators should be derived from.
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


class BaseOpticalAttenuatorChannel(BaseEquipmentBlock):
    """
    Base Optical Attenuator channel class that all attenuator channels should be derived from.
    """

    CAPABILITY = {'attenuation_range': {'min': None, 'max': None},
                  'attenuation_offset_range': {'min': None, 'max': None},
                  'speed_range': {'min': None, 'max': None},
                  'wavelength_range': {'min': None, 'max': None},
                  }

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

    @property
    def attenuation(self):
        """
        :value: attenuation level in dB
        :type: float
        """
        raise NotImplementedError

    @attenuation.setter
    def attenuation(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def attenuation_offset(self):
        """
        :value: attenuation offset
        :type: float
        """
        raise NotImplementedError

    @attenuation_offset.setter
    def attenuation_offset(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def output(self):
        """
        Disable or Enable attenuator output

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
    def speed(self):
        """
        Attenuation filter speed

        :value: speed  (dB/s)
        :type: float
        """
        raise NotImplementedError

    @speed.setter
    def speed(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def wavelength(self):
        """
        Wavelength of signal

        :value: wavelength (nm)
        :type: float
        """
        raise NotImplementedError

    @wavelength.setter
    def wavelength(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

