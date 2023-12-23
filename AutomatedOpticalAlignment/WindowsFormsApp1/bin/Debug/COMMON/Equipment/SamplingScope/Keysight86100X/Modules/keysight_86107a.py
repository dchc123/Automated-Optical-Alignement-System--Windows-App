"""
| $Revision:: 279008                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-10 14:10:01 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For Precision Timebase API:
See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86107a.Keysight86107A`
::

    >>> from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x import Keysight86100X
    >>> scope = Keysight86100X('GPIB1::23::INSTR')
    >>> scope.connect()
    >>> scope.precision_timebase.state = 'ENABLE'
    >>> scope.precision_timebase.ref_clock_frequency
    100000.0
    >>> scope.precision_timebase.ref_clock_frequency = 1e7
    >>> scope.precision_timebase.reset_time_reference()
"""

from CLI.Equipment.SamplingScope.base_sampling_scope import BaseSamplingScopeModule
from decimal import Decimal


class Keysight86107A(BaseSamplingScopeModule):
    """
    Keysight 86107A Module
    """
    CAPABILITY = {'rc_frequency': {'min': 2.4e9, 'max': 48e9}}

    def __init__(self, module_id, module_option, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module slot index
        :type module_id: int
        :param module_option: available added options for module
        :type module_option: str
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._module_option = module_option

    @property
    def auto_detect_ref_clock(self):
        """
        Disable or Enable auto detect

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":PTIMebase1:RFR:AUTO?")]

    @auto_detect_ref_clock.setter
    def auto_detect_ref_clock(self, value): # TODO: Add Polling
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':PTIMebase1:RFR:AUTO {}'.format(input_dict[value]), type_='stb_poll_sync')

    @property
    def method(self):
        """
        Specify precision timebase method

        :value: - 'FAST'
                - 'LINEAR'
        :type: str
        :raise ValueError: exception if input is not 'FAST' or 'LINEAR'
        """
        output_dict = {'FAST': 'FAST', 'OLIN': 'LINEAR'}
        return output_dict[self._read("PTIMebase1:RMEThod?", dummy_data='FAST')]

    @method.setter
    def method(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'FAST': 'FAST', 'LINEAR': 'OLIN'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'FAST' or 'LINEAR'")
        else:
            self._write('PTIMebase1:RMEThod {}'.format(input_dict[value]))

    @property
    def rc_frequency(self):
        """
        Reference clock frequency

        :value: reference clock frequency in Hz
        :type: float
        """
        return float(self._read(":PTIMebase1:RFR?"))

    @rc_frequency.setter
    def rc_frequency(self, value):
        """
        :type value: float
        """
        self.auto_detect_ref_clock = 'DISABLE'
        min_freq = self.CAPABILITY['rc_frequency']['min']
        max_freq = self.CAPABILITY['rc_frequency']['max']

        if min_freq <= value <= max_freq:
            self._write(':PTIMebase1:RFR {:.2E}'.format(Decimal(value)))
        else:
            raise ValueError('rc_frequency must be between {} and {}'.format(min_freq,
                                                                             max_freq))

    @property
    def state(self):
        """
        Disable or Enable precision timebase

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not "ENABLE" or "DISABLE"
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":PTIMebase1:STAT?")]

    @state.setter
    def state(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not "ENABLE" or "DISABLE"
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':PTIMebase1:STAT {}'.format(input_dict[value]), type_='stb_poll_sync')

    def reset_time_reference(self):
        """
        Resets time reference
        """
        self._write('PTIMebase1:RTR')
