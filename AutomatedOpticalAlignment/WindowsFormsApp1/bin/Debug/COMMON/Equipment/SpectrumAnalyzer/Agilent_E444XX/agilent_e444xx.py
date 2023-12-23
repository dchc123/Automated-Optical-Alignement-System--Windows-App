"""
| $Revision:: 284258                                   $:  Revision of last commit
| $Author:: lagapie@SEMNET.DOM                         $:  Author of last commit
| $Date:: 2018-11-28 20:54:15 +0000 (Wed, 28 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.AgilentN9030A`

::
    >>> from CLI.Equipment.SpectrumAnalyzer.Agilent_E444XX.agilent_e444xx import AgilentE444XX
    >>> specA = AgilentE444XX('TCPIP0::10.14.2.199::inst0::INSTR')
    >>> specA.connect()

    >>> specA.mode = 'PNOISE'
    >>> specA.get_phase_noise_rj('ENABLE', 12.89e9, 100e6, 20e9, -20, 5)

For Spectal Analysis block level API:
:py:class:`.AgilentE444XXSpectralAnalysis`

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
    >>> specA.phase_noise.freq_stop = 2e9
"""

from CLI.Equipment.SpectrumAnalyzer.base_spectrum_analyzer import BaseSpectrumAnalyzer
from CLI.Equipment.SpectrumAnalyzer.base_spectrum_analyzer import BaseSpectrumAnalyzerSpectralAnalysis
from CLI.Equipment.SpectrumAnalyzer.base_spectrum_analyzer import BaseSpectrumAnalyzerPhaseNoise
from CLI.Utilities.custom_exceptions import NotSupportedError
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from time import sleep


