from decimal import Decimal
import re
import os
from time import sleep
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock
from CLI.Utilities.custom_structures import CustomDict
from CLI.Equipment.SamplingScope.base_sampling_scope import BaseSamplingScope
from CLI.Equipment.SamplingScope.base_sampling_scope import BaseSamplingScopeTrigger
from CLI.Equipment.SamplingScope.base_sampling_scope import BaseSamplingScopeTimebase
# Optical Modules
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_optical_module import Keysight86100XSingleOpticalModule
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86105d import Keysight86105DSingleOpt
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86105d import Keysight86105DSingleElec
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86105c import Keysight86105CSingleElec
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86105c import Keysight86105CSingleOpt
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86116c import Keysight86116CSingleOpt
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86116c import Keysight86116CSingleElec
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86116a import Keysight86116ASingleElec
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86116a import Keysight86116ASingleOpt
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_n1092a import KeysightN1092ASingleOpt
# Electrical Modules
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module import\
    Keysight86100XSingleElectricalModule
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_n1045a import KeysightN1045ASingle
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_n1045a import KeysightN1045ADiff
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_n1046a import KeysightN1046ASingle
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_n1046a import KeysightN1046ADiff
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_n1055a import KeysightN1055ASingle
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_n1055a import KeysightN1055ADiff
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86118a import Keysight86118ASingle
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86118a import Keysight86118ADiff
# Precision Timebase
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_86107a import Keysight86107A
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100DPrecisionTimebase
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XJitterMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XEyeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import _Keysight86100XDisplayMemory
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XOscilloscopeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XPAMEyeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XPAMOscilloscopeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_n1076a import KeysightN1076A
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100DTDECQ


