"""
| $Revision:: 281646                                   $:  Revision of last commit
| $Author:: wleung@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-16 20:09:50 +0100 (Thu, 16 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
import re
import time
from decimal import Decimal
from COMMON.Utilities.custom_structures import CustomList
from COMMON.Equipment.RealtimeScope.base_realtime_scope import BaseRealtimeScope
from COMMON.Equipment.RealtimeScope.base_realtime_scope import BaseRealtimeScopeChannel
from COMMON.Equipment.RealtimeScope.base_realtime_scope import BaseRealtimeScopeSubBlock
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_exceptions import NotSupportedError


class AgilentXSOX3xxxA(BaseRealtimeScope):
    """
    Driver for Agilent XSOX3xxxA Real-time Scope
    """
    CAPABILITY = {'horizontal_scale': {'min': 1e-9, 'max': 50}}

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
        """:type: list of AgilentXSOX3xxxAChannel"""
        self.channel.append(AgilentXSOX3xxxAChannel(channel_number=1, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentXSOX3xxxAChannel(channel_number=2, interface=interface, dummy_mode=dummy_mode))
        self.trigger = AgilentXSOX3xxxATrigger(interface=interface, dummy_mode=dummy_mode)
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
    def position(self):
        """
        Specify scope scale

        :value: time in seconds
        :type: float
        """
        return float(self._read(":TIMebase:WINDow:POSition?"))

    @position.setter
    def position(self, value):
        """
        :type: float
        """
        self._write(":TIMebase:WINDow:POSition {:.2E}".format(Decimal(value)))

    @property
    def reference(self):
        """
        Specify scope reference

        :value: - 'CENTER'
                - 'LEFT'
                - 'RIGHT'
        :type: str
        :raise ValueError: exception if input is not CENTER/LEFT/RIGHT
        """
        output_dict = {'CENT': 'CENTER', 'LEFT': 'LEFT', 'RIGH': 'RIGHT'}
        return output_dict[self._read(":TIMebase:REFerence?", dummy_data='CENT')]

    @reference.setter
    def reference(self, value):
        """
        :type: str
        :raise ValueError: exception if input is not CENTER/LEFT/RIGHT
        """
        value = value.upper()
        input_dict = {'CENTER': 'CENT', 'LEFT': 'LEFT', 'RIGHT': 'RIGH'}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'CENTER' , 'LEFT' or 'RIGHT'")
        else:
            self._write(":TIMebase:REFerence {}".format(value))

    @property
    def zoom(self):
        """

        :return: true if zoom is enabled
        :type: bool
        """
        return True if self._read(":TIMebase:MODE?") == 'MAIN' else False

    @zoom.setter
    def zoom(self, value):
        """

        :value: true to enable zoom mode
        :type: bool
        """
        if value:
            self._write(":TIMebase:MODE WINDow")
        else:
            self._write(":TIMebase:MODE MAIN")

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
        output_dict = {'ZOOM': 'ZOOM', 'AUTO': 'AUTO', 'MAIN': 'MAIN', 'GATE': 'GATE'}
        return output_dict[self._read(":MEASure:WINDow?", dummy_data='MAIN')]

    @measure_window.setter
    def measure_window(self, value):
        input_dict = {'ZOOM': 'ZOOM', 'AUTO': 'AUTO', 'MAIN': 'MAIN', 'GATE': 'GATE'}
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

    def clear(self):
        """
        Clears the display and resets all associated measurements
        """
        self._write(':DISPlay:CLEar')

    def clear_measurements(self):
        """
        Clears all measurements
        """
        self._write(':MEASure:CLEar')

    def save_waveform(self, length, file_format='CSV'):
        """
        Saves current waveform

        :param length: - (int) record length # TODO: [AE] good documentation?
                       - (str) 'MAX'
        :param file_format: - 'ASCII'
                            - 'BINARY'
                            - 'CSV'
        """
        file_format = file_format.upper()
        input_dict = {'CSV': 'CSV', 'BINARY': 'BINary', 'ASCII': 'ASCiixy'}

        if file_format not in input_dict.keys():
            raise ValueError("Please specify file type as 'CSV', 'ASCII' pr 'BINARY'")
        else:
            self._write(':SAVE:WAVeform:FORMat {}'.format(input_dict[file_format]))

        if length == 'MAX':
            self._write(":SAVE:WAVeform:LENGth:MAX ON")
        else:
            # [ael-khouly] Max settings must be disabled for the length command to take effect
            self._write(":SAVE:WAVeform:LENGth:MAX OFF")
            self._write(":SAVE:WAVeform:LENGth {}".format(length))

    def save_image(self, base_name='image_', file_format='PNG'):
        """
        Saves screen image

        :param base_name:
        :type base_name:str
        :param file_format:
        :type file_format: str
        """
        valid_formats = ('TIFF', 'BMP', 'BMP24bit', 'BMP8bit', 'PNG')
        if file_format not in valid_formats:
            raise ValueError("Please specify file type as 'TIFF', 'BMP', 'BMP24bit', 'BMP8bit' or 'PNG'")
        else:
            # new file format given
            if self._image_file_format != file_format:
                self._write(":SAVE:IMAGe:FORMat {}".format(file_format))
                self._image_file_format = file_format

        base_name = re.sub('\..{3}$', "", base_name)  # remove extention if we put them in
        # if a new base_name is supplied, change the base_name and record the new basename for this instance.
        if self._file_base_name != base_name:
            self._write(":SAVE:FILename '{}'".format(base_name))
            self._file_base_name = base_name

        self.logger.info("Writting {} to {}".format(base_name, self.save_working_directory))
        # time to allow the measurements to refresh, in case a measurement was read just before taking a screenshot
        time.sleep(0.2)
        self._write(":SAVE:IMAGe:STARt", type_='stb_poll_sync')

    @property
    def save_working_directory(self):
        """
        The directory where files are saved

        :return:  directory where files are saved
        :rtype:  str
        """
        return self._read(":SAVE:PWD?")

    @save_working_directory.setter
    def save_working_directory(self, directory):
        """
        The directory where files are saved

        :param directory: sets the dir where files are saved
        :type:  str
        """
        self._write(":SAVE:PWD '{}'".format(directory), type_='stb_poll_sync')

    def run(self):
        """
        Switches mode to RUN
        """
        self._mode = "RUN"
        self._write(':RUN')

    def single(self):
        """
        Switches mode to SINGLE
        """
        self._mode = "SINGLE"
        self._write(':SINGle')

    def stop(self):
        """
        Switches mode to STOP
        """
        self._mode = "STOP"
        self._write(':STOP')

    @property
    def mode(self):
        """

        :return:
        :rtype:
        """
        return self._mode

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
        self._mode = value
        self._write(f":{input_dict[value]}")


class AgilentXSOX3xxxAChannel(BaseRealtimeScopeChannel):
    """
    Agilent XSOX3xxxA Channel driver
    """
    CAPABILITY = {'bandwidth': [25e6, 500e6],
                  'offset': {'min': -50, 'max': 50},
                  'scale': {'min': 0.001, 'max': 5.0},
                  'range': {'min': 0.008, 'max': 40}}

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
        self.probe = AgilentXSOX3xxxAProbe(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode)
        self.measurement = AgilentXSOX3xxxAMeasurement(channel_number=channel_number, interface=interface,
                                                       dummy_mode=dummy_mode)

    @property
    def bandwidth(self):
        """
        Specify channel bandwidth limit

        :value: bandwidth limit
        :type: float
        :raise ValueError: exception if bandwidth is not 25e6 or 500e6
        """
        return float(self._read(":CHANnel{}:BANDwidth?".format(self._channel_number)))

    @bandwidth.setter
    def bandwidth(self, value):
        """
        :type value: float
        :raise ValueError: exception if bandwidth is not 25e6 or 500e6
        """
        if value not in self.CAPABILITY['bandwidth']:
            raise ValueError('Please specify one of the following: {}'.format(
                self.CAPABILITY['bandwidth']
            ))
        else:
            self._write(":CHANnel{}:BANDwidth {}".format(self._channel_number, float(value)))

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
    def coupling(self):
        """
        Specify channel coupling

        :value: - 'AC'
                - 'DC'
        :type: str
        :raise ValueError: exception if input is not AC/DC
        """
        return self._read(":CHANnel{}:COUPling?".format(self._channel_number), dummy_data='DC')

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
            self._write(":CHANnel{}:COUPling {}" .format(self._channel_number, value))
            
    @property
    def display(self):
        """
        Specify channel coupling

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
        Specify channel range

        :value: range in V
        :type: float
        :raise ValueError: exception if range not in between 8mV and 40V
        """
        return float(self._read(":CHANnel{}:RANGe?".format(self._channel_number)))

    @range.setter
    def range(self, value):
        """
        :type value: float
        :raise ValueError: exception if range not in between 8mV and 40V
        """
        if self.CAPABILITY['range']['min'] <= value <= self.CAPABILITY['range']['max']:
            self._write(":CHANnel{}:RANGe {:.2E}".format(self._channel_number, Decimal(value)))
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
        Auto Scale Real-time Scope
        """
        self._write(':AUToscale CHANnel{}'.format(self._channel_number), type_='stb_poll_sync')


