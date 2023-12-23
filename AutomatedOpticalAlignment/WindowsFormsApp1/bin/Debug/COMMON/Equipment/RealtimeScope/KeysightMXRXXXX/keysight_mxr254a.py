from COMMON.Equipment.RealtimeScope.KeysightMXRXXXX.keysight_mxrxxxx import KeysightMXRXXXX, KeysightMXRXXXXChannel, \
    KeysightMXRXXXXProbe, KeysightMXRXXXXTrigger, KeysightMXRXXXXDigitalChannel, KeysightMXRXXXXFunction
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_structures import CustomList


class KeysightMXR254A(KeysightMXRXXXX):
    """
    Driver for Keysight MXR254A Real-time Scope
    """
    CAPABILITY = {'horizontal_scale': {'min': 5e-12, 'max': 200}}

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
        """:type: list of KeysightMXR254AChannel"""
        self.channel.append(KeysightMXR254AChannel(channel_number=1, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(KeysightMXR254AChannel(channel_number=2, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(KeysightMXR254AChannel(channel_number=3, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(KeysightMXR254AChannel(channel_number=4, interface=interface, dummy_mode=dummy_mode))
        self.trigger = KeysightMXR254ATrigger(interface=interface, dummy_mode=dummy_mode)
        self.function = CustomList()
        """:type: list of KeysightMSOS804AFunction"""
        for i in range(1, 17):
            self.function.append(KeysightMXRXXXXFunction(function_number=i, interface=interface, dummy_mode=dummy_mode))
        self.digital_channel = CustomList(start_index=0)
        """:type: list of KeysightMSOS804ADigitalChannel"""
        for i in range(0, 15):
            self.digital_channel.append(KeysightMXR254ADigitalChannel(channel_number=i, interface=interface,
                                                                      dummy_mode=dummy_mode))


class KeysightMXR254AChannel(KeysightMXRXXXXChannel):
    """
    Keysight MXR254A Channel driver
    """
    CAPABILITY = {'offset': {'min': -200, 'max': 200},
                  'scale': {'min': 0.001, 'max': 5.0},
                  'range': {'min': 0.008, 'max': 40}}

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
        self.probe = KeysightMXR254AProbe(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode)


class KeysightMXR254AProbe(KeysightMXRXXXXProbe):
    """
    KeysightMXR254A Probe driver
    """
    CAPABILITY = {'attenuation': {'min': 0.0001, 'max': 1000},
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


class KeysightMXR254ATrigger(KeysightMXRXXXXTrigger):
    """
    KeysightMXR254A trigger driver
    """
    CAPABILITY = {'level': {'min': -40, 'max': 40}}

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


class KeysightMXR254ADigitalChannel(KeysightMXRXXXXDigitalChannel):
    """
    Keysight MXR254A Digital Channel driver
    """
    CAPABILITY = {"threshold": {"min": -8, "max": 8}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialise instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface:
        :type interface:
        :param dummy_mode:
        :type dummy_mode:
        :param kwargs:
        :type kwargs:
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