class Keysight86100X(BaseSamplingScope):
    """
    Keysight Scope driver
    """

    CAPABILITY = {'functions': ['ADD', 'ALIGn', 'AMPLify', 'AVERage', 'BESSel', 'BUTTerworth',
                                'CONVolve', 'CTLE', 'DCONvolve', 'DDEConvolve', 'DDEMbed',
                                'DEConvolve', 'DELay', 'DEMbed', 'DFEQualizer', 'DIFFerence',
                                'FFEQualizer', 'FFT', 'GAUSsian', 'INTegrate', 'INTerpolate',
                                'INVert', 'MAX', 'MEDian', 'MIN', 'MULTiply', 'RANDom', 'SINC',
                                'SQUare', 'SROot', 'SUBTract', 'SUMMation', 'TEQualizer', 'VERSus',
                                'BUSer', 'USER']}

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

        self.func = CustomDict()
        """:type: list of Keysight86100XFunction"""
        self.wf = CustomDict()
        """:type: list of Keysight86100XWaveformMemory"""
        self.cgsx = CustomDict()
        """:type: list of Keysight86100XCGSX"""
        self.elec = CustomDict()
        """:type: list of Keysight86100XSingleElectricalModule"""
        self.opt = CustomDict()
        """:type: list of Keysight86100XSingleOpticalModule"""
        self.cdr = CustomDict()
        """:type: list of Keysight86100DClockDataRecovery"""

        self.timebase = Keysight86100XTimebase(interface=interface, dummy_mode=dummy_mode)
        self.trigger = Keysight86100XTrigger(interface=interface, dummy_mode=dummy_mode)
        self.limit_test = Keysight86100XLimitTest(interface=interface, dummy_mode=dummy_mode)
        self.int_precision_timebase = None

        self._wf_memory_index = 1
        self._cgsx_memory_index = 1
        self._pam = None
        self._electrical_channel_counter = 1
        self._state = None

    @property
    def display_mode(self):
        """
        Specify scope display mode

        :value: - 'OVERLAP'
                - 'TILE'
                - 'STACK'
                - 'ZOOM'
        :type: str
        :raise ValueError: exception if mode not 'OVERLAP', 'TILE', 'STACK', 'ZOOM'
        """
        output_dict = {'OVER': 'OVERLAP', 'TIL': 'TILE', 'STIL': 'STACK', 'ZTIL': 'ZOOM'}
        return output_dict[self._read("DISPlay:WINDow:TIME1:DMODe?", dummy_data='OVER')]

    @display_mode.setter
    def display_mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'OVERLAP', 'TILE', 'STACK', 'ZOOM'
        """
        value = value.upper()
        input_dict = {'OVERLAP': 'OVER', 'TILE': 'TIL', 'STACK': 'STIL', 'ZOOM': 'ZTIL'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'OVERLAP', 'TILE', 'STACK', or 'ZOOM'")
        else:
            self._write("DISPlay:WINDow:TIME1:DMODe {}".format(input_dict[value]))

    @property
    def display_persistence(self):
        """
        Specify scope display persistence.
        Acceptable values when in scope mode are only 'COLOR_GRADE' and 'GRAY_SCALE'

        :value: - 'MINIMUM'
                - 'INFINITE'
                - 'COLOR_GRADE'
                - 'GRAY_SCALE'
                - 'VARIABLE'
        :type: str
        :raise ValueError: exception if persistence not 'MIN', 'INF', 'CGR', 'GSC', or 'VAR'
        """
        if self.mode == 'OSC':
            input_dict = {'MIN': 'MINIMUM', 'INF': 'INFINITE', 'CGR': 'COLOR_GRADE',
                          'GSC': 'GRAY_SCALE', 'VAR': 'VARIABLE'}
        else:
            input_dict = {'CGR': 'COLOR_GRADE', 'GSC': 'GRAY_SCALE'}

        return input_dict[self._read("DISP:PERS?", dummy_data='CGR')]

    @display_persistence.setter
    def display_persistence(self, value):
        """
        :type value: str
        :raise ValueError: exception if persistence not 'MIN', 'INF', 'CGR', 'GSC', or 'VAR'
        """
        value = value.upper()
        if self.mode == 'OSC':
            input_dict = {'MINIMUM': 'MIN', 'INFINITE': 'INF', 'COLOR_GRADE': 'CGR',
                          'GRAY_SCALE': 'GSC', 'VARIABLE': 'VAR'}
        else:
            input_dict = {'COLOR_GRADE': 'CGR', 'GRAY_SCALE': 'GSC'}

        if value not in input_dict.keys():
            raise ValueError("Please specify either %s" % list(input_dict))
        else:
            self._write("DISP:PERS {}".format(input_dict[value]))

    @property
    def measurements_list(self):
        """
        **READONLY**

        :value: dictionary of all measurements displayed on the screen and the details associated
        :type: dict
        """
        output = {}
        ans = self._read(":MEASure:Results?",
                         dummy_data='Name=Fall Time,Source=3A,Current=2.346E-11,Min=2.346E-11,'
                                    'Max=2.346E-11,Count=1.5E+1,Name=VECP[OMA XP],Source=3A,'
                                    'Current=1.5E-1,Min=1.5E-1,Max=1.5E-1,Count=2.4E+1,'
                                    'Name=Jitter[rms],Source=1A,Current=1.008E-12,Min=1.008E-12,'
                                    'Max=1.030E-12,Count=3.2E+1').split(',')


        return_iterator = iter(ans)
        key_value_parser = re.compile(r"(?P<key>\w*?)=(?P<value>.*?)$")

        # The following assumes that the returen string appears as a commma seperated list
        # with a form :
        # Name=yyy,Source=xxx,fact_1=###,fact_2=###,...,Name=zzz...
        for item in return_iterator:
            parsed_string = key_value_parser.search(item)

            if parsed_string.group('key') == 'Name':
                current_measurement = parsed_string.group('value')
                parsed_string = key_value_parser.search(return_iterator.__next__())
                if parsed_string.group('key') != 'Source':
                    raise ValueError("Returned measurements list does not have the expected form.")
                current_source = parsed_string.group('value')

                if current_source not in output.keys():
                    output[current_source] = {}
                if current_measurement not in output[current_source].keys():
                    output[current_source][current_measurement] = {}
                else:
                    # While rare, you can have the same measurement twice (presumably with a
                    # slightly different configuration for each)
                    append_value = 1
                    while (current_measurement + '.' + str(append_value)) in output[current_source].keys():
                        append_value += 1
                    output[current_source][current_measurement + '.' + str(append_value)] = {}
            else:
                # Assume items are for the last identified measurement
                try:
                    output[current_source][current_measurement].update(
                        {parsed_string.group('key'): float(parsed_string.group('value'))}
                    )
                except ValueError:
                    output[current_source][current_measurement].update(
                        {parsed_string.group('key'): parsed_string.group('value')}
                    )
        return output

    @property
    def measurement_threshold(self):
        """
        Specify measurement threshold: either 90 --> 10%, 50%, 90%
        or 80 --> 20%, 50%, 80%

        :value: - 90
                - 80
        :type: int
        :raise ValueError: exception if measurement threshold 90 or 80
        """
        output_dict = {'P205080': 80, 'P105090': 90}
        return int(output_dict[self._read(":MEASure:THReshold:METHod?", dummy_data='P105090')])

    @measurement_threshold.setter
    def measurement_threshold(self, value):
        """
        :type value: int
        :raise ValueError: exception if measurement threshold 90 or 80
        """
        input_dict = {80: 'P205080', 90: 'P105090'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either 90 or 80')
        else:
            self._write(":MEASure:THReshold:METHod {}".format(input_dict[value]))

    @property
    def mode(self):
        """
        Specify scope mode

        :value: - 'EYE'
                - 'OSC'
                - 'JITT'
        :type: str
        :raise ValueError: exception if mode not 'EYE', 'JITT' or 'OSC'
        """
        return self._read("SYST:MODE?", dummy_data='OSC')

    @mode.setter
    def mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'EYE', 'JITT' or 'OSC'
        """
        value = value.upper()
        if value not in ['EYE', 'OSC', 'JITT']:
            raise ValueError('Please specify either "EYE", "JITT" or "OSC"')
        else:
            self._write("SYST:MODE {}".format(value))
            _Keysight86100XDisplayMemory._MODE_STATE = value

    @property
    def modules(self):
        """
        **READONLY**

        :value: returns a list of dictionaries of all modules and module ids connected
        :type: list
        """
        # Create 2 dicts with module names as keys
        # and a list of module numbers/options as the value
        modules_and_options = {'PAM': False, 'PTB': False}
        dummy_modules = ['86118A', '86105D', '86107A', 'Not Present', 'Not Present']
        for module_id in range(1, 6):
            module_name = self._read(":SYSTem:MODel? SLOT%s" % module_id,
                                     dummy_data=dummy_modules[module_id - 1])
            option = self._read(':SYSTem:OPTions? SLOT%s' % module_id,
                                dummy_data=dummy_modules[module_id - 1])
            modules_and_options[module_id] = {'module_name': module_name, 'module_option': option}

        opt = self._read('*OPT?', dummy_data='PAM')

        if 'PAM' in opt:
            modules_and_options['PAM'] = True
        if 'PTB' in opt:
            modules_and_options['PTB'] = True

        return modules_and_options

    def _configure(self):
        """
        Queries the hardware to determine its configuration and configures the drivers accordingly.
        """

        modules_and_options = self.modules
        self.find_function(create_objects='ENABLE')

        self._electrical_channel_counter = 1
        self._optical_channel_counter = 1

        if modules_and_options['PTB']:
            self.int_precision_timebase = Keysight86100DPrecisionTimebase(dummy_mode=self.dummy_mode,
                                                                          interface=self._interface)
        if modules_and_options['PAM']:
            self.tdecq = Keysight86100DTDECQ(interface=self._interface,
                                             dummy_mode=self.dummy_mode)

        # TODO: Fix remaining channel names when configuring. Current channel names are placeholders for some modules.
        for module_id in range(1, 6, 1):
            module_name = modules_and_options[module_id]['module_name']
            module_option = modules_and_options[module_id]['module_option']
            pam = modules_and_options['PAM']

            if "86118A" in module_name:
                self.elec['{}{}'.format(module_id, 'A')] = Keysight86118ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86118ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['{}{}'.format(module_id+1, 'A')] = Keysight86118ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id+1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86118ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id+1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['D{}A'.format(module_id)] = Keysight86118ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86118ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

            elif "86116A" in module_name:
                self.elec['{}{}'.format(module_id, 'A')] = Keysight86116ASingleElec(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86116ASingleElec(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.opt['{}{}'.format(module_id+1, 'A')] = Keysight86116ASingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id+1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.opt[self._optical_channel_counter] = Keysight86116ASingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id+1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._optical_channel_counter += 1

            elif "N1045A" in module_name:
                # TODO this module can have different number of channels and would need to query before creating the channels
                self.elec['{}{}'.format(module_id, 'A')] = KeysightN1045ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1045ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['{}{}'.format(module_id, 'B')] = KeysightN1045ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='B', handle='CHAN{}B'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1045ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='B', handle='CHAN{}B'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['D{}A'.format(module_id)] = KeysightN1045ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1045ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['{}{}'.format(module_id, 'C')] = KeysightN1045ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='C', handle='CHAN{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1045ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='C', handle='CHAN{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['{}{}'.format(module_id, 'D')] = KeysightN1045ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='CHAN{}D'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1045ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='CHAN{}D'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['D{}C'.format(module_id)] = KeysightN1045ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1045ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

            elif "N1046A" in module_name:
                #TODO this module can have different number of channels and would need to query before creating the channels
                self.elec['{}{}'.format(module_id, 'A')] = KeysightN1046ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1046ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['{}{}'.format(module_id, 'B')] = KeysightN1046ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='B', handle='CHAN{}B'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1046ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='B', handle='CHAN{}B'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['D{}A'.format(module_id)] = KeysightN1046ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1046ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['{}{}'.format(module_id, 'C')] = KeysightN1046ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='C', handle='CHAN{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1046ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='C', handle='CHAN{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['{}{}'.format(module_id, 'D')] = KeysightN1046ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='CHAN{}D'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1046ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='CHAN{}D'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['D{}C'.format(module_id)] = KeysightN1046ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = KeysightN1046ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

            elif "N1055A" in module_name:

                self.elec['{}{}'.format(module_id, 'A')] = KeysightN1055ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec['{}{}'.format(module_id, 'B')] = KeysightN1055ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='B', handle='CHAN{}B'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec['{}{}'.format(module_id, 'C')] = KeysightN1055ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='C', handle='CHAN{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec['{}{}'.format(module_id, 'D')] = KeysightN1055ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='CHAN{}D'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec['D{}A'.format(module_id)] = KeysightN1055ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec['D{}C'.format(module_id)] = KeysightN1055ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='C', handle='DIFF{}C'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

            elif "N1010A" in module_name:
                self.elec['{}{}'.format(module_id, 'A')] = Keysight86118ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86118ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['{}{}'.format(module_id, 'B')] = Keysight86118ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='B', handle='CHAN{}B'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86118ASingle(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='B', handle='CHAN{}B'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.elec['D{}A'.format(module_id)] = Keysight86118ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86118ADiff(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='D', handle='DIFF{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

            elif "86105D" in module_name:

                self.opt['{}{}'.format(module_id, 'A')] = Keysight86105DSingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.opt[self._optical_channel_counter] = Keysight86105DSingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._optical_channel_counter += 1

                self.elec['{}{}'.format(module_id + 1, 'A')] = Keysight86105DSingleElec(
                    module_id=module_id + 1,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id + 1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86105DSingleElec(
                    module_id=module_id + 1,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id + 1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

            elif "86105C" in module_name:

                self.opt['{}{}'.format(module_id, 'A')] = Keysight86105CSingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.opt[self._optical_channel_counter] = Keysight86105CSingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._optical_channel_counter += 1

                self.elec['{}{}'.format(module_id+1, 'A')] = Keysight86105CSingleElec(
                    module_id=module_id+1,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id+1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86105CSingleElec(
                    module_id=module_id+1,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id+1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

            elif "86116C" in module_name:

                self.elec['{}{}'.format(module_id, 'A')] = Keysight86116CSingleElec(
                    module_id=module_id + 1,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.elec[self._electrical_channel_counter] = Keysight86116CSingleElec(
                    module_id=module_id + 1,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id + 1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._electrical_channel_counter += 1

                self.opt['{}{}'.format(module_id + 1, 'A')] = Keysight86116CSingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id + 1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.opt[self._optical_channel_counter] = Keysight86116CSingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id + 1), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._optical_channel_counter += 1

            elif "86107A" in module_name:

                self.precision_timebase = Keysight86107A(module_id=module_id,
                                                         module_option=module_option,
                                                         dummy_mode=self.dummy_mode,
                                                         interface=self._interface)

            elif "N1076A" in module_name:

                self.cdr = KeysightN1076A(module_id=module_id,
                                          dummy_mode=self.dummy_mode,
                                          interface=self._interface)

            elif "N1092A" in module_name:

                self.opt['{}{}'.format(module_id, 'A')] = KeysightN1092ASingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self.opt[self._optical_channel_counter] = KeysightN1092ASingleOpt(
                    module_id=module_id,
                    module_option=module_option,
                    channel_number='A', handle='CHAN{}A'.format(module_id), pam=pam,
                    dummy_mode=self.dummy_mode, interface=self._interface)

                self._optical_channel_counter += 1

            else:
                if module_name != 'Not Present':
                    self.logger.error('%s is not a supported module' % module_name)

    def add_function(self, func_index, func_type, operand1, operand2=None):
        """
        Add a function channel. Operands must include the correct suffix as shown in the examples
        below.
        If a single-ended channel shows up as '1A' on the FlexDCA, then what should be
        passed as an input is 'CHAN1A'.
        If it was a differential channel, for example 'D1A', then the operand would be 'DIFF1A'.
        A function can also be used as an operand. 'FUNC' prefix needs to be added to the
        function number, for example 'FUNC2' will use function 2 as an operand.

        For functions needing additional configuration, please refer to CLI team member for
        support.

        :param func_index: function index (1-16)
        :type func_index: int
        :param func_type: function type (e.g 'AVERAGE')
        :type func_type: str
        :param operand1: channel (e.g 'CHAN1A' or 'DIFF1A' or 'FUNC1')
        :type operand1: str
        :param operand2: channel (e.g 'CHAN1A' or 'DIFF1A' or 'FUNC1')
        :type operand2: str
        :return: function name
        :rtype: str
        :raise ValueError: exception if 'func_type' is not valid
        """
        func_type = func_type
        if func_type not in self.CAPABILITY['functions']:
            raise ValueError('Please specify a valid function type')
        else:
            if self.find_function()[('FUNC_{0}'.format(func_index))] != 'NONE':
                self.logger.warning('Existing function will be replaced')

            self._unblock_setattr()
            self._write(':FUNCtion{}:FOP {}'.format(func_index, func_type))
            self._write(':FUNCtion{}:OPERand1 {}'.format(func_index, operand1))

            if operand2:
                self._write(':FUNCtion{}:OPERand2 {}'.format(func_index, operand2))

            self.func['F{}'.format(func_index)] = Keysight86100XFunction(module_id=func_index,
                                                                         module_option=0,
                                                                         channel_number=0,
                                                                         handle='FUNCtion{}'.format(func_index),
                                                                         pam=self.modules['PAM'],
                                                                         interface=self._interface,
                                                                         dummy_mode=self.dummy_mode)

            self._block_setattr()

            return 'FUNC' + str(func_index)

    def find_function(self, create_objects='DISABLE'):
        """
        Returns a dictionary of all the functions that exist

        :return: Dictionary of exisiting functions
        :rtype: dict
        """
        functions = {}

        for n in range(1, 17, 1):
            func_name = self._read(':FUNC{0}:FOP?'.format(n))
            functions['FUNC_{0}'.format(n)] = func_name

            if create_objects == 'ENABLE':
                if self._read(':FUNC{0}:STAT?'.format(n)) == 'AVA':
                    self.func['F{0}'.format(n)] = Keysight86100XFunction(module_id=n,
                                                                         module_option=0,
                                                                         channel_number=0,
                                                                         handle='FUNCtion{}'.format(n),
                                                                         pam=self.modules['PAM'],
                                                                         interface=self._interface,
                                                                         dummy_mode=self.dummy_mode)

        return functions

    def auto_scale(self, blocking=False, timeout=60):
        """
        Perform auto scale
        """
        if blocking:
            self._write(":SYST:AUT", type_='stb_poll_sync', timeout=timeout)
        else:
            self._write(":SYST:AUT")

    def clear(self):
        """
        Clears display
        """
        self._write(":ACQuire:CDIS")

    def clear_measurements(self):
        """
        Method to clear the measurements pane at the bottom of the screen
        """
        self._write(':MEAS:EYE:LIST:CLE')
        self._write(':MEAS:OSC:LIST:CLE')
        self._write(':MEAS:JITT:LIST:CLE')

    def delete_function(self, func_index):
        """
        Delete a function that was previously created. If the function is 'F1', then 1 should be
        passed as a func_index.

        :param func_index: index of function (e.g 'F1') or '_all_'
        :type func_index: str
        :raise ValueError: exception if function index is incorrect
        """
        self._unblock_setattr()

        if func_index == '_all_':
            index = 17
            func_index = 'F1'
        else:
            index = 2

        for n in range(1, index, 1):
            if ('F{}'.format(func_index[1:])) not in self.func.keys():
                if index == 1:
                    raise ValueError('Function index is incorrect')

            else:
                del self.func['F{}'.format(func_index[1:])]
                self._write(':FUNC{0}:FOP NONE'.format(func_index[1:]))

            func_index = 'F{0}'.format(n+1)

        self._block_setattr()

    def load_cgsx(self, file):
        """
        Load an existing cgsx memory file

        :param file: cgsx file path
        :type file: str
        """
        self._unblock_setattr()
        self._write(':EMEMory{}:FILE:NAME "{}"'.format(
            self._cgsx_memory_index, file))
        self._write(':EMEMory{}:FILE:LOAD'.format(self._cgsx_memory_index))

        self.cgsx['CM{}'.format(self._cgsx_memory_index)] = Keysight86100XCGSX(
            0, 0, 0, 'CGMemory{}'.format(self._cgsx_memory_index), 'EMEMory{}'.format(
                self._cgsx_memory_index), interface=self._interface, dummy_mode=self.dummy_mode)

        self.cgsx[self._cgsx_memory_index] = Keysight86100XCGSX(
            0, 0, 0, 'CGMemory{}'.format(self._cgsx_memory_index), 'EMEMory{}'.format(
                self._cgsx_memory_index), interface=self._interface, dummy_mode=self.dummy_mode)

        if self._cgsx_memory_index < 8:
            self._cgsx_memory_index += 1
        self._block_setattr()

    def load_wf_memory(self, file):
        """
        Load an existing waveform memory file

        :param file: waveform file path
        :type file: str
        """
        self._unblock_setattr()
        self._write(r':WMEMory{}:FILE:NAME "{}"'.format(
            self._wf_memory_index, file))
        self._write(':WMEMory{}:FILE:LOAD'.format(self._wf_memory_index))
        if self._read(':WMEMory{}:SIGN:TYPE?'.format(self._wf_memory_index)) == 'PAM4':
            pam = True

        self.wf['W{}'.format(self._wf_memory_index)] = Keysight86100XWaveformMemory(
            0, 0, 0, 'WMEMory{}'.format(self._wf_memory_index), pam=pam, interface=self._interface, dummy_mode=self.dummy_mode)

        self.wf[self._wf_memory_index] = Keysight86100XWaveformMemory(
            0, 0, 0, 'WMEMory{}'.format(self._wf_memory_index), pam=pam, interface=self._interface, dummy_mode=self.dummy_mode)

        if self._wf_memory_index < 8:
            self._wf_memory_index += 1
        self._block_setattr()

    def run(self, blocking=False, timeout=60):
        """
        Changes acquiring state to 'RUN'

        :param timeout: time before equipment write times out. Can be changed if longer measurements are performed
        :type timeout: int
        :param blocking: blocking call for when running limit tests
        :type blocking: bool
        """
        if blocking:
            self._write(":ACQuire:RUN", type_='stb_poll_sync', timeout=timeout)
        else:
            self._write(":ACQuire:RUN")

    def save_screen(self, filename):
        """
        Saves a picture of the network analyzer screen to the PC running CLI.
        Saves as a .png file.

        :param filename: path and file e. Path is relative to PC running CLI.
        :type filename: str
        """

        orig = self._interface.visa_handle.read_termination
        self._interface.visa_handle.read_termination = None

        # Dummy image saved on scope before transferring it to PC
        scope_path = 'D:\\User Files\\Screen Images\\test_image.png'
        try:
            self._write(':DISK:SIMage:FNAMe "{}"'.format(scope_path))
            self._write(':DISK:SIM:SAVE')
            self._read('*OPC?')
        except Exception as e:
            err_msg = 'EXCEPTION: ' + str(e.args)
            self.logger.warning(err_msg)
            self._write("*CLS")
            self._write(':DISK:SIMage:FNAMe "{}"'.format(scope_path))
            self._write(':DISK:SIM:SAVE')

        data = self._interface.visa_handle.query_binary_values(':DISK:BFILE? "' + scope_path + '"', datatype='s')

        if not filename.endswith('.png'):
            filename += '.png'

        fh = open(filename, 'wb')
        fh.write(data[0])
        fh.close()
        self.logger.info("Image saved to {}".format(os.path.realpath(fh.name)))

        self._interface.visa_handle.read_termination = orig

    def single(self):
        """
        Changes acquiring state to 'SINGLE'
        """
        self._write(":ACQuire:SING")

    def stop(self):
        """
        Changes acquiring state to 'STOP'
        """
        self._write(":ACQuire:STOP")


class Keysight86100XLimitTest(BaseEquipmentBlock):
    """
    Keysight 86100X Acquisition Limit Test Block
    """

    def __init__(self, interface, dummy_mode, **kwargs):
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

    @property
    def number(self):
        """
        Number of samples or number of waveforms, depending on
        selected acquisition limit type.

        :value: number of waveforms/samples
        :type: int
        """
        if self.type == 'WAVEFORM':
            return int(self._read(':LTESt:ACQuire:CTYPe:WAVeforms?'))
        elif self.type == 'SAMPLE':
            return int(self._read(':LTESt:ACQuire:CTYPe:SAMPles?'))
        else:
            return int(self._read(':LTESt:ACQuire:CTYPe:PATTerns?'))

    @number.setter
    def number(self, value):
        """
        :type value: float
        """
        if self.type == 'WAVEFORM':
            self._write(':LTESt:ACQuire:CTYPe:WAVeforms {}'.format(value))
        elif self.type == 'SAMPLE':
            self._write(':LTESt:ACQuire:CTYPe:SAMPles {}'.format(value))
        else:
            self._write(':LTESt:ACQuire:CTYPe:PATTerns {}'.format(value))

    @property
    def state(self):
        """
        Disable or Enable acquisition limits

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":LTESt:ACQuire:STATe?")]

    @state.setter
    def state(self, value):  # TODO: Add Polling
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':LTESt:ACQuire:STATe {}'.format(input_dict[value]))

    @property
    def type(self):
        """
        Select acquisition limit type

        :value: - 'WAVEFORM'
                - 'SAMPLE'
        :type: str
        :raise ValueError: exception if limit_type is not "WAVEFORM" or "SAMPLE"
        """
        output_dict = {'WAV': 'WAVEFORM', 'SAMP': 'SAMPLE', 'PATT': 'PATTERN', 'DUMMY_DATA': 'WAVEFORM'}
        return output_dict[self._read(':LTESt:ACQuire:CTYPe?')]

    @type.setter
    def type(self, value):
        """
        :type value: str
        :raise ValueError: exception if limit_type is not "WAVEFORM" or "SAMPLE"
        """
        value = value.upper()
        input_dict = {'WAVEFORM': 'WAV', 'SAMPLE': 'SAMP', 'PATTERN': 'PATT'}
        # TODO: Can only put in pattern mode when scope is pattern locked. Need to add error checking.
        if value not in input_dict.keys():
            raise ValueError('Please specify either "WAVEFORM" or "SAMPLE"')
        else:
            self._write(':LTESt:ACQuire:CTYPe {}'.format(input_dict[value]))


class Keysight86100XTrigger(BaseSamplingScopeTrigger):
    """
    Keysight 86100X Trigger Block
    """
    CAPABILITY = {'symbol_rate': {'min': 50e6, 'max': 1e12},
                  'divide_ratio': {'min': 1, 'max': 256},
                  'level': {'min': -1, 'max': 1},
                  'pattern_length': {'min': 1, 'max': 2147483647}}

    def __init__(self, interface, dummy_mode, **kwargs):
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
        self._source = None

    @property
    def divide_ratio(self):
        """
        Divide ratio

        :value: - 'AUTO'
                - int
        :type: int
        :raise ValueError: exception if input is not 'AUTO' or int
        """
        if self._read(":TRIGger:DCDRatio:AUTodetect?") == '0':
            return int(self._read(':TRIGger:DCDRatio?').strip('SUB'))
        else:
            return 'AUTO'

    @divide_ratio.setter
    def divide_ratio(self, value):
        """
        :type value: int
        :raise ValueError: exception if input is not 'AUTO' or in acceptable range
        """
        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if str(value).upper() == 'AUTO':
            self._write(':TRIGger:DCDRatio:AUTodetect ON')
        elif self.CAPABILITY['divide_ratio']['min'] <= value <= \
                self.CAPABILITY['divide_ratio']['max']:
            self._write(':TRIGger:DCDRatio:AUTodetect OFF')
            if value == 1:
                self._write(':TRIGger:DCDRatio UNIT')
            else:
                self._write(':TRIGger:DCDRatio SUB{}'.format(value))
        else:
            raise ValueError("Please specify either 'AUTO' or an int between 1 and 256")

    @property
    def hysteresis(self):
        """
        Hysteresis

        :value: - 'NORMAL'
                - 'HIGH_SENS'
        :type: str
        :raise ValueError: exception if value not 'NORMAL' or 'HIGH_SENS'
        """
        output_dict = {'NORM': 'NORMAL', 'HSEN': 'HIGH_SENS', 'DUMMY_DATA': 'NORMAL'}
        return output_dict[self._read(":TRIGger:HYSTeresis?")]

    @hysteresis.setter
    def hysteresis(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'NORMAL' or 'HIGH_SENS'
        """
        input_dict = {'NORMAL': 'NORM', 'HIGH_SENS': 'HSEN'}
        value = value.upper()

        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if self.mode == 'CLOCK':
            raise ValueError('Hysteresis cannot be adjusted in Clock/Divided Mode')

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'NORMAL' or 'HIGH_SENS'")
        else:
            self._write(":TRIGger:HYSTeresis {}".format(input_dict[value]))

    @property
    def level(self):
        """
        :value: trigger level (V)
        :type: float
        """
        return float(self._read(":TRIGger:LEVel?"))

    @level.setter
    def level(self, value):
        """
        :type value: float
        """
        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if self.mode == 'CLOCK':
            raise ValueError('Level cannot be adjusted in Clock/Divided Mode')

        if self.CAPABILITY['level']['min'] <= value <= \
                self.CAPABILITY['level']['max']:
            self._write(':TRIGger:LEVel {:.2E}'.format(Decimal(value)))
        else:
            raise ValueError('Trigger level must be between {} and {}'.format(
                self.CAPABILITY['level']['min'], self.CAPABILITY['level']['max']))

    @property
    def mode(self):
        """
        Trigger mode

        :value: - 'FILTERED'
                - 'EDGE'
        :type: str
        :raise ValueError: exception if mode not 'FILTERED' or 'EDGE'
        """
        output_dict = {'FILT': 'FILTERED', 'EDGE': 'EDGE', 'CLOC': 'CLOCK'}
        return output_dict[self._read(":TRIGger:MODE?", dummy_data='FILT')]

    @mode.setter
    def mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'FILTERED' or 'EDGE'
        """
        input_dict = {'FILTERED': 'FILT', 'EDGE': 'EDGE', 'CLOCK': 'CLOC'}
        value = value.upper()

        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'FILTERED', 'EDGE' or 'CLOCK'")
        else:
            self._write(":TRIGger:MODE {}".format(input_dict[value]))

    @property
    def pattern_length(self):
        """
        Pattern length

        :value: - 'AUTO'
                - int
        :type: int
        :raise ValueError: exception if input is not 'AUTO' or an int between 1 and 2147483647
        """
        if self._read(":TRIGger:PLENgth:AUTodetect?") == '0':
            return int(self._read(':TRIGger:PLENgth?'))
        else:
            return 'AUTO'

    @pattern_length.setter
    def pattern_length(self, value):
        """
        :type value: int
        :raise ValueError: exception if input is not 'AUTO' or an int between 1 and 2147483647
        """
        range_min = self.CAPABILITY['pattern_length']['min']
        range_max = self.CAPABILITY['pattern_length']['max']

        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if str(value).upper() == 'AUTO':
            self._write(':TRIGger:PLENgth:AUTodetect ON')
        elif isinstance(value, int) and range_min < value < range_max:
            self._write(':TRIGger:PLENgth:AUTodetect OFF')
            self._write(':TRIGger:PLENgth {}'.format(value))
        else:
            raise ValueError("Please specify either 'AUTO' or an int between %s and %s"
                             % (range_min, range_max))

    @property
    def pattern_lock(self):  # TODO: Add Polling
        """
        Disable or Enable pattern lock

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":TRIGger:PLOCk?")]

    @pattern_lock.setter
    def pattern_lock(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}

        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':TRIGger:PLOCk {}'.format(input_dict[value]), type_='stb_poll_sync')

    @property
    def signal_type(self):
        """
        Signal type

        :value: - 'AUTO'
                - 'CLOCK'
                - 'DATA'
        :type: str
        :raise ValueError: exception if input is not 'AUTO', 'CLOCK' or 'DATA'
        """
        output_dict = {'CLOC': 'CLOCK', 'DATA': 'DATA'}

        if self._read(":MEASure:JITTer:DEFine:SIGNal:AUTodetect?") == '0':
            return output_dict[self._read(":MEASure:JITTer:DEFine:SIGNal?")]
        else:
            return 'AUTO'

    @signal_type.setter
    def signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not 'AUTO', 'CLOCK' or 'DATA'
        """
        value = value.upper()

        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if value not in ['AUTO', 'CLOCK', 'DATA']:
            raise ValueError("Please specify either 'AUTO', 'CLOCK' or 'DATA'")
        elif value == 'AUTO':
            self._write(':MEASure:JITTer:DEFine:SIGNal:AUTodetect ON')
        else:
            self._write(':MEASure:JITTer:DEFine:SIGNal:AUTodetect OFF')
            self._write(':MEASure:JITTer:DEFine:SIGNal {}'.format(value))

    @property
    def slope(self):
        """
        Trigger slope

        :value: - 'RISE'
                - 'FALL'
        :type: str
        :raise ValueError: exception if mode not 'RISE' or 'FALL'
        """
        output_dict = {'POS': 'RISE', 'NEG': 'FALL'}
        return output_dict[self._read(":TRIGger:SLOPe?", dummy_data='POS')]

    @slope.setter
    def slope(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'RISE' or 'FALL'
        """
        input_dict = {'RISE': 'POS', 'FALL': 'NEG'}
        value = value.upper()

        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if self.mode == 'CLOCK':
            raise ValueError('Slope cannot be adjusted in Clock/Divided Mode')

        if value not in input_dict.keys():
            raise ValueError("Please specify either 'RISE' or 'FALL'")
        else:
            self._write(":TRIGger:SLOPe {}".format(input_dict[value]))

    @property
    def source(self):
        """
        Trigger source

        :value: - 'FREE_RUN'
                - 'FRONT_PANEL'
        :type: str
        :raise ValueError: exception if mode not 'FREE_RUN' or 'FRONT_PANEL'
        """
        output_dict = {'FPAN': 'FRONT_PANEL', 'FRUN': 'FREE_RUN'}
        self._source = output_dict[self._read(":TRIGger:SOURce?", dummy_data='FPAN')]
        return self._source

    @source.setter
    def source(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'FREE_RUN' or 'FRONT_PANEL'
        """
        input_dict = {'FREE_RUN': 'FRUN', 'FRONT_PANEL': 'FPAN'}
        value = value.upper()
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'FREE_RUN' or 'FRONT_PANEL'")
        else:
            self._write(":TRIGger:SOURce {}".format(input_dict[value]))
            self._source = value

    @property
    def symbol_rate(self):
        """
        Symbol rate

        :value: - 'AUTO'
                - float
        :type: float
        :raise ValueError: exception if input is not 'AUTO' or a float between 50e6 and 1e12
        """
        if self._read(":TRIGger:SRATe:AUTodetect?") == '0':
            return float(self._read(':TRIGger:SRATe?'))
        else:
            return 'AUTO'

    @symbol_rate.setter
    def symbol_rate(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is not 'AUTO' or a float between 50e6 and 1e12
        """
        if self._source == 'FREE_RUN':
            raise ValueError('Advanced trigger settings cannot be accessed if trigger'
                             ' source is "FREE_RUN"')

        if str(value).upper() == 'AUTO':
            self._write(':TRIGger:SRATe:AUTodetect ON')
        elif 50e6 <= value <= 1e12:
            self._write(':TRIGger:SRATe:AUTodetect OFF')
            self._write(':TRIGger:SRATe {}'.format(value))
        else:
            raise ValueError("Please specify either 'AUTO' or a float between 50e6 and 1e12")


class Keysight86100XTimebase(BaseSamplingScopeTimebase):
    """
    Keysight 86100X Trigger Block
    """
    CAPABILITY = {'sec_scale': {'min': 100e-15, 'max': 124e-6},
                  'ui_scale': {'min': 10e-3, 'max': 12.4e6},
                  'ui_position': {'min': 239, 'max': 5e9},
                  'sec_position': {'min': 24e-9, 'max': 2.5e-3}}

    def __init__(self, interface, dummy_mode, **kwargs):
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

    @property
    def position(self):
        """
        Timebase position

        :value: delay at reference in seconds/UI
        :type: float
        """
        if self.units == 'SECONDS':
            return float(self._read(":TIMebase:POSition?"))
        else:
            return float(self._read(":TIMebase:UIP?"))

    @position.setter
    def position(self, value):
        """
        :type value: float
        """
        if self.units == 'SECONDS':
            self._write(':TIMebase:POSition {:.2E}'.format(Decimal(value)))
        else:
            self._write(':TIMebase:UIP {}'.format(value))

    @property
    def reference(self):
        """
        Timebase reference

        :value: - 'LEFT'
                - 'CENTER'
        :type: str
        :raise ValueError: exception if mode not 'LEFT' or 'CENTER'
        """
        output_dict = {'LEFT': 'LEFT', 'CENT': 'CENTER'}
        return output_dict[self._read(":TIMebase:REFerence?", dummy_data='LEFT')]

    @reference.setter
    def reference(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'LEFT' or 'CENTER'
        """
        input_dict = {'LEFT': 'LEFT', 'CENTER': 'CENT'}
        value = value.upper()
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'LEFT' or 'CENTER'")
        else:
            self._write(":TIMebase:REFerence {}".format(input_dict[value]))

    @property
    def scale(self):
        """
        :value: horizontal scale in seconds/baud
        :type: float
        """
        if self.units == 'SECONDS':
            return float(self._read(":TIMebase:SCALe?"))
        else:
            return float(self._read(':TIMebase:SRATe?'))

    @scale.setter
    def scale(self, value):
        """
        :type value: float
        """
        if self.units == 'SECONDS':
            self._write(':TIMebase:SCALe {:.2E}'.format(Decimal(value)))
        else:
            self._write(':TIMebase:SRATe {:.2E}'.format(Decimal(value)))

    @property
    def units(self):
        """
        Specify scope timebase units
        See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86100x.Keysight86100XTimebase.scale`
        See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86100x.Keysight86100XTimebase.position`

        :value: - 'SECONDS'
                - 'UI'
        :type: str
        :raise ValueError: exception if mode not 'SECONDS' or 'UI'
        """
        output_dict = {'SEC': 'SECONDS', 'UINT': 'UI'}
        return output_dict[self._read(":TIMebase:UNITs?", dummy_data='SEC')]

    @units.setter
    def units(self, value):
        """
        :type value: str
        :raise ValueError: exception if mode not 'SECONDS' or 'UI'
        """
        input_dict = {'SECONDS': 'SEC', 'UI': 'UINT'}
        value = value.upper()
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'SECONDS' or 'UI'")
        else:
            self._write(":TIMebase:UNITs {}".format(input_dict[value]))


class Keysight86100XFunction(BaseEquipmentBlock):
    """
    Keysight 86100X Function Block
    """
    def __init__(self, module_id=None, module_option=None, channel_number=None, handle=None,
                 pam=None, interface=None, dummy_mode=False, **kwargs):
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
        self._module_option = module_option
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = _Keysight86100XDisplayMemory(self._handle, interface, dummy_mode)

        self.osc = Keysight86100XOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                         self._display_memory, interface, dummy_mode)
        self.eye = Keysight86100XEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                self._display_memory, interface, dummy_mode)
        self.jitter = Keysight86100XJitterMeasurement(self._module_id, self._channel_number, self._handle,
                                                      self._display_memory, interface, dummy_mode)
        if pam:
            self.pam_eye = Keysight86100XPAMEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                           self._display_memory, interface, dummy_mode)
            self.pam_osc = Keysight86100XPAMOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                                    self._display_memory, interface, dummy_mode)

    @property
    def colour(self):
        """
        Sets function colour

        :value: - 'brown'
                - 'cyan'
                - 'blue'
                - 'aqua'
                - 'green'
                - 'pink'
                - 'red'
                - 'baby blue'
                - 'blue-grey'
                - 'yellow-orange'
                - 'lavender'
                - 'burgundy'
                - 'red-purple'
                - 'purple'
                - 'orange'
                - 'lime'
        :type: str
        """
        input_dict = {1: 'brown', 2: 'green', 3: 'blue-grey', 4: 'red-purple', 5: 'cyan', 6: 'pink', 7: 'yellow-orange',
                      8: 'purple', 9: 'blue', 10: 'red', 11: 'lavender', 12: 'orange', 13: 'aqua', 14: 'baby-blue',
                      15: 'burgundy', 16: 'lime'}
        return input_dict[int(self._read(':FUNC{0}:COL?'.format(self._module_id))[4:])]

    @colour.setter
    def colour(self, value):
        """
        :type: str
        """
        output_dict = {'brown': 1, 'green': 2, 'blue-grey': 3, 'red-purple': 4, 'cyan': 5, 'pink': 6,
                       'yellow-orange': 7, 'purple': 8, 'blue': 9, 'red': 10, 'lavender': 11, 'orange': 12, 'aqua': 13,
                       'baby-blue': 14, 'burgundy': 15, 'lime': 16}
        self._write(':FUNC{0}:COL TCOL{1}'.format(self._module_id, output_dict[value]))

    @property
    def display(self):
        """
        Enable or disable the function on the display

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read(':FUNC{0}:DISP?'.format(self._module_id))]

    @display.setter
    def display(self, value):
        """
        :type: str
        """
        output_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        self._write(':FUNC{0}:DISP {1}'.format(self._module_id, output_dict[value.upper()]))

    @property
    def bessel_bandwidth(self):
        """
        Bessel cutoff frequency

        :value: bandwidth in Hz
        :type: float
        """
        return float(self._read(':SPR{0}:BESS:BAND?'.format(self._module_id)))

    @bessel_bandwidth.setter
    def bessel_bandwidth(self, value):
        """
        :type value: float
        """
        if isinstance(value, float):
            if 10e6 <= value <= 1e12:
                self._write(':SPR{0}:BESS:BAND {1}'.format(self._module_id, value))
            else:
                raise ValueError("Valid input value range is 1e6 to 1e12 Hz")
        else:
            raise TypeError("Input value must be a float")

    @property
    def bessel_pnoise_bandwidth(self):
        """
        Bandwidth used when preserving the input waveform's noise on the output waveform

        :value: - 'AUTO' or float (Hz)
        :type: float
        """
        if self._read('SPR{0}:BESS:PNO:BAND:AUT?'.format(self._module_id)) == 'ON':
            self.logger.info('{0} math channel {1} Bessel Phase noise bandwidth is currently in auto mode'
                             .format(self._name, self._module_id))
        return float(self._read('SPR{0}:BESS:PNO:BAND?'.format(self._module_id)))

    @bessel_pnoise_bandwidth.setter
    def bessel_pnoise_bandwidth(self, value):
        """
        :type value: str or float
        """
        if isinstance(value, str):
            self._write('SPR{0}:BESS:PNO:BAND:AUT ON'.format(self._module_id))
        elif isinstance(value, float) or isinstance(value, int):
            if 10e6 <= value <= 1e12:
                self._write('SPR{0}:BESS:PNO:BAND:AUT OFF'.format(self._module_id))
                self._write(':SPR{0}:BESS:PNO:BAND {1}'.format(self._module_id, value))
            else:
                raise ValueError("Valid input value range is 1e6 to 1e12 Hz")
        else:
            raise TypeError("Input value must be a str, float, or int")

    @property
    def ctle_dc_gain(self):
        """
        DC Gain applied be a first-order transfer CTLE

        :value: DC Gain
        :type: float
        """
        return float(self._read('SPR{0}:CTL:GAIN?'.format(self._module_id)))

    @ctle_dc_gain.setter
    def ctle_dc_gain(self, value):
        """
        :type value: float
        """
        self._write('SPR{0}:CTL:GAIN {1}'.format(self._module_id, value))

    @property
    def ctle_pcount(self):
        """
        Specifies the number of poles for the CTLE

        :value: - 2
                - 3
        :type: int
        """
        return float(self._read('SPR{0}:CTL:PCO?'.format(self._module_id)))

    @ctle_pcount.setter
    def ctle_pcount(self, value):
        """
        :type value: int
        """
        self._write('SPR{0}:CTL:PCO {1}'.format(self._module_id, value))

    @property
    def ctle_pnoise(self):
        """
        Perserve Noise of a CTLE filter

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read('SPR{0}:CTL:PNO?'.format(self._module_id))]

    @ctle_pnoise.setter
    def ctle_pnoise(self, value):
        """
        :type value: str
        """
        output_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        self._write('SPR{0}:CTL:PNO {1}'.format(self._module_id, output_dict[value.upper()]))

    @property
    def ctle_pnoise_bandwidth(self):
        """
        Bandwidth used when preserving the input waveform's noise on the output waveform

        :value: 'AUTO' or float (Hz)
        :type: float
        """
        if self._read('SPR{0}:CTL:PNO:BAND:AUT?'.format(self._module_id)) == 'ON':
            self.logger.info('{0} math channel {1} CTLE bandwidth is currently in auto mode'
                             .format(self._name, self._module_id))
        return float(self._read('SPR{0}:CTL:PNO:BAND?'.format(self._module_id)))

    @ctle_pnoise_bandwidth.setter
    def ctle_pnoise_bandwidth(self, value):
        """
        :type value: str or float
        """
        if isinstance(value, str):
            self._write('SPR{0}:CTL:PNO:BAND:AUT ON'.format(self._module_id))
        else:
            self._write('SPR{0}:CTL:PNO:BAND:AUT OFF'.format(self._module_id))
            self._write(':SPR{0}:CTL:PNO:BAND {1}'.format(self._module_id, value))

    @property
    def ctle_preset(self):
        """
        Load a preset for the CTLE (ie. "OIF CEI-28G-VSR (3db)")

        :value: Decibel value for the preset
        :type: str
        """
        return self._read('SPR{0}:CTL:PRES?'.format(self._module_id))

    @ctle_preset.setter
    def ctle_preset(self, value):
        """
        :type value: str or float
        """
        if isinstance(value, str):
            if value in self.ctle_preset_list:
                self._write('SPR{0}:CTL:PRES "{1}"'.format(self._module_id, value))
            else:
                raise ValueError("Preset does not exist")
        else:
            raise TypeError("Input value must be string")

    @property
    def ctle_preset_list(self):
        """
        ***READ-ONLY***

        Returns a list of all available presets

        :value: Preset names
        :type: list of strings
        """
        return self._read('SPR{0}:CTL:PRES:SEL?'.format(self._module_id)).replace('"', '').split(", ")

    def ctle_pole_frequency_get(self, pole):
        """
        Returns the frequency of the specified pole

        :param pole: - 1
                      - 2
                      - 3
        :type pole: int
        :return: frequency in Hz
        :rtype: float
        """
        self._write(':SPR{0}:CTL:POLE{1}?'.format(self._module_id, pole))

    def ctle_pole_frequency_set(self, pole, frequency):
        """
        Sets the frequency of the specified pole

        :param pole: - 1
                      - 2
                      - 3
        :type pole: int
        :param frequency: frequency in Hz
        :type frequency: float
        """
        self._write(':SPR{0}:CTL:POLE{1} {2}'.format(self._module_id, pole, frequency))

    def ctle_zero_frequency_get(self, zero):
        """
        Returns the frequency of the specified zero

        :param zero: - 1
                      - 2
        :type zero: int
        :return: frequency in Hz
        :rtype: float
        """
        self._write(':SPR{0}:CTL:ZERO{1}?'.format(self._module_id, zero))

    def ctle_zero_frequency_set(self, zero, frequency):
        """
        Sets the frequency of the specified zero

        :param zero: - 1
                      - 2
        :type zero: int
        :param frequency: frequency in Hz
        :type frequency: float
        """
        if isinstance(zero, int):
            if isinstance(frequency, float):
                if 1 <= zero <= 2:
                    if 10e6 <= frequency <= 1e12:
                        self._write(':SPR{0}:CTL:ZERO{1} {2}'.format(self._module_id, zero, frequency))
                    else:
                        raise ValueError("Valid frequency input range is 10e6 to 1e12")
                else:
                    raise ValueError("Valid zero input range is 1 to 2")
            else:
                raise TypeError("Frequency input must be float")
        else:
            raise TypeError("Zero input must be integer")

    @property
    def tdecq_dc_gain(self):
        """
        ***READ-ONLY***
        Returns if DC Gain is enabled for the specified TDECQ math function

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        return float(self._read('SPR{0}:TEQ:DCGain?'.format(self._module_id)))

    @property
    def tdecq_iterative_optimization(self):
        """
        Turns on Iterative Optimization which allows you to define seed taps for the TDECQ equalizer

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """

        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[(self._read('SPR{0}:TEQ:TAPS:IOPT?'.format(self._module_id)))]

    @tdecq_iterative_optimization.setter
    def tdecq_iterative_optimization(self, value):
        """
        :type value: str
        """
        if self._read('SPR{0}:TEQ:TAPS:AUTo?'.format(self._module_id)) == '0':
            raise SystemError('{0} math channel {1} TDECQ taps is currently not in auto mode. Enable automatic taps '
                              'then try to configure iterative optimzation'.format(self._name, self._module_id))
        output_dict = {'ENABLE': '1', 'DISABLE': '0'}
        self._write('SPR{0}:TEQ:TAPS:IOPT {1}'.format(self._module_id, output_dict[value.upper()]))

    def tdecq_normalize(self):
        """
        ***RUN-ONLY***

        Automatically adjusts the tap values of the TDECQ Equalizer for a maximum equalizer gain of 0 dB (unity).\n
        The relative contributions of the tap values are maintained. Automatic tap configuration must be disabled
        """

        if self._read('SPR{0}:TEQ:TAPS:AUTo?'.format(self._module_id)) == '1':
            raise SystemError('{0} math channel {1} TDECQ taps is currently in auto mode. Define taps manually then try'
                              ' to normalize gain'.format(self._name, self._module_id))
        self._write(':SPR{0}:TEQ:TAPS:NORM'.format(self._module_id))

    @property
    def tdecq_number_of_taps(self):
        """
        Returns the number of taps used in the TDECQ math function

        :value: number of taps
        :type: int
        """
        return int(self._read('SPR{0}:TEQ:TAPS:COUNt?'.format(self._module_id)))

    @tdecq_number_of_taps.setter
    def tdecq_number_of_taps(self, value):
        """
        :type value: int
        """
        if isinstance(value, int):
            if self._read('SPR{0}:TEQ:TAPS:AUTo?'.format(self._module_id)) == '1':

                if self.tdecq_iterative_optimization == 'DISABLE':
                    if self.tdecq_seed_taps_enable == 'ENABLE':
                        max_taps = 9
                    else:
                        max_taps = 64
                    if 1 <= value <= max_taps:
                        self._write('SPR{0}:TEQ:TAPS:COUNt {1}'.format(self._module_id, value))
                    else:
                        raise ValueError("Input Value should be between 1 and %s" % max_taps)
                else:
                    raise ValueError("TDECQ iterative optimization must be disabled in order to control tap count")
            else:
                raise ValueError("Automatic taps must be enabled in order to control taps count")
        else:
            raise TypeError("Input value must be an integer")

    @property
    def tdecq_pnoise_bandwidth(self):
        """
        Sets the bandwidth used when preserving the input waveform's noise on the output waveform.

        :value: bandwidth (float) or 'AUTO' string
        :type: float or str
        """
        if self._read('SPR{0}:TEQ:PNOise:BANDwidth:AUTo?'.format(self._module_id)) == 'ON':
            self.logger.info('{0} math channel {1} TDECQ Phase Noise bandwidth is currently in auto mode'
                             .format(self._name, self._module_id))
        return float(self._read('SPR{0}:TEQ:PNOise:BANDwidth?'.format(self._module_id)))

    @tdecq_pnoise_bandwidth.setter
    def tdecq_pnoise_bandwidth(self, value):
        """
        :type value: float or str
        """
        if isinstance(value, str):
            if value.upper() == 'AUTO':
                self._write('SPR{0}:TEQ:PNOise:BANDwidth:AUTO ON'.format(self._module_id))
            else:
                raise ValueError('Please enter a valid string')
        elif isinstance(value, float):
            if 10e6 <= value <= 1e12:
                self._write('SPR{0}:TEQ:PNOise:BANDwidth:AUTo OFF'.format(self._module_id))
                self._write('SPR{0}:TEQ:PNOise:BANDwidth {1}'.format(self._module_id, value))

            else:
                raise ValueError("Input value must be between 10e6 and 1e12 Hz")
        else:
            raise TypeError("Type must be string or float")

    @property
    def tdecq_precursors(self):
        """
        Defines the number of precursors. Default is 0

        :value: Number of precursors
        :type: int
        """
        if self._read('SPR{0}:TEQ:NPR:AUTO?'.format(self._module_id)) == 'ON':
            self.logger.info('Auto Precursors is currently enabled.')
        return int(self._read('SPR{0}:TEQ:NPRecursors?'.format(self._module_id)))

    @tdecq_precursors.setter
    def tdecq_precursors(self, value):
        """
        :type value: int
        """
        if isinstance(value, int):
            if self._read('SPR{0}:TEQ:TAPS:AUTo?'.format(self._module_id)) == '1':
                if self.tdecq_iterative_optimization == 'DISABLE':
                    if 0 <= value <= int(self.tdecq_number_of_taps)-1:
                        if self._read('SPR{0}:TEQ:NPR:AUTO?'.format(self._module_id)) == '1':
                            self.logger.info('Setting the maximum number of precursors to be used. '
                                             'Disable automatic precursors to define a specific number of precursors')
                            self._write('SPR{0}:TEQ:MNPR {1}'.format(self._module_id, value))
                        else:
                            self.logger.info('Setting the number of precursors to be used.'
                                             'Enable automatic precursors to define a maximum number of precursors')
                            self._write('SPR{0}:TEQ:NPR {1}'.format(self._module_id, value))
                    else:
                        raise ValueError("Input value must be between 0 and %s" % self.tdecq_number_of_taps)
                else:
                    raise ValueError("TDECQ iterative optimization must be disabled in order to control precursors")
            else:
                raise ValueError("Automatic taps must be enabled in order to control taps count")
        else:
            raise TypeError("Type must be string or int")

    @property
    def tdecq_precursors_auto(self):
        """
        Sets automatic configuration of the TDECQ precursors

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[self._read('SPR{0}:TEQ:NPR:AUTO?'.format(self._module_id))]

    @tdecq_precursors_auto.setter
    def tdecq_precursors_auto(self, value):
        """
        :type value: str
        """
        if isinstance(value, str):
            if self._read('SPR{0}:TEQ:TAPS:AUTo?'.format(self._module_id)) == '1':
                if self.tdecq_iterative_optimization == 'DISABLE':
                    output_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
                    if value.upper() in output_dict:
                        self._write('SPR{0}:TEQ:NPR:AUTO {1}'.format(self._module_id, output_dict[value.upper()]))
                    else:
                        raise ValueError('Invalid string input')
                else:
                    raise ValueError("TDECQ iterative optimization must be disabled in order to enable auto precursors")
            else:
                raise ValueError("TDECQ Automatic taps must be enabled in order to enable automatic precursors")
        else:
            raise TypeError('Input type must be string')

    @property
    def tdecq_preset(self):
        """
        Load a preset for the TDECQ (ie. "IEEE 802.3bs Draft 2.2" or "IEEE 802.3bs Draft 3.2")

        :value: present name
        :type: str
        """
        return self._read('SPR{0}:TEQ:PRES?'.format(self._module_id))

    @tdecq_preset.setter
    def tdecq_preset(self, value):
        """
        :type value: str
        """
        if isinstance(value, str):
            if value in self.tdecq_preset_list:
                self._write('SPR{0}:TEQ:PRES "{1}"'.format(self._module_id, value))
            else:
                raise ValueError("Preset does not exist")
        else:
            raise TypeError("Input value must be string")

    @property
    def tdecq_preset_list(self):
        """
        ***READ-ONLY***

        Returns a list of all available presets

        :value: Preset names
        :type: list of strings
        """
        return self._read('SPR{0}:TEQ:PRES:SEL?'.format(self._module_id)).replace('"', '').split(", ")

    def tdecq_recalculate(self):
        """
        ***RUN-ONLY***

        Initiates a re-calculation of the tap values for the TDECQ Equalizer.\n
        Automatic tap configuration must be enabled.
        """
        # TODO: need to figure how to amke this a blocking call *OPC? does not work
        self._write(':SPR{0}:TEQ:TAPS:REC'.format(self._module_id))

    @property
    def tdecq_seed_taps(self):
        """
        When Iterative Optimization is turned on for the TDECQ equalizer allows you to enter seed tap values

        :value: list of seed tap values
        :type: list of floats
        """
        return list(map(float, self._read('SPR{0}:TEQ:TAPS:SEED?'.format(self._module_id)).split(",")))

    @tdecq_seed_taps.setter
    def tdecq_seed_taps(self, value):
        """
        :type value: list of floats
        """
        taps = ''
        for tap in value:
            taps += ',' + str(tap)
        self._write('SPR{0}:TEQ:TAPS:SEED {1}'.format(self._module_id, taps[1:]))

    def tdecq_seed_taps_copy(self):
        """
        ***RUN-ONLY***

        When Iterative Optimization is turned on for the TDECQ equalizer, copies the current automatically calculated
        tap values to use as the seed taps
        """
        self._write('SPR{0}:TEQ:TAPS:SEED:COPY')

    @property
    def tdecq_seed_taps_enable(self):
        """
        When Iterative Optimization is turned on for the TDECQ equalizer, enables the application of the seed taps
        that are defined

        :value: - 'ENABLE'
                - 'DISABLE'
        :type: str
        """
        input_dict = {'1': 'ENABLE', '0': 'DISABLE'}
        return input_dict[(self._read('SPR{0}:TEQ:TAPS:SEED:ENABle?'.format(self._module_id)))]

    @tdecq_seed_taps_enable.setter
    def tdecq_seed_taps_enable(self, value):
        """
        :type value: str
        """
        if self._read('SPR{0}:TEQ:TAPS:AUTo?'.format(self._module_id)) == '1':
            if self.tdecq_iterative_optimization == 'ENABLE':
                output_dict = {'ENABLE': '1', 'DISABLE': '0'}
                self._write('SPR{0}:TEQ:TAPS:SEED:ENABle {1}'.format(self._module_id, output_dict[value.upper()]))
            else:
                raise ValueError("TDECQ iterative optimization must be enabled in order to enable seed taps")
        else:
            raise SystemError('{0} math channel {1} TDECQ taps is currently not in auto mode. Enable automatic taps '
                              'then try to configure seed taps'.format(self._name, self._module_id))

    @property
    def tdecq_taps(self):
        """
        Defines the taps used in the TDECQ math funcition. Increasing the number of taps in your model increases the
        fidelity of the filter's frequency response as compared to an ideal response.

        :value: list of tap values or 'AUTO' string
        :type: list of floats or string
        """
        if self._read('SPR{0}:TEQ:TAPS:AUTo?'.format(self._module_id)) == 'ON':
            self.logger.info('{0} math channel {1} TDECQ taps is currently in auto mode'
                             .format(self._name, self._module_id))
        return list(map(float, self._read('SPR{0}:TEQ:TAPS?'.format(self._module_id)).split(",")))

    @tdecq_taps.setter
    def tdecq_taps(self, value):
        """
        :type value: list of floats or str
        """
        if isinstance(value, str):
            if value.upper() == 'AUTO':
                self._write('SPR{0}:TEQ:TAPS:AUTo ON'.format(self._module_id))
            else:
                raise ValueError('Please enter a valid string')
        else:
            if len(value) == self.tdecq_number_of_taps:
                taps = ''
                for tap in value:
                    taps += ',' + str(tap)
                self._write('SPR{0}:TEQ:TAPS:AUTO OFF'.format(self._module_id))
                self._write('SPR{0}:TEQ:TAPS {1}'.format(self._module_id, taps[1:]))
            else:
                raise ValueError('The length of the taps list is not the same as the number of taps set on the scope')


class Keysight86100XWaveformMemory(BaseEquipmentBlock):
    """
    Keysight 86100X Memory Block
    """
    def __init__(self, module_id=None, module_option=None, channel_number=None, handle=None,
                 pam=None, interface=None, dummy_mode=False, **kwargs):
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
        self._module_option = module_option
        self._channel_number = channel_number
        self._handle = handle
        self._display_memory = _Keysight86100XDisplayMemory(self._handle, interface, dummy_mode)

        self.osc = Keysight86100XOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                         self._display_memory, interface, dummy_mode)
        self.eye = Keysight86100XEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                self._display_memory, interface, dummy_mode)
        self.jitter = Keysight86100XJitterMeasurement(self._module_id, self._channel_number, self._handle,
                                                      self._display_memory, interface, dummy_mode)
        if pam:
            self.pam_eye = Keysight86100XPAMEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                           self._display_memory, interface, dummy_mode)
            self.pam_osc = Keysight86100XPAMOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                                    self._display_memory, interface, dummy_mode)


class Keysight86100XCGSX(BaseEquipmentBlock):
    """
    Keysight 86100X CGSX Block
    """
    def __init__(self, module_id=None, module_option=None, channel_number=None, handle=None,
                 display_handle=None, interface=None, dummy_mode=False, **kwargs):
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
        self._module_option = module_option
        self._channel_number = channel_number
        self._handle = handle
        # This block needs another handle since channel name handle is different when turning
        # the channel on/off (EMEM) and when taking measurements (CGM)
        self._display_handle = display_handle
        self._display_memory = _Keysight86100XDisplayMemory(self._display_handle, interface, dummy_mode)

        self.eye = Keysight86100XEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                self._display_memory, interface, dummy_mode)
