"""
| $Revision:: 279062                                   $:  Revision of last commit
| $Author:: ael-khouly@SEMNET.DOM                      $:  Author of last commit
| $Date:: 2018-07-10 19:29:10 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the Jitter Module API: See :py:mod:`Equipment.BERT.AnritsuMP1800.Modules.anritsu_mp1800_jitter`
::

    >>> from CLI.Equipment.BERT.AnritsuMP1800.anritsu_mp1800 import AnritsuMP1800
    >>> bert = AnritsuMP1800('GPIB1::23::INSTR')
    >>> bert.connect()
    >>> bert.jitter[1].global_output
    'DISABLE'
    >>> bert.jitter[1].global_output = 'ENABLE'
    >>> bert.jitter[1].global_output
    'ENABLE'
"""
from .anritsu_mp1800_jitter import AnritsuMP1800Jitter
from .anritsu_mp1800_jitter import AnritsuMP1800BUJitter
from .anritsu_mp1800_jitter import AnritsuMP1800SJitter
from .anritsu_mp1800_jitter import AnritsuMP1800SSCJitter
from .anritsu_mp1800_jitter import AnritsuMP1800RJitter


class AnritsuMU181500B(AnritsuMP1800Jitter):
    """
    Anritsu MU181500B Jitter Module
    """
    def __init__(self, module_id, channel_number, synth_mod_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param channel_number: number targeting channel
        :type channel_number: int
        :param synth_mod_id: Synthesizer module identification string
        :type synth_mod_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, channel_number=channel_number, synth_mod_id=synth_mod_id,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.bu = AnritsuMU181500BBUJitter(module_id=module_id, interface=interface, dummy_mode=dummy_mode)
        self.sj = AnritsuMU181500BSJitter(module_id=module_id, interface=interface, dummy_mode=dummy_mode)
        self.scj = AnritsuMU181500BSSCJitter(module_id=module_id, interface=interface, dummy_mode=dummy_mode)
        self.rj = AnritsuMU181500BRJitter(module_id=module_id, interface=interface, dummy_mode=dummy_mode)


class AnritsuMU181500BBUJitter(AnritsuMP1800BUJitter):
    """
    AnritsuMU181500B BU Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, interface=interface, dummy_mode=dummy_mode, **kwargs)


class AnritsuMU181500BSSCJitter(AnritsuMP1800SSCJitter):
    """
    Anritsu MU181500B SSC Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, interface=interface, dummy_mode=dummy_mode, **kwargs)


class AnritsuMU181500BRJitter(AnritsuMP1800RJitter):
    """
    Anritsu MU181500B R Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, interface=interface, dummy_mode=dummy_mode, **kwargs)


class AnritsuMU181500BSJitter(AnritsuMP1800SJitter):
    """
    Anritsu MU181500B S Jitter Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self.source = 1

