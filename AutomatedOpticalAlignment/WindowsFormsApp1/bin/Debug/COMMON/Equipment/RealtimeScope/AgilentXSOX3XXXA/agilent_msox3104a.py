from .agilent_xsox3xxxa import AgilentXSOX3xxxA, AgilentXSOX3xxxAChannel, AgilentXSOX3xxxATrigger, AgilentXSOX3xxxAProbe, AgilentXSOX3xxxAMeasurement
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_structures import CustomList


class AgilentMSOX3104A(AgilentXSOX3xxxA):
    """
    Driver for Agilent MSOX3104A Real-time Scope
    """
    CAPABILITY = {'horizontal_scale': {'min': 1e-9, 'max': 50}}

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """

        :param address:
        :param interface:
        :param dummy_mode:
        :param kwargs:
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of AgilentMSOX3104AChannel"""
        self.channel.append(AgilentMSOX3104AChannel(channel_number=1, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentMSOX3104AChannel(channel_number=2, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentMSOX3104AChannel(channel_number=3, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentMSOX3104AChannel(channel_number=4, interface=interface, dummy_mode=dummy_mode))
        self.trigger = AgilentMSOX3104ATrigger(interface=interface, dummy_mode=dummy_mode)
        self._mode = None


class AgilentMSOX3104AChannel(AgilentXSOX3xxxAChannel):
    """
    Agilent MSOX3104A Channel driver
    """
    CAPABILITY = {'bandwidth': [25e6, 500e6],
                  'offset': {'min': -50, 'max': 50},
                  'scale': {'min': 0.001, 'max': 5.0},
                  'range': {'min': 0.008, 'max': 40}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """

        :param channel_number:
        :param interface:
        :param dummy_mode:
        :param kwargs:
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self.probe = AgilentMSOX3104AProbe(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode)
        self.measurement = AgilentMSOX3104AMeasurement(channel_number=channel_number, interface=interface,
                                                       dummy_mode=dummy_mode)


class AgilentMSOX3104ATrigger(AgilentXSOX3xxxATrigger):
    """
    AgilentMSOX3104A Probe driver
    """
    CAPABILITY = {'level': {'min': -30, 'max': 30}}

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


class AgilentMSOX3104AProbe(AgilentXSOX3xxxAProbe):
    """
    AgilentMSOX3104A Probe driver
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


class AgilentMSOX3104AMeasurement(AgilentXSOX3xxxAMeasurement):
    """
    AgilentMSOX3104A Measurement block driver
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