class AgilentE444XX(BaseSpectrumAnalyzer):
    """
    AgilentE444XX spectrum analyzer
    """

    CAPABILITY = {'frequency': None}

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
        self.spectral_analysis = AgilentE444XXSpectralAnalysis(interface=interface, dummy_mode=dummy_mode)
        self.phase_noise = AgilentE444XXPhaseNoise(interface=interface, dummy_mode=dummy_mode)
        self._mode = None
        # Temporary disabling STB to get the model number even if there are errors
        self.stb_error_mask = 0x00

    def _configure(self):
        """
        Queries the hardware to determine its configuration and configures the drivers accordingly.
        """
        self._write('*RST')
        self._mode = self.mode
        self.spectral_analysis._mode = self._mode
        self.phase_noise._mode = self._mode
        self._model_capability()
        self.continuous_sweep = "Disable"
        # Enabling STB
        self.stb_error_mask = 0x04


    def _model_capability(self):
        """
        Discovers the model and upgrade capabilities
        :rtype: float
        """
        model_0a = {"frequency": 26.5e9,
                    "max_freq_range": 27e9,
                    }
        model_6a = {"frequency": 44e9,
                    "max_freq_range": 44.5e9,
                    }
        option_dict = {'E4440A': model_0a,
                       'E4446A': model_6a}
        option = self._read("*IDN?", dummy_data="'E4440A").split(",")[1].strip()
        if option not in option_dict:
            raise ValueError("%s : Model is not covered !" % option)

        self.CAPABILITY['frequency'] = option_dict[option]['frequency']
        self.spectral_analysis.CAPABILITY['frequency'] = option_dict[option]['frequency']
        self.phase_noise.CAPABILITY['frequency'] = option_dict[option]['frequency']
        self.spectral_analysis.CAPABILITY['center_freq']['max'] = option_dict[option]['max_freq_range']
        self.phase_noise.CAPABILITY['center_freq']['max'] = option_dict[option]['max_freq_range']

    # todo: errors the instrument I have shows error when I try to run this even when STP is disbled;
    # ['+622,"External reference missing or out of range"',
    #  '+101,"Frequency Reference Unlock"',
    #  '+10560,"Carrier Not Present.  Verify frequency and amplitude settings."

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
        return self.phase_noise.marker_y * 1e12

    def run_sweep(self):
        """
        Runs Sweep
        """
        if self.continuous_sweep == 'ENABLE':
            self.continuous_sweep = "Enable"
        else:
            self._write(':INIT:IMM')

    def alignment_status(self):
        """
        Returns the state of the spectrum analyzer's calibration

        :value: - 'EXPIRED'
                - 'GOOD'
        :type: str
        """
        cal_status = 'EXPIRED'
        # enable the calibration report since the user can change it
        self._write(":STATus:QUEStionable:CALibration:EXTended:FAILure:ENABle 32767")
        if self._read(':STATus:QUEStionable:CALibration:EXTended:FAILure?') == "+0":
            cal_status = 'GOOD'
        return cal_status

    def align_now(self):
        """
        Runs the alignment calibration immediately
        """
        self.logger.info('Please wait 1 minute for alignment...')
        # self._configure_interface()
        # self._write(':CAL:ALL')
        self._interface.write(':CAL:ALL')
        sleep(60)
        if self._read(":STAT:QUES:CAL:COND?") == '+0':
            self.logger.info('Alignment complete')
            return
        else:
            self.logger.info('ALIGNMENT FAILED!')

    @property
    def auto_align(self):
        """
        Configure background auto alignment mode.

        :value: - 'OFF' - same as Alert
                - 'ALERT' - every 24 H or 3 C temp. change -> Alert
                - 'ON' - every 15 min or 1.5 C temp. change -> RF Aligns
        :type: str
        """
        return self._read(':CAL:AUTO?')

    @auto_align.setter
    def auto_align(self, value):
        """
        :type: str
        """
        value_check = ('OFF', 'ON', 'ALERT')
        if value.upper() not in value_check:
            raise ValueError('VALUE parameter must be one of: \n{0}'.format(value_check))
        self._write(":CAL:AUTO {0}".format(value))

    @property
    def continuous_sweep(self):
        """
        ENABLE/DISABLE continuous sweeping

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read(':INIT:CONT?')]

    @continuous_sweep.setter
    def continuous_sweep(self, value):
        """
        :type: str
        """
        output_dict = {'ENABLE': '1', 'DISABLE': '0'}
        if value.upper() not in output_dict:
            raise ValueError('VALUE parameter must be one of the following... \n{0}'.format(output_dict))
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
        value_check = ('SA', 'PNOISE')
        val = value.upper()
        if val not in value_check:
            raise ValueError('VALUE parameter must be one of the following... \n{0}'.format(value_check))
        self._write(":INST:SELect {0};".format(value))
        self._mode = val
        self.spectral_analysis._mode = val
        self.phase_noise._mode = val


class AgilentE444XXSpectralAnalysis(BaseSpectrumAnalyzerSpectralAnalysis):
    """
    AgilentE444XX spectrum analyzer Spectral Analysis class
    """

    CAPABILITY = {'frequency': 0,
                  'average_range': {'min': 1, 'max': 8192},
                  'peak_excursion': {'min': 0, 'max': 100},
                  'center_freq': {'min': -100e6, 'max': None}
                  }

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
        self._marker_number = 1  # TODO: Add additional dynamic markers up to 4 markers
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
        NOTE: If no valid peak is found, an error “No Peak Found” is displayed. Press ESC to clear this
        message before attempting another search.

        :param direction: 'LEFT' or 'RIGHT' or 'NEXT'
        :type direction:  str
        """
        self._checkmode()
        value_check = ('LEFT', 'RIGHT', 'NEXT')
        if direction.upper() not in value_check:
            raise ValueError('VALUE parameter must be one of the following... \n{0}'.format(value_check))
        self._write(':CALC:MARK{0}:MAX:{1}'.format(self._marker_number, direction))

    @property
    def averaging(self):
        """
        ENABLE/DISABLE averaging

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        value_check = {'1': 'ENABLE', '0': 'DISABLE'}
        return value_check[self._read(':AVERage:STATe?')]

    @averaging.setter
    def averaging(self, value):
        """
        :type: str
        """

        value_check = {'ENABLE': '1', 'DISABLE': '0'}
        # for differences with N9030 see notes on N9060-90027.pdf pag.984
        if value.upper() in value_check:
            self._write(":AVERage:STATe %s" % value_check[value.upper()])
        else:
            raise ValueError('VALUE parameter must be one of the following... \n{0}'.format(value_check))


    @property
    def averaging_count(self):
        """
        Set number of traces used for average.

        :value: defines number of averages to take
        :type: int
        """
        self._checkmode()
        return int(self._read(':AVER:COUNt?'))

    @averaging_count.setter
    def averaging_count(self, value):
        """
        :type value: int
        """
        self._checkmode()
        range_min = self.CAPABILITY['average_range']['min']
        range_max = self.CAPABILITY['average_range']['max']
        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid Averaging range. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        self._write(':AVER:COUNt {0};'.format(value))

    def average_clear(self):
        """
        Clears averages
        """
        self._write(':AVER:CLEAR')

    @property
    def bandwidth_resolution(self):
        """
        Set bandwidth resolution.
        Values are from 1Hz to 3MHz and 4, 5, 6, 8MHz. Invalid value will be fitted to the closest one.

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
        self._check_freq_limits(value)
        self._write(":SENS:FREQ:CENT {0};".format(value))

    @property
    def freq_span(self):
        """
        Set frequency span. Max Span may be limited by center Frequency setting.

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
        if 0 <= value <= self.CAPABILITY['frequency']:
            self._write(":SENS:FREQ:SPAN {0};".format(value))
        else:
            raise ValueError('{0} only supports frequencies from 0 to {1}GHz'.format(self.name,
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
        range_min = self.CAPABILITY['center_freq']['min']
        range_max = self.CAPABILITY['center_freq']['max']
        if not (range_min <= value < range_max):
            raise ValueError("%s is an invalid Frequency. Supported range is:"
                             "(min:%s|max:%s)" % (value, range_min, range_max -1))
        self._write(':SENSe:FREQ:STARt {0};'.format(value))

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
        self._check_freq_limits(value)
        self._write(':SENS:FREQ:STOP {0};'.format(value))

    @property
    def marker(self):
        """
        Enable/Disable specific markers (1-4)

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
        if value.upper() not in output_dict:
            raise ValueError("%s is an invalid choice. Use one of: %s ."
                                 % (value, list(output_dict.keys())))
        self._write(':CALC:MARK{0}:STATE {1}'.format(self._marker_number, output_dict[value.upper()]))

    @property
    def marker_mode(self):
        """
        Allow the marker control menu. Apply to the currently selected marker(1-4)

        :value: - 'Normal'
                - 'Delta'
                - 'Delta Pair'
                - 'Span Pair'
                - 'Off'
        :type: str
        """
        self._checkmode()
        input_dict = {'POS': 'NORMAL',
                      'DELT': 'DELTA',
                      'BAND': 'DELTA PAIR',
                      'SPAN': 'SPAN PAIR',
                      'OFF': 'OFF'}
        return input_dict[self._read(':CALC:MARK{0}:MODE?'.format(self._marker_number))]

    @marker_mode.setter
    def marker_mode(self, value):
        """
        :type value: str
        """
        self._checkmode()
        output_dict = {'NORMAL': 'POS',
                       'DELTA': 'DELTA',
                       'DELTA PAIR': 'BAND',
                       'SPAN PAIR': 'SPAN',
                       'OFF': 'OFF'}
        if value.upper() not in output_dict:
            raise ValueError("%s is an invalid Marker mode. Use one of: %s ."
                             % (value, list(output_dict.keys())))
        else:
            self._write(':CALC:MARK{0}:MODE {1}'.format(self._marker_number, output_dict[value.upper()]))

    @property
    def marker_peak_threshold(self):
        """
        Marker Peak Threshold.
        Minimal signal level to qualify as Marker Peak. Signal should rise then fall by <Peak Excursion> to qualify.

        :value: dbm
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:MARK{0}:PEAK:THReshold?' .format(self._marker_number)))

    @marker_peak_threshold.setter
    def marker_peak_threshold(self, value):
        """
        :type value: float
        """
        self._checkmode()
        self._write(':CALC:MARK{0}:PEAK:THReshold {1}'.format(self._marker_number, value))

    @property
    def marker_peak_excursion(self):
        """
        Marker Peak Excursion.
        Minimal amplitude variation of signal that the marker can identify as separate peak.

        :value: dbm
        :type: float
        """
        self._checkmode()
        return float(self._read(':CALC:MARK:PEAK{0}:EXCursion?'.format(self._marker_number)))

    @marker_peak_excursion.setter
    def marker_peak_excursion(self, value):
        """
        :type value: float
        """
        self._checkmode()
        range_min = self.CAPABILITY['peak_excursion']['min']
        range_max = self.CAPABILITY['peak_excursion']['max']
        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid Peak Excursion setting. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        else:
            self._write(':CALC:MARK{0}:PEAK:EXCursion {1}'.format(self._marker_number, value))

    @property
    def marker_x(self):
        """
        Marker X position

        :value: freq or time
        :type: float
        """
        self._checkmode()
        if self.marker == 'DISABLE':
            raise ValueError('Marker {0} is DISABLED !' .format(self._marker_number))
        else:
            return float(self._read(':CALC:MARK{0}:X?'.format(self._marker_number)))

    @marker_x.setter
    def marker_x(self, value):
        """
        :type value: float
        """
        self._checkmode()
        if self.marker == 'DISABLE':
            raise ValueError('Marker {0} is DISABLED !' .format(self._marker_number))

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
        if self.marker == 'DISABLE':
            raise ValueError('Marker {0} is DISABLED !' .format(self._marker_number))
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
        :type value: str
        """
        self._checkmode()
        output_dict = {'LIN', 'LOG'}
        if value.upper() not in output_dict:
            raise ValueError("%s is an invalid Type of Vertical Scale. Use one of: %s ."
                             % (value, output_dict))
        self._write('DISP:WIND1:TRAC:Y:SCAL:SPAC {0}'.format(value))

    def _check_freq_limits(self,value):
        range_min = self.CAPABILITY['center_freq']['min']
        range_max = self.CAPABILITY['center_freq']['max']
        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid Frequency. Supported range is:"
                             "(min:%s|max:%s)" % (value, range_min, range_max))


