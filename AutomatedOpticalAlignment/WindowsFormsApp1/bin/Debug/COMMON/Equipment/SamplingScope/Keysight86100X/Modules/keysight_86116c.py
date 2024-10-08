"""
| $Revision:: 278910                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-06 01:01:42 +0100 (Fri, 06 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For Optical Modules API:
See :py:mod:`Equipment.SamplingScope.Keysight86100X.Modules.keysight_optical_module`
See :py:mod:`Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks`
::

    >>> from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x import Keysight86100X
    >>> scope = Keysight86100X('GPIB1::23::INSTR')
    >>> scope.connect()
    >>> scope.mode = 'OSC'
    >>> scope.opt[1].osc.avg
    0.5
    >>> scope.mode = 'EYE'
    >>> scope.opt[1].eye.amplitude
    1.0
    >>> scope.opt[1].mask_test.load('MASK_PATH')
    >>> scope.opt[1].histogram[1].state = 'ENABLE'
    >>> scope.opt[1].histogram[1].placement = 'TOP'
"""

from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_optical_module import Keysight86100XOpticalModule
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_optical_module import Keysight86100XSingleOpticalModule
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module import \
    Keysight86100XSingleElectricalModule


class Keysight86116C(Keysight86100XOpticalModule):
    """
    Keysight 86116C Module
    """
    CAPABILITY = {'wavelength': {'min': 1300, 'max': 1620}}

    def __init__(self, module_id, module_option, channel_number, handle,
                 interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module slot index
        :type module_id: int
        :param module_option: available added options for module
        :type module_option: str
        :param channel_number: channel index
        :type channel_number: int or str
        :param handle: channel handle (e.g 'CHAN1A')
        :type handle: str
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, module_option=module_option,
                         channel_number=channel_number, handle=handle,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)


class Keysight86116CSingleOpt(Keysight86100XSingleOpticalModule):
    """
    Keysight 86116C Single Channel
    """
    def __init__(self, module_id, module_option, channel_number, handle,
                 pam, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module slot index
        :type module_id: int
        :param module_option: available added options for module
        :type module_option: str
        :param channel_number: channel index
        :type channel_number: int or str
        :param handle: channel handle (e.g 'CHAN1A')
        :type handle: str
        :param pam: flag to specify pam license available for this module
        :type pam: bool
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, module_option=module_option,
                         channel_number=channel_number, handle=handle,
                         pam=pam, interface=interface, dummy_mode=dummy_mode, **kwargs)


class Keysight86116CSingleElec(Keysight86100XSingleElectricalModule):
    """
    Keysight 86116C Module
    """
    def __init__(self, module_id, module_option, channel_number, handle,
                 pam, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module slot index
        :type module_id: int
        :param module_option: available added options for module
        :type module_option: str
        :param channel_number: channel index
        :type channel_number: int or str
        :param handle: channel handle (e.g 'CHAN1A')
        :type handle: str
        :param pam: flag to specify pam license available for this module
        :type pam: bool
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, module_option=module_option,
                         channel_number=channel_number, handle=handle, pam=pam,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
