"""
| $Revision:: 279008                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-10 14:10:01 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For Electrical Modules API:
See :py:mod:`Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module`
See :py:mod:`Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks`
::

    >>> from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x import Keysight86100X
    >>> scope = Keysight86100X('GPIB1::23::INSTR')
    >>> scope.connect()

    >>> scope.elec[1].mode
    'SINGLE'
    >>> scope.elec[1].mode = 'DIFFERENTIAL'
    # Note that you can access channels by an int index or by their display names
    >>> scope.elec['1A'].mode
    'DIFFERENTIAL'
    >>> scope.mode = 'OSC'
    >>> scope.elec[1].mode = 'SINGLE'
    >>> scope.elec[1].osc.avg
    0.5
    >>> scope.mode = 'EYE'
    >>> scope.elec[1].eye.amplitude
    1.0
    >>> scope.elec[1].mask_test.load('MASK_PATH')
    >>> scope.elec[1].histogram[1].state = 'ENABLE'
    >>> scope.elec[1].histogram[1].placement = 'TOP'
"""

from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module import Keysight86100XElectricalModule
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module import \
    Keysight86100XSingleElectricalModule
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module import Keysight86100XDiffElectricalModule


class KeysightN1045A(Keysight86100XElectricalModule):
    """
    Keysight N1045A Module
    """

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


class KeysightN1045ASingle(Keysight86100XSingleElectricalModule):
    """
    Keysight N1045A Single Channel
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

    @property
    def bandwidth(self):
        """
        Specify channel bandwidth in GHz

        :value: - '20.0E+9'
                - '35.0E+9'
                - '45.0E+9'
                - '60.0E+9'
        :type: int
        :raise ValueError: exception if bandwidth is not 20.0E+9, 35.0E+9, 45.0E+9, 60.0E+9
        """
        return self._read(":CHAN{}{}:BANDwidth:FREQuency?".format(
            self._module_id, self._channel_number))

    @bandwidth.setter
    def bandwidth(self, value):
        """
        :type value: int
        :raise ValueError: exception if bandwidth is not 20.0E+9, 35.0E+9, 45.0E+9, 60.0E+9
        """
        input_list = ['20.0E+9', '35.0E+9', '45.0E+9', '60.0E+9']
        if value not in input_list:
            raise ValueError('Please specify either 20.0E+9, 35.0E+9, 45.0E+9 or 60.0E+9')
        else:
            self._write(':CHAN{}{}:BANDwidth:FREQuency {}'.format(self._module_id,
                                                                  self._channel_number,
                                                                  value))


class KeysightN1045ADiff(Keysight86100XDiffElectricalModule):
    """
    Keysight N1045A Module
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


