"""
| $Revision:: 284259                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-11-28 20:56:08 +0000 (Wed, 28 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
import re
import time
from math import ceil
from CLI.Utilities.custom_exceptions import NotSupportedError
from CLI.Equipment.BERT.base_bert import BaseBERTErrorDetector
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock


class KeysightM80XXXED(BaseBERTErrorDetector):
    """
    Keysight BERT Error Detector channel class that all ED channels should be derived from
    """
    def __init__(self, module_id, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

        self._prbs_poly_xml_string =r'<sequenceDefinition ' \
                                    r'xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
                                    r'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                                    r'xmlns="http://www.agilent.com/schemas/M8000/DataSequence">' \
                                    r'<description />' \
                                    r'<sequence>' \
                                    r'<syncAndLoopBlock length="1024">' \
                                    r'<prbs polynomial="2^31-1" />' \
                                    r'</syncAndLoopBlock>' \
                                    r'</sequence>' \
                                    r'</sequenceDefinition>'
        self._module_id = module_id
        self._channel_number = channel_number
        self._pattern = None

        self._identifier = "'M{0}.DataIn'".format(self._module_id)

        self.sijt_measurement = KeysightSIJTMeasurementBlock(module_id=module_id, interface=interface,
                                                             dummy_mode=dummy_mode)
        self.ber_measurement = KeysightBERMeasurementBlock(module_id=module_id, interface=interface,
                                                           dummy_mode=dummy_mode)

    def align_all(self):
        """
        ***RUN ONLY***

        Runs alignment on both decision threshold voltage and sample delay from the received data

        :return: - 'SUCCESS'
                  - 'FAILED'
                  - 'INPROGRESS'
                  - 'ABORTED'
                  - 'UNKNOWN'
        :rtype: str
        """

        self._read(':INP:ALIG:EYE:AUTO {0};*OPC?'.format(self._identifier))
        return self._read(':INP:ALIG:STAT:VAL? {0}'.format(self._identifier))

    def align_threshold(self):
        """
        ***RUN ONLY***

        Runs decision threshold voltage alignment from the received data

        :return: - 'SUCCESS'
                  - 'FAILED'
                  - 'INPROGRESS'
                  - 'ABORTED'
                  - 'UNKNOWN'
        :rtype: str
        """

        self._write(':INP:ALIG:EYE:ACEN {0};*OPC?'.format(self._identifier))
        return self._read(':INP:ALIG:STAT:VAL? {0}'.format(self._identifier))

    def align_phase(self):
        """
        ***RUN ONLY***

        Runs sample delay alignment from the received data


        :return: - 'SUCCESS'
                  - 'FAILED'
                  - 'INPROGRESS'
                  - 'ABORTED'
                  - 'UNKNOWN'
        :rtype: str
        """

        self._write(':INP:ALIG:EYE:TCEN {0};*OPC?'.format(self._identifier))
        return self._read(':INP:ALIG:STAT:VAL? {0}'.format(self._identifier))

    @property
    def align_threshold_ber(self):
        """
        BER eye contour that the error detector will use for auto alignment

        :value: BER alignment threshold
        :type: float
        """
        return float(self._read(":INPUT:ALIGNMENT:EYE:THRESHOLD? {0}".format(self._identifier)))

    @align_threshold_ber.setter
    def align_threshold_ber(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            if 1e-9 <= value <= 1e-1:
                self._write(":INPUT:ALIGNMENT:EYE:THRESHOLD {0},{1}".format(self._identifier, value))
            else:
                raise ValueError("Value must be within 1e-1 and 1e-9")
        else:
            raise TypeError("Value must be a float")

    def align_threshold_result_nrz(self):
        """
        Returns the result from the last NRZ threshold alignment that was run

        :value: BER alignment threshold result
        :type: float
        """
        return float(self._read(':INP:ALIG:EYE:RES:NRZ:THR? {0}'.format(self._identifier)))

    def align_threshold_result_pam(self, eye=None):
        """
        Returns the result from the last PAM threshold alignment that was run

        :value: BER alignment threshold result
        :type: float
        """
        if not eye:
            raise ValueError('Eye parameter is required and must be a value of 1, 2, or 3')
        eye = int(eye)
        if eye in [1, 2, 3]:
            return float(self._read(':INP:ALIG:EYE:RES:PAM4:THR{0}? {1}'.format(eye, self._identifier)))
        else:
            raise ValueError('Eye parameter must be a value of 1, 2, or 3')

    def align_phase_result(self):
        """
        Returns the result from the last phase alignment that was run

        :value: BER alignment threshold result
        :type: float
        """
        return float(self._read(':INP:ALIG:EYE:RES:DEL? {0}'.format(self._identifier)))

    @property
    def cdr_loop_bandwidth(self):
        """
        :value: CDR's loop bandwidth frequency in Hz
        :type: int
        """
        raise NotSupportedError('KeysightM8046AChannel does not support cdr_loop_bandwidth settings')

    @cdr_loop_bandwidth.setter
    def cdr_loop_bandwidth(self, value):
        """
        :type value: int
        """
        raise NotSupportedError('KeysightM8046AChannel does not support cdr_loop_bandwidth settings')

    @property
    def cdr_target_frequency(self):
        """
        :value: CDR's target frequency in Hz
        :type: int
        """
        raise NotSupportedError('KeysightM8046AChannel does not support cdr_loop_bandwidth settings')

    @cdr_target_frequency.setter
    def cdr_target_frequency(self, value):
        """
        :type value: int
        """
        raise NotSupportedError('KeysightM8046AChannel does not support cdr_loop_bandwidth settings')

    @property
    def clock_delay(self):
        """
        Clock delay

        :value: clock delay in s
        :type: float
        :raise ValueError: exception if delay is not between -6.7e-9s and 6.7e-9s
        """
        return float(self._read(":INPut:DELay? 'M{}.DataIn'".format(self._module_id)))

    @clock_delay.setter
    def clock_delay(self, value):
        """
        :type value: float
        :raise ValueError: exception if delay is not between -6.7ns and 6.7ns
        """
        if -6.7e-9 < value < 6.7e-9:
            self._write(":INPut:DELay 'M{}.DataIn', {}".format(self._module_id, value))
        else:
            raise ValueError("Clock delay out of acceptable range [-6.7, 6.7] ns")

    @property
    def clock_loss(self):
        """
        **READONLY**

        :value: clock loss count for current or last measurement
        :type: int
        """
        output_dict = {'1': 'CLK_LOSS', '0': 'CLK_IN_SYNC'}
        return output_dict[self._read(":STATus:INSTrument:CLOSs? 'M{}.DataIn'".format(self._module_id), dummy_data='1')]

    @property
    def clock_source(self):
        """
        Clock recovery source

        :value: - 'EXTERNAL'
                - 'RECOVERED'
        :type: str
        :raise ValueError: exception if source is not 'EXTERNAL' or 'RECOVERED'
        """
        output_dict = {'CLK': 'EXTERNAL', 'SYS': 'RECOVERED'}
        return output_dict[self._read(":CLOCk:SOURce? 'M{}.DataIn'".format(self._module_id), dummy_data='CLK')]

    @clock_source.setter
    def clock_source(self, value):
        """
        :type value: str
        :raise ValueError: exception if source is not 'EXTERNAL' or 'RECOVERED'
        """
        value = value.upper()
        input_dict = {'EXTERNAL': 'CLK', 'RECOVERED': 'SYS'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'EXTERNAL' or 'RECOVERED'")
        else:
            self._write(":CLOCk:SOURce 'M{}.DataIn', {}".format(self._module_id, input_dict[value]))

    def error_rate(self, line_coding='NRZ'):
        """
        Returns 'instantaneous' error rate (front panel indicator value)

        :param line_coding: - 'PAM4'
                            - 'NRZ'
        :type line_coding: str
        :rvalue: error rate values
        :rtype: dict
        """

        instant_ber = self._read(':FETCh:IBERate? "M{}.DataIn"'.format(self._module_id)).strip('()').split(',')

        rvalue = {'BER': float(instant_ber[2])}
        if line_coding == 'PAM4':
            rvalue.update( {'SER': float(instant_ber[3]),
                            'SER0': float(instant_ber[4]),
                            'SER1': float(instant_ber[5]),
                            'SER2': float(instant_ber[6]),
                            'SER3': float(instant_ber[7])})
        return rvalue

    @property
    def input_delay(self):
        """
        **READONLY**

        Gets the delay detected at the last alignment run.

        :type: float
        """
        return float(self._read(":INPut:ALIGnment:EYE:RESult:DELay? 'M{}.DataIn'".format(self._module_id)))

    @property
    def input_mode(self):
        """
        input data mode

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
                - 'NORMAL'
                - 'COMPLEMENT'
                - SENormal|SEComplement|DIFFerential|SINGleended>
        :type: str
        :raise ValueError: exception if mode is not "DIFFERENTIAL", "SINGLE", "NORMAL", "COMPLEMENT"
        """
        output_dict = {'SING': 'SINGLE', 'DIFF': 'DIFFERENTIAL', 'NORMAL': 'SENormal', 'COMPLEMENT': 'SEComplement'}
        return output_dict[self._read(":INPut:CMODe? 'M{}.DataIn'".format(self._module_id), dummy_data='SING')]

    @input_mode.setter
    def input_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode is not "DIFFERENTIAL", "SINGLE", "NORMAL", "COMPLEMENT"
        """
        value = value.upper()
        input_dict = {'SINGLE': 'SING', 'DIFFERENTIAL': 'DIFF', 'SENORMAL': 'NORMAL', 'SECOMPLEMENT': 'COMPLEMENT'}
        if value not in input_dict.keys():
            raise ValueError("Please specify 'SINGLE', 'DIFFERENTIAL', 'SENORMAL', 'SECOMPLEMENT'")
        else:
            self._write(":INPut:CMODe 'M{}.DataIn', {}".format(self._module_id, input_dict[value]))

    @property
    def input_threshold(self):
        """
        Input threshold voltage (in Volts). To maximize compatibility with
        different BERTs, the recommended voltage range is [-0.25, 0.25] V.

        :value: threshold in V
        :type: float
        :raise ValueError: exception if threshold is not between -0.25V and 0.25V
        """
        return float(self._read(":INPut:THReshold? 'M{}.DataIn'".format(self._module_id)))

    @input_threshold.setter
    def input_threshold(self, value):
        """
        :type value: float
        :raise ValueError: exception if threshold is not between -0.25V and 0.25V
        """
        if value < -0.25 or value > 0.25:
            raise ValueError("Threshold out of range [-0.25, 0.25] V")
        else:
            self._write(":INPut:THReshold 'M{}.DataIn',{} V".format(self._module_id, value))

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
        :type: str or list
        :raise ValueError: exception if option is not binary, hex, PRBS or a list input for saved patterns
        """
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        """
        :type value: str or list
        :raise ValueError: exception if option is not binary, hex, PRBS or a list input for saved patterns
        """
        self._pattern = value
        if value[0] == 'P':
            self.prbs_pattern = value
        elif value[0] == "H" or value[0] == 'B':
            self.user_pattern = value
        else:
            if isinstance(value, list):
                self.saved_pattern = value
            else:
                raise ValueError("Please specify either 'PRBSX', 'BXXXXXXX', 'HXXXXXXX'. If you are loading"
                                 "a saved pattern, please pass a list [file_path, pattern_length]")

    @property
    def polarity(self):
        """
        Data input polarity

        :value: - 'NORMAL'
                - 'INVERTED'
        :type: str
        :raise ValueError: exception if polarity is not 'NORMAL' or 'INVERTED'
        """
        output_dict = {'NORM': 'NORMAL', 'INV': 'INVERTED',
                       'INVerted': 'INVERTED', 'NORMal': 'NORMAL'}
        return output_dict[self._read(":INPut:POLarity? 'M{}.DataIn'".format(self._module_id), dummy_data='NORM')]

    @polarity.setter
    def polarity(self, value):
        """
        :type value: str
        :raise ValueError: exception if polarity is not 'NORMAL' or 'INVERTED'
        """
        value = value.upper()
        input_dict = {'NORMAL': 'NORMal', 'INVERTED': 'INVerted'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'NORMAL' or 'INVERTED'")
        else:
            self._write(":INPut:POLarity 'M{}.DataIn', {}".format(self._module_id, input_dict[value]))

    @property
    def prbs_pattern(self):
        """
        Desired PRBS pattern

        :value: - 'PRBS7'
                - 'PRBS9'
                - 'PRBS10'
                - 'PRBS11'
                - 'PRBS15'
                - 'PRBS20'
                - 'PRBS23'
                - 'PRBS31'
        :type: str
        :raise ValueError: exception if passed value does not start with 'P'
        """
        return self._pattern

    @prbs_pattern.setter
    def prbs_pattern(self, value):
        """
        :type value: str
        :raise ValueError: exception if passed value does not start with 'P'
        """
        if value[0] != 'P':
            raise ValueError("Please specify 'PRBSX'")
        pattern = value[4:]  # strip "PRBS" off of pattern string
        xml_command_string = re.sub(r'prbs polynomial="2\^31-1"', r'prbs polynomial="2^{}-1"'.format(pattern),
                                    self._prbs_poly_xml_string)

        xml_command_string = '#3%d' % len(xml_command_string) + xml_command_string

        self._write(':DATA:SEQuence:VALue "Analyzer",{}'.format(xml_command_string))
        self._pattern = value

    @property
    def saved_pattern(self):
        """
        Desired saved pattern

        :value: [file_path, length]
        :type: list
        :raise ValueError: exception if passed value is not a list
        """
        return self._pattern

    @saved_pattern.setter
    def saved_pattern(self, value):
        """
        :type value: list
        :raise ValueError: exception if passed value is not a list
        """
        if not isinstance(value, list):
            raise ValueError('Please enter [pattern path, pattern length] as a list')

        xlm_string_analyzer = r'<?xml version="1.0" encoding="utf-16"?>' \
                              r'<sequenceDefinition ' \
                              r'xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
                              r'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                              r'xmlns="http://www.agilent.com/schemas/M8000/DataSequence">' \
                              r'<version>1.0.0</version><description />' \
                              r'<sequence>' \
                              r'<syncAndLoopBlock length="%d">' \
                              r'<pattern source="%s"/>' \
                              r'</syncAndLoopBlock>' \
                              r'</sequence>' \
                              r'</sequenceDefinition>' % (value[1], value[0])

        xlm_cmd_string_analyzer = '#3%d' % len(xlm_string_analyzer) + xlm_string_analyzer
        self._write(':DATA:SEQuence:VALue "Analyzer",{}'.format(xlm_cmd_string_analyzer))
        self._pattern = value

    @property
    def signal_type(self):
        """
        Signal type

        :value: - 'NRZ'
                - 'PAM4'
        :type: str
        :raise ValueError: exception if type is not NRZ or PAM4
        """
        return self._read(":DATA:LINecoding? 'M{}.DataIn'".format(self._module_id, self._channel_number),
                          dummy_data='NRZ')

    @signal_type.setter
    def signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if type is not NRZ or PAM4
        """
        raise NotSupportedError('Keysight BERT does not allow you to change a signal type on a single channel/module.'
                                'Please use bert.global_ed_signal_type instead')

    def symbol_mapping(self, value):
        """
        Symbol Mapping method which combines both symbol mapping CLI properties

        :value: - 'NONE'
                - 'GRAY'
                - 'CUST'
                -  ['11','00','01','10']
        :type: str or list of strings
        :rtype: ValueError: exception if type is not NONE or GRAY or CUST or list of symbols
        """
        if isinstance(value, list):
            if len(value) == 4:
                if all(isinstance(n, str) for n in value):  # if list of strings with length 4
                    self.symbol_mapping_mode = 'CUST'
                    self.symbol_custom_mapping = value
        elif isinstance(value, str):
            self.symbol_mapping_mode = value
        else:
            raise ValueError("Method only accepts str or list of strings. See docstring")

    @property
    def symbol_mapping_mode(self):
        """
        Symbol mapping mode

        :value: - 'NONE'
                - 'GRAY'
                - 'CUST'
        :type: str
        :raise ValueError: exception if type is not NONE or GRAY or CUST
        """
        return self._read(":DATA:LINecoding:PAM4:MAPP? 'M{}.DataIn'".format(self._module_id),
                          dummy_data='NONE')

    @symbol_mapping_mode.setter
    def symbol_mapping_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if type is not NONE or GRAY or CUST
        """
        self._write(":DATA:LINecoding:PAM4:MAPP 'M{}.DataIn', {}".format(self._module_id,
                                                                        value.upper()))

    @property
    def symbol_custom_mapping(self):
        """
        Custom symbol mapping

        :value: comma separated str of symbol encoding (i.e ['11','00','01','10'] (no spaces))
        :type: list of str
        :raise ValueError: exception if type is not list of str
        """
        return self._read(":DATA:LINecoding:PAM4:MAPP:CUST? 'M{}.DataIn'".format(self._module_id))

    @symbol_custom_mapping.setter
    def symbol_custom_mapping(self, value):
        """
        :type value: list of str
        :raise ValueError: exception if type is not list of str
        """
        if self.symbol_mapping_mode == 'CUST':
            mapping = ''
            for n in range(4):  # converts list to string
                if n != 3:
                    mapping += value[n] + ','
                else:
                    mapping += value[n]
            self._write(":DATA:LINecoding:PAM4:MAPP:CUST 'M{}.DataIn', {}".format(self._module_id,
                                                                                  mapping))
        else:
            raise NotSupportedError("{0} must be in 'custom' symbol mapping mode to define the custom symbol mapping"
                                    .format(self.name))

    @property
    def sync_loss_threshold(self):
        """
        BER at which sync loss is indicated

        :value: BER alignment threshold
        :type: float
        """

        return float(self._read(f":DATA:SYNC:THRESHOLD? 'M{self._module_id}.DataIn'"))

    @sync_loss_threshold.setter
    def sync_loss_threshold(self, value):
        """
        :type value: float
        """

        self._write(f":DATA:SYNC:THRESHOLD 'M{self._module_id}.DataIn',{value}")

    @property
    def sync_loss(self):
        """
        **READONLY**

        :value: sync loss count for current or last measurement
        :type: int
        """
        raise NotSupportedError('Keysight M8000 does not support sync loss counts')

    @property
    def sync_status(self):
        """
        **READONLY** State of pattern sync

        :value: - 'IN_SYNC'
                - 'LOSS_OF_SYNC'
        :type: str
        """
        output_dict = {'0': 'IN_SYNC', '1': 'LOSS_OF_SYNC'}
        return output_dict[self._read(":STATus:INSTrument:SLOSs? 'M{}.DataIn'".format(self._module_id), dummy_data='1')]

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
    def track_ppg(self, value):  # TODO: Emulate tracking
        """
        :type value:
        """
        raise NotImplementedError

    @property
    def user_pattern(self):
        """
        Desired user pattern

        :value: - Hex string i.e. 'H02948ACFE'
                - Bin string i.e. 'B010101100'
        :type: str
        """
        return self._pattern

    @user_pattern.setter
    def user_pattern(self, value):
        """
        :type value: str
        """
        # XML string for clearing Analyzer pattern
        clear_xml = r'<?xml version="1.0" encoding="utf-16"?>' \
                    r'<sequenceDefinition xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
                    r'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                    r'xmlns="http://www.agilent.com/schemas/M8000/DataSequence">' \
                    r'<description />' \
                    r'<sequence />' \
                    r'</sequenceDefinition>'
        clear_xml = '#3%d' % len(clear_xml) + clear_xml

        self._write(':DATA:SEQuence:VALue "Analyzer",{}'.format(clear_xml))

        if value[0] == "H":
            # Convert hex string to hex number, convert to binary string, strip off "0b"
            pattern = bin(int(value[1:], 16))[2:]
        elif value[0] == "B":
            # Strip off leading "B"
            pattern = value[1:]

        command_str = ':DATA:PATTern:IDATa "shared:myAnalyzerPattern",0,{}'.format(len(pattern))
        num_bytes = int(ceil(float(len(pattern)) / 8))

        for i in range(num_bytes):
            # Get a 1-byte slice from the pattern
            byte_ = pattern[i * 8:(i * 8) + 8]
            # Pad zeros to end of byte if less than 8 bits left
            if len(byte_) < 8:
                byte_ += "0" * (8 - len(byte_))
            # Convert to int
            byte_ = int(byte_, 2)
            # Append to the command string
            command_str += (",%d" % byte_)

        self._write(':DATA:PATTern:USE "shared:myAnalyzerPattern",{}'.format(len(pattern)))
        self._write(command_str)

        # XML string for using new pattern
        pattern_xml = r'<?xml version="1.0" encoding="utf-16"?>' \
                      r'<sequenceDefinition xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
                      r'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                      r'xmlns="http://www.agilent.com/schemas/M8000/DataSequence">' \
                      r' <description />' \
                      r'<sequence>' \
                      r' <loop>' \
                      r'<block length="%d">' \
                      r'<pattern source="shared:myAnalyzerPattern" />' \
                      r'</block>' \
                      r' </loop>' \
                      r'</sequence>' \
                      r'</sequenceDefinition>' % len(pattern)
        pattern_xml = '#3%d' % len(pattern_xml) + pattern_xml

        self._write(':DATA:SEQuence:VALue "Analyzer",{}'.format(pattern_xml))
        self._pattern = value

    def align_single(self, timeout=30, blocking=True):  # TODO: add polling
        """
        Tells the BERT to acquire inbound data, align, and open eye to maximum on this
        channel.

        :param timeout: timeout value for the auto align in s
        :type timeout: int
        :param blocking: blocking/non-blocking call
        :type blocking: bool
        """
        """
        See :py:func:`Equipment.BERT.base_bert.BaseEDChannel.auto_align`
        """

        self._write(":INP:ALIGNMENT:EYE:AUTO 'M%d.DataIn'" % self._module_id)

        # From the command documentation in the Command Expert program :
        # This command cannot be used in the same compound SCPI statement that is starting the alignment procedure.
        # If this command is sent to the instrument right after the command that is initiating the alignment procedure,
        # then the returned value is undefined and can reflect the state that was valid before the alignment.
        #
        # This can be overcome by reading any value from the instrument (e.g. *ESE?), except for *OPC? as this
        # will block until the alignment procedure is finished.

        # May not be necessary as it is not a 'compound' SCPI command ...
        dummy_read = self._read('*ESE?')

        status = self._read(':INPut:ALIGnment:STATus:VALue? "M%d.DataIn"' % self._module_id).strip('"')

        if blocking:
            start_time = time.time()

            while (status == 'INPROGRESS') and (time.time() - start_time < timeout):
                status = self._read(':INPut:ALIGnment:STATus:VALue? "M%d.DataIn"'
                                    % self._module_id).strip('"')
                self.sleep(0.5)
                self.logger.info(f"B, {timeout-(time.time() - start_time)}s remaining")

            if status == 'INPROGRESS':  # Timed out or other failure ...
                self._write(":INPut:ALIGnment:EYE:ABORt 'M%d.DataIn'" % self._module_id)
                status = self._read(':INPut:ALIGnment:STATus:VALue? "M%d.DataIn"' % self._module_id)
                self.sleep(3)

        return status


class KeysightSIJTMeasurementBlock(BaseEquipmentBlock):
    """
    Keysight SIJT Measurement Block
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
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._measurement_id = None
        self._start_time = 0
        self._end_time = 0

    @property
    def catalogue(self):
        """
        **READONLY**

        :value: list of created SIJT measurement names
        :type: list
        """
        return self._read(":PLUGin:JTOL:CATalog?", dummy_data='A,B,C').replace('"', '').split(',')

    @property
    def data(self):
        """
        **READONLY**
        Returns jitter tolerance measurement's data

        :value: full_output_dict {"Frequency": {"Frequency": int, "Amplitude": int, "Num_Bits": int, "Num_Errors": int,
         "BER": float, "Result": str}
        :type: list
        :raise ValueError: exception if there are no SIJT measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create an SIJT measurement')
        else:
            data = self._read("PLUGin:JTOLerance:FETCh:DATA? '{}'".format(self._measurement_id
                                                                          )).split(',')
        output_list = []
        temp_output_dict = {}
        previous_frequency = None
        row_dict = {}

        # remove the leading field
        data.pop(0)
        # compute the number of rows of 6 columns each
        num_rows = int(len(data) / 6)
        for row in range(0, num_rows, 1):
            row_dict['Frequency'] = int(data.pop(0))
            row_dict['Amplitude'] = "%.15f" % float(data.pop(0))
            row_dict['Num_Bits'] = int(data.pop(0))
            row_dict['Num_Errors'] = int(data.pop(0))
            row_dict['BER'] = "%.3E" % float(data.pop(0))
            row_dict['Result'] = data.pop(0).strip('"")')
            if 'PASS' in row_dict["Result"]:
                if previous_frequency == row_dict['Frequency'] or previous_frequency is None:
                    temp_output_dict = row_dict.copy()
                    previous_frequency = row_dict['Frequency']
                else:
                    output_list.append(temp_output_dict.copy())
                    previous_frequency = row_dict['Frequency']
        else:
            output_list.append(temp_output_dict.copy())

        return output_list

    @property
    def elapsed_time(self):
        """
        **READONLY**

        :value: elapsed time for current or last measurement
        :type: int
        """
        return int(time.time() - self._start_time)

    @property
    def generator(self):
        """
        Specify which ppg and channel to use as the generator

        :value: ppg identifier
        :type: str
        :raise ValueError: exception if there are no SIJT measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create an SIJT measurement')
        else:
            return self._read("PLUG:JTOL:INST:GEN? '{}'".format(self._measurement_id)).replace('"', '')

    @generator.setter
    def generator(self, value):
        """
        :type value: str
        :raise ValueError: exception if there are no SIJT measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create an SIJT measurement')
        else:
            self._write("PLUG:JTOL:INST:GEN '{}', '{}'".format(self._measurement_id, value))

    @property
    def measurement_id(self):
        """
        Specify measurement to control if multiple SIJT measurements are present

        :value: measurement identifier
        :type: str
        :raise ValueError: exception if there are no SIJT measurements
        """
        return self._measurement_id

    @measurement_id.setter
    def measurement_id(self, value):
        """
        :type value: str
        :raise ValueError: exception if there are no SIJT measurements
        """
        if value not in self.catalogue:
            raise ValueError('Measurement does not exist')
        else:
            self._measurement_id = value

    @property
    def progress(self):
        """
        **READONLY**
        Returns jitter tolerance measurement progress status

        :value: sijt_progress
        :type: float
        :raise ValueError: exception if there are no SIJT measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create an SIJT measurement')
        else:
            return float(self._read("PLUGin:JTOLerance:RUN:PROGress? '{}'".format(self._measurement_id)))

    @property
    def status(self):
        """
        **READONLY**
        Returns jitter tolerance measurement status

        :value: - 'ACTIVE'
                - 'INACTIVE'
        :type: float
        :raise ValueError: exception if there are no SIJT measurements
        """
        output_dict = {'1': 'ACTIVE', '0': 'INACTIVE'}
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create an SIJT measurement')
        else:
            return output_dict[self._read("PLUGin:JTOLerance:RUN? '{}'".format(self._measurement_id), dummy_data='0')]

    @property
    def template_file(self):
        """
        Specify the template file

        :value: template file path
        :type: str
        :raise ValueError: exception if there are no SIJT measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create an SIJT measurement')
        else:
            return self._read("PLUG:JTOL:MSET:TEMP:FILE? '{}'".format(self._measurement_id))

    @template_file.setter
    def template_file(self, value):
        """
        :type value: str
        :raise ValueError: exception if there are no SIJT measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create an SIJT measurement')
        else:
            self._write("PLUG:JTOL:MSET:TEMP:FILE '{}',\"{}\"".format(self._measurement_id, value))

    def get(self):
        """
        Overriding this method to allow for save_configuration without the need to create measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            self.logger.warning('No measurements exist')
            return {}
        else:
            return super().get()

    def _get_configuration(self):
        """
        Overriding this method to allow for save_configuration without
        the need to create measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            return {}
        else:
            return super()._get_configuration()

    def create_measurement(self, measurement_id=None, template_file=None, bset_tber="1e-11",
                           bset_clev="99", bset_art="0.1", bset_frt="2", grap_clim="1",
                           grap_tlim="1", grap_tpo="1", mset_freq_start="100",
                           mset_freq_stop="500000000", mset_npo="10", mset_mode="CHAR",
                           mset_alg="BULInear", mset_bin_size="0.005", mset_lin_size="0.005", template_points='OFF'):
        """
        Method to create a BERT SIJT measurement.
        TODO: Add description and type to docstring fields
        :param measurement_id:
        :type measurement_id:
        :param template_file:
        :type template_file:
        :param bset_tber:
        :type bset_tber:
        :param bset_clev:
        :type bset_clev:
        :param bset_art:
        :type bset_art:
        :param bset_frt:
        :type bset_frt:
        :param grap_clim:
        :type grap_clim:
        :param grap_tlim:
        :type grap_tlim:
        :param grap_tpo:
        :type grap_tpo:
        :param mset_freq_start:
        :type mset_freq_start:
        :param mset_freq_stop:
        :type mset_freq_stop:
        :param mset_npo:
        :type mset_npo:
        :param mset_mode:
        :type mset_mode:
        :param mset_alg:
        :type mset_alg:
        :param mset_bin_size:
        :type mset_bin_size:
        :param mset_lin_size:
        :type mset_lin_size:
        :param template_points:
        :type template_points:
        """

        if measurement_id is not None:
            self._measurement_id = measurement_id
        else:
            measurement_id = 'SIJT'
            self._measurement_id = 'SIJT'
        
        if self._measurement_id in self.catalogue:
            self.delete_measurement(self._measurement_id)
            self._measurement_id = measurement_id
            
        self._write("PLUG:JTOL:NEW '{}'".format(self._measurement_id))

        self._write("PLUG:JTOL:BSET:TBER '{}', {}".format(self._measurement_id, bset_tber))
        self._write("PLUG:JTOL:BSET:CLEV '{}',{}".format(self._measurement_id, bset_clev))
        self._write("PLUG:JTOL:BSET:ART '{}',{}".format(self._measurement_id, bset_art))
        self._write("PLUG:JTOL:BSET:FRT '{}',{}".format(self._measurement_id, bset_frt))

        if template_points == 'ON':
            self._write(":PLUGin:JTOLerance:MSETup:MTPoints '{}', {}".format(self._measurement_id, template_points))

        self._write("PLUG:JTOL:INST:ANAL '{}', 'M{}.DataIn'".format(self._measurement_id,
                                                                    self._module_id))

        self._write("PLUG:JTOL:GRAP:CLIM '{}',{}".format(self._measurement_id, grap_clim))
        self._write("PLUG:JTOL:GRAP:TLIM '{}',{}".format(self._measurement_id, grap_tlim))
        self._write("PLUG:JTOL:GRAP:TPO '{}',{}".format(self._measurement_id, grap_tpo))

        if template_file is not None:
            self._write("PLUG:JTOL:MSET:TEMP:FILE '{}',\"{}\"".format(self._measurement_id,
                                                                      template_file))

        self._write("PLUG:JTOL:MSET:FREQ:STARt '{}',{}".format(self._measurement_id, mset_freq_start))
        self._write("PLUG:JTOL:MSET:FREQ:STOp '{}',{}".format(self._measurement_id, mset_freq_stop))
        self._write("PLUG:JTOL:MSET:NPO '{}',{}".format(self._measurement_id, mset_npo))
        self._write("PLUG:JTOL:MSET:MODE '{}',{}".format(self._measurement_id, mset_mode))
        self._write("PLUG:JTOL:MSET:ALG '{}',{}".format(self._measurement_id, mset_alg))
        self._write("PLUG:JTOL:MSET:BIN:SSIZe '{}',{}".format(self._measurement_id, mset_bin_size))
        self._write("PLUG:JTOL:MSET:LIN:SSIZe '{}',{}".format(self._measurement_id, mset_lin_size))

    def delete_measurement(self, measurement_id=None):
        """

        :param measurement_id: Measurement identifier on the BERT
        :type: string
        :raise ValueError: exception if there are no measurements to delete
        """
        if measurement_id is None:
            if self._measurement_id is None:
                self._measurement_id = self.catalogue[-1]
            measurement_id = self._measurement_id

        if measurement_id == '':
            raise ValueError('There are currently no measurements to delete')
        else:
            self._write(":PLUGin:JTOL:DELete '{}'".format(measurement_id))
            self._measurement_id = self.catalogue[-1]

    def start_measurement(self):
        """
        Method to start the given jitter tolerance measurement, the measurement configuration is
        saved on the BERT itself.
        """
        if self._measurement_id is None or self._measurement_id == '':
            self.create_measurement()
        self._write("PLUGin:JTOLerance:STARt '{}'".format(self._measurement_id))
        self._start_time = time.time()

    def stop_measurement(self):
        """
        Method to stop the given jitter tolerance measurement,
        the measurement configuration is saved on the BERTitself.

        :raise ValueError: exception if no measurements are currently running
        """
        if self._measurement_id is None:
            raise ValueError('No measurements are currently running')
        self._write("PLUGin:JTOLerance:STOP '{}'".format(self._measurement_id))
        self._end_time = time.time()