class AgilentXSOX3xxxATrigger(BaseRealtimeScopeSubBlock):
    """
    AgilentXSOX3xxxA Probe driver
    """
    CAPABILITY = {'level': {'min': -30, 'max': 30}}

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
        return self._read(":TRIGger:COUPling?", dummy_data='DC')

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
            self._write(":TRIGger:COUPling {}".format(value))

    @property
    def hf_reject(self):
        """
        Enable or Disable high frequency reject

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'ON': 'ENABLE', '1': 'ENABLE', 'OFF': 'DISABLE', '0': 'DISABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":TRIGger:HFReject?")]

    @hf_reject.setter
    def hf_reject(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write(":TRIGger:HFReject {}".format(input_dict[value]))

    @property
    def level(self):
        """
        Specify trigger threshold

        :value: set trigger level threshold
        :type: float
        """
        return float(self._read(":TRIGger:LEVel?"))

    @level.setter
    def level(self, value):
        """
        :type: float
        """
        if self.CAPABILITY['level']['min'] <= value <= self.CAPABILITY['level']['max']:
            self._write(":TRIGger:LEVel {:.2E}".format(Decimal(value)))
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

        :value: - 'EDGE'
                - 'GLITCH'
                - 'PATTERN'
                - 'TV'
                - 'DELAY'
                - 'EBURST'
                - 'OR'
                - 'RUNT'
                - 'SHOLD'
                - 'TRANSITION'
                - 'SBUS1'
                - 'SBUS2'
                - 'USB'
        :type: str
        :raise ValueError: exception if input is not in [EDGE, GLITCH, PATTERN, TV, DELAY, EBURST,
         OR, RUNT, SHOLD, TRANSITION, SBUS1, SBUS2, USB]
        """
        output_dict = {'EDGE': 'EDGE', 'GLIT': 'GLITCH', 'PATT': 'PATTERN',
                       'TV': 'TV', 'DEL': 'DELAY', 'EBUR': 'EBURST', 'OR': 'OR', 'RUNT': 'RUNT',
                       'SHOL': 'SHOLD', 'TRAN': 'TRANSITION', 'SBUS1': 'SBUS1', 'SBUS2': 'SBUS2',
                       'USB': 'USB'}
        return output_dict[self._read(":TRIGger:MODE?", dummy_data='EDGE')]

    @trigger_mode.setter
    def trigger_mode(self, value):
        """
        :type: str
        :raise ValueError: exception if input is not in [EDGE, GLITCH, PATTERN, TV,
         DELAY, EBURST, OR, RUNT, SHOLD, TRANSITION, SBUS1, SBUS2, USB]
        """
        value = value.upper()
        input_dict = {'EDGE': 'EDGE', 'GLITCH': 'GLITch', 'PATTERN': 'PATTern', 'TV': 'TV',
                      'DELAY': 'DELay', 'EBURST': 'EBURst', 'OR': 'OR', 'RUNT': 'RUNT',
                      'SHOLD': 'SHOLd', 'TRANSITION': 'TRANsition',
                      'SBUS1': 'SBUS1', 'SBUS2': 'SBUS2', 'USB': 'USB'}

        if value not in input_dict.keys():
            raise ValueError('Please specify a valid mode: [EDGE, GLITCH, PATTERN, TV,'
                             ' DELAY, EBURST, OR, RUNT, SHOLD,'
                             'TRANSITION, SBUS1, SBUS2, USB]')
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
        output_dict = {'POS': 'POSitive', 'NEG': 'NEGative', 'EITH': 'EITHer', 'ALT':'ALTERNATE'}
        return output_dict[self._read(":TRIGger:EDGE:SLOPe?")]

    @slope.setter
    def slope(self, value):
        """

        :param value:
        :type value:
        """
        value = value.upper()
        input_dict = {'POSITIVE': 'POSitive', 'NEGATIVE': 'NEGative', 'EITHER': 'EITHer', 'ALTERNATE':'ALTernate'}
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


