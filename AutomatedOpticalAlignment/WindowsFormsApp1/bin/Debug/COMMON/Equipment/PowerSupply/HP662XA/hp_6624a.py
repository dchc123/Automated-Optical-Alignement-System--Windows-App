"""
$Author:: tbrooks@semtech.com
"""
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_structures import CustomList
from .hp_662xa import HP662XA
from .hp_662xa import HP662XAChannel
from .hp_662xa import HP662XAVoltageBlock
from .hp_662xa import HP662XACurrBlock


class HP6624A(HP662XA):
    """
    HP 6624A 4 channel power supply driver
    """
    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialise instance

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
        """:type: list of HP6624AChannel"""
        for c in range(1, 5):
            self.channel.append(HP6624AChannel(channel_number=c, interface=interface, dummy_mode=dummy_mode))


class HP6624AChannel(HP662XAChannel):
    """
    HP 6624A channel
    """
    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialise instance

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
        # if statement to allow channel 1 and 2 capabilities to be different from channel 3 and 4
        if channel_number < 3:
            self.voltage = HP6624AVoltageBlock7(channel_number=channel_number, interface=interface,
                                                dummy_mode=dummy_mode, name=self.name + 'VoltageMeasure')
            self.current = HP6624ACurrBlock5(channel_number=channel_number, interface=interface,
                                             dummy_mode=dummy_mode, name=self.name + 'currentMeasure')
        else:
            self.voltage = HP6624AVoltageBlock20(channel_number=channel_number, interface=interface,
                                                 dummy_mode=dummy_mode, name=self.name + 'VoltageMeasure')
            self.current = HP6624ACurrBlock2(channel_number=channel_number, interface=interface,
                                             dummy_mode=dummy_mode, name=self.name + 'currentMeasure')


class HP6624AVoltageBlock7(HP662XAVoltageBlock):
    """
    HP6624A 7V Voltage block
    """
    CAPABILITY = {'voltage': {'min': 0.0, 'max': 7.07}}

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


class HP6624ACurrBlock5(HP662XACurrBlock):
    """
    HP6624A 5A current block
    """
    CAPABILITY = {'current': {'min': 0.08, 'max': 5.15}}

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


class HP6624AVoltageBlock20(HP662XAVoltageBlock):
    """
    HP6624A 20V Voltage block
    """
    CAPABILITY = {'voltage': {'min': 0.0, 'max': 20.2}}

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


class HP6624ACurrBlock2(HP662XACurrBlock):
    """
    HP6624A 2A current block
    """
    CAPABILITY = {'current': {'min': 0.08, 'max': 2.06}}

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