class KeysightBERMeasurementBlock(BaseEquipmentBlock):
    """
    Keysight BER Measurement Block
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
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
        self._measurement_id = None
        self._start_time = 0
        self._end_time = 0
        self._module_id = module_id

    @property
    def bit_count(self):
        """
        **READONLY**

        :value: accumulated bit count of current or last measurement
        :type: int
        """
        return self.data["total_bits"]

    @property
    def catalogue(self):
        """
        **READONLY**

        :value: list of created BER measurement names
        :type: list
        """
        return self._read(":PLUGin:ERATio:CATalog?",
                          dummy_data='A,B,C').replace('"', '').split(',')

    @property
    def data(self):
        """
        **READONLY**

        Returns a dict of the following data from the last measurement (or current,
        if it's still running):

        =============  ============  =====
             Key       Description   Type
        =============  ============  =====
        timestamp      Timestamp     int
        counted_1s     Counted 1s    int
        counted_0s     Counted 0s    int
        total_bits     Total Bits    int
        errored_1s     Errored 1s    int
        errored_0s     Errored 0s    int
        total_errors   Total Errors  int
        ber_1s         BER 1s        float
        ber_0s         BER 0s        float
        total_ber      Total BER     float
        =============  ============  =====

        :value: BER data
        :type: dict
        :raise ValueError: exception if passed there are no BER measurements cerated
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create a BER measurement')
        else:
            data = self._read(":PLUGin:ERAtio:FETCh? '{}'".format(
                self._measurement_id), dummy_data='0,1,2,3,4,5').split(',')

        if data == "":
            return {}
        else:
            data_dict = {"duration": float(data[1]),  # convert from ps to s
                         "counted_1s": int(data[2]),
                         "counted_0s": int(data[3]),
                         "errored_1s": int(data[4]),
                         "errored_0s": int(data[5])}

            data_dict["total_bits"] = data_dict["counted_1s"] + data_dict["counted_0s"]
            data_dict["total_errors"] = data_dict["errored_1s"] + data_dict["errored_0s"]
            data_dict["ber_1s"] = float(data_dict["errored_1s"]) / float(data_dict["counted_1s"])
            data_dict["ber_0s"] = float(data_dict["errored_0s"]) / float(data_dict["counted_0s"])
            data_dict["total_ber"] = (float(data_dict["total_errors"])
                                      / float(data_dict["total_bits"]))

            return data_dict

    @property
    def duration_type(self):
        """
        Accumulation Duration

        :value: - 'FTIME'
                - 'IND'
        :type: str
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create a BER measurement')
        else:
            return self._read(":PLUGin:ERATio:ACQuisition:DURation? '{}'".format(
                self._measurement_id))

    @duration_type.setter
    def duration_type(self, value):
        """
        :type value: str
        """
        value = value.upper()
        if value in ['FTIM', 'IND']:
            self._write(":PLUGin:ERATio:ACQuisition:DURation '{}', {}".format(
                self._measurement_id, value))
        else:
            raise ValueError('Please specify either "FTIM" or "IND"')

    @property
    def elapsed_time(self):
        """
        **READONLY**

        :value: elapsed time for current or last measurement
        :type: int
        """
        return int(time.time() - self._start_time)

    @property
    def error_count(self, line_coding='NRZ'):
        """
        **READONLY**

        :param line_coding: the coding of the signal (either NRZ or PAM4)
        :type line_coding: str
        :value: error count of current or last measurement
        :type: int
        """
        if line_coding == 'NRZ':
            return self.data["total_errors"]
        elif line_coding == 'PAM4':
            return self.pam4_data["total_errors"]
        else:
            raise ValueError('line_coding must be either NRZ or PAM4!')

    @property
    def error_rate(self, line_coding='NRZ'):
        """
        **READONLY**

        :param line_coding: the coding of the signal (either NRZ or PAM4)
        :type line_coding: str
        :value: error rate of current or last measurement
        :type: float
        """
        if line_coding == 'NRZ':
            return self.data["total_ber"]
        elif line_coding == 'PAM4':
            return self.pam4_data["total_ber"]
        else:
            raise ValueError('line_coding must be either NRZ or PAM4!')

    @property
    def gating_period(self):
        """
        Gating period for fixed accumulation time

        :value: measurement period in s
        :type: int
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create a BER measurement')
        else:
            return float(self._read(":PLUGin:ERATio:ACQuisition:TIME? '{}'".format(
                                                                            self._measurement_id)))

    @gating_period.setter
    def gating_period(self, value):
        """
        :type value: int
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create a BER measurement')
        else:
            self.duration_type = 'FTIM'
            self._write(":PLUGin:ERATio:ACQuisition:TIME '{}', {}".format(self._measurement_id, value))

    @property
    def measurement_id(self):
        """
        Specify measurement to control if multiple BER measurements are present

        :value: measurement identifier
        :type: str
        """
        return self._measurement_id

    @measurement_id.setter
    def measurement_id(self, value):
        """
        :type value: str
        """
        if value not in self.catalogue:
            raise ValueError('Measurement does not exist')
        else:
            self._measurement_id = value

    @property
    def status(self):
        """
        **READONLY**

        :value: - 'INACTIVE'
                - 'ACTIVE'
        :type: str
        """
        output_dict = {'1': 'ACTIVE', '0': 'INACTIVE'}
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create a BER measurement')
        else:
            return output_dict[self._read(":PLUGin:ERATio:RUN? '{}'".format(
                self._measurement_id), dummy_data='0')]

    @property
    def pam4_data(self):
        """
        **READONLY**

        Returns a dict of the following data from the last measurement (or current,
        if it's still running):

        =============  ============  =====
             Key       Description   Type
        =============  ============  =====
        timestamp      Timestamp     int
        counted_1s     Counted 1s    int
        counted_0s     Counted 0s    int
        total_bits     Total Bits    int
        errored_1s     Errored 1s    int
        errored_0s     Errored 0s    int
        total_errors   Total Errors  int
        ber_1s         BER 1s        float
        ber_0s         BER 0s        float
        total_ber      Total BER     float
        =============  ============  =====

        :value: BER data
        :type: dict
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            raise ValueError('Please create a BER measurement')
        else:
            data = self._read(":PLUGin:ERAtio:FETCh? '{}'".format(
                self._measurement_id), dummy_data='1,2,3,4,5,6,8,9,10,11,12,13,14,15,16'
                                                  ',17').split(',')

        # No data returned, measurement probably hasn't been run yet.
        if data == "":
            return {}

        else:
            return_key = ['Timestamp', 'Counted_Ones', 'Counted_Zeros', 'Errored_Ones',
                          'Errored_Zeros', 'Compared_Symbols', 'Errored_Symbols',
                          'Symbol_0_Compared_Symbols', 'Symbol_0_Errored_Symbols',
                          'Symbol_1_Compared_Symbols', 'Symbol_1_Errored_Symbols',
                          'Symbol_2_Compared_Symbols', 'Symbol_2_Errored_Symbols',
                          'Symbol_3_Compared_Symbols', 'Symbol_3_Errored_Symbols']

            data_dict = {}
            for k, v in zip(return_key, data[1:]):
                data_dict[k] = float(v.strip(')'))

            for level in range(4):
                data_dict['SER{}'.format(level)] = data_dict['Symbol_{}_Errored_Symbols'.format(
                    level)] / data_dict['Symbol_{}_Compared_Symbols'.format(level)]

            data_dict['SER'] = data_dict['Errored_Symbols'] / data_dict['Compared_Symbols']
            data_dict['total_ber'] = (data_dict['Errored_Ones'] + data_dict['Errored_Zeros']) \
                                     / (data_dict['Counted_Ones'] + data_dict['Counted_Zeros'])
            data_dict['total_errors'] = (data_dict['Errored_Ones'] + data_dict['Errored_Zeros'])

            return data_dict

    def get(self):
        """
        Overriding this method to allow for save_configuration without
        the need to create measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            self.logger.warning('No measurements exist')
            return {}
        else:
            return super().get()

    def _get_configuration(self):
        """
        Overriding this method to allow for save_configuration without
        the need to create measurements
        """
        if self._measurement_id is None:
            self._measurement_id = self.catalogue[-1]

        if self._measurement_id == '':
            return {}
        else:
            return super()._get_configuration()

    def create_measurement(self, measurement_id=None):
        """
        Creates a new BER name identifier. If it already exists, the existing identifier is
        overwritten.

        :param measurement_id: BER measurement identifier
        :type measurement_id: str
        """
        if measurement_id is not None:
            self._measurement_id = measurement_id
        else:
            measurement_id = 'BERMeasurement'
            self._measurement_id = 'BERMeasurement'

        if self._measurement_id in self.catalogue:
            self.delete_measurement(self._measurement_id)
            self._measurement_id = measurement_id

        self._write(":PLUGin:ERATio:NEW '{}'".format(self._measurement_id))

        # Set to detailed view
        self._write(":PLUGin:ERATio:SHOW:RVMode '{}', DET".format(self._measurement_id))

        # Set the accumulation duration to infinite
        self._write(":PLUGin:ERATio:ACQuisition:DURation '{}', IND".format(self._measurement_id))

        # Set the module ID
        self._write(":PLUGin:ERATio:ACQuisition:ALOCation '{}','M{}.DataIn'".format(self._measurement_id,
                                                                                    self._module_id))

    def delete_measurement(self, measurement_id=None):
        """
        Deletes an existing BER name identifier.

        :param measurement_id: BER measurement identifier to delete
        :type measurement_id: str
        :raise ValueError: exception if there are no current measurements to delete
        """
        if measurement_id is None:
            if self._measurement_id is None:
                self._measurement_id = self.catalogue[-1]
            measurement_id = self._measurement_id

        if measurement_id == '':
            raise ValueError('There are currently no measurements to delete')
        else:
            self._write(":PLUGin:ERATio:DELete '{}'".format(measurement_id))
            self._measurement_id = self.catalogue[-1]

    def start_measurement(self):
        """
        Start BER measurement
        """
        if self._measurement_id is None or self._measurement_id == '':
            self.create_measurement()

        self._write(":PLUGin:ERATio:STARt '{}'".format(self._measurement_id))
        self._start_time = time.time()

    def stop_measurement(self):
        """
        Stop BER measurement
        """
        self._write(":PLUGin:ERATio:STOP '{}'".format(self._measurement_id))
        self._end_time = time.time()