class AgilentXSOX3xxxAProbe(BaseRealtimeScopeSubBlock):
    """
    AgilentXSOX3xxxA Probe driver
    """
    CAPABILITY = {'attenuation': {'min': 0.1, 'max': 10000},
                  'skew': {'min': -100e-9, 'max': 100e-9}}

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
    def attenuation(self):
        """
        Specify probe attenuation

        :value: probe attenuation
        :type: float
        """
        return float(self._read(':CHANnel{}:PROBe?'.format(self._channel_number)))

    @attenuation.setter
    def attenuation(self, value):
        """
        :type value: float
        """
        if self.CAPABILITY['attenuation']['min'] <= value <= self.CAPABILITY['attenuation']['max']:
            self._write(":CHANnel{}:PROBe {}".format(self._channel_number, float(value)))
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
        raise NotSupportedError('AgilentXSOX3xxxA does not support head type settings')

    @head_type.setter
    def head_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not in ['SEND0', 'SEND6', 'SEND12', 'SEND20',
         'DIFF0', 'DIFF6', 'DIFF12', 'DIFF20', 'NONE']
        """
        raise NotSupportedError('AgilentXSOX3xxxA does not support head type settings')

    @property
    def signal_type(self):
        """
        Specify probe signal type

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
        :type: str
        :raise ValueError: exception if input is not in ['DIFFERENTIAL', 'SINGLE']
        """
        raise NotSupportedError('AgilentXSOX3xxxA does not support signal type settings')

    @signal_type.setter
    def signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not in ['DIFFERENTIAL', 'SINGLE']
        """
        raise NotSupportedError('AgilentXSOX3xxxA does not support signal type settings')

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


