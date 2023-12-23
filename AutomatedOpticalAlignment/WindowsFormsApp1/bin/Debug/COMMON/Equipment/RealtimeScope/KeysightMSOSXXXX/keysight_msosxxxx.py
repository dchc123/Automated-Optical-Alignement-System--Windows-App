"""
| $Revision:: 281646                                   $:  Revision of last commit
| $Author:: wleung@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-16 20:09:50 +0100 (Thu, 16 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from decimal import Decimal
import time
from COMMON.Utilities.custom_structures import CustomList
from COMMON.Equipment.RealtimeScope.base_realtime_scope import BaseRealtimeScope
from COMMON.Equipment.RealtimeScope.base_realtime_scope import BaseRealtimeScopeChannel
from COMMON.Equipment.RealtimeScope.base_realtime_scope import BaseRealtimeScopeSubBlock
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_exceptions import NotSupportedError


class KeysightMSOSXXXX(BaseRealtimeScope):
    """
    Driver for Keysight MSOS series Real-time Scopes
    """
    CAPABILITY = {'horizontal_scale': {'min': None, 'max': None}}

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
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
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of KeysightMSOSXXXXChannel"""
        self.trigger = KeysightMSOSXXXXTrigger(interface=interface, dummy_mode=dummy_mode)
        self.function = CustomList()
        """:type: list of KeysightMSOSXXXXFunction"""
        self.digital_channel = CustomList(start_index=0)
        """:type: list of KeysightMSOSXXXXDigitalChannel"""
        self._mode = None
        self._file_base_name = ''
        self._image_file_format = ''

    @property
    def horizontal_scale(self):
        """
        Specify scope scale

        :value: time/div in seconds
        :type: float
        """
        return float(self._read(":TIMebase:SCALe?"))

    @horizontal_scale.setter
    def horizontal_scale(self, value):
        """
        :type: float
        """
        if (self.CAPABILITY['horizontal_scale']['min'] <= value <=
                self.CAPABILITY['horizontal_scale']['max']):
            self._write(":TIMebase:SCALe {:.2E}".format(Decimal(value)))
        else:
            raise ValueError('Please specify a value between {} and {}'.format(
                self.CAPABILITY['horizontal_scale']['min'],
                self.CAPABILITY['horizontal_scale']['max']))

    @property
    def label(self):
        """
        returns the state of the display of analog channel labels.Label names can be up to 6
        characters long

        :rtype: str ON|OFF
        """
        input_dict = {0: "OFF", 1: 'ON'}
        return input_dict[int(self._read(":DISPlay:LABel?"))]

    @label.setter
    def label(self, value):
        """
        turns on or off the display of analog channel labels. Label names can be up to 6 characters long
        :param value: 'on'|'off'
        :type value: str

        """
        value = value.upper()
        output_dict = {'ON': 'ON',
                       'OFF': 'OFF'
                       }
        self._write(f":DISPlay:LABel {output_dict[value]}")

    @property
    def position(self):
        """
        Specify scope scale

        :value: time in seconds
        :type: float
        """
        return float(self._read(":TIMebase:POSition?"))

    @position.setter
    def position(self, value):
        """
        :type: float
        """
        self._write(":TIMebase:POSition {:.2E}".format(Decimal(value)))

    @property
    def reference(self):
        """
        Specify scope reference

        :value: - 'CENTER'
                - 'LEFT'
                - 'RIGHT'
                - 'PERCENT
        :type: str
        :raise ValueError: exception if input is not CENTER/LEFT/RIGHT
        """
        output_dict = {'CENT': 'CENTER', 'LEFT': 'LEFT', 'RIGH': 'RIGHT', 'PERC': 'PERCENT'}
        return output_dict[self._read(":TIMebase:REFerence?", dummy_data='CENT')]

    @reference.setter
    def reference(self, value):
        """
        :type: str
        :raise ValueError: exception if input is not CENTER/LEFT/RIGHT
        """
        value = value.upper()
        input_dict = {'CENTER': 'CENT', 'LEFT': 'LEFT', 'RIGHT': 'RIGH', 'PERCENT': 'PERC'}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'CENTER' , 'LEFT', 'RIGHT' 'PERCENT'")
        else:
            self._write(":TIMebase:REFerence {}".format(value))

    @property
    def zoom(self):
        """

        :return: true if zoom is enabled
        :type: bool
        """
        return True if self._read(":TIMebase:VIEW?") == 'MAIN' else False

    @zoom.setter
    def zoom(self, value):
        """

        :value: true to enable zoom mode
        :type: bool
        """
        if value:
            self._write(":TIMebase:VIEW WINDow")
        else:
            self._write(":TIMebase:VIEW MAIN")

    @property
    def zoom_position(self):
        """

        :return: current horizontal position in the delayed view
        """
        return float(self._read(":TIMebase:WINDow:POSition?"))

    @zoom_position.setter
    def zoom_position(self, value):
        """

        :param value:  zoom window delay position
        :type value: float
        """
        self._write(":TIMebase:WINDow:POSition {:.2E}".format(Decimal(value)))

    @property
    def zoom_scale(self):
        """
        sets the time/div in the delayed view

        :return:  scaled window time, in seconds/div
        :type: float
        """
        return float(self._read(":TIMebase:WINDow:SCALe?"))

    @zoom_scale.setter
    def zoom_scale(self, value):
        """
        sets the time/div in the delayed view

        :param value:  zoom window scaled time in seconds/division
        :type value: float
        """
        self._write(":TIMebase:WINDow:SCALe {:.2E}".format(Decimal(value)))

    @property
    def measure_window(self):
        """

        :return: ZOOM, COLOR_GRADE or MAIN
        :type: str
        """
        output_dict = {'ZOOM': 'ZOOM', 'CGR': 'COLOUR_GRADE', 'MAIN': 'MAIN', 'ALL': 'MAIN'}
        return output_dict[self._read(":MEASure:WINDow?", dummy_data='MAIN')]

    @measure_window.setter
    def measure_window(self, value):
        input_dict = {'ZOOM': 'ZOOM', 'COLOUR_GRADE': 'CGR', 'MAIN': 'MAIN'}
        value = value.upper()
        if value not in input_dict.keys():
            raise ValueError(f"Please specify either {input_dict.keys()}")
        else:
            self._write(f":MEASure:WINDow {input_dict[value]}")

    @property
    def serial_data(self):
        """
        **READONLY**

        :value: returns a list of Real-time Scope serial data
        :type: list
        """
        return list(self._read(':LISTer:DATA?'))

    def clear_measurements(self):
        """
        Clears all measurements
        """
        self._write(':MEASure:CLEar')

    def reset_statistics(self):
        """
        Clears all measurements
        """
        self._write(':MEASure:STATistics:RESet')

    def save_image(self, file_name='image_', file_format='PNG'):
        """
        Saves screen image

        :param file_name:
        :type file_name:str
        :param file_format:
        :type file_format: str
        """
        valid_formats = ('TIF', 'GIF', 'BMP', 'JPEG', 'PNG')
        if file_format not in valid_formats:
            raise ValueError("Please specify file type as 'TIF', 'GIF', 'BMP', 'JPEG' or 'PNG'")

        self.logger.info("Writing {} to {}".format(file_name, self.working_directory))
        # time to allow the measurements to refresh, in case a measurement was read just before taking a screenshot
        time.sleep(0.2)
        self._write(f':DISK:SAVE:IMAGe "{file_name}", {file_format}', type_='stb_poll_sync')

    @property
    def working_directory(self):
        """
        The directory where files are saved

        :return:  directory where files are saved
        :rtype:  str
        """
        return self._read("DISK:PWD?")

    @working_directory.setter
    def working_directory(self, directory):
        """
        The directory where files are saved

        :param directory: sets the dir where files are saved
        :type:  str
        """
        self._write(':DISK:CDIRectory "{}"'.format(directory))

    def run(self):
        """
        Switches mode to RUN
        """
        self._write(':RUN')

    def single(self):
        """
        Switches mode to SINGLE
        """
        self._write(':SINGle')

    def stop(self):
        """
        Switches mode to STOP
        """
        self._write(':STOP')

    @property
    def mode(self):
        """

        :return:
        :rtype:
        """
        output_dict = {'RUN': 'RUN',
                       'STOP': 'STOP',
                       'SING': 'SINGLE'}
        return output_dict[self._read(":ASTate?")]

    @mode.setter
    def mode(self, value):
        """
        set the scope state to run, single or stop.
        :param value: RUN, SINGLE, STOP
        :type value: str
        """
        value = value.upper()
        input_dict = {'RUN': 'RUN',
                      'STOP': 'STOP',
                      'SINGLE': 'SING'}
        self._write(f":{input_dict[value]}")

    @property
    def results(self):
        """
        **READONLY**


        :return: dictionary of measurements
        :rtype: Dict
        """
        res_list = list(self._read(":MEASure:RESults?").split(','))
        res_dict = {}
        if self.statistics == 'ON':
            meas = {"CURRENT": None, "MINIMUM": None, "MAXIMUM": None, "MEAN": None, "STDDEV": None,
                    "COUNT": None}
            num_meas = len(meas)
            num_keys = int(len(res_list) / (1 + num_meas))
            for n in range(num_keys):
                try:
                    lab = self.measurement_labels[n]
                except IndexError:
                    lab = res_list[num_meas * n + n]
                res_dict.update({lab: dict(
                    zip(meas, map(float, res_list[num_meas * n + n + 1:num_meas * (n + 1) + n + 1])))})
        else:
            num_keys = len(res_list)
            for n in range(num_keys):
                res_dict.update({self.measurement_labels[n]: {self.statistics: float(res_list[n])}})

        return res_dict

    @property
    def statistics(self):
        """
        **READONLY**
        returns the current statistics mode. ON means all the statistics are on.

        :return: {Measurement Label | CURRent | MINimum | MAXimum | MEAN | STDDev | COUNt}
        :rtype: str
        """
        return self._read(":MEASure:STATistics?")

    @statistics.setter
    def statistics(self, mode):
        """
        Determines the type of information returned by the :MEASure:RESults? query. ON means all the statistics are on.

        :param mode: {{ON | 1} | CURRent | MINimum | MAXimum | MEAN | STDDev | COUNt}
        :type mode: str
        """
        mode = mode.upper()
        mode_dict = {"ON": "ON", "CURRENT": "CURRent", "MINIMUM": "MINimum", "MAXIMUM": "MAXimum", "MEAN": "MEAN",
                     "STDDEV": "STDDev"}

        if mode not in mode_dict.keys():
            raise ValueError('Please specify a valid statistics mode: [ON, CURRENT, MINIMUM, MAXIMUM, MEAN, '
                             'STDDEV]')
        else:
            self._write(":MEASure:STATistics {}".format(mode_dict[mode]))

    @property
    def measurement_labels(self):
        labs = list()
        for i in range(1, 21):
            lab = self._read(f":MEASurement{i}:NAME?")
            if lab == '"no meas"':  # return early if
                return labs
            else:
                labs.append(lab)
        return labs

    @measurement_labels.setter
    def measurement_labels(self, value):
        """

        :param value: list of labels
        :type value: list
        """
        for i, name in enumerate(value):
            self._write(f":MEASurement{i+1}:NAME {name}")

    def delta_time_define(self, start_edge_channel=1, stop_edge_channel=2,
                          start_edge_direction="RISING", start_edge_position="UPPER", start_edge_number=1,
                          stop_edge_direction="RISING", stop_edge_position="UPPER", stop_edge_number=1):
        """
        Method for setting up a delta measurement

        :param start_edge_channel: Channel number for stop edges. 1->4 are analogue channels. 5->20 are Digital channels
        :type start_edge_channel: int
        :param stop_edge_channel: Channel number for stop edges. 1->4 are analogue channels. 5->20 are Digital channels
        :type stop_edge_channel: int
        :param start_edge_direction: {RISING | FALLING | EITHER} for start directions.
        :type start_edge_direction: str
        :param start_edge_position: {UPPER | MIDDLE | LOWER} for start edge positions.
        :type start_edge_position: str
        :param start_edge_number: An integer from 1 to 65534 for start edge numbers.
        :type start_edge_number: int
        :param stop_edge_direction: {RISING | FALLING | EITHER} for stop directions.
        :type stop_edge_direction: str
        :param stop_edge_position: {UPPER | MIDDLE | LOWER} for stop edge positions.
        :type stop_edge_position: str
        :param stop_edge_number: An integer from 1 to 65534 for stop edge numbers.
        :type stop_edge_number: int
        """
        if 1 <= stop_edge_channel <= 4:
            stop_edge_channel = f"CHANnel{stop_edge_channel}"
        elif 5 <= stop_edge_channel <= 20:
            stop_edge_channel = f"DIGital{stop_edge_channel-5}"
        else:
            raise ValueError(f"stop_edge_channel {stop_edge_channel} should be an integer. 1->4 is analogue channel "
                             f"1->4, 5->20 is digital channel 1->16")
        if 1 <= start_edge_channel <= 4:
            start_edge_channel = f"CHANnel{start_edge_channel}"
        elif 5 <= start_edge_channel <= 20:
            start_edge_channel = f"DIGital{start_edge_channel-5}"
        else:
            raise ValueError(f"start_edge_channel {start_edge_channel} should be an integer. 1->4 is analogue channel "
                             f"1->4, 5->20 is digital channel 1->16")

        self._write(f":MEASure:SOURce {start_edge_channel}, {stop_edge_channel}")

        start_edge_direction = start_edge_direction.upper()
        stop_edge_direction = stop_edge_direction.upper()
        start_edge_position = start_edge_position.upper()
        stop_edge_position = stop_edge_position.upper()
        edge_directions = {"RISING": "RISing", "FALLING": "FALLing", "EITHER": "EITHer"}
        edge_positions = {"UPPER": "UPPer", "MIDDLE": "MIDDle", "LOWER": "LOWer"}

        if start_edge_direction not in edge_directions.keys():
            raise ValueError(f'Please specify a valid start edge direction: {edge_directions.keys()}')
        if stop_edge_direction not in edge_directions.keys():
            raise ValueError(f'Please specify a valid stop edge direction: {edge_directions.keys()}')
        if start_edge_position not in edge_positions.keys():
            raise ValueError(f'Please specify a valid start edge position: {edge_positions.keys()}')
        if stop_edge_position not in edge_positions.keys():
            raise ValueError(f'Please specify a valid stop edge position: {edge_positions.keys()}')
        if start_edge_number not in range(1, 65535):
            raise ValueError("please specify starting edge number between 1 and 65534")
        if stop_edge_number not in range(1, 65535):
            raise ValueError("please specify stopping edge number between 1 and 65534")

        self._write(f":MEASure:DELTatime:DEFine {start_edge_direction},{start_edge_number},"
                    f"{start_edge_position},{stop_edge_direction},{stop_edge_number},"
                    f"{stop_edge_position}")
        self._write(f":MEASure:DELTatime {start_edge_channel}")
        return self._read(":MEASure:DELTatime:DEFine?")


