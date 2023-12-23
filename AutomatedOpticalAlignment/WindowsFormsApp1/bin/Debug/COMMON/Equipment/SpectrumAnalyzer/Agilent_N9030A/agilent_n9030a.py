"""
| $Revision:: 282849                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-15 20:25:16 +0100 (Mon, 15 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.AgilentN9030A`

::
    >>> from CLI.Equipment.SpectrumAnalyzer.Agilent_N9030A.agilent_n9030a import AgilentN9030A
    >>> specA = AgilentN9030A('GPIB0::24::INSTR')
    >>> specA.connect()

    >>> specA.mode = 'PNOISE'
    >>> specA.get_phase_noise_rj('ENABLE', 12.89e9, 100e6, 20e9, -20, 5)

For Spectal Analysis block level API:
:py:class:`.AgilentN9030SpectralAnalysis`

::
    >>> specA.spectral_analysis.freq_center = 12.89e9
    >>> specA.spectral_analysis.y_scale_type = 'LOG'
    >>> specA.spectral_analysis.marker = 'ENABLE'
    >>> specA.spectral_analysis.marker_peak_threshold

For Phase Noise block level API:
:py:class:`.AgilentN9030SpectralAnalysis`

::
    >>> specA.phase_noise.bandwidth_auto_resolution = 'ENABLE'
    >>> specA.phase_noise.freq_start = 100e6
    >>> specA.phase_noise.freq_stop = 20e9
    >>> specA.phase_noise.rmsnoise_mode = 'JITTER'
"""

from CLI.Equipment.SpectrumAnalyzer.base_spectrum_analyzer import BaseSpectrumAnalyzer
from CLI.Equipment.SpectrumAnalyzer.base_spectrum_analyzer import BaseSpectrumAnalyzerSpectralAnalysis
from CLI.Equipment.SpectrumAnalyzer.base_spectrum_analyzer import BaseSpectrumAnalyzerPhaseNoise
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from time import sleep