class AgilentXSOX3xxxAMeasurement(BaseRealtimeScopeSubBlock):
    """
    AgilentXSOX3xxxA Measurement block driver
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
        self.threshold_type = None

    @property
    def threshold_method(self):
        """
        Returns the method for specifying thresholds
        :return: percentacge or absolute
        :rtype: str
        """
        output_dict = {"ABS": "ABSOLUTE", "PERC": "PERCENTAGE"}
        return output_dict[self._read(f":MEASure:DEFine? THResholds,CHANnel{self._channel_number}").split(',')[1]]

    @property
    def thresholds(self):
        """
        Returns a dictionary of levels or percentages
        :return: thresholds
        :rtype: dict
        """
        input_dict = {"PERC": 'PERCENTAGE', "ABS": "ABSOLUTE"}
        levels = self._read(f":MEASure:DEFine? THResholds,CHANnel{self._channel_number}").split(',')
        return {'levels': {'upper': float(levels[2]), 'middle': float(levels[3]), 'lower': float(levels[4])},
                'type': 'GENERAL',
                'method': input_dict[levels[1]]}

    @thresholds.setter
    def thresholds(self, value):
        """

        :param value: dictionary of threshold levels, type and method
        :type value: dict
        """
        input_dict = {"PERCENTAGE": 'PERCent', "ABSOLUTE": "ABSolute"}
        self._write(f":MEASure:DEFine THResholds,{input_dict[value['method']]},{value['levels']['upper']},"
                    f"{value['levels']['middle']},{value['levels']['lower']},CHANnel{self._channel_number}")

    @property
    def avg(self):
        """
        **READONLY**

        :value: returns waveform avg voltage
        :type: float
        """
        self._write(':MEASure:VAVerage CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:VAVerage? CHANnel{}".format(self._channel_number)))

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
    def r_edges(self):
        """
        **READONLY**

        :value: returns count of rising edges on screen
        :type: float
        """
        self._write(':MEASure:PEDGes CHANnel{}'.format(self._channel_number), dummy_data=1)
        return float(self._read(":MEASure:PEDGes? CHANnel{}".format(self._channel_number)))

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
    def delta_time(self):
        """
        **READONLY**

        measures the delta time between two edges.

        run delta_time_define to set up this measurement
        :return:  the measured delta time value.
        :rtype: float
        """

        return float(self._read(":MEASure:DELay?"))

    @property
    def measure_mark(self):
        """
        turns on or off "track measurement" markers for a specified measurement. "Track measurement" markers show you
        where the oscilloscope is making an automatic measurement
        :return:
        :rtype: str
        """
        output_dict = {'MEAS': 'ON', 'OFF': "OFF", 'MAN': "OFF", 'WAV': "OFF", 'BIN': "OFF", 'HEX': "OFF"}
        return output_dict[self._read(":MARKer:MODE?")]

    @measure_mark.setter
    def measure_mark(self, value):
        """

        :param value: ON or OFF
        """
        value = value.upper()
        input_dict = {'ON': 'MEASurement', 'OFF': 'OFF',
                      1: 'MEASurement', 0: 'OFF'}
        if value not in ['ON', 'OFF', 1, 0]:
            raise ValueError("Please specify either 'ON', or 'OFF'")
        else:
            self._write(f':MARKer:Mode {input_dict[value]}')

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
        edge_directions = {"RISING": "RISing", "FALLING": "FALLing"}
        edge_positions = {"UPPER": "UPPer", "MIDDLE": "MIDDle", "LOWER": "LOWer"}

        if start_edge_direction not in edge_directions.keys():
            raise ValueError(f'Please specify a valid start edge direction: {edge_directions.keys()}')
        if stop_edge_direction not in edge_directions.keys():
            raise ValueError(f'Please specify a valid stop edge direction: {edge_directions.keys()}')
        if start_edge_position not in edge_positions.keys():
            raise ValueError(f'Please specify a valid start edge position: {edge_positions.keys()}')
        if start_edge_position != 'MIDDLE':
            raise ValueError(f'Only MIDDLE edge position valid for this firmware (7.30)')
        if stop_edge_position not in edge_positions.keys():
            raise ValueError(f'Please specify a valid stop edge position: {edge_positions.keys()}')
        if stop_edge_position != 'MIDDLE':
            raise ValueError(f'Only MIDDLE edge position valid for this firmware (7.30)')
        if start_edge_number not in range(1, 1000):
            raise ValueError("please specify starting edge number between 1 and 1000")
        if stop_edge_number not in range(1, 1000):
            raise ValueError("please specify stopping edge number between 1 and 1000")

        self._write(f":MEASure:DELay:DEFine {start_edge_direction},{start_edge_number},"
                    f"{start_edge_position},{stop_edge_direction},{stop_edge_number},"
                    f"{stop_edge_position}")
        self._write(f":MEASure:DELay CHANnel{self._channel_number}")
        return self._read(f":MEASure:DELay? CHANnel{self._channel_number}")
