"""
| $Revision:: 283346                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-02 15:12:45 +0000 (Fri, 02 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.KeysightN7762A`
::

    >>> from CLI.Equipment.OpticalAttenuator.KeysightN776XX.keysight_n7762a import KeysightN7762A
    >>> Att = KeysightN7762A('GPIB1::23::INSTR')
    >>> Att.connect()
    >>> Att.zero_all()

For channel level API:
:py:class:`.KeysightN7762AChannel`
::

    >>> Att.channel[2].power_units = "dBm"
    >>> Att.channel[1].attenuation = 10
    >>> Att.channel[1].attenuation
    10.0
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_structures import CustomList
from .keysight_n776xx import KeysightN776XX
from .keysight_n776xx import KeysightN776XXChannel


class KeysightN7762A(KeysightN776XX):
    """
    Keysight N7762A optical attenuator with power control driver
    """

    CAPABILITY = {'channels': 2}

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
        """:type: list of KeysightN7762AChannel"""
        self.channel.append(KeysightN7762AChannel(channel_number=1, interface=interface, dummy_mode=dummy_mode))
        # Additional channels are on an offset for SCPI commands
        self.channel.append(KeysightN7762AChannel(channel_number=3, interface=interface, dummy_mode=dummy_mode))


class KeysightN7762AChannel(KeysightN776XXChannel):
    """
    Keysight N7762A optical attenuator with power control channel
    """

    CAPABILITY = {'attenuation_range': {'min': 0, 'max': 45},
                  'attenuation_offset_range': {'min': -200, 'max': 200},
                  'opm_avg_time': {'min': 0.002, 'max': 1},
                  'power_level_dBm_range': {'min': -50, 'max': 20},
                  'power_level_offset_range': {'min': -60, 'max': 60},
                  'power_level_watt_range': {'min': 0.00000001, 'max': 0.1},
                  'speed_range': {'min': 0.1, 'max': 1000},
                  'wavelength_range': {'min': 1260, 'max': 1640},
                  }

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the attenuator
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
