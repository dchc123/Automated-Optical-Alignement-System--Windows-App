"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`Equipment.PowerSupply.KeysightN67XXX.keysight_n670xx`
::

    >>> from CLI.Equipment.PowerSupply.KeysightN67XXX.keysight_n670xx import KeysightN670XX
    >>> ps = KeysightN670XX('GPIB1::23::INSTR')
    >>> ps.connect()
    >>> ps.output_coupling([1,2,3])
    >>> ps.output_coupling()

For channel level API:
:py:class:`.KeysightN6732BChannel`
::

    >>> ps.channel[1].voltage.setpoint = 3
    >>> ps.channel[1].voltage.setpoint
    3
    >>> ps.channel[1].voltage.value
    3.0012
    >>> ps.channel[1].current.value
    0.102
    >>> ps.channel[1].voltage.protection_level = 7
    >>> ps.channel[1].voltage.setpoint = 8
    >>> ps.channel[1].protection_tripped
    True
    >>> ps.channel[1].voltage.setpoint = 5
    >>> ps.channel[1].voltage.clear_protection()
"""

from .keysight_n67xxx import KeysightN67XXXChannel
from .keysight_n67xxx import KeysightN67XXXVoltBlock
from .keysight_n67xxx import KeysightN67XXXCurrBlock


class KeysightN6732BChannel(KeysightN67XXXChannel):
    """
    Keysight N6732B Channel
    """

    CAPABILITY = {'4_wire_sensing': True, 'precision': False}

    def __init__(self, channel_number, channel_options, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param channel_options: options on the power supply module
        :type channel_options: str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, channel_options=channel_options,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

        self.voltage = KeysightN6732BVoltBlock(channel_number=channel_number, channel_options=channel_options,
                                               interface=interface, dummy_mode=dummy_mode,
                                               name=self.name+'VoltageMeasure')
        self.current = KeysightN6732BCurrBlock(channel_number=channel_number, channel_options=channel_options,
                                               interface=interface, dummy_mode=dummy_mode,
                                               name=self.name+'CurrentMeasure')


class KeysightN6732BVoltBlock(KeysightN67XXXVoltBlock):
    """
    Keysight N6732B voltage sub block
    """

    CAPABILITY = {'voltage': {'min': 0.015, 'max': 8.16}}

    def __init__(self, channel_number, channel_options, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param channel_options: options on the power supply module
        :type channel_options: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, channel_options=channel_options, interface=interface,
                         dummy_mode=dummy_mode, **kwargs)


class KeysightN6732BCurrBlock(KeysightN67XXXCurrBlock):
    """
    Keysight N6732B current sub block
    """

    CAPABILITY = {'current': {'min': 0.04, 'max': 6.375}}

    def __init__(self, channel_number, channel_options, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the power supply module
        :type channel_number: int
        :param channel_options: options on the power supply module
        :type channel_options: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, channel_options=channel_options, interface=interface,
                         dummy_mode=dummy_mode, **kwargs)
