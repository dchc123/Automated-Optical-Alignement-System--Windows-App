"""
| $Revision:: 281933                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-08-28 15:50:46 +0100 (Tue, 28 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

The base_bert module partitions a BERT driver into 4 functional classes: BERT, BERT_Jitter,
BERT_ED, and BERT_PPG

- The BERT is the overall container class that holds the rest of the functional classes
- The BERT_Jitter is the class responsible for all the BERT's jitter functionality
- The BERT_ED is the class responsible for all the BERT's error detection functionality
- The BERT_PPG is the class responsible for all the BERT's pattern generation functionality
"""
from CLI.Equipment.Base.base_equipment import BaseEquipment
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseBERT(BaseEquipment):
    """
    All BERT drivers are derived from this abstract class. It contains all base method
    prototypes that must be implemented.
    The BERT is the overall container class that holds the rest of the functional classes. It
    should be limited to functionality that globally applies or affects the more specialized
    classes it contains.
    """
    def __init__(self, address, interface, dummy_mode, **kwargs):
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

    @property
    def clock_frequency(self):
        """
        BERT clock frequency. This is the preferred property for setting a clock
        frequency. Even if the actual commands are sent to a PPG or jitter module, they'll be
        masked by this generic method.

        :value: desired clock frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @clock_frequency.setter
    def clock_frequency(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def global_output(self):
        """
        Enable state of the global data and clock output. This is a single global setting that
        supersedes all output states of specialized classes such as
        :py:attr:`Equipment.base_bert.BaseBERTPatternGenerator.data_output`

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @global_output.setter
    def global_output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def reference_clock_source(self):
        """
        Reference clock source to internal or external

        :value: - 'INTERNAL'
                - 'EXTERNAL'
        :type: str
        """
        raise NotImplementedError

    @reference_clock_source.setter
    def reference_clock_source(self, value):
        """
        :type value: str
        """
        raise NotImplementedError


