"""
| $Revision:: 283942                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-23 16:54:47 +0000 (Fri, 23 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from decimal import Decimal
from CLI.Equipment.SamplingScope.base_sampling_scope import BaseSamplingScopeMeasurement
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock


class _Keysight86100XDisplayMemory(BaseEquipmentBlock):
    """
    Keysight Measurement block
    """
    _MODE_STATE = None

    def __init__(self, handle, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._handle = handle
        self._channel_state = None

    @property
    def channel_display(self):
        """
        Disable or Enable channel display

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read("{}:DISPlay?".format(self._handle))]

    @channel_display.setter
    def channel_display(self, value):  # TODO: Add Polling
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        elif value != self._channel_state:
            if self._handle[:4] == 'DIFF':
                self.diff_disp_mode = 'ENABLE'
            self._write(':{}:DISPlay {}'.format(self._handle,
                                                input_dict[value]))
            self._channel_state = value

    @property
    def diff_disp_mode(self):
        """
        Disable or Enable differential display

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read("{}:DMOD?".format(self._handle))]

    @diff_disp_mode.setter
    def diff_disp_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        self._write(':{}:DMOD ON'.format(self._handle))

    @property
    def scope_mode(self):
        """
        Specify scope mode

        :value: - 'EYE'
                - 'OSC'
                - 'JITT'
        :type: str
        :raise ValueError: exception if mode not 'EYE', 'JITT' or 'OSC'
        """
        return self._read("SYST:MODE?", dummy_data='OSC')

    @scope_mode.setter
    def scope_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'EYE', 'JITT' or 'OSC'
        """
        if _Keysight86100XDisplayMemory._MODE_STATE is None:
            _Keysight86100XDisplayMemory._MODE_STATE = self.scope_mode

        value = value.upper()
        if value not in ['EYE', 'OSC', 'JITT']:
            raise ValueError('Please specify either "EYE", "JITT" or "OSC"')
        elif value != _Keysight86100XDisplayMemory._MODE_STATE:
            raise ValueError('Please change the scope mode to "{}" before'
                             ' taking this measurement'.format(value))


class Keysight86100XMeasurement(BaseSamplingScopeMeasurement):
    """
    Keysight 86100X Measurement that all keysight measurement blocks should be derived from
    """
    _DISPLAY_MEASUREMENTS = True

    def __init__(self, interface, dummy_mode, **kwargs):
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
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def display_measurements(self):
        """
        Disable or Enable the display of measurements on the scope screen.
        If disabled, measurement queries will only return a value.
        This command will take effect only on future "display_measurements" commands.

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {False: 'DISABLE', True: 'ENABLE'}
        return output_dict[Keysight86100XMeasurement._DISPLAY_MEASUREMENTS]

    @display_measurements.setter
    def display_measurements(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': True, 'DISABLE': False}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            Keysight86100XMeasurement._DISPLAY_MEASUREMENTS = input_dict[value]


class Keysight86100XOscilloscopeMeasurement(Keysight86100XMeasurement):
    """
    Keysight Measurement block
    """

    def __init__(self, module_id, channel_number, handle, display_memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = display_memory

    def amplitude(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns amplitude measurement

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform amplitude
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VAMP:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VAMP', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VAMP', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VAMP', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VAMP{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VAMP{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def amplitude_pp(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns amplitude peak to peak measurement

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform peak-to-peak voltage
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VPP:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VPP', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VPP', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VPP', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VPP{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VPP{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def avg(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns average voltage

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform avg voltage
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VAV:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VAV', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VAV', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VAV', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VAV{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VAV{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def delta_time(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal delta time

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns signal delta time
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:DELT:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:DELT', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:DELT', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:DELT', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:DELT{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:DELT{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def duty_cycle(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal duty cycle

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns signal duty cycle
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:DUTY:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:DUTY', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:DUTY', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:DUTY', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:DUTY{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:DUTY{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def fall_time(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal edge fall time

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform fall time
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:FALL:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:FALL', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:FALL', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:FALL', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:FALL{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:FALL{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result
    
    def frequency(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal frequency

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform frequency
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:FREQ:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:FREQ', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:FREQ', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:FREQ', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:FREQ{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:FREQ{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def jitter_pp(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal jitter peak to peak

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform pp jitter
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:JITT:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:OSC:JITT:FORM PP', dummy_data=1.0)

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:JITT', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:JITT', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:JITT', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:JITT{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:JITT{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def jitter_rms(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal jitter rms

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform rms jitter
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:JITT:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:OSC:JITT:FORM RMS', dummy_data=1.0)

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:JITT', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:JITT', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:JITT', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:JITT{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:JITT{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def lower_amplitude(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal lower amplitude

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns the amplitude at lower value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VLOWER:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VLOWER', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VLOWER', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VLOWER', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VLOWER{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VLOWER{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def max(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal max voltage

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform max voltage
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VMAX:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VMAX', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VMAX', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VMAX', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VMAX{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VMAX{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def middle_amplitude(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal middle amplitude

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns the amplitude at middle value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VMIDDLE:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VMIDDLE', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VMIDDLE', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VMIDDLE', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VMIDDLE{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VMIDDLE{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def min(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal min voltage

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform min voltage
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VMIN:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VMIN', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VMIN', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VMIN', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VMIN{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VMIN{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def oma(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal OMA

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns signal oma
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:OMA:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:OMA', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:OMA', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:OMA', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:OMA{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:OMA{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def overshoot(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal overshoot

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns signal overshoot
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:OVER:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:OVER', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:OVER', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:OVER', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:OVER{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:OVER{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def period(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal period

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns signal period
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:PER:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:PER', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:PER', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:PER', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:PER{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:PER{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def preshoot(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal pre-overshoot

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns signal pre-overshoot
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:PRES:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:PRES', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:PRES', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:PRES', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:PRES{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:PRES{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def pulse_width_pos(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal positive pulse width

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns positive pulse width
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:PWIDTH:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:PWIDTH', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:PWIDTH', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:PWIDTH', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:PWIDTH{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:PWIDTH{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def pulse_width_neg(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal negative pulse width

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns negative pulse width
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:NWIDTH:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:NWIDTH', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:NWIDTH', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:NWIDTH', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:NWIDTH{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:NWIDTH{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def rise_time(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal rise time

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform rise time
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:RIS:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:RIS', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:RIS', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:RIS', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:RIS{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:RIS{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def rms_ac(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal AC RMS voltage

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform AC rms voltage
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VRMS:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:OSC:VRMS:TYPe AC')

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VRMS', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VRMS', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VRMS', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VRMS{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VRMS{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def rms_dc(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal DC RMS voltage

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns waveform DC rms voltage
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VRMS:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:OSC:VRMS:TYPe DC')

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VRMS', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VRMS', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VRMS', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VRMS{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VRMS{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result

    def upper_amplitude(self, measure_type='_all_'):
        """
        ***READ-ONLY***\n
        Returns signal upper voltage amplitude

        :param measure_type: Measurement acquire type. min, max, mean, instant, standard deviation
        :type measure_type: str
        :return: returns the amplitude at upper value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:VUPPER:SOURce1 {}'.format(self._handle))

        measure_type_check = {'INST': "", 'MEAN': ":MEAN", 'SDEV': ":SDEV", 'MIN': ":MIN", 'MAX': ":MAX"}
        if measure_type == '_all_':
            all_types = True
            self._write(':MEAS:OSC:VUPPER', dummy_data=1.0)

        elif isinstance(measure_type, str) and measure_type in measure_type_check:
            if measure_type == 'INST':
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEAS:OSC:VUPPER', dummy_data=1.0)
            else:
                self._write(':MEAS:OSC:VUPPER', dummy_data=1.0)
            all_types = False

        else:
            raise ValueError('Measure_type allowed inputs are {0}'.format(measure_type_check))

        result = {}
        for n in measure_type_check:
            if all_types:
                value = float(self._read(':MEAS:OSC:VUPPER{0}?'.format(measure_type_check[n])))
            else:
                value = float(self._read(':MEAS:OSC:VUPPER{0}?'.format(measure_type_check[measure_type])))
                return value

            result[n] = value
        return result


class Keysight86100XOpticalOscilloscopeMeasurement(Keysight86100XOscilloscopeMeasurement):
    """
    Keysight Optical Measurement block
    """

    def __init__(self, module_id, channel_number, handle, display_memory, interface, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, channel_number=channel_number, handle=handle,
                         display_memory=display_memory, interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def avg_power_watt(self):
        """
        **READONLY**

        :value: returns waveform average power in watts
        :type: float
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:APOW:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:OSC:APOW:UNIT WATT', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:OSC:APOW', dummy_data=1.0)
        return float(self._read(':MEAS:OSC:APOW:MEAN?'))

    @property
    def avg_power_dbm(self):
        """
        **READONLY**

        :value: returns waveform average power in dbm
        :type: float
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:OSC:APOW:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:OSC:APOW:UNIT DBM', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:OSC:APOW', dummy_data=1.0)
        return float(self._read(':MEAS:OSC:APOW:MEAN?'))