class KeysightMSOSXXXXChannel(BaseRealtimeScopeChannel):
    """
    Keysight MSOS series Channel driver
    """
    CAPABILITY = {'offset': {'min': None, 'max': None},
                  'scale': {'min': None, 'max': None},
                  'range': {'min': None, 'max': None}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

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
        self._channel_number = channel_number
        self.probe = KeysightMSOSXXXXProbe(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode)
        self.measurement = KeysightMSOSXXXXMeasurement(channel_number=channel_number, interface=interface,
                                                       dummy_mode=dummy_mode)

    @property
    def label(self):
        """
        The :CHANnel<N>:LABel command sets the channel label to the quoted string
        :return: return lable
        :rtype: str
        """
        return self._read(f':CHANnel{self._channel_number}:LABel?')

    @label.setter
    def label(self, value):
        """
        Channel label
        :param value: up to 16 ascii character string
        :type value: str
        """
        # check if characters are ascii characters
        if all(ord(c) < 128 for c in value):
            if len(value) < 17:  # shorter than 17 characters
                self._write(f':CHANnel{self._channel_number}:LABel "{value}"')
            else:
                raise ValueError(f"label length ({len(value)}) too long. It must be 16 characters or less")
        else:
            ValueError(f'Label must be ASCII characters')

    @property
    def bandwidth_limit(self):
        """
        Enable or Disable bandwidth limit

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'ON': 'ENABLE', '1': 'ENABLE', 'OFF': 'DISABLE', '0': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":CHANnel{}:BWL?".format(self._channel_number))]

    @bandwidth_limit.setter
    def bandwidth_limit(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write(":CHANnel{}:BWL {}".format(self._channel_number, input_dict[value]))
            if value == 'ENABLE':
                self.logger.warning('Bandwidth changes to 25e6 on enabling limit')

    @property
    def display(self):
        """
        Specify channel display

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'ON': 'ENABLE', '1': 'ENABLE', 'OFF': 'DISABLE', '0': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":CHANnel{}:DISPlay?".format(self._channel_number))]
    
    @display.setter
    def display(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write(":CHANnel{}:DISPlay {}".format(self._channel_number, input_dict[value]))
    
    @property
    def offset(self):
        """
        Specify channel vertical offset

        :value: vertical offset
        :type: float
        """
        return float(self._read(":CHANnel{}:OFFSet?".format(self._channel_number)))
    
    @offset.setter
    def offset(self, value):
        """
        :type value: float
        """
        if self.CAPABILITY['offset']['min'] <= value <= self.CAPABILITY['offset']['max']:
            self._write(":CHANnel{}:OFFSet {:.2E}".format(self._channel_number, Decimal(value)))
        else:
            raise ValueError('Please specify a value between {} and {}'.format(
                self.CAPABILITY['offset']['min'],
                self.CAPABILITY['offset']['max']))

    @property
    def range(self):
        """
        returns the channel range in V/div. As there are 8 divisions,

        :value: range in V/div
        :type: float
        :raise ValueError: exception if range not in between 16mV and 40V when probe is 1:1
        """
        return float(self._read(":CHANnel{}:RANGe?".format(self._channel_number)))/8

    @range.setter
    def range(self, value):
        """
        Sets the channel range. takes in the range per div. As there are 8 divisions, multiply value by 8

        :type value: float
        :raise ValueError: exception if range not in between 16mV and 40V (1:1 probe)
        """
        if self.CAPABILITY['range']['min'] <= (value*8)/self.probe.attenuation[0] <= self.CAPABILITY['range']['max']:
            self._write(":CHANnel{}:RANGe {:.2E}V".format(self._channel_number, Decimal(value*8)))  # 8* volts per div
        else:
            raise ValueError('Please specify a value between {} and {}'.format(
                self.CAPABILITY['range']['min'],
                self.CAPABILITY['range']['max']))

    @property
    def scale(self):
        """
        Specify channel scale

        :value: vertical units per division in V
        :type: float
        """
        return float(self._read(":CHANnel{}:SCALe?".format(self._channel_number)))

    @scale.setter
    def scale(self, value):
        """
        :type value: float
        """
        if self.CAPABILITY['scale']['min'] <= value <= self.CAPABILITY['scale']['max']:
            self._write(":CHANnel{}:SCALe {:.2E}".format(self._channel_number, Decimal(value)))
        else:
            raise ValueError('Please specify a value between {} and {}'.format(
                self.CAPABILITY['scale']['min'],
                self.CAPABILITY['scale']['max']))

    def auto_scale(self):
        """
        Auto Scale Real-time Scope, including triggers and timescale
        """
        self._write(':AUToscale'.format(self._channel_number), type_='stb_poll_sync')

    def auto_scale_vert(self):
        """
        Vertical Auto Scale a certain channel
        """
        self._write(f':AUToscale:VERTical CHANnel{self._channel_number}', type_='stb_poll_sync')


class KeysightMSOSXXXXDigitalChannel(BaseRealtimeScopeSubBlock):
    """
    Keysight MSOS Seires Digital Channel driver
    """
    CAPABILITY = {"threshold": {"min": None, "max": None}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialise instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface:
        :type interface:
        :param dummy_mode:
        :type dummy_mode:
        :param kwargs:
        :type kwargs:
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number

        self._enabled = False

    @property
    def enabled(self):
        """
        Digital interface enable property

        :return: true if digital is enabled
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        """
        Enable the digital interface

        :param value: True enables the digital interface, False disables it
        :type value: bool
        """
        if value:
            self._write(":ENABle DIGital")
        else:
            self._write(":DISable DIGital")
        self._enabled = value

    @property
    def label(self):
        """
        The :DIGital<N>:LABel command sets the channel label to the quoted string
        :return: return lable
        :rtype: str
        """
        return self._read(f':DIGital{self._channel_number}:LABel?')

    @label.setter
    def label(self, value):
        """
        Channel label
        :param value: up to 16 ascii character string
        :type value: str
        """
        # check if characters are ascii characters
        if all(ord(c) < 128 for c in value):
            if len(value) < 17:  # shorter than 17 characters
                self._write(f':DIGital{self._channel_number}:LABel "{value}"')
            else:
                raise ValueError(f"label length ({len(value)}) too long. It must be 16 characters or less")
        else:
            ValueError(f'Label must be ASCII characters')

    @property
    def display(self):
        """
        Specify channel display

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'ON': 'ENABLE', '1': 'ENABLE', 'OFF': 'DISABLE', '0': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":DIGital{}:DISPlay?".format(self._channel_number))]

    @display.setter
    def display(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            if not self.enabled:
                self.enabled = True
            self._write(":DIGital{}:DISPlay {}".format(self._channel_number, input_dict[value]))

    @property
    def size(self):
        """
        Changes the vertical size of all the displayed digital channels.

        :return: SMALL | MEDIUM | LARGE
        :rtype: str
        """
        output_dict = {'SMALl': 'SMALL',
                       'MEDium': 'MEDIUM',
                       'LARGe': 'LARGE'}
        if not self.enabled:
            self.enabled = True
        return output_dict[self._read(f":DIGital{self._channel_number}:SIZE?")]

    @size.setter
    def size(self, value):
        """

        :param value:
        :type value:
        """
        value = value.upper()
        input_dict = {'SMALL': 'SMALl',
                      'MEDIUM': 'MEDium',
                      'LARGE': 'LARGe'}
        if not self.enabled:
            self.enabled = True
        self._write(f":DIGital{self._channel_number}:SIZE {input_dict[value]}")

    @property
    def threshold(self):
        """

        :return: current Threshold value
        :rtype: float
        """
        input_dict = {
            'CMOS50': 2.5,
            'CMOS33': 1.65,
            'CMOS25': 1.25,
            'ECL': -1.3,
            'PECL': 3.7,
            'TTL': 1.4,
            'DIFFerential': 0}

        try:
            ret = float(self._read(f":DIGital{self._channel_number}:THReshold?"))
        except ValueError:
            ret = input_dict[self._read(f":DIGital{self._channel_number}:THReshold?")]
        return ret

    @threshold.setter
    def threshold(self, value):
        """
        Sets the logic threshold value for a pod.
        Setting the threshold for digital channels 0 through 7 sets the threshold for pod 1
        while setting the threshold for digital channels 8 through 15 sets the threshold for
        pod 2.
        The threshold is used for triggering purposes and for displaying the digital data as
        high (above the threshold) or low (below the threshold).

        :param value: 
        :type value: 
        """
        if self.CAPABILITY["threshold"]["min"] <= value <= self.CAPABILITY["threshold"]["max"]:
            self._write(f":DIGital{self._channel_number}:THReshold {value}")
        else:
            raise ValueError(f"Threshold {value} should be between "
                             f"{self.CAPABILITY['threshold']['min']} and "
                             f"{self.CAPABILITY['threshold']['max']}")

    
class KeysightMSOSXXXXTrigger(BaseRealtimeScopeSubBlock):
    """
    KeysightMSOS Series trigger driver
    """
    CAPABILITY = {'level': {'min': None, 'max': None}}

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
    def coupling(self):
        """
        Specify channel coupling

        :value: - 'AC'
                - 'DC'
                - 'LFR'
        :type: str
        :raise ValueError: exception if input is not AC/DC/LFR
        """
        return self._read(":TRIGger:EDGE:COUPling?", dummy_data='DC')

    @coupling.setter
    def coupling(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not AC/DC/LFR
        """
        value = value.upper()
        if value not in ['AC', 'DC', 'LFR']:
            raise ValueError("Please specify either 'AC', 'DC', or 'LFR'")
        else:
            self._write(":TRIGger:EDGE:COUPling {}".format(value))

    @property
    def level(self):
        """
        Specify trigger threshold

        :value: set trigger level threshold
        :type: float
        """
        return float(self._read(f":TRIGger:LEVel? {self.source}"))

    @level.setter
    def level(self, value):
        """
        :type: real
        """
        if self.CAPABILITY['level']['min'] <= value <= self.CAPABILITY['level']['max']:
            self._write(f":TRIGger:LEVel {self.source},{value}")
        else:
            raise ValueError('Please specify a value between {} and {}'.format(
                self.CAPABILITY['level']['min'],
                self.CAPABILITY['level']['max']))

    @property
    def noise_reject(self):
        """
        Enable or Disable noise reject

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'ON': 'ENABLE', '1': 'ENABLE', 'OFF': 'DISABLE', '0': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":TRIGger:NREJect?")]

    @noise_reject.setter
    def noise_reject(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write(":TRIGger:NREJect {}".format(input_dict[value]))

    @property
    def trigger_mode(self):
        """
        Specify scope reference

        :value: - 'COMM'
                - 'DELAY'
                - 'EDGE'
                - 'GLITCH'
                - 'PATTERN'
                - 'PWIDTH'
                - 'RUNT'
                - 'SBUS1'
                - 'SBUS2'
                - 'SBUS3'
                - 'SBUS4'
                - 'SHOLD'
                - 'STATE'
                - 'TIMEOUT'
                - 'TRANSITION'
                - 'TV'
                - 'WINDOW'
        :type: str
        :raise ValueError: exception if input is not in ['COMM', 'DELAY', 'EDGE', 'GLITCH', 'PATTERN', 'PWIDTH',
        'RUNT', 'SBUS1', 'SBUS2', 'SBUS3', 'SBUS4', 'SHOLD', 'STATE', 'TIMEOUT', 'TRANSITION', 'TV', 'WINDOW']
        """
        output_dict = {'COMM': 'COMM', 'DEL': 'DELAY', 'EDGE': 'EDGE', 'GLIT': 'GLITCH', 'PATT': 'PATTERN',
                       'PWID': 'PWIDTH', 'RUNT': 'RUNT', 'SBUS1': 'SBUS1', 'SBUS2': 'SBUS2', 'SBUS3': 'SBUS3',
                       'SBUS4': 'SBUS4', 'SHOL': 'SHOLD', 'STAT': 'STATE', 'TIM': 'TIMEOUT', 'TRAN': 'TRANSITION',
                       'TV': 'TV', 'WIND': 'WINDOW'}
        return output_dict[self._read(":TRIGger:MODE?", dummy_data='EDGE')]

    @trigger_mode.setter
    def trigger_mode(self, value):
        """
        :type: str
        :raise ValueError: exception if input is not in [EDGE, GLITch, PATTern, CAN, DURation, I2S, IIC, EBURst,
        LIN, M1553, SEQuence, SPI, TV, UART, USB, FLEXray]
        """
        value = value.upper()
        input_dict = {'COMM': 'COMM', 'DELAY': 'DELay', 'EDGE': 'EDGE', 'GLITCH': 'GLITch', 'PATTERN': 'PATTern',
                      'PWIDTH': 'PWIDth', 'RUNT': 'RUNT', 'SBUS1': 'SBUS1', 'SBUS2': 'SBUS2', 'SBUS3': 'SBUS3',
                      'SBUS4': 'SBUS4', 'SHOLD': 'SHOLd', 'STATE': 'STATe', 'TIMEOUT': 'TIMeout',
                      'TRANSITION': 'TRANsition', 'TV': 'TV', 'WINDOW': 'WINDow'}

        if value not in input_dict.keys():
            raise ValueError(f'Please specify a valid mode: {input_dict.keys()}')
        else:
            self._write(":TRIGger:MODE {}".format(input_dict[value]))

    @property
    def trigger_sweep(self):
        """
        trigger sweep mode

        :return:  returns true if trigger sweep mode is AUTO, false if NORMal
        :rtype: str
        """
        output_dict = {'AUTO': 'AUTO', 'TRIG': 'TRIGGERED', 'SING': 'SINGLE'}
        return output_dict[self._read(":TRIGger:SWEep?", dummy_data='AUTO')]

    @trigger_sweep.setter
    def trigger_sweep(self, value):
        """
        selects the trigger sweep mode.
        If Auto is set to True, a baseline is displayed in the absence of a signal. If a signal is present but the
        oscilloscope is not triggered, the unsynchronized signal is displayed instead of a baseline.
        Otherwise, if no trigger is present, the instrument does not sweep, and the data acquired on the previous
        trigger remains on the screen.

        :param value:
        :type value: str
        """
        value = value.upper()
        input_dict = {'AUTO': 'AUTO', 'TRIGGERED': 'TRIGgered', 'SINGLE': 'SINGle'}
        if value not in input_dict.keys():
            raise ValueError(f'Please specify a valid trigger sweep: {input_dict.keys()}')
        else:
            self._write(f":TRIGger:SWEep {input_dict[value]}")

    @property
    def source(self):
        """
        trigger source

        :return:  returns current trigger source {CHANnel<N> | DIGital<M> | AUX | LINE}
        :rtype: str
        """
        return self._read(":TRIGger:EDGE:SOURce?")

    @source.setter
    def source(self, source=1):
        """
        selects the trigger (edge) source.
        Source 1-4 are the analogue inputs, 5-20 are the digital inputs

        :param source: {CHANnel<N> | DIGital<M> | AUX | LINE}
        :type source: Union[int,str]
        """

        if isinstance(source, int):
            if 1 <= source <= 4:
                self._write(f":TRIGger:EDGE:SOURce CHANnel{source}")
            elif 5 <= source <= 20:
                self._write(f":TRIGger:EDGE:SOURce DIGital{source-4}")
            else:
                raise ValueError(f"Source ={source}. Please provide an analogue source in the range 1 to 4 or digital "
                                 f"range 1+4 to 16+4")

        else:
            assert source.upper() in ('AUX', 'LINE'), "trigger source can only be a channel number, 'AUX' or " \
                                                         "'line'. You specified {}".format(source.upper())
            self._write(":TRIGger:EDGE:SOURce {}".format(source.upper()))

    @property
    def slope(self):
        """
        trigger edge slope

        :return:  returns current trigger edge slope {POSitive | NEGative | EITHer}
        :rtype: str
        """
        output_dict = {'POS': 'POSitive', 'NEG': 'NEGative', 'EITH': 'EITHer'}
        return output_dict[self._read(":TRIGger:EDGE:SLOPe?")]

    @slope.setter
    def slope(self, value):
        """

        :param value:
        :type value:
        """
        value = value.upper()
        input_dict = {'POSITIVE': 'POSitive', 'NEGATIVE': 'NEGative', 'EITHER': 'EITHer'}
        if value not in input_dict.keys():
            raise ValueError(f'Please specify a valid slope: {input_dict.keys()}')
        else:
            self._write(":TRIGger:EDGE:SLOPe {}".format(input_dict[value]))

    def pattern_logic(self, channel, logic=None):
        """
        Defines the logic criteria for a selected channel

        :type channel: int
        :param channel: 1->4 = Analogue, 5->20 = 1->16 digital
        :param logic: HIGH | LOW | DONTcare | RISing | FALLing
        :type logic: str
        :return: returns the current logic criteria for a selected channel
        :rtype: str
        """
        input_dict = {"HIGH": "HIGH", "LOW": "LOW", "DONT_CARE": "DONTcare",
                      "RISING": "RISing", "FALLING": "FALLing"}
        output_dict = {"HIGH": "HIGH", "LOW": "LOW", "DONT": "DONT_CARE",
                       "RIS": "RISING", "FALL": "FALLING"}
        if logic is None:
            if 1 <= channel <= 4:
                return output_dict[self._read(f":TRIGger:PATTern:LOGic? CHANnel{channel}")]
            elif 5 <= channel <= 20:
                return output_dict[self._read(f":TRIGger:PATTern:LOGic? DIGital{channel-4}")]
            else:
                raise ValueError(f"Source ={channel}. Please provide an analogue source in the range 1 to 4 or  "
                                 f"digital range 1+4 to 16+4")
        else:
            value = logic.upper()
            if value not in input_dict.keys():
                raise ValueError(f'Please specify a valid slope: {input_dict.keys()}')
            else:
                if 1 <= channel <= 4:
                    self._write(f":TRIGger:PATTern:LOGic CHANnel{channel}, {input_dict[value]}")
                elif 5 <= channel <= 20:
                    self._write(f":TRIGger:PATTern:LOGic DIGital{channel-5}, {input_dict[value]}")
                else:
                    raise ValueError(f"Source ={channel}. Please provide an analogue source in the range 1 to 4 or  "
                                     f"digital range 1+4 to 16+4")

    def pattern_condition(self, condition=None, greater_than_time=None, less_than_time=None):
        """
        defines the the condition applied to the trigger pattern to actually generate a trigger.

        :param less_than_time: optional timeout for less than time
        :type less_than_time: float or None
        :param greater_than_time: optional timeout for more than time
        :type greater_than_time: float or None
        :param condition: ENTERED | EXITED | GT | GT_TIMEOUT | GT_PATTERN_EXITS | LT | RANGE | OR
        :type condition: str or None
        :return:
        :rtype:
        """
        if condition is None:
            return self._read(f":TRIGger:PATTern:CONDition?")
        else:
            condition = condition.upper()
            if condition == "ENTERED" or condition == "EXITED" or condition == "OR":
                self._write(f":TRIGger:PATTern:CONDition {condition}")
            elif condition == "GT":
                self._write(f":TRIGger:PATTern:CONDition {condition},{greater_than_time}")
            elif condition == "GT_TIMEOUT":
                self._write(f":TRIGger:PATTern:CONDition GT,{greater_than_time},TIMeout")
            elif condition == "GT_PATTERN_EXITS":
                self._write(f":TRIGger:PATTern:CONDition GT,{greater_than_time},PEXits")
            elif condition == "LT":
                self._write(f":TRIGger:PATTern:CONDition {condition},{less_than_time}")
            elif condition == "RANGE":
                self._write(f":TRIGger:PATTern:CONDition RANGe,{greater_than_time},{less_than_time}")


class KeysightMSOSXXXXProbe(BaseRealtimeScopeSubBlock):
    """
    KeysightMSOS Series Probe driver
    """
    CAPABILITY = {'attenuation': {'min': None, 'max': None},
                  'skew': {'min': None, 'max': None}}

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

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
        self._channel_number = channel_number

    @property
    def info(self):
        """
        The :CHANnel<N>:PROBe:INFO? query returns a comma-separated list of probe information
        :return: return info
        :rtype: str
        """
        return self._read(f':CHANnel{self._channel_number}:PROBe:INFO?')

    @property
    def id(self):
        """
        The :CHANnel<N>:PROBe:ID? query returns the type of probe attached to the specified oscilloscope channel.
        :return: probe id
        :rtype: str
        """
        return self._read(f':CHANnel{self._channel_number}:PROBe:ID?')

    @property
    def attenuation(self):
        """
        Specify probe attenuation.

        :value: probe attenuation, ratio or decibel
        :type: str
        """
        ret = self._read(':CHANnel{}:PROBe?'.format(self._channel_number), dummy_data="10.0,DUMMY_DATA").split(',')
        return float(ret[0]), ret[1]

    @attenuation.setter
    def attenuation(self, value):
        """
        :type value: float
        """
        if self.CAPABILITY['attenuation']['min'] <= value <= self.CAPABILITY['attenuation']['max']:
            self._write(":CHANnel{}:PROBe {}, RATio".format(self._channel_number, float(value)))
        else:
            raise ValueError('Please specify a value between {} and {}'.format(
                self.CAPABILITY['attenuation']['min'],
                self.CAPABILITY['attenuation']['max']))

    @property
    def head_type(self):
        """
        Specify probe head type

        :value: - 'SEND0'
                - 'SEND6'
                - 'SEND12'
                - 'SEND20'
                - 'DIFF0'
                - 'DIFF6'
                - 'DIFF12'
                - 'DIFF20'
                - 'NONE'
        :type: str
        :raise ValueError: exception if input is not in ['SEND0', 'SEND6', 'SEND12', 'SEND20',
         'DIFF0', 'DIFF6', 'DIFF12', 'DIFF20', 'NONE']
        """
        raise NotSupportedError('KeysightMSOS Series does not support head type settings')

    @head_type.setter
    def head_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not in ['SEND0', 'SEND6', 'SEND12', 'SEND20',
         'DIFF0', 'DIFF6', 'DIFF12', 'DIFF20', 'NONE']
        """
        raise NotSupportedError('KeysightMSOS Series does not support head type settings')

    @property
    def signal_type(self):
        """
        Specify probe signal type

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
        :type: str
        :raise ValueError: exception if input is not in ['DIFFERENTIAL', 'SINGLE']
        """
        raise NotSupportedError('KeysightMSOS Series does not support signal type settings')

    @signal_type.setter
    def signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not in ['DIFFERENTIAL', 'SINGLE']
        """
        raise NotSupportedError('KeysightMSOS Series does not support signal type settings')

    @property
    def skew(self):
        """
        Specify probe skew

        :value: probe skew in seconds
        :type: float
        :raise ValueError: exception if input is between -100ns and 100ns
        """
        return float(self._read(":CHANnel{}:PROBe:SKEW?".format(self._channel_number)))

    @skew.setter
    def skew(self, value):
        """
        :type: float
        :raise ValueError: exception if input is between -100ns and 100ns
        """
        if self.CAPABILITY['skew']['min'] <= value <= self.CAPABILITY['skew']['max']:
            self._write(":CHANnel{}:PROBe:SKEW {}".format(self._channel_number, float(value)))
        else:
            raise ValueError('Please specify a value between {} and {}'.format(
                self.CAPABILITY['skew']['min'],
                self.CAPABILITY['skew']['max']))

    @property
    def coupling(self):
        """
        Specify probe coupling

        :value: - 'AC'
                - 'DC'
        :type: str
        :raise ValueError: exception if input is not AC/DC
        """
        return self._read(":CHANnel{}:PROBe:COUPling?".format(self._channel_number), dummy_data='DC')

    @coupling.setter
    def coupling(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not AC/DC
        """
        value = value.upper()
        if value not in ['AC', 'DC']:
            raise ValueError("Please specify either 'AC', or 'DC'")
        else:
            self._write(":CHANnel{}:PROBe:COUPling {}".format(self._channel_number, value))


class KeysightMSOSXXXXMeasurement(BaseRealtimeScopeSubBlock):
    """
    KeysightMSOS Series Measurement block driver
    """
    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

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
        self._channel_number = channel_number
        self.levels = None
        self.THRESHOLD_TYPE_DICT = {'GENERAL': 'GENeral', 'RISE_FALL': 'RFALl', 'SERIAL': 'SERial'}
        self.threshold_type = self.THRESHOLD_TYPE_DICT['GENERAL']

    @property
    def threshold_method(self):
        """
        Returns the method for specifying thresholds
        :return: percentacge, absolute, Hysteresis, T1090 or T2080
        :rtype: str
        """
        output_dict = {"ABS": "ABSOLUTE", "PERC": "PERCENTAGE", "HYST": "HYSTERESIS",
                       "T1090": "T1090", "T2080": "T2080"}
        return output_dict[self._read(f":MEASure:THResholds:{self.threshold_type}:METHod? "
                                      f"CHANnel{self._channel_number}")]

    @threshold_method.setter
    def threshold_method(self, value):
        """
        :param value: threshold method
        :type value:
        """
        input_dict = {"ABSOLUTE": "ABS", "PERCENTAGE": "PERC", "HYSTERESIS": "HYST",
                      "T1090": "T1090", "T2080": "T2080"}
        value = value.upper()
        if value not in input_dict.keys():
            raise ValueError(f"Expected Threshold Method should be one of {input_dict.keys} ")
        else:
            self._write(f":MEASure:THResholds:{self.threshold_type}:METHod CHANnel{self._channel_number},"
                        f"{input_dict[value]}")

    @property
    def thresholds(self):
        """
        Returns a dictionary of levels or percentages
        :return: thresholds
        :rtype: dict
        """
        input_dict = {"PERCENTAGE": 'PERCent', 'HYSTERESIS': 'HYSTeresis', "ABSOLUTE": "ABSolute"}
        txt = f":MEASure:THResholds:{self.threshold_type}:{input_dict[self.threshold_method]}? " \
              f"CHANnel{self._channel_number}"
        levels = list(map(float, self._read(txt).split(',')))
        return {'levels': {'upper': levels[0], 'middle': levels[1], 'lower': levels[2]},
                'type': self.threshold_type,
                'method': self.threshold_method}

    @thresholds.setter
    def thresholds(self, value):
        """

        :param value: dictionary of threshold levels, type and method
        :type value: dict
        """
        self._write(f":MEASure:THResholds:METHod CHANnel{self._channel_number},PERCent")
        input_dict = {"PERCENTAGE": 'PERCent', 'HYSTERESIS': 'HYSTeresis', "ABSOLUTE": "ABSolute"}
        txt = f":MEASure:THResholds:{value['type']}:{input_dict[value['method']]} " \
              f"CHANnel{self._channel_number},{value['levels']['upper']},{value['levels']['middle']}," \
              f"{value['levels']['lower']}"
        self._write(txt)

    @property
    def thresholds_top_base(self):
        """
        Returns a dictionary of levels or percentages
        :return: thresholds
        :rtype: dict
        """
        top_base = self._read(f":MEASure:THResholds:{self.threshold_type}:TOPBase:ABSolute? "
                              f"CHANnel{self._channel_number}").split(',')
        return {'top_base': {'top': top_base[0], 'base': top_base[1]},
                'type': self.threshold_type,
                'method': 'ABSOLUTE'}

    @thresholds_top_base.setter
    def thresholds_top_base(self, value):
        """

        :param value: dictionary of Top and Base Absolute levels, type and method
        :type value: dict
        """
        t = f":MEASure:THResholds:{value['type']}:TOPBase:METHod CHANnel{self._channel_number},ABSolute"
        # print(t)
        self._write(t)
        txt = f":MEASure:THResholds:{value['type']}:TOPBase:ABSolute " \
              f"CHANnel{self._channel_number},{value['top_base']['top']},{value['top_base']['base']}"
        self._write(txt)

    @property
    def avg(self):
        """
        **READONLY**

        :value: returns waveform avg voltage
        :type: float
        """
        self._write(':MEASure:VAVerage DISPlay,CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:VAVerage? DISPlay,CHANnel{}".format(self._channel_number)))

    @property
    def fall_time(self):
        """
        **READONLY**

        :value: returns waveform fall time
        :type: float
        """
        self._write(':MEASure:FALLtime CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:FALLtime? CHANnel{}".format(self._channel_number)))

    @property
    def frequency(self):
        """
        **READONLY**

        :value: returns waveform frequency
        :type: float
        """
        self._write(':MEASure:FREQuency CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:FREQuency? CHANnel{}".format(self._channel_number)))

    @property
    def max(self):
        """
        **READONLY**

        :value: returns waveform max voltage
        :type: float
        """
        self._write(':MEASure:VMAX CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:VMAX? CHANnel{}".format(self._channel_number)))

    @property
    def min(self):
        """
        **READONLY**

        :value: returns waveform min voltage
        :type: float
        """
        self._write(':MEASure:VMIN CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:VMIN? CHANnel{}".format(self._channel_number)))

    @property
    def rise_time(self):
        """
        **READONLY**

        :value: returns waveform rise time
        :type: float
        """
        self._write(':MEASure:RISetime CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:RISetime? CHANnel{}".format(self._channel_number)))

    @property
    def rms(self):
        """
        **READONLY**

        :value: returns waveform rms voltage
        :type: float
        """
        self._write(':MEASure:VRMS CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:VRMS? CHANnel{}".format(self._channel_number)))

    @property
    def vpp(self):
        """
        **READONLY**

        :value: returns waveform peak-to-peak voltage
        :type: float
        """
        self._write(':MEASure:VPP CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:VPP? CHANnel{}".format(self._channel_number)))

    @property
    def duty_cycle(self):
        """
        **READONLY**

        :value: returns ratio of positive pulse width to period
        :type: float
        """
        self._write(':MEASure:DUTYcycle CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:DUTYcycle? CHANnel{}".format(self._channel_number)))

    @property
    def overshoot(self):
        """
        **READONLY**
        measures and returns the overshoot of the edge closest to the trigger reference.
        For a rising edge:
            overshoot = ((Vmax-Vtop) / (Vtop- Vbase)) x 100
        For a falling edge:
            overshoot = ((Vbase- Vmin) / (Vtop- Vbase)) x 100

        :value: overshoot %
        :type: float
        """
        self._write(':MEASure:OVERshoot CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:OVERshoot? CHANnel{}".format(self._channel_number)))

    @property
    def delta_time(self):
        """
        **READONLY**

        measures the delta time between two edges.

        run delta_time_define to set up this measurement
        :return:  the measured delta time value.
        :rtype: float
        """

        return float(self._read(":MEASure:DELTatime?"))

    @property
    def measure_mark(self):
        """
        turns on or off "track measurement" markers for a specified measurement. "Track measurement" markers show you
        where the oscilloscope is making an automatic measurement
        :return:
        :rtype: str
        """
        output_dict = {'1': 'ON', '0': "OFF"}
        return output_dict[self._read(":MEASure:MARK?")]

    @measure_mark.setter
    def measure_mark(self, value):
        """

        :param value: ON or OFF
        """
        value = value.upper()
        if value not in ['ON', 'OFF', 1, 0]:
            raise ValueError("Please specify either 'ON', or 'OFF'")
        else:
            for lab in self.measurement_labels:
                self._write(f':MEASure:MARK {lab},{value}')

    # too many parameters to make this measurement a property
    def delta_time_define(self, stop_edge_channel=2,
                          start_edge_direction="RISING", start_edge_position="UPPER", start_edge_number=1,
                          stop_edge_direction="RISING", stop_edge_position="UPPER", stop_edge_number=1):
        """
        Method for setting up a delta measurement

        :param stop_edge_channel: Channel number for stop edges
        :type stop_edge_channel: int
        :param start_edge_direction: {RISING | FALLING | EITHER} for start directions.
        :type start_edge_direction: str
        :param start_edge_position: {UPPER | MIDDLE | LOWER} for start edge positions.
        :type start_edge_position: str
        :param start_edge_number: An integer from 1 to 65534 for start edge numbers.
        :type start_edge_number: int
        :param stop_edge_direction: {RISING | FALLING | EITHER} for stop directions.
        :type stop_edge_direction: str
        :param stop_edge_position: {UPPER | MIDDLE | LOWER} for stop edge positions.
        :type stop_edge_position: str
        :param stop_edge_number: An integer from 1 to 65534 for stop edge numbers.
        :type stop_edge_number: int
        """
        if stop_edge_channel > 4:
            raise ValueError("start edge channel should be between 1 and 4")

        self._write(f":MEASure:SOURce CHANnel{self._channel_number}, CHANnel{stop_edge_channel}")
        
        start_edge_direction = start_edge_direction.upper()
        stop_edge_direction = stop_edge_direction.upper()
        start_edge_position = start_edge_position.upper()
        stop_edge_position = stop_edge_position.upper()
        edge_directions = {"RISING": "RISing", "FALLING": "FALLing", "EITHER": "EITHer"}
        edge_positions = {"UPPER": "UPPer", "MIDDLE": "MIDDle", "LOWER": "LOWer"}

        if start_edge_direction not in edge_directions.keys():
            raise ValueError(f'Please specify a valid start edge direction: {edge_directions.keys()}')
        if stop_edge_direction not in edge_directions.keys():
            raise ValueError(f'Please specify a valid stop edge direction: {edge_directions.keys()}')
        if start_edge_position not in edge_positions.keys():
            raise ValueError(f'Please specify a valid start edge position: {edge_positions.keys()}')
        if stop_edge_position not in edge_positions.keys():
            raise ValueError(f'Please specify a valid stop edge position: {edge_positions.keys()}')
        if start_edge_number not in range(1, 65535):
            raise ValueError("please specify starting edge number between 1 and 65534")
        if stop_edge_number not in range(1, 65535):
            raise ValueError("please specify stopping edge number between 1 and 65534")

        self._write(f":MEASure:DELTatime:DEFine {start_edge_direction},{start_edge_number},"
                    f"{start_edge_position},{stop_edge_direction},{stop_edge_number},"
                    f"{stop_edge_position}")
        self._write(f":MEASure:DELTatime CHANnel{self._channel_number}")
        return self._read(":MEASure:DELTatime:DEFine?")

    @property
    def measurement_labels(self):
        labs = list()
        for i in range(1, 21):
            lab = self._read(f":MEASurement{i}:NAME?")
            if lab == '"no meas"':  # return early if
                return labs
            else:
                labs.append(lab)
        return labs


class KeysightMSOSXXXXFunction(BaseRealtimeScopeSubBlock):
    """
    Function block
    """
    SOURCES = ('CHANnel', 'CHAN', 'DIFF', 'COMMonmode', 'COMM', 'FUNCtion', 'FUNC', 'EQUalized', 'EQU',
               'WMEMory', 'WMEM', 'MTRend', 'MTR', 'MSPectrum', 'MSP', 'XT', 'PNOise', 'PNO')

    def __init__(self,  function_number, interface, dummy_mode, **kwargs):
        """
        init instance

        :param function_number:
        :type function_number:
        :param interface:
        :type interface:
        :param dummy_mode:
        :type dummy_mode:
        :param kwargs:
        :type kwargs:
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._function_number = function_number

    @property
    def display(self):
        """
        Specify channel display

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'ON': 'ENABLE', '1': 'ENABLE', 'OFF': 'DISABLE', '0': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":FUNCtion{}:DISPlay?".format(self._function_number))]

    @display.setter
    def display(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write(":FUNCtion{}:DISPlay {}".format(self._function_number, input_dict[value]))

    @property
    def function_definition(self):
        """
        returns the currently defined source(s) for the function
        :return:
        :rtype: str
        """
        self._write(":SYST:HEAD ON")  # if headers are not on, only the operands (eg CHAN1) are displayed
        func_def = self._read(f":FUNCtion{self._function_number}?")
        self._write(":SYST:HEAD OFF")
        return func_def

    def minimum(self, source_index=1, source_type="CHAN"):
        """
        The :FUNCtion<F>:MINimum command defines a function that computes the minimum of each time bucket for the
        defined operand's waveform.
        :return:
        :rtype: str
        """
        if source_type not in self.SOURCES:
            raise ValueError(f"source type {source_type} not recognised - chose one of {self.SOURCES}")
        else:
            self._write(f":FUNCtion{self._function_number}:MINimum {source_type}{source_index}")

    def maximum(self, source_index=1, source_type="CHAN"):
        """
        The :FUNCtion<F>:MAXimum command defines a function that computes the maximum of each time bucket for the
        defined operand's waveform.
        :param source_type:
        :type source_type: str|float
        :type source_index: int
        :param source_index: eg 1 for channel 1
        """
        if source_type not in self.SOURCES:
            raise ValueError(f"source type {source_type} not recognised - chose one of {self.SOURCES}")
        else:
            self._write(f":FUNCtion{self._function_number}:MAXimum {source_type}{source_index}")