class BaseBERTJitter(BaseEquipmentBlock):
    """
    Base jitter channel class that all jitter module channels should be derived from.
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

    @property
    def global_output(self):
        """
        Enable state of the global jitter output. When this setting is toggled to enable,
        only previously enabled jitter types are re-enabled. Note that both the global_output and
        the specific jitter output must be enabled for any jitter to be outputted.

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @global_output.setter
    def global_output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def external_jitter_output(self):
        """
        Enable state of external jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @external_jitter_output.setter
    def external_jitter_output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError


class BaseBERTBlockBUJitter(BaseEquipmentBlock):
    """
    This container class groups Bounded Uncorrelated Jitter functionality
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

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float 
        """
        raise NotImplementedError

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def bit_rate(self):
        """
        :value: PRBS bit-rate in b/s
        :type: int
        """
        raise NotImplementedError

    @bit_rate.setter
    def bit_rate(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def lpf(self):
        """
        :value: low-pass filter frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @lpf.setter
    def lpf(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def output(self):
        """
        Enable state of BU jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def prbs(self):
        """
        :value: the polynomial of the PRBS pattern
        :type: int 
        """
        raise NotImplementedError

    @prbs.setter
    def prbs(self, value):
        """
        :type value: int
        """
        raise NotImplementedError


class BaseBERTBlockPJitter(BaseEquipmentBlock):
    """
    This container class groups Periodic Jitter functionality
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

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float
        """
        raise NotImplementedError

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def frequency(self):
        """
        :value: jitter frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @frequency.setter
    def frequency(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def output(self):
        """
        Enable state of P jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def type(self):
        """
        Periodic jitter type

        :value: - 'SQUARE'
                - 'TRIANGLE'
        :type: str
        """
        raise NotImplementedError

    @type.setter
    def type(self, value):
        """
        :type value: str
        """
        raise NotImplementedError


class BaseBERTBlockSSCJitter(BaseEquipmentBlock):
    """
    This container class groups SSC Jitter functionality
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

    @property
    def frequency(self):
        """
        :value: modulation frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @frequency.setter
    def frequency(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def output(self):
        """
        Enable state of SSC jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def type(self):
        """
        SSC jitter type

        :value: - 'CENTER'
                - 'DOWN'
                - 'UP'
        :type: str
        """
        raise NotImplementedError

    @type.setter
    def type(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def deviation(self):
        """
        :value: SSC frequency deviation in ppm
        :type: int
        """
        raise NotImplementedError

    @deviation.setter
    def deviation(self, value):
        """
        :type value: int
        """
        raise NotImplementedError


class BaseBERTBlockRJitter(BaseEquipmentBlock):
    """
    This container class groups Random Jitter functionality
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

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float 
        """
        raise NotImplementedError

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def hpf(self):
        """
        :value: high-pass filter frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @hpf.setter
    def hpf(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def lpf(self):
        """
        :value: low-pass filter frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @lpf.setter
    def lpf(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def output(self):
        """
        Enable state of R jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError


class BaseBERTBlockSJitter(BaseEquipmentBlock):
    """
    This container class groups S Jitter functionality
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

    @property
    def amplitude(self):
        """
        :value: jitter amplitude in UI
        :type: float 
        """
        raise NotImplementedError

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def frequency(self):
        """
        :value: jitter frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @frequency.setter
    def frequency(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def output(self):
        """
        Enable state of S jitter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError


class BaseBERTErrorDetector(BaseEquipmentBlock):
    """
    Base BERT Error Detector channel class that all ED channels should be derived from
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

    @property
    def align_auto(self):
        """
        Control auto adjust

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @align_auto.setter
    def align_auto(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        raise NotImplementedError

    @property
    def align_threshold_ber(self):
        """
        BER eye contour that the error detector will use for auto alignment

        :value: BER alignment threshold
        :type: float
        """

        raise NotImplementedError

    @align_threshold_ber.setter
    def align_threshold_ber(self, value):
        """
        :type value: float
        """

        raise NotImplementedError

    @property
    def bit_count(self):
        """
        **READONLY**

        :value: accumulated bit count of current or last measurement
        :type: int
        """
        raise NotImplementedError

    @property
    def cdr_loop_bandwidth(self):
        """
        :value: CDR's loop bandwidth frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @cdr_loop_bandwidth.setter
    def cdr_loop_bandwidth(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def cdr_target_frequency(self):
        """
        :value: CDR's target frequency in Hz
        :type: int
        """
        raise NotImplementedError

    @cdr_target_frequency.setter
    def cdr_target_frequency(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def clock_delay(self):
        """
        Clock delay. To maximize compatibility with different BERTs, the recommended
        delay range is [-6.7, 6.7] ns

        TODO: support for delay in UI

        :value: clock delay in s
        :type: float
        """
        raise NotImplementedError

    @clock_delay.setter
    def clock_delay(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def clock_loss(self):
        """
        **READONLY**

        :value: clock loss count for current or last measurement
        :type: int
        """
        raise NotImplementedError

    @property
    def clock_source(self):
        """
        Clock recovery source

        :value: - 'EXTERNAL'
                - 'RECOVERED'
        :type: str
        """
        raise NotImplementedError

    @clock_source.setter
    def clock_source(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def elapsed_time(self):
        """
        **READONLY**

        :value: elapsed time for current or last measurement
        :type: int
        """
        raise NotImplementedError

    @property
    def error_count(self):
        """
        **READONLY**

        :value: error count of current or last measurement
        :type: int
        """
        raise NotImplementedError

    @property
    def error_rate(self):
        """
        **READONLY**

        :value: error rate of current or last measurement
        :type: float
        """
        raise NotImplementedError

    @property
    def gating_period(self):
        """
        Gating period for fixed accumulation time

        :value: measurement period in s
        :type: int
        """
        raise NotImplementedError

    @gating_period.setter
    def gating_period(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def input_mode(self):
        """
        input data mode

        :value: - 'DIFFERENTIAL'
                - 'SINGLE_POSITIVE'
                - 'SINGLE_NEGATIVE'
        :type: str
        """
        raise NotImplementedError

    @input_mode.setter
    def input_mode(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def input_threshold(self):
        """
        Input threshold voltage (in Volts). To maximize compatibility with
        different BERTs, the recommended voltage range is [-0.25, 0.25] V.

        :value: threshold in V
        :type: float
        """
        raise NotImplementedError

    @input_threshold.setter
    def input_threshold(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def pattern(self):
        """
        Desired PRBS or user pattern

        :value: - 'PRBS7'
                - 'PRBS9'
                - 'PRBS10'
                - 'PRBS11'
                - 'PRBS15'
                - 'PRBS20'
                - 'PRBS23'
                - 'PRBS31'
                - Hex string i.e. 'H02948ACFE'
                - Bin string i.e. 'B010101100'
                - <file_path>
        :type: str
        """
        raise NotImplementedError

    @pattern.setter
    def pattern(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def polarity(self):
        """
        Data output polarity

        :value: - 'NORMAL'
                - 'INVERTED'
        :type: str
        """
        raise NotImplementedError

    @polarity.setter
    def polarity(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def sync_loss(self):
        """
        **READONLY**

        :value: sync loss count for current or last measurement
        :type: int
        """
        raise NotImplementedError

    @property
    def sync_status(self):
        """
        **READONLY** State of pattern sync

        :value: - 'IN_SYNC'
                - 'LOSS_OF_SYNC'
        :type: str
        """
        raise NotImplementedError

    @property
    def sync_loss_threshold(self):
        """
        BER at which sync loss is indicated

        :value: BER alignment threshold
        :type: float
        """

        raise NotImplementedError

    @sync_loss_threshold.setter
    def sync_loss_threshold(self, value):
        """
        :type value: float
        """

        raise NotImplementedError

    @property
    def track_ppg(self):
        """
        Option to track PPG settings such as bit-rate, polarity, pattern

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @track_ppg.setter
    def track_ppg(self, value):
        """
        :type value:
        """
        raise NotImplementedError

    def align_single(self, timeout=30):
        """
        Tells the BERT to acquire inbound data, align, and open eye to maximum on this
        channel.

        :param timeout: timeout value for the auto align in s
        :type timeout: int
        """
        raise NotImplementedError

    def start_measurement(self):
        """
        Starts a BER measurement
        """
        raise NotImplementedError

    def stop_measurement(self):
        """
        Stops a BER measurement
        """
        raise NotImplementedError


class BaseBERTPatternGenerator(BaseEquipmentBlock):
    """
    Base BERT Pulse Pattern Generator channel class that all PPG channels should be derived from
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

    @property
    def amplitude(self):
        """
        Data amplitude after external attenuation

        :value: data amplitude in V
        :type: float
        """
        raise NotImplementedError

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def amplitude_mode(self):
        """
        Data amplitude mode

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
        :type: str
        """
        raise NotImplementedError

    @amplitude_mode.setter
    def amplitude_mode(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def clock_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @clock_output.setter
    def clock_output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def clock_source_rate(self):
        """
        Clock recovery source rate

        :value: - 'HALF'
                - 'FULL'
        :type: str
        """
        raise NotImplementedError

    @clock_source_rate.setter
    def clock_source_rate(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def data_output(self):
        """
        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @data_output.setter
    def data_output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def deemphasis(self):
        """
        :value: data de-emphasis in dB
        :type: int
        """
        raise NotImplementedError

    @deemphasis.setter
    def deemphasis(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def deemphasis_mode(self):
        """
        Data de-emphasis mode

        :value: - 'PRE'
                - 'POST'
        :type: str
        """
        raise NotImplementedError

    @deemphasis_mode.setter
    def deemphasis_mode(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def external_attenuation(self):
        """
        External attenuation value. It is used to calculate amplitude post attenuation

        :value: external attenuation in dB. Value is the "loss", so negative values
                interpreted as amplification.
        :type: int
        """
        raise NotImplementedError

    @external_attenuation.setter
    def external_attenuation(self, value):
        """
        :type value: int
        """
        raise NotImplementedError

    @property
    def offset(self):
        """
        :value: DC offset in V
        :type: float
        """
        raise NotImplementedError

    @offset.setter
    def offset(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def output(self):
        """
        Control both clock and data output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def pattern(self):
        """
        Desired PRBS or user pattern

        :value: - 'PRBS7'
                - 'PRBS9'
                - 'PRBS10'
                - 'PRBS11'
                - 'PRBS15'
                - 'PRBS20'
                - 'PRBS23'
                - 'PRBS31'
                - Hex string i.e. 'H02948ACFE'
                - Bin string i.e. 'B010101100'
                - <file_path>
        :type: str
        """
        raise NotImplementedError

    @pattern.setter
    def pattern(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def polarity(self):
        """
        Data output polarity

        :value: - 'NORMAL'
                - 'INVERTED'
        :type: str
        """
        raise NotImplementedError

    @polarity.setter
    def polarity(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def termination_mode(self):
        """
        Data termination mode

        :value: - 'AC'
                - 'DC'
        :type: str
        """
        raise NotImplementedError

    @termination_mode.setter
    def termination_mode(self, value):
        """
        :type value: str
        """
        raise NotImplementedError
