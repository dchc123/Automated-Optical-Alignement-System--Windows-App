
from typing import Union
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_exceptions import NotSupportedError
from ..base_awg import BaseAWG
from ..base_awg import BaseAWGWaveform


class Keysight332XXX(BaseAWG):
    """
    Keysight 332XXX common Arbitrary Waveform Generator
    """

    CAPABILITY = {
        'frequency_range': {'min': None, 'max': None},
        'amplitude_range': {'min': None, 'max': None},
        'pulse_period': {'min': None, 'max': None},
        'pulse_width': {'min': None, 'max': None},
        'transition_range': {'min': None, 'max': None},
        'output_load': {'min': None, 'max': None},
        'max_waveform_points': None,

    }

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
        self.waveform = Keysight332XXXWaveform(interface=interface, dummy_mode=dummy_mode)
        self._voltage = {"HIGH": None, "LOW": None}

    @property
    def beeper(self):
        """
        **Enable or Disable arb beeper**

        **EXAMPLE:** *arb.beeper = 'ENABLE'*

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":SYST:BEEP:STAT?")]

    @beeper.setter
    def beeper(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 1, 'DISABLE': 0}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write(":SYST:BEEP:STAT %s" % input_dict[value])

    @property
    def display(self):
        """
        **Disable normal screen function and display a message on the screen**

        **EXAMPLE:** *arb.display = 'test in progress...'*
        **RETURN display to normal operation** *arb.display = None*

        :value: - 'string'
                - None
        :type: str
        """
        if self._read(":DISP?"):
            return None
        else:
            return self._read(":DISP:TEXT?")

    @display.setter
    def display(self, value):
        """
        :type value: Union(str, NoneType)
        """
        if value:
            self._write("DISP OFF")
            self._write(f"DISP:TEXT '{value}'")
        else:
            self._write("DISP ON")

    @property
    def output(self):
        """
        **Enable or Disable ARB output**

        **EXAMPLE:** *arb.output = 'ENABLE'*

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        output_dict = {'1': 'ENABLE', '0': 'DISABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read("OUTP?")]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 1, 'DISABLE': 0}

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write("OUTP %s" % input_dict[value])

    @property
    def output_load(self):
        """
        **sets ARB output impedance**

        **EXAMPLE:** *arb.output_load = 50|INFINITY*

        :value: - integer between 1 and 10000
                - 'INFINITY' for high impeadance
        :type: Uninon(str,int)
        :raise ValueError: exception if value is not in range
        """
        load = float(self._read("OUTP:LOAD?"))
        if self.CAPABILITY['output_load']['max'] == "INFINITY" and load == 9.9e37:
            load = 'INFINITY'
        if load > self.CAPABILITY['output_load']['max']:
            load = 'INFINITY'
        return load

    @output_load.setter
    def output_load(self, value):
        """
        :type value: Union(str, int)
        """
        if isinstance(value, str):
            value = value.upper()
            if value != 'INFINITY':
                raise ValueError(f"Please specify either and integer between {self.CAPABILITY['output_load']['min']} "
                                 f"and {self.CAPABILITY['output_load']['max']} or 'INFINITY'")
        else:
            if not (self.CAPABILITY['output_load']['min'] <= value <= self.CAPABILITY['output_load']['max']):
                raise ValueError(f"Please specify either and integer between {self.CAPABILITY['output_load']['min']} "
                                 f"and {self.CAPABILITY['output_load']['max']} or 'INFINITY'")
        self._write(f"OUTP:LOAD {value}")

    @property
    def pattern(self):
        raise NotSupportedError

    @property
    def frequency(self):
        """
        Gets the output frequency

        :return: Frequency in HZ
        :rtype: float
        """
        return float(self._read("FREQ?"))

    @frequency.setter
    def frequency(self, value):
        """
        Set the output frequency

        :param value: output frequency
        :type value: Union(int, float, str)
        :raises ValueError: exception if frequency is out of range
        """
        input_list = ['MINIMUM', 'MAXIMUM', 'MIN', 'MAX']
        minimum = self.CAPABILITY['frequency_range']['min']
        maximum = self.CAPABILITY['frequency_range']['max']
        if isinstance(value, (int, float)):
            if value < minimum:
                raise ValueError(f'Minimum Frequency is {minimum}')
            elif value > maximum:
                raise ValueError(f'Maximum Frequency is {maximum}')
        else:
            if value not in input_list:
                raise ValueError('Please specify either %s or an integer' % input_list)

        self._write(f"FREQ {value}")

    @property
    def voltage(self):
        """
        Gets the output voltage amplitude
        :return: voltage
        :rtype: float
        """
        return float(self._read("VOLTage?"))

    @voltage.setter
    def voltage(self, value):
        """
        Set the output amplitude.

        :param value: Sets the amplitude (float or int) or the low level and high levels (tuple or list or dict). A
        dict can be used to set the AMPLITUDE and OFFSET or the LOW and HIGH levels
        :type value: Union(float, int, tuple, list, dict)
        """
        if isinstance(value, (float, int)):
            self._write(f"VOLTage {value}")
        elif isinstance(value, (tuple, list)):
            if len(value) != 2:
                raise ValueError("A tuple or list must have 2 values to specify a low and high voltage level")
            sorted_low_high = sorted(value)
            self._write(f"VOLTage:HIGH {sorted_low_high[1]}")
            self._write(f"VOLTage:LOW {sorted_low_high[0]}")
        elif isinstance(value, dict):
            try:
                self._write(f"VOLTage:HIGH {value['HIGH']}")
                self._write(f"VOLTage:LOW {value['LOW']}")
            except KeyError:
                try:
                    self._write(f"VOLTage {value['AMPLITUDE']}")
                    self._write(f"VOLTage:OFFSET {value['OFFSET']}")
                    # TODO optional voltage units
                except KeyError:
                    self.logger.exception("When supplying a voltage dictionary, keys 'LOW' and 'HIGH' or 'AMPLITUDE' "
                                          "and 'OFFSET' are mandatory")
            # TODO optional range

    @property
    def offset(self):
        """
        Gets the dc offset voltage.
        :return: voltage
        :rtype: float
        """
        return float(self._read("VOLTage:OFFSet?"))

    @offset.setter
    def offset(self, value):
        """
        Set the dc offset voltage.

        :param value: voltage offset to apply
        :type value: float
        """
        if abs(value)+self.voltage/2 > self.CAPABILITY["amplitude_range"]['max']:
            raise ValueError( "offset puts voltage out of range")
        else:
            self._write(f"VOLTage:OFFSet {value}")

    # TODO VOLT_UNITS
    # TODO VOLT_RANGE


class Keysight332XXXWaveform(BaseAWGWaveform):
    """
    Keysight 332XXX common waveform class
    """

    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param frequency_: frequency of periodic waveform in Hz
        :type frequency_: float
        :param type_: select between sine wave, square wave, ramp, pulse, noise, dc, user defined
        :type type_: str
        :param amplitude_:
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def type(self):
        """
        output function
        :return:  “SIN”, “SQU”, “RAMP”, “PULS”, “NOIS”, “DC”, or “USER”
        :rtype: str
        """
        output_dict = {'SIN': 'SINUSOID', 'SQU': 'SQUARE', 'RAMP': 'RAMP', 'PULS': 'PULSE', 'NOIS': 'NOISE',
                       'DC': 'DC', 'USER': 'USER'}
        return output_dict[self._read("FUNCtion?")]

    @type.setter
    def type(self, value):
        """
        Sets the output function to one of 'SINUSOID', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'DC' or 'USER'

        :param value:  Can be either
            a string for basic waveform configuration where frequency amplitude and offset have already been set,
            or a dict specifying 'FUNCTION' as a minimum and 'FREQUENCY', 'AMPLITUDE' or 'OFFSET' as optional
            key:value pairs
        :type value: Union(str, dict)
        """
        input_dict = {'SINUSOID': 'SIN', 'SQUARE': 'SQU', 'RAMP': 'RAMP', 'PULSE': 'PULS', 'NOISE': 'NOIS',
                       'DC': 'DC', 'USER': 'USER'}
        # list of functions that can be simply setup up with an 'APPLy' command
        apply_able = ('SINUSOID', 'SQUARE', 'RAMP', 'NOISE', 'DC')
        if isinstance(value, str):
            value = value.upper()
            if value not in input_dict.keys():
                raise ValueError("Please specify 'SINUSOID', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'DC' or 'USER'")
            else:
                self._write(f'APPLy:{input_dict[value]}')

        elif isinstance(value, dict):
            if 'FUNCTION' not in value.keys():
                raise ValueError("Please use the 'FUNCTION' key to specify a function type")
            else:
                if value['FUNCTION'] not in input_dict.keys():
                    raise ValueError("Please specify 'SINUSOID', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'DC' or 'USER'")
                else:
                    # if functions is simply set up with an APPLy command
                    if value['FUNCTION'] in apply_able:
                        # build options from dict keys
                        options = ''
                        if value['FUNCTION'] == "NOISE":
                            if 'AMPLITUDE' in value.keys():
                                # noise has no frequency, so set ot DEF
                                options += 'DEF, ', str(value['AMPLITUDE'])
                                if 'OFFSET' in value.keys():
                                    options += ', ', str(value['OFFSET'])
                        elif value['FUNCTION'] == "DC":
                            if 'OFFSET' in value.keys():
                                # DC voltage has only an offset value
                                options += 'DEF, DEF, ', str(value['OFFSET'])
                        else:
                            if 'FREQUENCY' in value.keys():
                                options += ' ', str(value['FREQUENCY'])
                                if 'AMPLITUDE' in value.keys():
                                    options += ', ', str(value['AMPLITUDE'])
                                    if 'OFFSET' in value.keys():
                                        options += ', ', str(value['OFFSET'])

                        self._write(f'APPLy:{input_dict[value]}{options}')

                    elif value['FUNCTION'] == 'PULSE':
                        pass
                    elif value['FUNCTION'] == 'USER':
                        pass
                    else:
                        raise ValueError(f"How did you ever get here!? value['FUNCTION']= {value['FUNCTION']}")