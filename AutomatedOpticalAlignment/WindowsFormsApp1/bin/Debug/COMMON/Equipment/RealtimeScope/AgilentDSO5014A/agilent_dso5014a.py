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


class AgilentDSO5014A(BaseRealtimeScope):
    """
    Driver for Agilent DSO5014A Real-time Scope
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
        """:type: list of AgilentDSO5014AChannel"""
        self.channel.append(AgilentDSO5014AChannel(channel_number=1, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentDSO5014AChannel(channel_number=2, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentDSO5014AChannel(channel_number=3, interface=interface, dummy_mode=dummy_mode))
        self.channel.append(AgilentDSO5014AChannel(channel_number=4, interface=interface, dummy_mode=dummy_mode))
        self.trigger = AgilentDSO5014ATrigger(interface=interface, dummy_mode=dummy_mode)
        self._mode = None
        self._file_base_name = ''
        self._image_file_format = ''
        self.measurement_labels = []

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

    def reset_statistics(self):
        """
        Clears all measurements
        """
        self._write(':MEASure:STATistics:RESet')

    def run(self):
        """
        Switches mode to RUN
        """
        self._write(':RUN')

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

        # if a new base_name is supplied, change teh base_name and record the new basename for this instance.
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

        :return: {ON | CURRent | MINimum | MAXimum | MEAN | STDDev | COUNt}
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
                     "STDDEV": "STDDev", "COUNT": "COUNt"}

        if mode not in mode_dict.keys():
            raise ValueError('Please specify a valid statistics mode: [ON, CURRENT, MINIMUM, MAXIMUM, MEAN, '
                             'STDDEV, COUNT]')
        else:
            self._write(":MEASure:STATistics {}".format(mode_dict[mode]))


class AgilentDSO5014AChannel(BaseRealtimeScopeChannel):
    """
    Agilent DSO5014A Channel driver
    """
    CAPABILITY = {'offset': {'min': -50, 'max': 50},
                  'scale': {'min': 0.002, 'max': 5.0},
                  'range': {'min': 0.016, 'max': 40}}

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
        self.probe = AgilentDSO5014AProbe(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode)
        self.measurement = AgilentDSO5014AMeasurement(channel_number=channel_number, interface=interface,
                                                       dummy_mode=dummy_mode)

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
        if self.CAPABILITY['range']['min'] <= (value*8)/self.probe.attenuation <= self.CAPABILITY['range']['max']:
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
        Auto Scale Real-time Scope
        """
        self._write(':AUToscale CHANnel{}'.format(self._channel_number), type_='stb_poll_sync')


class AgilentDSO5014ATrigger(BaseRealtimeScopeSubBlock):
    """
    AgilentDSO5014A trigger driver
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
        :raise ValueError: exception if input is not in [EDGE, GLITch, PATTern, CAN, DURation, I2S, IIC, EBURst,
        LIN, M1553, SEQuence, SPI, TV, UART, USB, FLEXray]
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
    def trigger_auto_sweep(self):
        """
        trigger sweep mode

        :return:  returns true if trigger sweep mode is AUTO, false if NORMal
        :rtype: str
        """
        return True if self._read(":TRIGger:SWEep?") == "AUTO" else False

    @trigger_auto_sweep.setter
    def trigger_auto_sweep(self, auto=False):
        """
        selects the trigger sweep mode.
        If Auto is set to True, a baseline is displayed in the absence of a signal. If a signal is present but the
        oscilloscope is not triggered, the unsynchronized signal is displayed instead of a baseline.
        Otherwise, if no trigger is present, the instrument does not sweep, and the data acquired on the previous
        trigger remains on the screen.

        :param auto:
        :type auto: bool
        """
        if auto:
            self._write(":TRIGger:SWEep AUTO")
        else:
            self._write(":TRIGger:SWEep NORMal")

    @property
    def source(self):
        """
        trigger source

        :return:  returns current trigger source {CHAN<n> | EXT | LINE | NONE}
        :rtype: str
        """
        return self._read(":TRIGger:SOURce?")

    @source.setter
    def source(self, source=1):
        """
        selects the trigger (edge) source.

        :param source: {CHANnel<n> | EXTernal | LINE}
        :type source: Union[int,str]
        """

        if isinstance(source, int):
            assert 1 <= source <= 4, "source {} out of range 1-4".format(source)
            self._write(":TRIGger:SOURce CHANnel{}".format(source))
        else:
            assert source.upper() in ('EXTERNAL', 'LINE'), "trigger source can only be a channel or 'external' or " \
                                                         "'line'. You specified {}".format(source.upper())
            self._write(":TRIGger:SOURce {}".format(source.upper()))


class AgilentDSO5014AProbe(BaseRealtimeScopeSubBlock):
    """
    AgilentDSO5014A Probe driver
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
        raise NotSupportedError('AgilentDSO5014A does not support head type settings')

    @head_type.setter
    def head_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not in ['SEND0', 'SEND6', 'SEND12', 'SEND20',
         'DIFF0', 'DIFF6', 'DIFF12', 'DIFF20', 'NONE']
        """
        raise NotSupportedError('AgilentDSO5014A does not support head type settings')

    @property
    def signal_type(self):
        """
        Specify probe signal type

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
        :type: str
        :raise ValueError: exception if input is not in ['DIFFERENTIAL', 'SINGLE']
        """
        raise NotSupportedError('AgilentDSO5014A does not support signal type settings')

    @signal_type.setter
    def signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not in ['DIFFERENTIAL', 'SINGLE']
        """
        raise NotSupportedError('AgilentDSO5014A does not support signal type settings')

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


class AgilentDSO5014AMeasurement(BaseRealtimeScopeSubBlock):
    """
    AgilentDSO5014A Measurement block driver
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