class AgilentE444XXPhaseNoise(BaseSpectrumAnalyzerPhaseNoise):
    """
    AgilentE444XX spectrum analyzer phase noise class
    """

    CAPABILITY = {'frequency': 0,
                  'average_count': {'min': 0, 'max': 1000},
                  'center_freq': {'min': -100e6, 'max': None},
                  }

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
        Configure instrument in log plot mode.
        """
        self._checkmode()
        self._write(":CONF:LPLOT")

    @property
    def average_count(self):
        """
        Set number of averages.
        Setting it to 0 will switch the averaging to OFF.

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
        range_min = self.CAPABILITY['average_count']['min']
        range_max = self.CAPABILITY['average_count']['max']
        if not (range_min <= value <= range_max):
            raise ValueError("%s is an invalid Peak Excursion setting. See supported range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))

        if value == 0:
            self._write(':SENS:LPL:AVER:COUN 1')
            self._write(':SENS:LPL:AVER:STAT OFF;')
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
        self.validate_entry(value, input_dict)
        self._write(':MON:BAND:RES:AUTO {0}'.format(input_dict[value.upper()]))

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
        if value <= self.CAPABILITY['frequency']:
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
        self.validate_entry(value, output_dict)
        self._write(':MON:BAND:VID:AUTO {0};'.format(output_dict[value.upper()]))

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
    '''
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
        range_min = self.CAPABILITY['center_freq']['min']
        range_max = self.CAPABILITY['center_freq']['max']
        if not (range_min <= value < range_max):
            raise ValueError("%s is an invalid Center Frequency, Supported range is:"
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        self._write(":SENS:FREQ:CENT {0};".format(value))

    '''
    @property
    def freq_start(self):
        """
        Start frequency. Dependent on Stop freq.

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
        range_min = 3
        range_max = self.freq_stop
        if not (range_min < value < range_max):
            raise ValueError("%s Start Frequency should be smaller than Stop Frequency, Supported range is:"
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        self._write(':SENS:LPL:FREQ:OFFS:STAR {0}'.format(value))

    @property
    def freq_stop(self):
        """
        Stop frequency. Depend on Start Freq.

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
        range_min = self.freq_start
        range_max = self.CAPABILITY['frequency']
        if not (range_min < value <= range_max ):
            raise ValueError("%s is an invalid Stop Frequency, Supported range is:"
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        self._write(':SENS:LPL:FREQ:OFFS:STOP {0}'.format(value))

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
        input_dict = {'NOISE FLOOR': 'DANL', 'PHASE NOISE': 'PN'}
        self.validate_entry(value, input_dict)
        self._write(':SENS:LPL:METH {0};'.format(input_dict[value.upper()]))

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
        # in N9030 this is broken into 3 commands - marker, marker_function, rms noise_mode
        input_dict = {'POS': 'POSITION', 'DELT': 'DELTA', 'RMSD': 'RMS DEGREES',
                      'RMSR': 'RMS RADIANS', 'RFM': 'RMS RESIDUAL FM', 'RMSJ': 'RMS JITTER', 'OFF': 'OFF'}
        return input_dict[self._read(':CALC:LPL:MARK{0}:MODE?'.format(self._marker_number))]

    @marker.setter
    def marker(self, value):
        """
        :type value: str
        """
        self._checkmode()
        input_dict = {'POSITION': 'POS', 'DELTA': 'DELTA', 'OFF': 'OFF'}
        #            Original list input_dict = {'POSITION': 'POS', 'DELTA': 'DELTA', 'RMS DEGREES': 'RMSD',
        #                       'RMS RADIANS': 'RMSR', 'RMS RESIDUAL FM': 'RFM', 'RMS JITTER': 'RMSJ', 'OFF': 'OFF'}
        self.validate_entry(value, input_dict)
        self._write(':CALC:LPL:MARK{0}:MODE {1}'.format(self._marker_number, input_dict[value.upper()]))

    @property
    def marker_bandwidth_left(self):
        """
        Sets the left edge freq/time - NOT SUPPORTED
        """
        raise NotSupportedError

    @marker_bandwidth_left.setter
    def marker_bandwidth_left(self, value):
        """
        Sets the left edge freq/time - NOT SUPPORTED
        """
        raise NotSupportedError

    @property
    def marker_bandwidth_right(self):
        """
        Sets the right edge freq/time - NOT SUPPORTED
        """
        raise NotSupportedError

    @marker_bandwidth_right.setter
    def marker_bandwidth_right(self, value):
        """
        Sets the right edge freq/time - NOT SUPPORTED
        """
        raise NotSupportedError

    @property
    def marker_bandwidth_span(self):
        """
        Sets the bandwith span - NOT SUPPORTED
        """
        raise NotSupportedError

    @marker_bandwidth_span.setter
    def marker_bandwidth_span(self, value):
        """
        Sets the bandwith span - NOT SUPPORTED
        """
        raise NotSupportedError

    @property
    def marker_function(self):
        """
        Set marker function

        :value: - 'RMS DEGREES'
                - 'RMS RADIANS'
                - 'RMS RESIDUAL FM'
                - 'RMS JITTER'
                - 'AVERAGE - Not supported'
                - 'OFF'
        :type: str
        """
        self._checkmode()
        # in N9030 this is broken into 3 commands - marker, marker_function, rms noise_mode
        input_dict = {'POS': 'POSITION', 'DELT': 'DELTA', 'RMSD': 'RMS DEGREES',
                      'RMSR': 'RMS RADIANS', 'RFM': 'RMS RESIDUAL FM', 'RMSJ': 'RMS JITTER', 'OFF': 'OFF'}
        return input_dict[self._read(':CALC:LPL:MARK{0}:MODE?'.format(self._marker_number))]

    @marker_function.setter
    def marker_function(self, value):
        """
        :type value: str
        """
        self._checkmode()
        #            Original list input_dict = {'POSITION': 'POS', 'DELTA': 'DELTA', 'RMS DEGREES': 'RMSD',
        #                       'RMS RADIANS': 'RMSR', 'RMS RESIDUAL FM': 'RFM', 'RMS JITTER': 'RMSJ', 'OFF': 'OFF'}
        input_dict = {'RMS DEGREES': 'RMSD', 'RMS RADIANS': 'RMSR', 'RMS RESIDUAL FM': 'RFM',
                      'RMS JITTER': 'RMSJ', 'OFF': 'OFF'}
        if value.upper() == "AVERAGE":
            raise NotSupportedError
        self.validate_entry(value, input_dict)
        self._write(':CALC:LPL:MARK{0}:MODE {1}'.format(self._marker_number, value.upper()))

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
        self.validate_entry(value, input_dict)
        self._write(':SENS:FREQ:CARR:TRACK {0};'.format(input_dict[value.upper()]))

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
        Set marker function

        :value: - 'RMS DEGREES'
                - 'RMS RADIANS'
                - 'RMS RESIDUAL FM'
                - 'RMS JITTER'
                - 'DBC -Not Supported

        :type: str
        """
        self._checkmode()
        # in N9030 this is broken into 3 commands - marker, marker_function, rms noise_mode
        input_dict = {'POS': 'POSITION', 'DELT': 'DELTA', 'RMSD': 'RMS DEGREES',
                      'RMSR': 'RMS RADIANS', 'RFM': 'RMS RESIDUAL FM', 'RMSJ': 'RMS JITTER', 'OFF': 'OFF'}
        return input_dict[self._read(':CALC:LPL:MARK{0}:MODE?'.format(self._marker_number))]

    @rmsnoise_mode.setter
    def rmsnoise_mode(self, value):
        """
        :type value: str
        """
        self._checkmode()
        if value.upper() == "DBC":
            raise NotSupportedError
        input_dict = {'RMS DEGREES': 'RMSD', 'RMS RADIANS': 'RMSR', 'RMS RESIDUAL FM': 'RFM',
                      'RMS JITTER': 'RMSJ'}
        self.validate_entry(value, input_dict)
        self._write(':CALC:LPL:MARK{0}:MODE {1}'.format(self._marker_number, value.upper()))

    @property
    def y_reference(self):
        """
        Set Y Reference Marker

        :value: reference level in dB
        :type: str
        """
        self._checkmode()
        return float(self._read(':DISP:MONITOR:WIND:TRACe:Y:RLEV?'))

    @y_reference.setter
    def y_reference(self, value):
        """
        :type value: float
        """
        self._checkmode()
        self._write(':DISP:MONITOR:WIND:TRACe:Y:RLEV {0};'.format(value))

    @property
    def y_scale(self):
        """
        Set Y scale

        :value: db
        :type: float
        """
        return float(self._read(':DISP:MON:WIND:TRAC:Y:PDIV?'))

    @y_scale.setter
    def y_scale(self, value):
        """
        :type: float
        """
        self._write(':DISP:MON:WIND:TRAC:Y:PDIV {0}'.format(value))

    def validate_entry(self, value, dic):
        """
        Validate user entry.

        :param value:
        :type value:
        :param dic:
        :type dic
        """
        if value.upper() not in dic:
            raise ValueError("%s is an invalid setting. The choices are: %s" % (value, list(dic.keys())))