class Keysight86100XPAMOscilloscopeMeasurement(Keysight86100XMeasurement):
    """
    Keysight PAM Osc Measurement block
    """

    def __init__(self, module_id, channel_number, handle, display_memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = display_memory

    @property
    def level(self):
        """
        **READONLY**

        :value: returns waveform level
        :type: float
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:OSCilloscope:PAM:LEVel:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:OSCilloscope:PAM:LEVel', dummy_data=1.0)
        return float(self._read(':MEASure:OSCilloscope:PAM:LEVel?'))

    @property
    def linearity(self):
        """
        **READONLY**

        :value: returns waveform linearity
        :type: float
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:OSCilloscope:PAM:LIN:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:OSCilloscope:PAM:LIN', dummy_data=1.0)
        return float(self._read(':MEASure:OSCilloscope:PAM:LIN?'))

    @property
    def rms(self):
        """
        **READONLY**

        :value: returns waveform rms level
        :type: float
        """
        self._display_memory.scope_mode = 'OSC'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:OSCilloscope:PAM:RMS:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:OSCilloscope:PAM:RMS', dummy_data=1.0)
        return float(self._read(':MEASure:OSCilloscope:PAM:RMS?'))


class Keysight86100XEyeMeasurement(Keysight86100XMeasurement):
    """
    Keysight86618A Measurement block driver
    """

    def __init__(self, module_id, channel_number, handle, display_memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = display_memory

    @property
    def bit_rate(self):
        """
        **READONLY**

        :value: returns eye bit rate
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:BITR:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:BITR', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:BITR?'))

    @property
    def crossing_point(self):
        """
        **READONLY**

        :value: returns eye crossing percentage
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:CROS:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:CROS', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:CROS?'))

    @property
    def crossing_time(self):
        """
        **READONLY**

        :value: returns eye crossing time
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:ECT:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:ECT', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:ECT?'))

    @property
    def duty_cycle_dist_percent(self):
        """
        **READONLY**

        :value: returns eye duty cycle distortion percentage
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:DCD:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:DCD:FORM PERC', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:DCD', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:DCD?'))

    @property
    def duty_cycle_dist_time(self):
        """
        **READONLY**

        :value: returns eye duty cycle distortion time
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:DCD:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:DCD:FORM TIME', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:DCD', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:DCD?'))

    @property
    def eye_amplitude(self):
        """
        **READONLY**

        :value: returns eye amplitude
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:AMPL:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:AMPL', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:AMPL?'))

    @property
    def eye_height_amplitude(self):
        """
        **READONLY**

        :value: returns eye height amplitude
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:EHE:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:EHE:FORM AMPL', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:EHE', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:EHE?'))

    @property
    def eye_height_ratio(self):
        """
        **READONLY**

        :value: returns eye height ratio
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:EHE:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:EHE:FORM RAT', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:EHE', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:EHE?'))

    @property
    def eye_width_time(self):
        """
        **READONLY**

        :value: returns eye width time
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:EWID:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:EWID:FORM TIME', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:EWID', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:EWID?'))

    @property
    def eye_width_ratio(self):
        """
        **READONLY**

        :value: returns eye width ratio
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:EWID:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:EWID:FORM RAT', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:EWID', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:EWID?'))

    @property
    def fall_time(self):
        """
        **READONLY**

        :value: returns eye fall time
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:FALL:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:FALL', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:FALL?'))

    @property
    def jitter_pp(self):
        """
        **READONLY**

        :value: returns waveform rms voltage
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:JITT:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:JITT:FORM PP', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:JITT', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:JITT?'))

    @property
    def jitter_rms(self):
        """
        **READONLY**

        :value: returns waveform rms jitter
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:JITT:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:JITT:FORM RMS', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:JITT', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:JITT?'))

    @property
    def one_level(self):
        """
        **READONLY**

        :value: returns eye one level
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:OLEV:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:OLEV', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:OLEV?'))

    @property
    def rise_time(self):
        """
        **READONLY**

        :value: returns eye rise time
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:RIS:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:RIS', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:RIS?'))

    @property
    def snr(self):
        """
        **READONLY**

        :value: returns eye signal-to-noise ratio
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:ESN:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:ESN', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:ESN?'))

    @property
    def vecp(self):
        """
        **READONLY**

        :value: returns vertical eye closure penalty
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:VECP:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:VECP', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:VECP?'))

    @property
    def zero_level(self):
        """
        **READONLY**

        :value: returns eye zero level
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:ZLEV:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:ZLEV', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:ZLEV?'))

    def measure_delta_time(self, operand2=None):
        """
        Method to measure delta time between 2 signals

        :value: returns eye delta time
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:DELT:SOURce1 {}'.format(self._handle))
        if operand2:
            self._write(':MEAS:EYE:DELT:SOURce2 {}'.format(operand2))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:DELT', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:DELT?'))


class Keysight86100XOpticalEyeMeasurement(Keysight86100XEyeMeasurement):
    """
    Keysight Optical Measurement block
    """

    def __init__(self, module_id, channel_number, handle, display_memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, channel_number=channel_number, handle=handle,
                         display_memory=display_memory, interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def avg_power_dbm(self):
        """
        **READONLY**

        :value: returns waveform average power in dbm
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:APOW:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:APOW:UNIT DBM', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:APOW', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:APOW:MEAN?'))

    @property
    def avg_power_watt(self):
        """
        **READONLY**

        :value: returns waveform average power in watts
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:APOW:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:APOW:UNIT WATT', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:APOW', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:APOW:MEAN?'))

    @property
    def er_ratio(self):
        """
        **READONLY**

        :value: returns extinction ratio
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:ERAT:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:ERAT:UNIT RAT', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:ERAT', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:ERATio:MEAN?'))

    @property
    def er_db(self):
        """
        **READONLY**

        :value: returns extinction ratio in decibels
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:ERAT:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:ERAT:UNIT DEC', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:ERAT', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:ERAT:MEAN?'))

    @property
    def er_percent(self):
        """
        **READONLY**

        :value: returns extinction ratio in percentage
        :type: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:ERAT:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:ERAT:UNIT PERC', dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:ERAT', dummy_data=1.0)
        return float(self._read(':MEAS:EYE:ERAT:MEAN?'))


