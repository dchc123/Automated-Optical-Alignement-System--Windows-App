"""
| $Revision:: 282849                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-15 20:25:16 +0100 (Mon, 15 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For Electrical Modules API:
See :py:mod:`Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module`
See :py:mod:`Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks`
::

    >>> from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x import Keysight86100X
    >>> scope = Keysight86100X('GPIB1::23::INSTR')
    >>> scope.connect()

    >>> scope.cdr.loop_bandwidth_mode = 'FIXED'
    >>> scope.cdr.locked
    'LOCKED'
    >>> scope.cdr.relock()
    >>> scope.cdr.recovered_clk_divider = 8
"""

from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100DClockDataRecovery


class KeysightN1076A(Keysight86100DClockDataRecovery):
    """
    Keysight N1076A Module
    """

    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module slot index
        :type module_id: int
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id

    def relock(self):
        """
        Attempts to lock the module to the data rate present on the input
        """
        self._write(':CREC{0}:RELock'.format(self._module_id))

    @property
    def auto_datarate_locking(self):
        """
        Enable or Disable automatic data-rate locking

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if input is not 'ENABLE' or 'DISABLE'
        """
        raise NotImplementedError('{0} does not support reading automatic datarate locking'.format(self.name))

    @auto_datarate_locking.setter
    def auto_datarate_locking(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        raise NotImplementedError('{0} does not support writing automatic datarate locking'.format(self.name))

    @property
    def continuous_loop_bandwidth(self):
        """
        Sets continuous loop bandwidth for this module.

        :value: bandwidth in Hz
        :type: float
        """
        return self._read('CREC{0}:CLB?'.format(self._module_id))

    @continuous_loop_bandwidth.setter
    def continuous_loop_bandwidth(self, value):
        """
        :type value: float
        """
        if self.loop_bandwidth_mode != 'FIX':
            raise ValueError("loop bandwidth mode must be in 'fixed' mode in order for this function to work")
        elif value >= 30e3 or value <= 20e6:
            self._write('CREC{0}:CLB {1}'.format(self._module_id, value))
        else:
            raise ValueError('Value must be between 30kHz and 20MHz')

    @property
    def data_rate_divider(self):
        """
        Sets data-rate divider. Used to compute LBW when in rate-dependent lbw mode

        :value: ratio
        :type: int
        """
        return self._read(':CREC{0}:RDIV?'.format(self._module_id))

    @data_rate_divider.setter
    def data_rate_divider(self, value):
        """
        :type value: int
        """
        self._write(':CREC{0}:RDIV {1}'.format(self._module_id, value))

    @property
    def edge_density(self):
        """
        *READ-ONLY*
        Calculated edge density of data signal

        :value: ratio of bit transitions to bits
        :type: float
        """
        return float(self._read(':CREC{0}:TDEN?'.format(self._module_id)))

    @property
    def input_type(self):
        """
        Sets module input type

        :value: - 'ELECTRICAL'
                - 'OPTICAL'
                - 'DIFFERENTIAL'
                - 'EINVERTED'
                - 'AUXILIARY'
        :type: str
        """
        input_dict = {'ELEC': 'ELECTRICAL', 'OPT': 'OPTICAL', 'DIFF': 'DIFFERENTIAL',
                      'EINV': 'EINVERTED', 'AUX': 'AUXILIARY'}
        return input_dict[self._read(':CREC{0}:INPut?'.format(self._module_id))]

    @input_type.setter
    def input_type(self, value):
        """
        :type value: str
        """
        self._write(':CREC{0}:INPut {1}'.format(self._module_id, value.upper()))

    @property
    def locked(self):
        """
        *READ-ONLY*
        Returns the locked status of the module
        :type: str
        """
        input_dict = {'1': 'LOCKED', '0': 'UNLOCKED'}
        return input_dict[self._read("CREC{0}:LOCK?".format(self._module_id))]

    @property
    def loop_bandwidth_mode(self):
        """
        Sets loop bandwidth mode

        :value: - 'FIXED'
                - 'RDEPENDENT'
        :type: str
        """
        return self._read(':CREC{0}:LBWMode?'.format(self._module_id))

    @loop_bandwidth_mode.setter
    def loop_bandwidth_mode(self, value):
        """
        :type value: str
        """
        self._write(':CREC{0}:LBWMode {1}'.format(self._module_id, value))

    @property
    def loop_transition_frequency(self):
        """
        Selects the Type-2 transition frequency (peaking)

        :value: - '12kHz'
                - '280kHz'
                - '640kHz'
                - '1.3MHz'
                - 'AUTO'
        :type: str
        """
        if self._read(':CREC{0}:LSEL:AUT?'.format(self._module_id)) == '1':
            self.logger.info('Automatic loop transition frequency is enabled!')
        input_dict = {'LOOP1': '12kHz', 'LOOP2': '280kHz', 'LOOP3': '640kHz', 'LOOP4': '1.3MHz'}
        return input_dict[self._read(':CREC{0}:LSEL?'.format(self._module_id))]

    @loop_transition_frequency.setter
    def loop_transition_frequency(self, value):
        """
        :type value: str
        """
        if value == 'AUTO':
            self._write(':CREC{0}:LSEL:AUT 1'.format(self._module_id))
        else:
            output_dict = {'12kHz': '1', '280kHz': '2', '640kHz': '3', '1.3MHz': '4'}
            self._write(':CREC{0}:LSEL:AUT 0'.format(self._module_id))
            self._write(':CREC{0}:LSEL LOOP{1}'.format(self._module_id, output_dict[value]))

    @property
    def peaking(self):
        """
        *READ-ONLY*
        Loop-gain in dB for specified type-2 transition freq
        :value: db
        :type: float
        """
        return self._read('CREC{0}:JSAN:PLL:JTF:PEAK?'.format(self._module_id))

    @property
    def rate(self):
        """
        Sets clock recovery module data rate

        :value: freq in Hz
        :type: float
        """
        return self._read('CREC{0}:CRAT?'.format(self._module_id))

    @rate.setter
    def rate(self, value):
        """
        :type value: float
        """
        self._write('CREC{0}:CRAT {1}'.format(self._module_id, value))

    @property
    def recovered_clk_divider(self):
        """
        Sets output clock divide ratio. Determines the data rate at the front-panel recovered clock output

        :value: - 1
                - 2
                - 4
                - 8
                - 16

        :type: int or str
        """
        if self._read(':CREC{0}:ODR:AUTO?'.format(self._module_id)) == '1':
            self.logger.info('Automatic recovered clock divider is enabled!')
        return int(self._read(':CREC{0}:ODR?'.format(self._module_id))[3:])

    @recovered_clk_divider.setter
    def recovered_clk_divider(self, value):
        """
        :type value: int or str
        """
        if isinstance(value, str):
            if value == 'AUTO':
                self._write(':CREC{0}:ODR:AUTO ON'.format(self._module_id))
            else:
                raise ValueError('Only valid string type input is "AUTO"')
        else:
            self._write(':CREC{0}:ODR:AUTO OFF'.format(self._module_id))
            self._write(':CREC{0}:ODR SUB{1}'.format(self._module_id, value))

    @property
    def recovered_clk_frequency(self):
        """
        ***READONLY***

        Returns frequency of the recovered clock

        :value: Frequency in Hz
        :type: float
        """
        return float(self._read(":CREC{0}:CFR?".format(self._module_id)))
