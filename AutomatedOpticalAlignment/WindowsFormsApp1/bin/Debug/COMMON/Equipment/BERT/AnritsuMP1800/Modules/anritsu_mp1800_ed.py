"""
| $Revision:: 282689                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-03 22:28:11 +0100 (Wed, 03 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------
"""
from datetime import datetime, timedelta
from CLI.Equipment.BERT.base_bert import BaseBERTErrorDetector
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock
from CLI.Utilities.custom_exceptions import NotSupportedError


class AnritsuMP1800ED(BaseBERTErrorDetector):
    """
    Base BERT Error Detector channel class that all ED channels should be derived from
    """
    GATING_PERIOD = {10: 'S10', 30: 'S30', 60: 'M1', 600: 'M10', 3600: 'H1'}
    GATING_PERIOD_INV = {'S10': 10, 'S30': 30, 'M1': 60, 'M10': 600, 'H1': 3600}

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
        self._module_id = module_id
        self._channel_number = channel_number
        self.ber_measurement = AnritsuBERMeasurementBlock(module_id, channel_number, interface, dummy_mode)

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)

    @property
    def align_mode(self):
        """
        Alignment mode to use

        - Manual: user manually sets sampling point
        - Request: user requests one-time alignment using
          :py:func:`Equipment.base_bert.BaseBERTErrorDetector.align`
        - Auto: user enabled continuous alignment using
          :py:func:`Equipment.base_bert.BaseBERTErrorDetector.align`

        :value: - 'MANUAL'
                - 'REQUEST'
                - 'AUTO'
        :type: str
        """
        raise NotImplementedError

    @align_mode.setter
    def align_mode(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def align_auto(self):
        """
        Control auto adjust

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        output_dict = {'0': 'DISABLE', '1': 'ENABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(':SENSe:MEASure:AADJ32:STATe?')]

    @align_auto.setter
    def align_auto(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._select_mod()

        if value.upper() == 'ENABLE':
            self._write(":SYSTem:CFUNction OFF")
            self.sleep(0.500)
            self._select_mod()
            self._write(":SENSe:MEASure:AADJ32:STOP")
            self._write(":SYSTem:CFUNction AADJ32")
            self.sleep(1)
            self._select_mod()
            self._write(":SENSe:MEASure:AADJ32:SLASet")
            self.sleep(1)
            self._write(":SENSe:MEASure:AADJ32:STARt")
            self.sleep(1)
        elif value.upper() == 'DISABLE':
            self._write(":SYSTem:CFUNction OFF")
            self.sleep(0.2)
            self._write(":SYSTem:CFUNction AADJ32")
            self.sleep(1)
            self._select_mod()
            self._write(":SENSe:MEASure:AADJ32:STOP")
            self.sleep(1)
            self._write(":SYSTem:CFUNction OFF")
        else:
            raise ValueError('Please specify either "ENABLE" or "DISABLE')

    @property
    def align_single_status(self):
        """
        **READONLY**

        :value: Reports the auto align status parameters. 1 for started, 0 for stopped,
         -1 for failure.
        :type: int
        """
        self._select_mod()

        if self.dummy_mode:
            status = 0
        else:
            current_function = self._read(":SYSTem:CFUNction?")

            if current_function != 'ASE32':
                self._write(":SYSTem:CFUNction ASE32")

            status = self._read(":SENS:MEAS:ASE:STATe?")

            if current_function != 'ASE32':
                self._write(":SYSTem:CFUNction %s" % current_function)

        return status

    @property
    def cdr_loop_bandwidth(self):
        """
        :value: CDR's loop bandwidth frequency in Hz
        :type: int
        """
        raise NotSupportedError('%s: CDR functionalities are not supported' % self.name)

    @cdr_loop_bandwidth.setter
    def cdr_loop_bandwidth(self, value):
        """
        :type value: int
        """
        raise NotSupportedError('%s: CDR functionalities are not supported' % self.name)

    @property
    def cdr_target_frequency(self):
        """
        :value: CDR's target frequency in Hz
        :type: int
        """
        raise NotSupportedError('%s: CDR functionalities are not supported' % self.name)

    @cdr_target_frequency.setter
    def cdr_target_frequency(self, value):
        """
        :type value: int
        """
        raise NotSupportedError('%s: CDR functionalities are not supported' % self.name)

    @property
    def clock_delay(self):
        """
        Clock delay in mUI (sample delay)
        :value: clock delay in mUI
        :type: float
        """
        self._select_mod()

        return float(self._read(":INPut:CLOCk:DELay? UI", dummy_data='1').strip(",UI"))

    @clock_delay.setter
    def clock_delay(self, value):
        """
        :type value: float
        """
        self._select_mod()

        status = self.align_auto

        if status == 'DISABLE':
            if -1000 < int(value) < 1000:
                self._write(":INPut:CLOCk:DELay %d,UI" % value)
            else:
                raise ValueError('Please enter a clock delay in the range -1000mUI to 1000mUI')
        else:
            raise ValueError('align_auto must be disabled to use clock_delay')

    @property
    def clock_source(self):
        """
        Clock recovery source

        :value: - 'EXTERNAL'
                - 'RECOVERED'
        :type: str
        :raise ValueError: exception if clock source is not "EXTERNAL" nor "RECOVERED"
        """
        self._select_mod()

        output_dict = {'EXT': 'EXTERNAL', 'REC': 'RECOVERED',
                       'EXTernal': 'EXTERNAL', 'RECovered': 'RECOVERED',
                       'DUMMY_DATA': 'EXTERNAL'}
        return output_dict[self._read(':INPut:CLOCk:SELection?')]

    @clock_source.setter
    def clock_source(self, value):
        """
        :type value: str
        :raise ValueError: exception if clock source is not "EXTERNAL" nor "RECOVERED"
        """
        self._select_mod()

        value = value.upper()
        input_dict = {'EXTERNAL': 'EXTernal', 'RECOVERED': 'RECovered'}
        if value not in input_dict.keys():
            raise ValueError('Clock source can either be "EXTERNAL" or "RECOVERED"')
        else:
            self._write(":INPut:CLOCk:SELection %s" % (input_dict[value]))

    @property
    def input_mode(self):
        """
        input data mode

        :value: - 'DIFFERENTIAL'
                - 'SINGLE_POSITIVE'
                - 'SINGLE_NEGATIVE'
        :type: str
        :raise ValueError: exception if mode is not "DIFFERENTIAL", "SINGLE_POSITIVE" or
         "SINGLE_NEGATIVE"
        """
        self._select_mod()

        output_dict = {'SING': {'DATA': 'SINGLE_POSITIVE', 'XDAT': 'SINGLE_NEGATIVE'},
                       'DIF50': 'DIFFERENTIAL',
                       'DIF100': 'DIF100ohm',
                       # dummy_mode keys
                       'DUMMY_DATA': 'DIFFERENTIAL',
                       'DATA': 'SINGLE_POSITIVE',
                       'XDATA': 'SINGLE_NEGATIVE',
                       'TRACking': 'DIFFERENTIAL'
                       }

        mode = self._read(':INPut:DATA:INTerface?')
        if mode == 'SING':
            port = self._read(':INPut:DATA:SINGle?')
            return output_dict[mode][port]
        else:
            return output_dict[mode]

    @input_mode.setter
    def input_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode is not "DIFFERENTIAL", "SINGLE_POSITIVE" or
         "SINGLE_NEGATIVE"
        """
        self._select_mod()

        value = value.upper()
        input_dict = {'SINGLE_POSITIVE': {'MODE': 'SINGle', 'PORT': 'DATA'},
                      'SINGLE_NEGATIVE': {'MODE': 'SINGle', 'PORT': 'XDATA'},
                      'DIFFERENTIAL': 'DIF50ohm',
                      'DIF50ohm': 'DIF50ohm', 'DIF100ohm': 'DIF100ohm'}

        if value == 'DIFFERENTIAL':
            self._write(':INPut:DATA:INTerface %s' % (input_dict[value]))
            self._write(':INPut:DATA:DIFFerential TRACking')
        elif 'SINGLE' in value:
            self._write(':INPut:DATA:INTerface %s' % (input_dict[value]['MODE']))
            self._write(':INPut:DATA:SINGle %s' % (input_dict[value]['PORT']))
        else:
            raise ValueError('Input mode can either be "DIFFERENTIAL", "SINGLE_POSITIVE" or'
                             ' "SINGLE_NEGATIVE"')

    @property
    def input_threshold(self):
        """
        Input threshold voltage (in Volts). To maximize compatibility with
        different BERTs, the recommended voltage range is [-0.25, 0.25] V.

        :value: threshold in V
        :type: float
        :raise ValueError: exception if threshold is not between -3.5V and 3.3V
        """
        self._select_mod()

        return float(self._read(":INPut:DATA:THReshold? DATA"))

    @input_threshold.setter
    def input_threshold(self, value):
        """
        :type value: float
        :raise ValueError: exception if threshold is not between -3.5V and 3.3V
        """
        self._select_mod()

        if value < -3.5 or value > 3.3:
            raise ValueError("Threshold out of range [-3.5, 3.3] V")

        self._write(":INPut:DATA:THReshold DATA, %.3f" % value)
        self._write(":INPut:DATA:THReshold XDATA, %.3f" % value)

    @property
    def measurement_status(self):
        """
        **READONLY** BER measurement status

        :value: - 'INACTIVE'
                - 'ACTIVE'
        :type: str
        """
        self._select_mod()

        return self._read(":SENSe:MEASure:EALarm:STATe?")

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
        :raise ValueError: exception pattern is unrecognizable
        """
        self._select_mod()

        return self._read(":SENSe:PATTern:TYPE?")

    @pattern.setter
    def pattern(self, value):
        """
        :type value: str
        :raise ValueError: exception pattern is unrecognizable
        """
        self._select_mod()

        if value[0] != "H" and value[0] != 'B':
            value = value[4:]  # strip "PRBS" off of pattern string

            self._write(":SENSe:PATTern:TYPE PRBS")
            self._write(":SENSe:PATTern:PRBS:LENGth %s" % value)

        else:
            if value[0] == "H":  # Hex pattern
                length = 4 * (len(value) - 1)
            elif value[0] == "B":  # Binary pattern
                length = (len(value) - 1)
            else:
                raise ValueError("Unrecognized pattern type")

            self._write(":SENSe:PATTern:TYPE DATA")
            self._write(":SENSe:PATTern:DATA:LENGth %s" % length)
            self._write(':SENSe:PATTern:DATA:WHOLe #H0,#H%X, "%s"' % (length - 1, value))

    @property
    def polarity(self):
        """
        Data output polarity

        :value: - 'NORMAL'
                - 'INVERTED'
        :type: str
        :raise ValueError: exception if unrecognized logic polarity returned from equipment
        """
        self._select_mod()

        output_dict = {'POS': 'NORMAL', 'NEG': 'INVERTED',
                       'POSitive': 'NORMAL', 'NEGative': 'INVERTED',
                       'DUMMY_DATA': 'NORMAL'}
        return output_dict[self._read(":SENSe:PATTern:LOGic?")]

    @polarity.setter
    def polarity(self, value):
        """
        :type value: str
        :raise ValueError: exception if invalid polarity requested
        """
        self._select_mod()

        value = value.upper()
        input_dict = {'NORMAL': 'POSitive', 'INVERTED': 'NEGative'}
        if value not in input_dict.keys():
            raise ValueError("Invalid polarity requested: %s" % value)
        else:
            self._write(":SENSe:PATTern:LOGic %s" % (input_dict[value]))

    @property
    def sync_loss(self):
        """
        **READONLY**

        :value: sync loss count for current or last measurement
        :type: int
        """
        self._select_mod()

        ret_str = self._read(':CALCulate:DATA:MON? "PSLoss"')
        if ret_str == "Occur":
            return 1
        else:
            return 0

    def align_single(self, timeout=30):
        """
        Tells the BERT to acquire inbound data, align, and open eye to maximum on this
        channel.

        :param timeout: timeout value for the auto align in s
        :type timeout: int
        """
        self._select_mod()

        self._write(":SYSTem:CFUNction OFF")
        self.sleep(1)
        self.align_auto = 'DISABLE'
        self.sleep(1)
        self._write(":SYSTem:CFUNction ASE")
        self.sleep(.2)
        self._select_mod()
        self._write(":SENSe:MEASure:ASEarch:SMODe COARse")
        self.sleep(.2)
        self._write(":SENSe:MEASure:ASEarch:MODE PTHR")
        self.sleep(.2)
        self._write(":SENSe:MEASure:ASEarch:SLAReset")
        self.sleep(.2)

        self._write(":SENS:MEAS:ASE:SLAS")
        # self._write(":SENSe:MEASure:ASearch:SELSlot SLOT%d,%d,1" % (self._module_id,
        #                                                             self._channel_number))
        self.sleep(0.5)
        self._write(":SENSe:MEASure:ASEarch:STARt")
        self.sleep(1)
        start_time = datetime.time()

        # print(self.align_single_status)
        # Loop as long as auto align is in progress and time elapsed isn't greater than the
        # timeout value
        while int(self.align_single_status) == 1 and (datetime.time() - start_time) < timeout:
            self.sleep(5)

        status = int(self.align_single_status)
        if status != 0:
            raise RuntimeError("Failure to autoalign, status = %d" % status)
        self._write(":SYSTem:CFUNction OFF")


class AnritsuBERMeasurementBlock(BaseEquipmentBlock):
    """
    Anritsu BER Measurement Block
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
        self._module_id = module_id
        self._channel_number = channel_number

    def _select_mod(self):
        self._write(":MODule:ID %s" % self._module_id)

    @property
    def bit_count(self):
        """
        **READONLY**

        :value: accumulated bit count of current or last measurement
        :type: int
        """
        self._select_mod()

        return int(self._read(':CALCulate:DATA:EALarm? "CURRent:CC:TOTal"'))

    @property
    def clock_loss(self):
        """
        **READONLY**

        :value: clock loss count for current or last measurement
        :type: int
        """
        # Might be the commented out SCPI command. Needs testing.
        # self._read(':CALCulate:DATA:EALarm? "AINTerval:CLOSs"')
        self._select_mod()

        return int(self._read(':CALCulate:DATA:EALarm? "CURRent:AINTerval:CLOSs"'))

    @property
    def elapsed_time(self):
        """
        **READONLY**

        :value: elapsed time for current or last measurement
        :type: int
        """
        self._select_mod()

        time_list = self._read(':SENSe:MEASure:EALarm:ELAPsed?', dummy_data='0, 0, 0, 0').split(',')
        seconds_in_day = 24 * 60 * 60
        seconds_in_hour = 60 * 60
        seconds_in_minute = 60

        # Return the elapsed time in seconds
        return int((float(time_list[0]) * seconds_in_day
                    + float(time_list[1]) * seconds_in_hour
                    + float(time_list[2]) * seconds_in_minute
                    + float(time_list[3])))

    @property
    def error_count(self):
        """
        **READONLY**

        :value: error count of current or last measurement
        :type: int
        """
        self._select_mod()

        return int(self._read(':CALCulate:DATA:EALarm? "CURRent:EC:TOTal"'))

    @property
    def error_rate(self):
        """
        **READONLY**

        :value: error rate of current or last measurement
        :type: float
        """
        self._select_mod()

        return float(self._read(':CALCulate:DATA:EALarm? "CURRent:ER:TOTal"'))

    @property
    def gating_period(self):
        """
        Gating period for fixed accumulation time

        :value: measurement period in s
        :type: int
        :raise ValueError: exception if gating period is not 10, 30, 60, 600 or 3600 seconds
        """
        self._select_mod()

        time_list = self._read(':SENSe:MEASure:EALarm:PERiod?', dummy_data='0, 0, 0, 0').split(',')
        return int(time_list[0]) * 86400 + int(time_list[1]) * 3600 + int(time_list[2]) * 60 + int(
            time_list[3])

    @gating_period.setter
    def gating_period(self, value):
        """
        :type value: int
        :raise ValueError: exception if gating period is not 10, 30, 60, 600 or 3600 seconds
        """
        self._select_mod()

        sec = timedelta(seconds=value)
        value = datetime(1, 1, 1) + sec

        self._write(':SENSe:MEASure:EALarm:PERiod %s,%s,%s,%s' % (value.day-1, value.hour, value.minute, value.second))

    @property
    def sync_status(self):
        """
        **READONLY** State of pattern sync

        :value: - 'IN_SYNC'
                - 'LOSS_OF_SYNC'
        :type: str
        """
        self._select_mod()

        return self._read(':CALCulate:DATA:EALarm? "CURRent:AINTerval:PSLoss"')

    def start_measurement(self):
        """
        Starts a BER measurement
        """
        self._select_mod()

        self._write(":SENSe:MEASure:STARt")

    def stop_measurement(self):
        """
        Stops a BER measurement
        """
        self._select_mod()

        self._write(":SENSe:MEASure:STOP")
