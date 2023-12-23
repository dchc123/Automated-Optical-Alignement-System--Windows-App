"""
| $Revision:: 282546                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-09-24 21:38:23 +0100 (Mon, 24 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.Base.base_equipment import BaseEquipment
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseSpectrumAnalyzer(BaseEquipment):
    """
    Base Spectrum Analyzer class that all Spectrum Analyzer should be derived from.
    """
    def __init__(self, address, interface, dummy_mode=False, **kwargs):
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
        self._mode = None

    def _configure(self):
        """
        Queries the hardware to determine its configuration and configures the drivers accordingly.
        """
        raise NotImplementedError

    @property
    def mode(self):
        """
        Set operating mode for spectrum analyzer

        :value: - 'SA'
                - 'PNOISE'
        :type: str
        """
        raise NotImplementedError

    @mode.setter
    def mode(self, value):
        """
        :type value: str
        """
        raise NotImplementedError


class BaseSpectrumAnalyzerSpectralAnalysis(BaseEquipmentBlock):
    """
    Base Spectrum Analyzer Spectral Analysis class
    """
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
        self._mode = None

    def _checkmode(self):
        """
        Checks if the current mode and the object type are the same.
        """
        raise NotImplementedError

    def average_clear(self):
        """
        Clears averages
        """
        raise NotImplementedError

    def marker_max_peak_search(self):
        """
        Sets marker to align with the tallest peak
        """
        raise NotImplementedError

    def marker_next_max_peak_search(self, direction):
        """
        Sets marker to align with the next tallest peak in specified direction

        :param direction: 'LEFT' or 'RIGHT' or 'NEXT'
        :type direction:  str
        """
        raise NotImplementedError

    @property
    def averaging_count(self):
        """
        Set number of averages

        :value: defines number of averages to take
        :type: int
        """
        raise NotImplementedError

    @averaging_count.setter
    def averaging_count(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def freq_center(self):
        """
        Set center(carrier) frequency

        :value: frequency in Hz
        :type: float
        """
        raise NotImplementedError

    @freq_center.setter
    def freq_center(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def freq_span(self):
        """
        Set frequency span

        :value: frequency in Hz
        :type: float
        """
        raise NotImplementedError

    @freq_span.setter
    def freq_span(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def freq_start(self):
        """
        Start frequency

        :value: frequency in Hz
        :type: float
        """
        raise NotImplementedError

    @freq_start.setter
    def freq_start(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def freq_stop(self):
        """
        Stop frequency

        :value: frequency in Hz
        :type: float
        """
        raise NotImplementedError

    @freq_stop.setter
    def freq_stop(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def marker(self):
        """
        Enable/Disable specific markers

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        raise NotImplementedError

    @marker.setter
    def marker(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def marker_peak_threshold(self):
        """
        Marker Peak Threshold

        :value: Maximum threshold value of y-axis (varies)
        :type: float
        """
        raise NotImplementedError

    @marker_peak_threshold.setter
    def marker_peak_threshold(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def marker_x(self):
        """
        Sets marker in specified X position

        :value: freq or time
        :type: float
        """
        raise NotImplementedError

    @marker_x.setter
    def marker_x(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def marker_y(self):
        """
        Sets marker in specified Y position

        :value: dbm
        :type: float
        """
        raise NotImplementedError

    @marker_y.setter
    def marker_y(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def y_scale_type(self):
        """
        Set Y scale type

        :value: - 'LOG'
                - 'LIN'
        :type: str
        """
        raise NotImplementedError

    @y_scale_type.setter
    def y_scale_type(self, value):
        """
        :type value: float
        """
        raise NotImplementedError


class BaseSpectrumAnalyzerPhaseNoise(BaseEquipmentBlock):
    """
    Base Spectrum Analyzer Phase Noise Class
    """
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
        self._mode = None

    def _checkmode(self):
        """
        Checks if the current mode and the object type are the same.
        """
        raise NotImplementedError

    def log_plot(self):
        """
        Set log plot
        """
        raise NotImplementedError

    @property
    def average_count(self):
        """
        Set number of averages

        :value: defines number of averages to take
        :type: int
        """
        raise NotImplementedError

    @average_count.setter
    def average_count(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def bandwidth_auto_resolution(self):
        """
        Enable/Disable automatic bandwidth resolution

        :value: - ENABLE
                - DISABLE
        :type: str
        """
        raise NotImplementedError

    @bandwidth_auto_resolution.setter
    def bandwidth_auto_resolution(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def bandwidth_resolution(self):
        """
        Set bandwidth resolution

        :value: Bandwidth, Hz
        :type: float
        """
        raise NotImplementedError

    @bandwidth_resolution.setter
    def bandwidth_resolution(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def bandwidth_auto_video(self):
        """
        ENABLE/DISABLE video analyzer post-detection filter automatic bandwidth

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        raise NotImplementedError

    @bandwidth_auto_video.setter
    def bandwidth_auto_video(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def bandwidth_video(self):
        """
        Set video analyzer post-detection filter bandwidth

        :value: Bandwidth, Hz
        :type: float
        """
        raise NotImplementedError

    @bandwidth_video.setter
    def bandwidth_video(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def freq_start(self):
        """
        Start frequency

        :value: frequency in Hz
        :type: float
        """
        raise NotImplementedError

    @freq_start.setter
    def freq_start(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def freq_stop(self):
        """
        Stop frequency

        :value: frequency in Hz
        :type: float
        """
        raise NotImplementedError

    @freq_stop.setter
    def freq_stop(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def log_plot_method(self):
        """
        Set log plot method

        :value: - 'Noise Floor'
                - 'Phase Noise'
        :type: str
        """
        raise NotImplementedError

    @log_plot_method.setter
    def log_plot_method(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def marker(self):
        """
        Configure marker mode

        :value: - 'POSITION'
                - 'DELTA'
                - 'OFF
        :type: str
        """
        raise NotImplementedError

    @marker.setter
    def marker(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def marker_bandwidth_left(self):
        """
        Sets the left edge freq/time for the band of the selected marker (right edge unaffected)
        NOTE: This changes the marker bandwidth span value

        :value: frequency or time
        :type: float
        """
        raise NotImplementedError

    @marker_bandwidth_left.setter
    def marker_bandwidth_left(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def marker_bandwidth_right(self):
        """
        Sets the right edge freq/time for the band of the selected marker (left edge unaffected)
        NOTE: This changes the marker bandwidth span value

        :value: frequency or time
        :type: float
        """
        raise NotImplementedError

    @marker_bandwidth_right.setter
    def marker_bandwidth_right(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def marker_bandwidth_span(self):
        """
        Sets the span of the selected marker. Will alter left and right bands

        :value: frequency or time
        :type: float
        """
        raise NotImplementedError

    @marker_bandwidth_span.setter
    def marker_bandwidth_span(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

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
        raise NotImplementedError

    @marker_function.setter
    def marker_function(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def signal_tracking(self):
        """
        Enable signal tracking

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        raise NotImplementedError

    @signal_tracking.setter
    def signal_tracking(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def marker_y(self):
        """
        **READONLY**
        Returns value of Y for selected marker from log plot

        :value: dB
        :type: float
        """
        raise NotImplementedError

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
        raise NotImplementedError

    @rmsnoise_mode.setter
    def rmsnoise_mode(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def y_reference(self):
        """
        Set Y Reference Marker

        :value: reference level in dB
        :type: str
        """
        raise NotImplementedError

    @y_reference.setter
    def y_reference(self, value):
        """
        :type value: float
        """
        raise NotImplementedError