class Keysight86100XPAMEyeMeasurement(Keysight86100XMeasurement):
    """
    Keysight86618A Measurement block driver
    """

    def __init__(self, module_id, channel_number, handle, display_memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = display_memory

    def eye_level(self, eye='_all_'):
        """
        Eye Level for specified eye

        :param eye: Selects which eye the measurement will be performed on
        :type eye: int or str
        :return: eye level
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:ELEV:SOURce {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:EYE:PAM:ELEV:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PAM:ELEV', dummy_data=1.0)
            value = float(self._read(':MEASure:EYE:PAM:ELEV?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye+n)] = value
        return result

    def eye_skew(self, eye='_all_'):
        """
        Eye skew for specified eye

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int or str
        :return: eye skew in seconds or UI
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:ESK:SOURce {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:EYE:PAM:ESK:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PAM:ESK', dummy_data=1.0)

            value = float(self._read(':MEASure:EYE:PAM:ESK?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(n)] = value
        return result

    def eye_height(self, eye='_all_', method='ZHITS', probability=1e-2):
        """
        Eye height for specified eye

        :param eye: Selects which eye the measurement will be performed on
        :type eye: int or str
        :param method: Selects the method used to determine the eye-opening
        :type method: - 'ZHITS'
                       - 'PROBABILITY'
        :param probability: Measurement-hit probability (1e-1 to 1e-9)
        :type probability: float
        :return: eye height in volts
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:EHE:SOURce {}'.format(self._handle))
        self._write(':MEAS:EYE:PAM:EHE:DEF:EOP {0}'.format(method))
        if method == 'PROBABILITY':
            if 1e-9 <= probability <= 1e-1:
                self._write(':MEAS:EYE:PAM:EHE:DEF:EOP:PROB {0}'.format(probability))
            else:
                raise ValueError('Probability value out of range. Must be 1e-1 to 1e-9')

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:EYE:PAM:EHE:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PAM:EHE', dummy_data=1.0)

            value = float(self._read(':MEASure:EYE:PAM:EHE?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(n)] = value
        return result

    def eye_width(self, eye='_all_', method='ZHITS', probability=1e-2):
        """
        Eye width for specified eye

        :param eye: Selects which eye the measurement will be performed on
        :type eye: int or str
        :param method: Selects the method used to determine the eye-opening
        :type method: - 'ZHITS'
                       - 'PROBABILITY'
        :param probability: Measurement-hit probability (1e-1 to 1e-9)
        :type probability: float
        :return: eye height in
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:EWID:SOURce {}'.format(self._handle))
        self._write(':MEAS:EYE:PAM:EHE:DEF:EOP {0}'.format(method))
        if method == 'PROBABILITY':
            if 1e-9 <= probability <= 1e-1:
                self._write(':MEAS:EYE:PAM:EWID:DEF:EOP:PROB {0}'.format(probability))
            else:
                raise ValueError('Probability value out of range. Must be 1e-1 to 1e-9')

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:EYE:PAM:EWID:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PAM:EWID', dummy_data=1.0)

            value = float(self._read(':MEASure:EYE:PAM:EWID?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(n)] = value
        return result

    def level_amplitude(self, level='_all_'):
        """
        Amplitude for specified level

        :param level: Selects which level the measurement will be performed on 
        :type level: int or str
        :return: eye level amplitude
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:LEV:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEAS:EYE:PAM:LEV:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PAM:LEV', dummy_data=1.0)

            value = float(self._read(':MEASure:EYE:PAM:LEV?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def level_pp(self, level='_all_'):
        """
        Eye level peak-peak for specified level

        :param level: Selects which level the measurement will be performed on 
        :type level: int or str
        :return: eye level peak
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:PP:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEAS:EYE:PAM:PP:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PAM:PP', dummy_data=1.0)

            value = float(self._read(':MEASure:EYE:PAM:PP?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def level_rms(self, level='_all_'):
        """
        Eye level rms for specified level

        :param level: Selects which level the measurement will be performed on 
        :type level: int or str
        :return: eye level rms
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:RMS:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEAS:EYE:PAM:RMS:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PAM:RMS', dummy_data=1.0)

            value = float(self._read(':MEASure:EYE:PAM:RMS?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def level_skew(self, level='_all_'):
        """
        Eye level skew for specified level

        :param level: Selects which level the measurement will be performed on 
        :type level: int or str
        :return: eye level skew
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:SKEW:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEAS:EYE:PAM:SKEW:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PAM:SKEW', dummy_data=1.0)

            value = float(self._read(':MEASure:EYE:PAM:SKEW?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def linearity_eye(self):
        """
        Linearity (RLM) using EYE method between all four amplitude levels

        :return: linearity ratio
        :rtype: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:LIN:SOURce1 {}'.format(self._handle))
        self._write(':MEASure:EYE:PAM:LIN:DEF EYE')
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:EYE:PAM:LIN', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:PAM:LIN?'))

    def linearity_rlma120(self):
        """
        Linearity (RLM) using RLMA120 method between all four amplitude levels

        :return: linearity ratio
        :rtype: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:LIN:SOURce1 {}'.format(self._handle))
        self._write(':MEASure:EYE:PAM:LIN:DEF RLMA120')
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:EYE:PAM:LIN', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:PAM:LIN?'))

    def linearity_rlmc94(self):
        """
        Linearity (RLM) using RLMC94 method between all four amplitude levels

        :return: linearity ratio
        :rtype: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:PAM:LIN:SOURce1 {}'.format(self._handle))
        self._write(':MEASure:EYE:PAM:LIN:DEF RLMC94')
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:EYE:PAM:LIN', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:PAM:LIN?'))

    def noise_margin(self):
        """
        Noise Margin (rms) measurement

        :return: Noise Margin
        :rtype: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:NMAR:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:EYE:NMAR', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:NMAR?'))

    def outer_extinction_ratio(self, unit):
        """
        Outer Extinction Ratio measurement

        :param unit: - 'DECIBEL'
                      - 'PERCENT'
                      - 'RATIO'
        :type unit: str
        :return: outer extinction ratio
        :rtype: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:EYE:OER:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:EYE:OER:UNIT {0}'.format(unit), dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEAS:EYE:OER', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:OER?'))

    def outer_oma(self, unit):
        """
        Outer optical modulation amplitude measurement

        :param unit:    - 'DBM'
                        - 'WATT'
        :type unit: str
        :return: Outer optical modulation amplitude
        :rtype: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:OOMA:SOURce1 {}'.format(self._handle))
        self._write(':MEASure:EYE:OOMA:UNITs {0}'.format(unit), dummy_data=1.0)
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:EYE:OOMA', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:OOMA?'))

    def partial_noise_margin(self, eye='_all_', side=None):
        """
        Partial Noise Margin measurement

        :param eye: Selects which eye the measurement will be performed on
        :type eye: int
        :param side: Selects which side of the waveform the measurement will be performed on
        :type side: str
        :return: partial noise margin
        :rtype: float
        """
        if not side:
            raise ValueError('SIDE parameter does not have a default value.')

        side_check = ('LEFT', 'RIGHT')
        if side in side_check:
            self._display_memory.scope_mode = 'EYE'
            self._display_memory.channel_display = 'ENABLE'
            self._write(':MEASure:EYE:PNM:SOURce {}'.format(self._handle))

            if eye == '_all_':
                eyes = 3
                eye = 0
            elif isinstance(eye, int) and 0 <= eye <= 2:
                eyes = 1
            else:
                raise ValueError('Eye integer or string "_all_" are allowed inputs')

            result = {}
            for n in range(eyes):
                self._write(':MEAS:EYE:PNM:EYE EYE{0}'.format(eye + n))
                self._write(':MEASure:EYE:PNM:SIDe {0}'.format(side.upper()))
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEASure:EYE:PNM', dummy_data=1.0)
                value = float(self._read(':MEASure:EYE:PNM?'))
                if eyes == 1:
                    return value

                result['EYE_{}'.format(eye + n)] = value
            return result
        else:
            raise ValueError('Side parameter must be one of the following... \n{0}'.format(side_check))

    def partial_ser(self, side):
        """
        Partial SER measurement

        :param side: Selects which side of the waveform the measurement will be performed on
        :type side: str
        :return: partial noise margin
        :rtype: float
        """
        side_check = ('LEFT', 'RIGHT')
        if side.upper() in side_check:
            self._display_memory.scope_mode = 'EYE'
            self._display_memory.channel_display = 'ENABLE'
            self._write(':MEASure:EYE:PSER:SOURce1 {0}'.format(self._handle))
            self._write(':MEASure:EYE:PSER:SIDe {0}'.format(side.upper()))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:EYE:PSER', dummy_data=1.0)
            return float(self._read(':MEASure:EYE:PSER?'))
        else:
            raise ValueError('SIDE parameter must be one of the following... \n{0}'.format(side_check))

    def tdec(self):
        """
        Tranmitter and Dispersion Eye Closure measurement

        :return: TDEC
        :rtype: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:TDEC:SOURce1 {0}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:EYE:TDEC', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:TDEC?'))

    def partial_tdecq(self, eye='_all_', side=None):
        """
        Partial Transmitter and Dispersion Eye Closure Quaternary measurement

        :param eye: Selects which eye the measurement will be performed on
        :type eye: int
        :param side: 'LEFT' or 'RIGHT'. Selects which side of the waveform the measurement will be performed on
        :type side: str
        :return: partial tdecq
        :rtype: float
        """
        if not side:
            raise ValueError('SIDE parameter does not have a default value.')
        side_check = ('LEFT', 'RIGHT')
        if side in side_check:
            self._display_memory.scope_mode = 'EYE'
            self._display_memory.channel_display = 'ENABLE'
            self._write(':MEASure:EYE:PAM:PTD:SOURce {}'.format(self._handle))

            if eye == '_all_':
                eyes = 3
                eye = 0
            elif isinstance(eye, int) and 0 <= eye <= 2:
                eyes = 1
            else:
                raise ValueError('Eye integer or string "_all_" are allowed inputs')

            result = {}
            for n in range(eyes):
                self._write(':MEAS:EYE:PAM:PTD:EYE EYE{0}'.format(eye + n))
                self._write(':MEASure:EYE:PTD:SIDe {0}'.format(side.upper()))
                if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                    self._write(':MEASure:EYE:PAM:PTD', dummy_data=1.0)
                value = float(self._read(':MEASure:EYE:PAM:PTD?'))
                if eyes == 1:
                    return value

                result['EYE_{}'.format(eye + n)] = value
            return result
        else:
            raise ValueError('Side parameter must be one of the following... \n{0}'.format(side_check))

    def tdecq(self):
        """
        Transmitter and Dispersion Eye Closure measurement

        :return: partial noise margin
        :rtype: float
        """
        self._display_memory.scope_mode = 'EYE'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:EYE:TDEQ:SOURce1 {}'.format(self._handle))
        if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
            self._write(':MEASure:EYE:TDEQ', dummy_data=1.0)
        return float(self._read(':MEASure:EYE:TDEQ?'))

    @property
    def units_amplitude(self):
        """
        Sets the units for the returned amplitude type measurements

        :value: - 'AMPLITUDE'
                - 'PERCENT'
        :type: str
        :raise ValueError: exception if input is not VOLTS or PERCENT
        """
        return self._read(':MEAS:PAM:AMPL:UNIT?')

    @units_amplitude.setter
    def units_amplitude(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not VOLTS or PERCENT
        """
        output_dict = {'AMPLITUDE': 'AMPL', 'PERCENT': 'PERC'}
        self._write(':MEAS:PAM:AMPL:UNIT {0}'.format(output_dict[value.upper()]))

    @property
    def units_time(self):
        """
        Sets the units for the returned time type measurements

        :value: - 'SECONDS'
                - 'UI'
        :type: str
        :raise ValueError: exception if input is not SECONDS or UI
        """
        return self._read(':MEAS:PAM:EYE:TIME:UNIT?')

    @units_time.setter
    def units_time(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not SECONDS or UI
        """
        output_dict = {'SECONDS': 'SEC', 'UI': 'UINT'}
        self._write(':MEAS:PAM:EYE:TIME:UNIT {0}'.format(output_dict[value.upper()]))


class Keysight86100XEyeMaskTest(BaseEquipmentBlock):
    """
    Keysight86100X Mask Test block driver
    """

    def __init__(self, module_id, channel_number, handle, display_memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = display_memory

    @property
    def hit_ratio(self):
        """
        :value: hit ratio
        :type: float
        :raise ValueError: exception if margin type is not 'AUTO_HIT_RATIO'
        """
        margin_type = self.margin_type
        if margin_type == 'AUTO_HIT_RATIO':
            return float(self._read(':MEASure:MTESt1:HRatio?'))
        else:
            raise ValueError('Hit Ratio is only available when margin_type is "AUTO_HIT_RATIO"')

    @property
    def hit_ratio_confidence(self):
        """
        :value: hit ratio confidence (+/-)
        :type: float
        :raise ValueError: exception if margin type is not 'AUTO_HIT_RATIO'
        """
        margin_type = self.margin_type
        if margin_type == 'AUTO_HIT_RATIO':
            return float(self._read(':MEASure:MTESt1:MUNCertainty?'))
        else:
            raise ValueError('Hit Ratio Confidence is only available when '
                             'margin_type is "AUTO_HIT_RATIO"')

    @property
    def margin(self):
        """
        **READONLY**

        :value: returns mask margin
        :type: float
        """
        return float(self._read(':MEAS:MTESt1:MARG?'))

    @property
    def margin_hits(self):
        """
        **READONLY**

        :value: returns mask test margin hits
        :type: float
        """
        return float(self._read(':MEAS:MTESt1:MHIT?'))

    @property
    def margin_state(self):
        """
        Disable or Enable mask test margins

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":MTESt1:MARGin:STATe?")]

    @margin_state.setter
    def margin_state(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':MTESt1:MARGin:STATe {}'.format(input_dict[value]))

    @property
    def margin_type(self):
        """
        margin_type will set or return combined margin type :
        Manual mode, Auto mode with hit count, Auto mode with Hit Ratio.

        :value: - 'AUTO_HIT_RATIO'
                - 'AUTO_HIT_COUNT'
                - 'MANUAL'
        :type: str
        :raise ValueError: exception if input is not AUTO_HIT_RATIO/AUTO_HIT_COUNT/MANUAL
        """
        output_dict = {'AUTO': 'AUTO', 'MAN': 'MANUAL', 'DUMMY_DATA': 'AUTO', 'HRAT': 'AUTO',
                       'HITS': 'AUTO'}
        method = output_dict[self._read(":MTESt1:MARGin:METHod?")]
        if method == 'AUTO':
            auto_type = self._read(':MTESt1:MARGin:AUTo:METHod?')
            if auto_type == 'HRAT':
                return 'AUTO_HIT_RATIO'
            else:
                return 'AUTO_HIT_COUNT'
        else:
            return 'MANUAL'

    @margin_type.setter
    def margin_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not AUTO_HIT_RATIO/AUTO_HIT_COUNT/MANUAL
        """
        value = value.upper()
        input_dict = {'AUTO_HIT_RATIO': ['AUTO', 'HRAT'],
                      'AUTO_HIT_COUNT': ['AUTO', 'HITS'],
                      'MANUAL': ['MAN']}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "AUTO_HIT_RATIO",'
                             ' "AUTO_HIT_COUNT" or "MANUAL"')
        else:
            self._write(':MTESt1:MARGin:METHod {}'.format(input_dict[value][0]))
            if input_dict[value][0] == 'AUTO':
                self._write(':MTESt1:MARGin:AUTo:METHod {}'.format(input_dict[value][1]))

    @property
    def margin_value(self):
        """
        Specify margin value (Manual mask margin value, Hit count or Hit ratio.
        Depends on margin_type)

        :value: eye mask test margin value
        :type: float
        """
        margin_type = self.margin_type
        if margin_type == 'AUTO_HIT_RATIO':
            return float(self._read(':MTESt1:MARGin:AUTo:HRATio?'))
        elif margin_type == 'AUTO_HIT_COUNT':
            return int(self._read(':MTESt1:MARGin:AUTo:HITS?'))
        else:
            return float(self._read(':MTESt1:MARGin:PERCent?'))

    @margin_value.setter
    def margin_value(self, value):
        """
        :type value: float
        """
        margin_type = self.margin_type
        if margin_type == 'AUTO_HIT_RATIO':
            self._write(':MTESt1:MARGin:AUTo:HRATio {}'.format(float(value)))
        elif margin_type == 'AUTO_HIT_COUNT':
            self._write(':MTESt1:MARGin:AUTo:HITS {}'.format(int(value)))
        else:
            self._write(':MTESt1:MARGin:PERCent {}'.format(float(value)))

    @property
    def samples(self):
        """
        **READONLY**

        :value: number of samples in 1 UI reporte in Mask test
        :type: float
        """
        return float(self._read(':MEAS:MTESt1:NSAM?'))

    @property
    def standard_hits(self):
        """
        **READONLY**

        Returns total standard mask violations in mask test.

        :value: mask hits
        :type: float
        """
        return float(self._read(':MEAS:MTESt1:HITS?'))

    @property
    def waveforms(self):
        """
        **READONLY**

        :value: number of waveforms in Mask test
        :type: float
        """
        return float(self._read(':MEAS:MTESt1:NWAV?'))

    def load(self, file):
        """
        Load mask file name

        :param file: file path
        :type file: str
        """
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MTEST1:SOURce {}'.format(self._handle))
        self._write(':MTESt1:LOAD:FNAMe "{}"'.format(file))
        self._write(':MTESt1:LOAD', dummy_data=1.0)

    def start(self):
        """
        Method to turn on test display and start it
        """
        self._write(':MTEST1:DISP ON')

    def stop(self):
        """
        Method to turn off test display and stop it
        """
        self._write(':MTEST1:DISP OFF')


class Keysight86100XJitterMeasurement(Keysight86100XMeasurement):
    """
    Keysight86618A Measurement block driver
    """

    def __init__(self, module_id, channel_number, handle, display_memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._module_id = module_id
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = display_memory

    def measurement_list_default(self, signal_type):
        # TODO: Revisit signal type usage to make easier for users
        """
        Resets the jitter Results table to show the default set of measurements. Valid inputs are 'NRZ' or 'PAM'

        :raise ValueError: Exception if input is not NRZ or PAM
        """
        if signal_type == 'NRZ':
            self._write(':MEAS:JITT:LIST:DEF')
        elif signal_type == 'PAM':
            self._write(':MEAS:PEYE:LIST:DEF')
        else:
            raise ValueError('Valid types are "NRZ" or "PAM"')

    def level_amplitude(self, level='_all_'):
        """
        Amplitude for specified level

        :param level: Selects which level the measurement will be performed on
        :type level: int or str
        :return: level amplitude
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:AMPL:LEV:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEASure:AMPL:LEV:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:AMPL:LEV', dummy_data=1.0)

            value = float(self._read(':MEASure:AMPL:LEV?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def ti(self, level='_all_'):
        """
        Total Interference for specified level (1e-5)

        :param level: Selects which level the measurement will be performed on
        :type level: int or str
        :return: total interference per level
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:AMPL:TI:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEASure:AMPL:TI:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:AMPL:TI', dummy_data=1.0)

            value = float(self._read(':MEASure:AMPL:TI?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def rn_rms(self, level='_all_'):
        """
        Random Noise for specified level

        :param level: Selects which level the measurement will be performed on
        :type level: int or str
        :return: Random Noise per level
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:AMPL:RN:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEASure:AMPL:RN:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:AMPL:RN', dummy_data=1.0)

            value = float(self._read(':MEASure:AMPL:RN?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def di_dd(self, level='_all_'):
        """
        Deterministic Interference for specified level

        :param level: Selects which level the measurement will be performed on
        :type level: int or str
        :return: Deterministic Interference per level
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:AMPL:DI:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEASure:AMPL:DI:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:AMPL:DI', dummy_data=1.0)

            value = float(self._read(':MEASure:AMPL:DI?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def isi_pp(self, level='_all_'):
        """
        Inter-Symbol Interference for specified level

        :param level: Selects which level the measurement will be performed on
        :type level: int or str
        :return: Inter-Symbol Interference per level
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:AMPL:ISI:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEASure:AMPL:ISI:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:AMPL:ISI', dummy_data=1.0)

            value = float(self._read(':MEASure:AMPL:ISI?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def pi_dd(self, level='_all_'):
        """
        Dual-dirac Periodic Interference for specified level

        :param level: Selects which level the measurement will be performed on
        :type level: int or str
        :return: Dual-dirac Periodic Interference per level
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:AMPL:PI:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEASure:AMPL:PI:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:AMPL:PI', dummy_data=1.0)

            value = float(self._read(':MEASure:AMPL:PI?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def pi_rms(self, level='_all_'):
        """
        RMS Periodic Interference for specified level

        :param level: Selects which level the measurement will be performed on
        :type level: int or str
        :return: RMS Periodic Interference per level
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEASure:AMPL:PIR:SOURce {}'.format(self._handle))

        if level == '_all_':
            levels = 4
            level = 0
        elif isinstance(level, int) and 0 <= level <= 3:
            levels = 1
        else:
            raise ValueError('Level integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(levels):
            self._write(':MEASure:AMPL:PIR:LEV LEV{0}'.format(level + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEASure:AMPL:PIR', dummy_data=1.0)

            value = float(self._read(':MEASure:AMPL:PIR?'))
            if levels == 1:
                return value

            result['LEVEL_{}'.format(n)] = value
        return result

    def signal_amplitude(self):
        """
        Signal Amplitude Measurement

        :return: amplitude, mV
        :rtype: float
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:AMPL:SAMP:SOURce1 {}'.format(self._handle))
        return float(self._read(':MEAS:AMPL:SAMP?'))

    def buj(self):
        """
        Bounded Uncorrelated Jitter Measurement

        :return: BUJ value
        :rtype: float
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:BUJ:SOURce1 {}'.format(self._handle))
        return float(self._read(':MEAS:JITT:BUJ?'))

    def buj_status(self):
        """
        Bounded Uncorrelated Jitter Measurement status

        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        return str(self._read(':MEAS:JITT:BUJ:STATus?'))

    def dcd(self, eye='_all_'):
        """
        Duty Cycle Distortion Measurement

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: DCD value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:DCD:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:DCD:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:DCD', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:DCD?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def dcd_status(self, eye='_all_'):
        """
        Duty Cycle Distortion  Measurement status

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:DCD:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:DCD:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:DCD:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    def dj(self, eye='_all_'):
        """
        Deterministic jitter measurement

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int or str
        :return: DJ value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:DJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:DJ:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:DJ', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:DJ?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def dj_status(self, eye='_all_'):
        """
        Deterministic jitter  Measurement status

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:DJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:DJ:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:DJ:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    def ddj(self, eye='_all_'):
        """
        Data-Dependent jitter measurement

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int or str
        :return: DDJ value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:DDJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:DDJ:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:DDJ', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:DDJ?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def ddj_status(self, eye='_all_'):
        """
        Data-Dependent jitter Measurement status

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:DDJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:DDJ:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:DDJ:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    def eoj(self, edge):
        """
        Even-Odd jitter measurement

        :param edge: Selects which edge the measurement will be performed on. 'ALL', 'R13', 'F32', etc
        :type edge: str
        :return: EOJ value
        :rtype: float or dict
        """
        if self.mode_twelve_edge == 'DISABLE':
            raise ValueError('Jitter mode must have twelve edge mode enabled to use this measurement')

        edge_check = ('ALL',
                      'R01', 'R02', 'R03', 'R12', 'R13', 'R23',
                      'F10', 'F20', 'F30', 'F21', 'F31', 'F32')
        if edge in edge_check:
            self._display_memory.scope_mode = 'JITT'
            self._display_memory.channel_display = 'ENABLE'
            self._write(':MEAS:JITT:OJIT:EOJ:SOURce1 {}'.format(self._handle))
            self._write(':MEAS:JITT:OJIT:EOJ:ECAT {0}'.format(edge))
            return float(self._read(':MEAS:JITT:OJIT:EOJ?'))
        else:
            raise ValueError('EDGE parameter must be one of the following...\n{0}'.format(edge_check))

    def eoj_status(self):
        """
        Even-Odd jitter measurement status

        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        return str(self._read(':MEAS:JITT:OJIT:EOJ:STATus?'))

    def isi(self, eye='_all_'):
        """
        Inter-Symbol Interference measurement

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int or str
        :return: ISI value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:ISI:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:ISI:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:ISI', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:ISI?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def isi_status(self, eye='_all_'):
        """
        Inter-Symbol Interference  Measurement status

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:ISI:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:ISI:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:ISI:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    def jn(self, eye='_all_', ber=None):
        """
        Total Jitter associated with specific symbol error ratio measurement

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int
        :param ber: - 'J1' (2.5x10^-2)
                     - 'J2' (2.5x10^-3)
                     - 'J3' (2.5x10^-4)
                     - 'J4' (2.5x10^-5)
                     - 'J5' (2.5x10^-6)
                     - 'J6' (2.5x10^-7)
                     - 'J7' (2.5x10^-8)
                     - 'J8' (2.5x10^-9)
                     - 'J9' (2.5x10^-10)
        :type ber: str
        :return: JN value
        :rtype: float
        """
        if not ber:
            raise ValueError('BER parameter does not have a default value.')

        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:JN:SOURce1 {}'.format(self._handle))
        self._write(':MEAS:JITT:JN:SJN {0}'.format(ber))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:JN:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:JN', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:JN?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def jn_status(self, eye='_all_'):
        """
        Total Jitter associated with specific symbol error ratio Measurement status

        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """

        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:JN:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:JN:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:JN:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    def j4u(self, edge):
        """
        Jitter measurement for specific edge

        :param edge: Selects which edge the measurement will be performed on
        :type edge: str
        :return: j4u value
        :rtype: float or dict
        """
        if self.mode_twelve_edge == 'DISABLE':
            raise ValueError('Jitter mode must have twelve edge mode enabled to use this measurement')

        edge_check = ('ALL',
                      'R01', 'R02', 'R03', 'R12', 'R13', 'R23',
                      'F10', 'F20', 'F30', 'F21', 'F31', 'F32')
        if edge in edge_check:
            self._display_memory.scope_mode = 'JITT'
            self._display_memory.channel_display = 'ENABLE'
            self._write(':MEAS:JITT:OJIT:J4U:ECAT {0}'.format(edge))
            return float(self._read(':MEAS:JITT:OJIT:J4U?'))
        else:
            raise ValueError('EDGE parameter must be one of the following...\n{0}'.format(edge_check))

    def j4u_status(self):
        """
        Jitter measurement status for specific edge and probability

        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        return str(self._read(':MEAS:JITT:OJIT:J4U:STATus?'))

    def jrms(self, edge):
        """
        RMS jitter measurement for specific edge

        :param edge: Selects which edge the measurement will be performed on
        :type edge: str
        :return: jrms value
        :rtype: float or dict
        """
        if self.mode_twelve_edge == 'DISABLE':
            raise ValueError('Jitter mode must have twelve edge mode enabled to use this measurement')

        edge_check = ('ALL',
                      'R01', 'R02', 'R03', 'R12', 'R13', 'R23',
                      'F10', 'F20', 'F30', 'F21', 'F31', 'F32')
        if edge in edge_check:
            self._display_memory.scope_mode = 'JITT'
            self._display_memory.channel_display = 'ENABLE'
            self._write(':MEAS:JITT:OJIT:JRMS:SOURce1 {}'.format(self._handle))
            self._write(':MEAS:JITT:OJIT:JRMS:ECAT {0}'.format(edge))
            return float(self._read(':MEAS:JITT:OJIT:JRMS?'))
        else:
            raise ValueError('EDGE parameter must be one of the following...\n{0}'.format(edge_check))

    def jrms_status(self):
        """
        RMS jitter measurement status for specific edge

        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        return str(self._read(':MEAS:JITT:OJIT:JRMS:STATus?'))

    def level_eye(self, eye):
        """
        Jitter Sampling level. Amplitude at which jitter measurements are made

        :param eye: Selects which eye the measurement will be performed on
        :type eye: int or str
        :return: eye level amplitude
        :rtype: float or list of float
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:LEV:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:LEV:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:LEV', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:LEV?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def level_eye_status(self, eye='_all_'):
        """
        Jitter sampling level measurement status for specific eye

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:LEV:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:LEV:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:LEV:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    @property
    def mode_twelve_edge(self):
        """
        Enables or disables 12-Edge Output Jitter Measurements

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read(':MEAS:JITT:OJIT:STAT?')]

    @mode_twelve_edge.setter
    def mode_twelve_edge(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        self._write(':MEAS:JITT:OJIT:STAT {0}'.format(output_dict[value]))

    def pj(self, eye='_all_'):
        """
        Periodic Jitter measurement

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int or str
        :return: PJ value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:PJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:PJ:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:PJ', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:PJ?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def pj_status(self, eye='_all_'):
        """
        Periodic Jitter Measurement status

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:PJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:PJ:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:PJ:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    def rj(self, eye='_all_'):
        """
        Random Jitter measurement

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int or str
        :return: RJ value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:RJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:RJ:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:RJ', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:RJ?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def rj_status(self, eye='_all_'):
        """
        Random Jitter Measurement status

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:RJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:RJ:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:RJ:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    def tj(self, eye='_all_'):
        """
        Total Jitter measurement

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int or str
        :return: TJ value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:TJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:TJ:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:TJ', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:TJ?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def tj_status(self, eye='_all_'):
        """
        Total Jitter Measurement status

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:TJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:TJ:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:TJ:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    def uj(self, eye='_all_'):
        """
        Uncorrelated Jitter measurement

        :param eye: Selects which eye the measurement will be performed on 
        :type eye: int or str
        :return: UJ value
        :rtype: float or dict
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:UJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:UJ:EYE EYE{0}'.format(eye + n))
            if Keysight86100XMeasurement._DISPLAY_MEASUREMENTS:
                self._write(':MEAS:JITT:UJ', dummy_data=1.0)
            value = float(self._read(':MEAS:JITT:UJ?'))
            if eyes == 1:
                return value

            result['EYE_{}'.format(eye + n)] = value
        return result

    def uj_status(self, eye='_all_'):
        """
        Uncorrelated Jitter Measurement status

        :param eye: Selects which eye the measurement will be performed on (0-2)
        :type eye: int or str
        :return: - 'CORR' - result is correct
                  - 'INV' - result is invalid
                  - 'QUES' - result is questionable
        :rtype: str
        """
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        self._write(':MEAS:JITT:UJ:SOURce1 {}'.format(self._handle))

        if eye == '_all_':
            eyes = 3
            eye = 0
        elif isinstance(eye, int) and 0 <= eye <= 2:
            eyes = 1
        else:
            raise ValueError('Eye integer or string "_all_" are allowed inputs')

        result = {}
        for n in range(eyes):
            self._write(':MEAS:JITT:UJ:EYE EYE{0}'.format(eye + n))
            value = str(self._read(':MEAS:JITT:UJ:STATus?'))
            result['EYE_{}'.format(eye + n)] = value
        return result

    @property
    def units_amplitude(self):
        """
        Sets the units for the returned amplitude type measurements

        :value: - 'VOLT'
                - 'UA'
        :type: str
        :raise ValueError: exception if input is not VOLTS or UA
        """
        return self._read(':MEAS:AMPL:DEF:UNIT?')

    @units_amplitude.setter
    def units_amplitude(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not VOLTS or PERCENT
        """
        output_dict = {'VOLT': 'VOLT', 'UA': 'UAMP'}
        self._write(':MEAS:AMPL:DEF:UNIT {0}'.format(output_dict[value.upper()]))

    @property
    def units_jitter(self):
        """
        Sets the units for the returned jitter type measurements

        :value: - 'SECONDS'
                - 'UI'
        :type: str
        :raise ValueError: exception if input is not VOLTS or PERCENT
        """
        return self._read(':MEAS:JITT:DEF:UNIT?')

    @units_jitter.setter
    def units_jitter(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not SECONDS or UI
        """
        output_dict = {'SECONDS': 'SEC', 'UI': 'UINT'}
        self._write(':MEAS:JITT:DEF:UNIT {0}'.format(output_dict[value.upper()]))

    def jitter_measurement(self, graph1, graph2=None, graph3=None, graph4=None):
        """
        Method to create a jitter measurement
        Valid measurement types are:
        - RJPJ
        - DDJ
        - TJ
        - DDJS
        - CTJ
        - CDD
        - RNPI
        - ISI
        - TI
        - CTI

        :param graph1: type of graph1
        :type graph1: str
        :param graph2: type of graph2
        :type graph2: str
        :param graph3: type of graph3
        :type graph3: str
        :param graph4: type of graph4
        :type graph4: str
        """
        input_dict = {'RJPJ': 'RJPJ', 'DDJ': 'DDJH', 'TJ': 'TJH', 'DDJS': 'DDJS',
                      'CTJ': 'CTJH', 'CDD': 'CDD', 'RNPI': 'RNPI', 'ISI': 'ISIH',
                      'TI': 'TIH', 'CTI': 'CTIH'}
        self._display_memory.scope_mode = 'JITT'
        self._display_memory.channel_display = 'ENABLE'
        if graph1 and not graph2 and not graph3 and not graph4:
            graph1 = graph1.upper()
            if graph1 in input_dict:
                self._write(':DISPlay:JITTer:LAYout SINGle', dummy_data=1.0)
                self._write(':DISPlay:JITTer:GRAPh1:TYPE {}'.format(input_dict[graph1]))
            else:
                raise ValueError('Please specify a valid measurement: []')
        elif graph1 and graph2 and not graph3 and not graph4:
            graph1 = graph1.upper()
            graph2 = graph2.upper()
            if graph1 in input_dict and graph2 in input_dict:
                self._write(':DISPlay:JITTer:LAYout SPLit', dummy_data=1.0)
                self._write(':DISPlay:JITTer:GRAPh1:TYPE {}'.format(input_dict[graph1]))
                self._write(':DISPlay:JITTer:GRAPh2:TYPE {}'.format(input_dict[graph2]))
            else:
                raise ValueError('Please specify a valid measurement: []')
        elif graph1 and graph2 and graph3 and not graph4:
            graph1 = graph1.upper()
            graph2 = graph2.upper()
            graph3 = graph3.upper()
            if graph1 in input_dict and graph2 in input_dict and graph3 in input_dict:
                self._write(':DISPlay:JITTer:LAYout QUAD', dummy_data=1.0)
                self._write(':DISPlay:JITTer:GRAPh1:TYPE {}'.format(input_dict[graph1]))
                self._write(':DISPlay:JITTer:GRAPh2:TYPE {}'.format(input_dict[graph2]))
                self._write(':DISPlay:JITTer:GRAPh3:TYPE {}'.format(input_dict[graph3]))
            else:
                raise ValueError('Please specify a valid measurement: []')
        else:
            graph1 = graph1.upper()
            graph2 = graph2.upper()
            graph3 = graph3.upper()
            graph4 = graph4.upper()
            if (graph1 in input_dict and graph2 in input_dict and graph3 in input_dict
                    and graph4 in input_dict):
                self._write(':DISPlay:JITTer:LAYout QUAD', dummy_data=1.0)
                self._write(':DISPlay:JITTer:GRAPh1:TYPE {}'.format(input_dict[graph1]))
                self._write(':DISPlay:JITTer:GRAPh2:TYPE {}'.format(input_dict[graph2]))
                self._write(':DISPlay:JITTer:GRAPh3:TYPE {}'.format(input_dict[graph3]))
                self._write(':DISPlay:JITTer:GRAPh4:TYPE {}'.format(input_dict[graph4]))


class Keysight86100XHistogram(BaseEquipmentBlock):
    """
    Keysight86100X Histogram block driver
    """
    CAPABILITY = {'v_size': {'min': 1.0, 'max': 10.0},
                  'h_size': {'min': 1.0, 'max': 8.0}}

    def __init__(self, hist_id, module_id, channel_number, handle, display_memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._hist_id = hist_id
        self._module_id = module_id
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = display_memory

    def _get_configuration(self):
        """
        Overriding this method to allow for load_configuration to work
        """
        # Loading did not work unless the state of the histograms is, loaded (which
        # sets invalid values to their max/min), then saved again. That way, the next load should
        # work

        data = super()._get_configuration()  # saving the state of the histograms for the 1st time
        try:
            self._set_configuration(data)  # try loading
        except RuntimeError:
            data = super()._get_configuration()  # save again if the loading failed

        return data

    @property
    def border(self):
        """
        Disable or Enable border display

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read(":HISTogram{}:WINDow:BORDer?".format(self._hist_id),
                                      dummy_data='OFF')]

    @border.setter
    def border(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':HISTogram{}:WINDow:BORDer {}'.format(self._hist_id, input_dict[value]))

    @property
    def mean(self):
        """
        **READONLY**

        :value: mean in seconds
        :type: float
        """
        if self.state == 'ENABLE':
            return float(self._read(':MEAS:HISTogram{}:MEAN?'.format(self._hist_id)))

    @property
    def peak_position(self):
        """
        **READONLY**

        :value: peak position in seconds
        :type: float
        """
        if self.state == 'ENABLE':
            return float(self._read(':MEAS:HISTogram{}:PPOS?'.format(self._hist_id)))

    @property
    def pp(self):
        """
        **READONLY**

        The width of the histogram.

        :value: peak to peak in seconds
        :type: float
        """
        if self.state == 'ENABLE':
            return float(self._read(':MEAS:HISTogram{}:PP?'.format(self._hist_id)))

    @property
    def placement(self):
        """
        Histogram placement

        :value: - 'LEFT'
                - 'RIGHT'
                - 'BOTTOM'
                - 'TOP'
        :type: str
        :raise ValueError: exception if input is not "LEFT", "RIGHT", "TOP" or "BOTTOM"
        """
        output_dict = {'LEFT': 'LEFT', 'RIGH': 'RIGHT', 'BOTT': 'BOTTOM', 'TOP': 'TOP'}
        return output_dict[self._read(':HISTogram{}:AXIS?'.format(self._hist_id),
                                      dummy_data='LEFT')]

    @placement.setter
    def placement(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not "LEFT", "RIGHT", "TOP" or "BOTTOM"
        """
        value = value.upper()
        input_dict = {'LEFT': 'LEFT', 'RIGHT': 'RIGH', 'BOTTOM': 'BOTT', 'TOP': 'TOP'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "LEFT", "RIGHT", "TOP" or "BOTTOM"')
        else:
            self._write(':HISTogram{}:AXIS {}'.format(self._hist_id, input_dict[value]))

    @property
    def scale(self):
        """
        Histogram scale

        :value: - 'LINEAR'
                - 'LOG'
        :type: str
        :raise ValueError: exception if input is not "LINEAR" or "LOG"
        """
        output_dict = {'LIN': 'LINEAR', 'LOG': 'LOG'}
        return output_dict[self._read(':HISTogram{}:SCALe?'.format(self._hist_id),
                                      dummy_data='LIN')]

    @scale.setter
    def scale(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not "LINEAR" or "LOG"
        """
        value = value.upper()
        input_dict = {'LINEAR': 'LIN', 'LOG': 'LOG'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "LINEAR" or "LOG"')
        else:
            self._write(':HISTogram{}:SCALe {}'.format(self._hist_id, input_dict[value]))

    @property
    def size(self):
        """
        :value: histogram size
        :type: float
        :raise ValueError: exception if size not between 1.0 and 10.0 or 1.0 and 8.0
        """
        if self.placement in ['LEFT', 'RIGHT']:
            return float(self._read(':HISTogram{}:VSIZe?'.format(self._hist_id)))
        else:
            return float(self._read(':HISTogram{}:HSIZe?'.format(self._hist_id)))

    @size.setter
    def size(self, value):
        """
        :type value: float
        :raise ValueError: exception if size not between 1.0 and 10.0 or 1.0 and 8.0
        """
        if self.placement in ['LEFT', 'RIGHT']:
            if self.CAPABILITY['v_size']['min'] <= value <= self.CAPABILITY['v_size']['max']:
                self._write(':HISTogram{}:VSIZe {}'.format(self._hist_id, value))
            else:
                raise ValueError('Size must be between {} and {}'.format(
                    self.CAPABILITY['v_size']['min'], self.CAPABILITY['v_size']['max']))
        elif self.CAPABILITY['h_size']['min'] <= value <= self.CAPABILITY['h_size']['max']:
            self._write(':HISTogram{}:HSIZe {}'.format(self._hist_id, value))
        else:
            raise ValueError('Size must be between {} and {}'.format(
                self.CAPABILITY['h_size']['min'], self.CAPABILITY['h_size']['max']))

    @property
    def state(self):
        """
        Disable or Enable histogram display

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":HISTogram{}:DISPlay?".format(self._hist_id))]

    @state.setter
    def state(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        self._display_memory.channel_display = 'ENABLE'
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':HISTogram{}:SOURce {}'.format(self._hist_id, self._handle))
            self._write(':HISTogram{}:DISPlay {}'.format(self._hist_id, input_dict[value]))

    @property
    def std_dev(self):
        """
        **READONLY**

        :value: standard deviation in seconds
        :type: float
        """
        if self.state == 'ENABLE':
            return float(self._read(':MEAS:HISTogram{}:STDDev?'.format(self._hist_id)))

    @property
    def x1(self):
        """
        :value: x1 coordinate in s
        :type: float
        """
        return float(self._read(':HISTogram{}:WINDow:X1?'.format(self._hist_id)))

    @x1.setter
    def x1(self, value):
        """
        :type value: float
        """
        self._write(':HISTogram{}:WINDow:X1 {}'.format(self._hist_id, value))

    @property
    def x2(self):
        """
        :value: x2 coordinate in s
        :type: float
        """
        return float(self._read(':HISTogram{}:WINDow:X2?'.format(self._hist_id)))

    @x2.setter
    def x2(self, value):
        """
        :type value: float
        """
        self._write(':HISTogram{}:WINDow:X2 {}'.format(self._hist_id, value))

    @property
    def y1(self):
        """
        :value: y1 coordinate in volts
        :type: float
        """
        return float(self._read(':HISTogram{}:WINDow:Y1?'.format(self._hist_id)))

    @y1.setter
    def y1(self, value):
        """
        :type value: float
        """
        self._write(':HISTogram{}:WINDow:Y1 {}'.format(self._hist_id, value))

    @property
    def y2(self):
        """
        :value: y2 coordinate in volts
        :type: float
        """
        return float(self._read(':HISTogram{}:WINDow:Y1?'.format(self._hist_id)))

    @y2.setter
    def y2(self, value):
        """
        :type value: float
        """
        self._write(':HISTogram{}:WINDow:Y1 {}'.format(self._hist_id, value))

    def default_window(self):
        """
        Reset histogram window to default parameters
        """
        self._write(':HISTogram1:WINDow:DEFault')


class Keysight86100DPrecisionTimebase(BaseEquipmentBlock):
    """
    Keysight86100D Precision Timebase
    """
    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    def find_symbol_sequence(self, sequence, channel):
        """
        Configures the scope to find the specified symbol sequence with the locked pattern

        :param sequence: Custom symbol sequence. Valid characters are  0,1,2,3, and ?(wildcard)
        :type sequence: str
        :param channel: Specify which channel to find the sequence on ('CHAN1A', 'DIFF2C', 'FUNC15').
        :type channel: str
        """
        if not isinstance(sequence, str):
            raise TypeError('sequence parameter must be a string')

        channel_check = ['CHAN', 'DIFF', 'FUNC']
        found = False
        for n in channel_check:
            if n in channel:
                found = True
                break

        if not found:
            raise ValueError('Channel parameter: "{0}", formatted incorrectly. Refer to DocString'.format(channel))

        ptn_length = int(self._read(':TRIG:PLEN?', dummy_data=8191))
        if ptn_length == 0:
            self.logger.warning('Pattern length equal to ZERO. Ensure signal is valid')
        self._write(':TIM:UIRange {0}'.format(ptn_length))
        self._write(':TIM:FIND:SIGNal {0}'.format(channel))
        self._write(':TIM:FIND:SEQ "{0}"'.format(sequence))

    def find_next_symbol_sequence(self):
        """
        Searches for the next specified symbol sequence in the pattern
        """
        self._write(':TIM:FIND:NEXT')

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
        return output_dict[self._read(":TIM:PTIM:RMEThod?", dummy_data='FAST')]

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
            self._write(':TIM:PTIM:RMEThod {}'.format(input_dict[value]))

    @property
    def ref_clock_auto(self):
        """
        Disable or Enable reference clock auto detect

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":TIM:PTIM:RFR:AUTO?")]

    @ref_clock_auto.setter
    def ref_clock_auto(self, value):  # TODO: Add Polling
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':TIM:PTIM:RFR:AUTO {}'.format(input_dict[value]), type_='stb_poll_sync')

    @property
    def ref_clock_frequency(self):
        """
        Reference clock frequency

        :value: reference clock frequency in Hz
        :type: float
        """
        return float(self._read(":TIM:PTIM:RFR?"))

    @ref_clock_frequency.setter
    def ref_clock_frequency(self, value):
        """
        :type value: float
        """
        self.ref_clock_auto = 'DISABLE'
        self._write(':TIM:PTIM:RFR {:.6E}'.format(Decimal(value)))

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
        return output_dict[self._read(":TIM:PTIM:STAT?")]

    @state.setter
    def state(self, value):  # TODO: Add Polling
        """
        :type value: str
        :raise ValueError: exception if input is not "ENABLE" or "DISABLE"
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':TIM:PTIM:STAT {}'.format(input_dict[value]), type_='stb_poll_sync')

    @property
    def status(self):
        """
        ***READ-ONLY***

        Returns the status of the time reference.
        *When this command is used the bit is reset until time referenece lost is asserted again*

        :return: Time reference status
        :rtype: str
        """
        status = self._read(':STAT:PTIM:EVEN?')
        if status == '1':
            return 'INVALID'
        elif status == '0':
            return 'VALID'
        else:
            raise ValueError('Unexpected returned value')

    def reset_time_reference(self):
        """
        Resets time reference
        """
        self._write(':TIM:PTIM:RTR')


class Keysight86100DClockDataRecovery(BaseEquipmentBlock):
    """
    Keysight86100D Clock Data Recovery
    """
    def __init__(self, module_id, interface, dummy_mode, **kwargs):
        """
        Initialize instance
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)


class Keysight86100DTDECQ(BaseEquipmentBlock):
    """
    Keysight86100D TDECQ Configuration
    """
    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def histogram_width(self):
        """
        Sets the width of the two histograms that are used to configure an Eye mode PAM4 TDECQ measurement.\n
        Adjust this setting when FlexDCA is not in pattern lock.\n
        It adjusts the histogram window so that additional data can be acquired to decrease the measurement time.

        :value: Unit Interval (UI)
        :type: float
        """
        return float(self._read(':MEAS:TDEQ:HWID?'))

    @histogram_width.setter
    def histogram_width(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            if 0.01 <= value <= 0.1:
                self._write(':MEAS:TDEQ:HWID {0}'.format(value))
            else:
                raise ValueError('Valid input range is between 0.01 and 0.1 (inclusive)')
        else:
            raise TypeError("Value must be a float")

    @property
    def histogram_left_position(self):
        """
        Sets the position in UI (unit interval) of the left of two measurement histogram windows.\n
        Must turn histogram time optimization off to use this function.\n

        :value: Unit Interval (UI)
        :type: float
        """
        return float(self._read(':MEAS:TDEQ:LHTime?'))

    @histogram_left_position.setter
    def histogram_left_position(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            if 0.25 <= value <= 0.45:
                if self.histogram_optimize_times == 'DISABLE':
                    self._write(':MEAS:TDEQ:LHTime {0}'.format(value))
                else:
                    raise SystemError("Turn histogram time optimization on to change histogram position")
            else:
                raise ValueError('Valid input range is between 0.25 and 0.45 (inclusive)')
        else:
            raise TypeError("Value must be a float")

    @property
    def histogram_optimize_times(self):
        """
        Time optimization can be used to reduce test times.\n
        Enabled - Allows you to adjust the spacing between the two measurement histograms.\n
        Disabled - Allows you to adjust the position of the left histogram.\n

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[(self._read(':MEAS:TDEQ:OHTime?'))]

    @histogram_optimize_times.setter
    def histogram_optimize_times(self, value):
        """
        :type value: str
        """
        output_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if isinstance(value, str):
            if value in output_dict:
                self._write(":MEAS:TDEQ:OHTime {0}".format(output_dict[value]))
        else:
            raise TypeError("Please enter the string 'ENABLE' or 'DISABLE'")

    @property
    def histogram_right_position(self):
        """
        Sets the position in UI (unit interval) of the right of two measurement histogram windows.\n
        Must turn histogram time optimization off to use this function.\n

        :value: Unit Interval (UI)
        :type: float
        """
        return float(self._read(':MEAS:TDEQ:RHTime?'))

    @histogram_right_position.setter
    def histogram_right_position(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            if 0.50 <= value <= 0.75:
                if self.histogram_optimize_times == 'DISABLE':
                    self._write(':MEAS:TDEQ:RHTime {0}'.format(value))
                else:
                    raise SystemError("Turn histogram time optimization on to change histogram position")
            else:
                raise ValueError('Valid input range is between 0.50 and 0.75 (inclusive)')
        else:
            raise TypeError("Value must be a float")

    @property
    def histogram_spacing(self):
        """
        Sets the time separation in UI between the left and the right measurement histogram windows.\n
        Must turn histogram time optimization on to use this function.\n

        :value: Unit Interval (UI)
        :type: float
        """
        return float(self._read(':MEAS:TDEQ:OHSeparation?'))

    @histogram_spacing.setter
    def histogram_spacing(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            if 0.0 <= value <= 0.25:
                if self.histogram_optimize_times == 'ENABLE':
                    self._write(':MEAS:TDEQ:OHSeparation {0}'.format(value))
                else:
                    raise SystemError("Turn histogram time optimization on to change spacing")
            else:
                raise ValueError('Valid input range is between 0.0 and 0.25 (inclusive)')
        else:
            raise TypeError("Value must be a float")

    @property
    def threshold_optimization(self):
        """
        Enables threshold optimization where you can move the thresholds of Eye mode's PAM4 TDECQ measurement .\n
        The thresholds can be moved by at most one percent of Outer OMA.\n

        :value: - 'ENABLE'
                - 'DISABLE
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[(self._read(':MEAS:TDEQ:OHTHresholds?'))]

    @threshold_optimization.setter
    def threshold_optimization(self, value):
        """
        :type value: str
        """
        output_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if isinstance(value, str):
            if value in output_dict:
                self._write(":MEAS:TDEQ:OHTHresholds {0}".format(output_dict[value]))
        else:
            raise TypeError("Please enter the string 'ENABLE' or 'DISABLE'")

    @property
    def threshold_optimization_limit(self):
        """
        Sets a limit to which thresholds can be moved from the standard definition.

        :value: Percent
        :type: float
        """
        return float(self._read(':MEAS:TDEQ:TALimit?'))

    @threshold_optimization_limit.setter
    def threshold_optimization_limit(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            if 1.0 <= value <= 100.0:
                self._write(":MEAS:TDEQ:TALimit {0}".format(value))
            else:
                raise ValueError("Value must be within 1.0 and 100.0.")
        else:
            raise TypeError("Value must be a float.")

    @property
    def preset(self):
        """
        Loads a previously saved settings, known as a preset.\n
        Presets can only be saved from the measurements Setup dialog box. There is no programming command for this task.

        :value: Preset name
        :type: str
        """
        return self._read(':MEAS:TDEQ:PRESets?')

    @preset.setter
    def preset(self, value):
        """
        :type value: str
        """
        if isinstance(value, str):
            if value in self.preset_list:
                self._write(':MEAS:TDEQ:PRESets "{0}"'.format(value))
            else:
                raise ValueError("Specified preset is not a valid selection. "
                                 "Preset must be manually created on the scope.")
        else:
            raise TypeError("Value must be a string")

    @property
    def preset_list(self):
        """
        ***READ-ONLY***

        Returns a list of all saved presets that are available to be called from the CLI preset command

        :rtype: list of str
        """
        presets = self._read(":MEAS:TDEQ:PRES:SEL?")
        return presets[1:len(presets)-1].split(", ")

    @property
    def target_ser(self):
        """
        Sets the target SER (Symbol Error Rate) for the TDECQ measurement.\n
        The optical power penalty of the measured optical transmitter is based on the amount of noise that would
        need to be added to obtain a target SER.\n

        :value: Symbol Error Rate
        :type: float
        """
        return float(self._read(':MEAS:TDEQ:TSER?'))

    @target_ser.setter
    def target_ser(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            if 1e-12 <= value <= 1e-1:
                self._write(":MEAS:TDEQ:TSER {0}".format(value))
            else:
                raise ValueError("Value must be within 1e-12 and 1e-1.")
        else:
            raise TypeError("Value must be a float.")