class AgilentN9030A(BaseSpectrumAnalyzer):
    """
    AgilentN9030 spectrum analyzer
    """

    CAPABILITY = {'frequency': 0}

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.spectral_analysis = AgilentN9030SpectralAnalysis(interface=interface, dummy_mode=dummy_mode)
        self.phase_noise = AgilentN9030PhaseNoise(interface=interface, dummy_mode=dummy_mode)
        self._mode = None

    def _configure(self):
        """
        Queries the hardware to determine its configuration and configures the drivers accordingly.
        """
        self._mode = self.mode
        self.spectral_analysis._mode = self.mode
        self.phase_noise._mode = self.mode
        option = self._read("*OPT?", dummy_data="'550").split(",")[0][1:]
        option_dict = {'503': 3.7e9,
                       '504': 3.88e9,
                       '506': 6.08e9,
                       '507': 7.1e9,
                       '508': 8.5e9,
                       '513': 13.8e9,
                       '526': 27.0e9,
                       '532': 32.5e9,
                       '543': 43.0e9,
                       '544': 44.5e9,
                       '550': 51e9}

        freq_option = option_dict[option]
        self.CAPABILITY['frequency'] = freq_option
        self.spectral_analysis.CAPABILITY['frequency'] = freq_option
        self.phase_noise.CAPABILITY['frequency'] = freq_option

    def options(self):
        """
        Discovers what options are installed
        :rtype: float
        """
        option = self._read("*OPT?").split(",")[0]
        print(option)
        option_dict = {'503': 3.7e9,
                       '504': 3.88e9,
                       '506': 6.08e9,
                       '507': 7.1e9,
                       '508': 8.5e9,
                       '513': 13.8e9,
                       '526': 27.0e9,
                       '532': 32.5e9,
                       '543': 43.0e9,
                       '544': 44.5e9,
                       '550': 51e9}
        print('testing')
        print(option_dict[option])
        return option_dict[option]

    def get_phase_noise_rj(self, reset, center_freq, start_freq, stop_freq, y_reference_level, averages):
        """
        Configures and Measures Phase Noise RJ (ps rms)

        :param reset: Resets Spectrum Analyzer to factory defaults ('ENABLED' or 'DISABLED')
        :type reset: str
        :param center_freq: Carrier frequency (Hz)
        :type center_freq: float
        :param start_freq: Phase Noise Analysis Starting freq (Hz)
        :type start_freq: float
        :param stop_freq: Phase Noise Analysis stopping freq (Hz)
        :type stop_freq: float
        :param y_reference_level: Phase Noise Y-axis reference level (varies)
        :type y_reference_level: float
        :param averages: Number of Phase Noise measurement averages
        :type averages: int
        :return: Phase Noise RJ (ps rms)
        :rtype: float
        """

        if reset == 'ENABLE':
            self.reset()
            sleep(0.5)
        self.mode = 'PNOISE'
        self.phase_noise.log_plot()
        self.phase_noise.log_plot_method = 'Phase Noise'
        sleep(0.5)
        self.phase_noise.freq_center = center_freq
        self.phase_noise.signal_tracking = 'DISABLE'
        self.phase_noise.freq_start = start_freq
        self.phase_noise.freq_stop = stop_freq
        self.phase_noise.y_reference = y_reference_level
        self.phase_noise.averaging_count = averages
        self.run_sweep()
        sleep(2)
        sleep((float(self.phase_noise.averaging_count)*1.5)+1)
        self.phase_noise.marker_function = 'RMSNoise'
        sleep(0.5)
        self.phase_noise.rmsnoise_mode = 'JITTER'
        sleep(0.5)
        self.phase_noise.marker_bandwidth_left = self.phase_noise.freq_start
        self.phase_noise.marker_bandwidth_right = self.phase_noise.freq_stop
        return self.phase_noise.marker_y * 1e12

    def run_sweep(self):
        """
        Runs Sweep
        """
        self._write(':INIT:CONT OFF')

    def alignment_status(self):
        """
        Returns the state of the spectrum analyzer's calibration

        :value: - 'EXPIRED'
                - 'GOOD'
        :type: str
        """
        input_dict = {'1': 'EXPIRED', '0': 'GOOD'}
        return input_dict[self._read(':CAL:EXP?')]

    def align_now(self):
        """
        Runs the alignment calibration immediately
        """
        self.logger.info('Please wait 1 minute for alignment...')
        # self._configure_interface()
        # self._write(':CAL:ALL')
        self._interface.write(':CAL:ALL')
        sleep(60)

        if self._read(':STAT:QUES:CAL:COND?') == '0':
            self.logger.info('Alignment complete')
            return
        else:
            self.logger.info('ALIGNMENT FAILED!')

    @property
    def auto_align(self):
        """
        Configure background auto alignment mode

        :value: - 'OFF'
                - 'PARTial'
                - 'ON'
        :type: str
        """
        return self._read(':CAL:AUTO?')

    @auto_align.setter
    def auto_align(self, value):
        """
        :type: str
        """
        self._write(":CAL:AUTO {0}".format(value))

    @property
    def auto_align_interval(self):
        """
        Configure when the alignment alert is sent

        :value: - 'TTEMP'
                - 'DAY'
                - 'WEEK'
                - 'NONE
        :type: str
        """
        return self._read(':CAL:AUTO:ALERt?')

    @auto_align_interval.setter
    def auto_align_interval(self, value):
        """
        :type: str
        """
        value_check = ('TTEMP', 'DAY', 'WEEK', 'NONE')
        if value.upper() in value_check:
            self._write(":CAL:AUTO:ALERt {0}".format(value.upper()))
        else:
            raise ValueError('VALUE parameter must be one of the following... \n{0}'.format(value_check))

    @property
    def continuous_sweep(self):
        """
        ENABLE/DISABLE continuous sweeping

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read('INIT:CONT?')]

    @continuous_sweep.setter
    def continuous_sweep(self, value):
        """
        :type: str
        """
        output_dict = {'ENABLE': '1', 'DISABLE': '0'}
        self._write(':INIT:CONT {0}'.format(output_dict[value.upper()]))

    @property
    def mode(self):
        """
        Set operating mode for spectrum analyzer

        :value: - 'SA'
                - 'PNOISE'
        :type: str
        """
        return self._read(":INST:SELect?")

    @mode.setter
    def mode(self, value):
        """
        :type value: str
        """
        self._write(":INST:SELect {0};".format(value))
        self._mode = value
        self.spectral_analysis._mode = value
        self.phase_noise._mode = value


class AgilentN9030SpectralAnalysis(BaseSpectrumAnalyzerSpectralAnalysis):
    """
    AgilentN9030 spectrum analyzer Spectral Analysis class
    """

    CAPABILITY = {'frequency': 0}

    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._marker_number = 1  # TODO: Add additional dynamic markers
        self._mode = None

    def _checkmode(self):
        """
        Checks if the current mode and the object type are the same.
        """
        if self._mode == 'DUMMY_DATA':
            return
        if self._mode != 'SA':
            raise TypeError("Cannot utilize Spectrum Analysis class when in {0} mode".format(self._mode))

    def marker_max_peak_search(self):
        """
        Sets marker to align with the tallest peak
        """
        self._checkmode()
        self._write(':CALC:MARK{0}:MAX'.format(self._marker_number))

    def marker_next_max_peak_search(self, direction):
        """
        Sets marker to align with the next tallest peak in specified direction

        :param direction: 'LEFT' or 'RIGHT' or 'NEXT'
        :type direction:  str
        """
        self._checkmode()
        self._write(':CALC:MARK{0}:MAX:{1}'.format(self._marker_number, direction))

    @property
    def averaging(self):
        """
        ENABLE/DISABLE averaging

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        return self._read(':TRAC:TYPE?')

    @averaging.setter
    def averaging(self, value):
        """
        :type: str
        """
        if value == 'ENABLE':
            self._write(':TRAC:TYPE AVER')
        elif value == 'DISABLE':
            self._write(':TRAC:TYPE WRIT')
        else:
            raise ValueError('Please input a correct value')

    @property
    def averaging_count(self):
        """
        Set number of averages

        :value: defines number of averages to take
        :type: int
        """
        self._checkmode()
        return int(self._read(':AVER:COUN?'))

    @averaging_count.setter
    def averaging_count(self, value):
        """
        :type value: int
        """
        self._checkmode()
        self._write(':AVER:COUN {0};'.format(value))

    def average_clear(self):
        """
        Clears averages
        """
        self._write(':AVER:CLEAR')

    @property
    def bandwidth_resolution(self):
        """
        Set bandwidth resolution

        :value: Bandwidth, Hz
        :type: float
        """
        self._checkmode()
        output_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        if output_dict[self._read(':SENS:BAND:RES:AUTO?')] == 'ENABLE':
            self.logger.info('{0} is currently in automatic bandwidth resolution mode')
        return float(self._read(':SENS:BAND:RES?'))

    @bandwidth_resolution.setter
    def bandwidth_resolution(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if isinstance(value, str):
            if value == 'AUTO':
                self._write(':SENS:BAND:RES:AUTO ON')
                return
        if value < self.CAPABILITY['frequency']:
            self._write(':SENS:BAND:RES:AUTO OFF')
            self._write(':SENS:BAND:RES {0};'.format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'
                             .format(self.name, self.CAPABILITY['frequency'] / 1e9))

    @property
    def freq_center(self):
        """
        Set center(carrier) frequency

        :value: frequency in Hz
        :type: float
        """
        self._checkmode()

        return float(self._read(":SENS:FREQ:CENT?"))

    @freq_center.setter
    def freq_center(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self._write(":SENS:FREQ:CENT {0};".format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def freq_span(self):
        """
        Set frequency span

        :value: frequency in Hz
        :type: float
        """
        self._checkmode()
        return float(self._read(":SENS:FREQ:SPAN?"))

    @freq_span.setter
    def freq_span(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self._write(":SENS:FREQ:SPAN {0};".format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def freq_start(self):
        """
        Start frequency

        :value: frequency in Hz
        :type: float
        """
        self._checkmode()
        return float(self._read(':SENS:FREQ:STARt?'))

    @freq_start.setter
    def freq_start(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self._write(':SENSe:FREQ:STARt {0};'.format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def freq_stop(self):
        """
        Stop frequency

        :value: frequency in Hz
        :type: float
        """
        self._checkmode()
        return float(self._read(':SENS:FREQ:STOP?'))

    @freq_stop.setter
    def freq_stop(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self._write(':SENS:FREQ:STOP {0};'.format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def marker(self):
        """
        Enable/Disable specific markers (1-12)

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        self._checkmode()
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read(':CALC:MARK{0}:STAT?'.format(self._marker_number))]

    @marker.setter
    def marker(self, value):
        """
        :type value: str
        """
        self._checkmode()
        output_dict = {'ENABLE': 1, 'DISABLE': 0}
        self._write(':CALC:MARK{0}:STATE {1}'.format(self._marker_number, output_dict[value]))

    @property
    def marker_peak_threshold(self):
        """
        Marker Peak Threshold

        :value: dbm
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:MARK:PEAK:THReshold?'))

    @marker_peak_threshold.setter
    def marker_peak_threshold(self, value):
        """
        :type value: float
        """
        self._checkmode()
        self._write(':CALC:MARK:PEAK:THReshold {0}'.format(value))

    @property
    def marker_x(self):
        """
        Marker X position

        :value: freq or time
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:MARK{0}:X?'.format(self._marker_number)))

    @marker_x.setter
    def marker_x(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self._write(':CALC:MARK{0}:X {1}'.format(self._marker_number, value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def marker_y(self):
        """
        *READONLY*
        Marker Y position

        :value: dbm
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:MARK{0}:Y?'.format(self._marker_number)))

    @property
    def y_scale(self):
        """
        Set Y scale

        :value: db
        :type: float
        """
        return float(self._read(':DISP:WIND1:TRAC:Y:PDIV?'))

    @y_scale.setter
    def y_scale(self, value):
        """
        :type value: float
        """
        self._write(':DISP:WIND1:TRAC:Y:PDIV {0}'.format(value))

    @property
    def y_scale_type(self):
        """
        Set Y scale type

        :value: - 'LOG'
                - 'LIN'
        :type: str
        """
        self._checkmode()
        return self._read('DISP:WIND1:TRAC:Y:SCAL:SPAC?')

    @y_scale_type.setter
    def y_scale_type(self, value):
        """
        :type value: float
        """
        self._checkmode()
        self._write('DISP:WIND1:TRAC:Y:SCAL:SPAC {0}'.format(value))


class AgilentN9030PhaseNoise(BaseSpectrumAnalyzerPhaseNoise):
    """
    AgilentN9030 spectrum analyzer phase noise class
    """

    CAPABILITY = {'frequency': 0}

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
        self._marker_number = 1  # TODO: Add additional dynamic markers
        self._mode = None

    def _checkmode(self):
        """
        Checks if the current mode and the object type are the same.
        """
        if self._mode == 'DUMMY_DATA':
            return
        if self._mode != 'PNOISE':
            raise TypeError("Cannot utilize Phase Noise class when in {0} mode".format(self._mode))

    def log_plot(self):
        """
        Set log plot
        """
        self._checkmode()
        self._write(":CONF:LPLOT")

    @property
    def average_count(self):
        """
        Set number of averages

        :value: defines number of averages to take
        :type: int
        """
        self._checkmode()
        return int(self._read(':SENS:LPL:AVER:COUN?'))

    @average_count.setter
    def average_count(self, value):
        """
        :type value: int
        """
        self._checkmode()
        if value == 0:
            self._write(':SENS:LPL:AVER:STAT OFF;')
            self._write(':SENS:LPL:AVER:COUN 1;')
        else:
            self._write(':SENS:LPL:AVER:STAT ON;')
            self._write(':SENS:LPL:AVER:COUN {0};'.format(value))

    @property
    def bandwidth_auto_resolution(self):
        """
        Enable/Disable automatic bandwidth resolution

        :value: - ENABLE
                - DISABLE
        :type: str
        """
        self._checkmode()
        output_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return output_dict[self._read(':MON:BAND:RES:AUTO?')]

    @bandwidth_auto_resolution.setter
    def bandwidth_auto_resolution(self, value):
        """
        :type value: str
        """
        self._checkmode()
        input_dict = {'ENABLE': 1, 'DISABLE': 0}
        self._write(':MON:BAND:RES:AUTO {0};'.format(input_dict[value]))

    @property
    def bandwidth_resolution(self):
        """
        Set bandwidth resolution

        :value: Bandwidth, Hz
        :type: float
        """
        self._checkmode()
        return float(self._read(':MON:BAND:RES?'))

    @bandwidth_resolution.setter
    def bandwidth_resolution(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self.bandwidth_auto_resolution = 'DISABLE'
            self._write(':MON:BAND:RES {0};'.format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def bandwidth_auto_video(self):
        """
        ENABLE/DISABLE video analyzer post-detection filter automatic bandwidth

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read(':MON:BAND:VID:AUTO?')]

    @bandwidth_auto_video.setter
    def bandwidth_auto_video(self, value):
        """
        :type value: str
        """
        output_dict = {'ENABLE': 1, "DISABLE": 0}
        self._write(':MON:BAND:VID:AUTO {0};'.format(output_dict[value]))

    @property
    def bandwidth_video(self):
        """
        Set video analyzer post-detection filter bandwidth

        :value: Bandwidth, Hz
        :type: float
        """
        return float(self._read(':MON:BAND:VID?'))

    @bandwidth_video.setter
    def bandwidth_video(self, value):
        """
        :type value: float
        """
        if value < self.CAPABILITY['frequency']:
            self.bandwidth_auto_video = 'DISABLE'
            self._write(':MON:BAND:VID {0};'.format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def freq_center(self):
        """
        Set center(carrier) frequency

        :value: frequency in Hz
        :type: float
        """
        self._checkmode()

        return float(self._read(":SENS:FREQ:CENT?"))

    @freq_center.setter
    def freq_center(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self._write(":SENS:FREQ:CENT {0};".format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def freq_start(self):
        """
        Start frequency

        :value: frequency in Hz
        :type: float
        """
        self._checkmode()
        return float(self._read(':SENS:LPL:FREQ:OFFS:STAR?'))

    @freq_start.setter
    def freq_start(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self._write(':SENS:LPL:FREQ:OFFS:STAR {0};'.format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def freq_stop(self):
        """
        Stop frequency

        :value: frequency in Hz
        :type: float
        """
        self._checkmode()
        return float(self._read(':SENS:LPL:FREQ:OFFS:STOP?'))

    @freq_stop.setter
    def freq_stop(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if value < self.CAPABILITY['frequency']:
            self._write(':SENS:LPL:FREQ:OFFS:STOP {0}'.format(value))
        else:
            raise ValueError('{0} only supports frequencies of up to {1}GHz'.format(self.name,
                                                                                    self.CAPABILITY['frequency']/1e9))

    @property
    def log_plot_method(self):
        """
        Set log plot method

        :value: - 'Noise Floor'
                - 'Phase Noise'
        :type: str
        """
        self._checkmode()
        output_dict = {'DANL': 'Noise Floor', 'PN': 'Phase Noise'}
        return output_dict[self._read(':SENS:LPL:METH?')]

    @log_plot_method.setter
    def log_plot_method(self, value):
        """
        :type value: str
        """
        self._checkmode()
        input_dict = {'Noise Floor': 'DANL', 'Phase Noise': 'PN'}
        self._write(':SENS:LPL:METH {0};'.format(input_dict[value]))

    @property
    def marker(self):
        """
        Configure marker mode

        :value: - 'POSITION'
                - 'DELTA'
                - 'OFF
        :type: str
        """
        self._checkmode()
        input_dict = {'POS': 'POSITION', 'DELT': 'DELTA', 'OFF': 'OFF'}
        return input_dict[self._read(':CALC:LPL:MARK{0}:MODE?'.format(self._marker_number))]

    @marker.setter
    def marker(self, value):
        """
        :type value: str
        """
        self._checkmode()
        if value == 'POSITION' or 'DELTA' or 'OFF':
            self._write(':CALC:LPL:MARK{0}:MODE {1}'.format(self._marker_number, value))
        else:
            raise ValueError("Please enter a valid marker mode. See docstring")

    @property
    def marker_bandwidth_left(self):
        """
        Sets the left edge freq/time for the band of the selected marker (right edge unaffected)
        NOTE: This changes the marker bandwidth span value

        :value: frequency or time
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:LPL:MARK{0}:BAND:LEFT?'.format(self._marker_number)))

    @marker_bandwidth_left.setter
    def marker_bandwidth_left(self, value):
        """
        :type value: float
        """
        self._checkmode()
        self._write(':CALC:LPL:MARK{0}:BAND:LEFT {1}'.format(self._marker_number, value))

    @property
    def marker_bandwidth_right(self):
        """
        Sets the right edge freq/time for the band of the selected marker (left edge unaffected)
        NOTE: This changes the marker bandwidth span value

        :value: frequency or time
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:LPL:MARK{0}:BAND:RIGHT?;'.format(self._marker_number)))

    @marker_bandwidth_right.setter
    def marker_bandwidth_right(self, value):
        """
        :type value: float
        """
        self._checkmode()
        self._write(':CALC:LPL:MARK{0}:BAND:RIGHT {1};'.format(self._marker_number, value))

    @property
    def marker_bandwidth_span(self):
        """
        Sets the span of the selected marker. Will alter left and right bands

        :value: frequency or time
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:LPL:MARK{0}:BAND:SPAN?;'.format(self._marker_number)))

    @marker_bandwidth_span.setter
    def marker_bandwidth_span(self, value):
        """
        :type value: float
        """
        self._checkmode()
        self._write(':CALC:LPL:MARK{0}:BAND:SPAN {1};'.format(self._marker_number, value))

    @property
    def marker_function(self):
        """
        Set marker function

        :value: - 'RMSNoise'
                - 'RFM'
                - 'AVERAGE'
                - 'OFF'
        :type: str
        """
        self._checkmode()
        input_dict = {'RMSN': 'RMSNoise', 'RFM': 'RFM', 'AVER': 'AVERAGE', 'OFF': 'OFF'}
        return input_dict[self._read(':CALC:LPL:MARK{0}:FUNC?'.format(self._marker_number))]

    @marker_function.setter
    def marker_function(self, value):
        """
        :type value: str
        """
        self._checkmode()
        self._write(':CALC:LPL:MARK{0}:FUNC {1}'.format(self._marker_number, value.upper()))

    @property
    def signal_tracking(self):
        """
        Enable signal tracking

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        self._checkmode()
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read(':SENS:FREQ:CARR:TRACK?')]

    @signal_tracking.setter
    def signal_tracking(self, value):
        """
        :type value: str
        """
        self._checkmode()
        input_dict = {'ENABLE': 1, 'DISABLE': 0}
        self._write(':SENS:FREQ:CARR:TRACK {0};'.format(input_dict[value]))

    @property
    def marker_y(self):
        """
        **READONLY**
        Returns value of Y for selected marker from log plot

        :value: dB
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:LPL:MARK{0}:Y?'.format(self._marker_number)))

    @property
    def rmsnoise_mode(self):
        """
        Set RMSNoise marker mode

        :value: - 'DEGREE'
                - 'RADIAN'
                - 'JITTER'
                - 'DBC'
        :type: str
        """
        self._checkmode()
        input_dict = {'DEGR': "DEGREE", "RAD": "RADIAN", "JITT": "JITTER", "DBC": 'DBC'}
        return input_dict[self._read(':CALC:LPL:MARK{0}:RMSNoise:MODE?'.format(self._marker_number))]

    @rmsnoise_mode.setter
    def rmsnoise_mode(self, value):
        """
        :type value: str
        """
        self._checkmode()
        self._write(':CALC:LPL:MARK{0}:RMSNoise:MODE {1};'.format(self._marker_number, value))

    @property
    def y_reference(self):
        """
        Set Y Reference Marker

        :value: reference level in dB
        :type: str
        """
        self._checkmode()
        return float(self._read(':DISP:LPL:VIEW:WIND:TRACe:Y:RLEV?'))

    @y_reference.setter
    def y_reference(self, value):
        """
        :type value: float
        """
        self._checkmode()
        self._write(':DISP:LPL:VIEW:WIND:TRACe:Y:RLEV {0};'.format(value))

    @property
    def y_scale(self):
        """
        Set Y scale

        :value: db
        :type: float
        """
        return float(self._read(':DISP:MON:VIEW1:WIND1:TRAC:Y:PDIV?'))

    @y_scale.setter
    def y_scale(self, value):
        """
        :type: float
        """
        self._write(':DISP:MON:VIEW1:WIND1:TRAC:Y:PDIV {0}'.format(value))
