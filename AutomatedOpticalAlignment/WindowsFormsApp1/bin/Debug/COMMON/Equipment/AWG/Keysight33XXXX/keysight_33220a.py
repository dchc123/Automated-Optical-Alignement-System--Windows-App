
from typing import Union
from .keysight_332xxx import Keysight332XXX


class Keysight33220a(Keysight332XXX):
    """
    Keysight 33220A common Arbitrary Waveform Generator
    """

    CAPABILITY = {
        'frequency_range': {'min': 2e-6, 'max': 20e6},
        'amplitude_range': {'min': 10e-3, 'max': 10},
        'pulse_period': {'min': 2e-7, 'max': 2000},
        'pulse_width': {'min': 20e-9, 'max': 2000},
        'output_load': {'min': 50, 'max': 'INFINITY'},
        'max_waveform_points': 64e3,

    }

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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)

