"""
| $Revision:: 281646                                   $:  Revision of last commit
| $Author:: wleung@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-16 20:09:50 +0100 (Thu, 16 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Utilities.custom_structures import CustomList
from .agilent_dso7xxxa import AgilentDSO7XXXA
from .agilent_dso7xxxa import AgilentDSO7XXXAChannel
from .agilent_dso7xxxa import AgilentDSO7XXXATrigger
from .agilent_dso7xxxa import AgilentDSO7XXXAProbe
from .agilent_dso7xxxa import AgilentDSO7XXXAMeasurement
from COMMON.Interfaces.VISA.cli_visa import CLIVISA


class AgilentDSO7034A(AgilentDSO7XXXA):
    """
    Driver for Agilent DSO7034A Real-time Scope
    """
    CAPABILITY = {'horizontal_scale': {'min': 1e-9, 'max': 50}}

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
        self.channel = CustomList()
        """:type: list of AgilentDSO7034AChannel"""
        self.channel.append(AgilentDSO7034AChannel(channel_number=1, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentDSO7034AChannel(channel_number=2, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentDSO7034AChannel(channel_number=3, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentDSO7034AChannel(channel_number=4, interface=interface, dummy_mode=dummy_mode))
        self.trigger = AgilentDSO7034ATrigger(interface=interface, dummy_mode=dummy_mode)
        self._mode = None
        self._file_base_name = ''
        self._image_file_format = ''
        self.measurement_labels = []


class AgilentDSO7034AChannel(AgilentDSO7XXXAChannel):
    """
    Agilent DSO7034A Channel driver
    """
    CAPABILITY = {'offset': {'min': -50, 'max': 50},
                  'scale': {'min': 0.002, 'max': 5.0},
                  'range': {'min': 0.016, 'max': 40}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self.probe = AgilentDSO7034AProbe(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode)
        self.measurement = AgilentDSO7034AMeasurement(channel_number=channel_number, interface=interface,
                                                      dummy_mode=dummy_mode)


class AgilentDSO7034ATrigger(AgilentDSO7XXXATrigger):
    """
    AgilentDSO7034A trigger driver
    """
    CAPABILITY = {'level': {'min': -100, 'max': 100}}

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


class AgilentDSO7034AProbe(AgilentDSO7XXXAProbe):
    """
    AgilentDSO7034A Probe driver
    """
    CAPABILITY = {'attenuation': {'min': 0.1, 'max': 10000},
                  'skew': {'min': -100e-9, 'max': 100e-9}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number


class AgilentDSO7034AMeasurement(AgilentDSO7XXXAMeasurement):
    """
    AgilentDSO7034A Measurement block driver
    """
    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
