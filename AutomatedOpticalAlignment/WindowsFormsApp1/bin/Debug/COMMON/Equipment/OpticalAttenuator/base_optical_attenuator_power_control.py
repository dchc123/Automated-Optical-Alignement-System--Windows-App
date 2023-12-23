"""
| $Revision:: 283617                                   $:  Revision of last commit
| $Author:: lagapie@SEMNET.DOM                         $:  Author of last commit
| $Date:: 2018-11-14 18:11:37 +0000 (Wed, 14 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.OpticalAttenuator.base_optical_attenuator import BaseOpticalAttenuator
from CLI.Equipment.OpticalAttenuator.base_optical_attenuator import BaseOpticalAttenuatorChannel


class BaseOpticalAttenuatorPowerControl(BaseOpticalAttenuator):
    """
    Base Optical Attenuator with Power Control class that all Optical Attenuators with power control
    should be derived from.
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

    def zero_all(self):
        """
        Zeros the electrical offsets of the attenuator’s integrated power meter for all channels
        """
        raise NotImplementedError


class BaseOpticalAttenuatorPowerControlChannel(BaseOpticalAttenuatorChannel):
    """
    Base Optical Attenuator with Power Control channel class that all attenuator with power control
    channels should be derived from.
    """

    CAPABILITY = {'attenuation_range': {'min': None, 'max': None},
                  'attenuation_offset_range': {'min': None, 'max': None},
                  'opm_avg_time': {'min': None, 'max': None},
                  'power_level_dBm_range': {'min': None, 'max': None},
                  'power_level_offset_range': {'min': None, 'max': None},
                  'power_level_watt_range': {'min': None, 'max': None},
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
    def opm_avg_time(self):
        """
        :value: optical power meter averaging time (s)
        :type: float
        """
        raise NotImplementedError

    @opm_avg_time.setter
    def opm_avg_time(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def power_control(self):
        """
        Disable or Enable power control mode

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @power_control.setter
    def power_control(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def power_offset(self):
        """
        :value: power offset (dB)
        :type: float
        """
        raise NotImplementedError

    @power_offset.setter
    def power_offset(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def power_setpoint(self):
        """
        :value: power setpoint
        :type: float
        """
        raise NotImplementedError

    @power_setpoint.setter
    def power_setpoint(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def power_unit(self):
        """
        Power unit

        :value: - 'dBm'
                - 'Watt'
        :type: str
        """
        raise NotImplementedError

    @power_unit.setter
    def power_unit(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def power_value(self):
        """
        READONLY

        Value relies on power units
        :py:class:`.power_unit`

        :value: power meter reading
        :type: float
        """
        raise NotImplementedError

    def zero_offset(self):
        """
        Zeros the electrical offsets of the attenuator’s integrated power meter
        """
        raise NotImplementedError
