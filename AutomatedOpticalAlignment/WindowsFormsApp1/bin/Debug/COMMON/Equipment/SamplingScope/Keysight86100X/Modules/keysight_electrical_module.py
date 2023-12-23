"""
| $Revision:: 283969                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-26 13:59:37 +0000 (Mon, 26 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------
"""

from CLI.Utilities.custom_structures import CustomList
from CLI.Equipment.SamplingScope.base_sampling_scope import BaseSamplingScopeModule
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import _Keysight86100XDisplayMemory
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XEyeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XJitterMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XEyeMaskTest
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XHistogram
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks  import Keysight86100XOscilloscopeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XPAMEyeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XPAMOscilloscopeMeasurement
from CLI.Utilities.custom_exceptions import NotSupportedError
import os


class Keysight86100XElectricalModule(BaseSamplingScopeModule):
    """
    Keysight86100X Electrical Module
    """
    CAPABILITY = {'software_delay': {'min': -10e-9, 'max': 10e-9},
                  'skew': {'min': -1, 'max': 1}}

    def __init__(self, module_id=None, module_option=None, channel_number=None, handle=None,
                 interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param module_id: module slot index
        :type module_id: int
        :param module_option: available added options for module
        :type module_option: str
        :param channel_number: channel index
        :type channel_number: int or str
        :param handle: channel handle (e.g 'CHAN1A')
        :type handle: str
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
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
        self.histogram = CustomList()
        """:type: list of Keysight86100XHistogram"""

    @property
    def display(self):
        """
        Disable or Enable channel display

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        return self._display_memory.channel_display

    @display.setter
    def display(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        self._display_memory.channel_display = value

    @property
    def offset(self):
        """
        Specify channel offset

        :value: offset between -10ns and 10ns
        :type: float
        :raise ValueError: exception if offset is not between -10ns and 10ns
        """
        return float(self._read(':{}:YOFF?'.format(self._handle)))

    @offset.setter
    def offset(self, value):
        """
        :type value: float
        :raise ValueError: exception if offset is not between -10ns and 10ns
        """
        self._write(':{}:YOFF {}'.format(self._handle, value))

    @property
    def scale(self):
        """
        Specify channel scale

        :value: scale between -10ns and 10ns
        :type: float
        :raise ValueError: exception if scale is not between -10ns and 10ns
        """
        return float(self._read(':{}:YSC?'.format(self._handle)))

    @scale.setter
    def scale(self, value):
        """
        :type value: float
        :raise ValueError: exception if scale is not between -10ns and 10ns
        """
        self._write(':{}:YSC {}'.format(self._handle, value))

    @property
    def software_delay(self):
        """
        Specify channel software delay

        :value: delay between -10ns and 10ns
        :type: float
        :raise ValueError: exception if delay is not between -10ns and 10ns
        """
        return float(self._read(':{}:TDEL?'.format(self._handle)))

    @software_delay.setter
    def software_delay(self, value):
        """
        :type value: float
        :raise ValueError: exception if delay is not between -10ns and 10ns
        """
        if self.CAPABILITY['software_delay']['min'] <= value <= \
                self.CAPABILITY['software_delay']['max']:
            self._write(':{}:TDEL {}'.format(self._handle, value))
        else:
            raise ValueError('Please specify delay is between {} and {}'.format(
                self.CAPABILITY['software_delay']['min'],
                self.CAPABILITY['software_delay']['max']))

    @property
    def signal_type(self):
        """
        Specify signal type

        :value: - 'AUTO'
                - 'NRZ'
                - 'PAM4'
        :type: str
        :raise ValueError: exception if type is not 'AUTO, 'NRZ' or 'PAM4'
        """
        if self._read(":{}:SIGNal:TYPE:AUTO?".format(self._handle)) == '0':
            return self._read(":{}:SIGNal:TYPE?".format(self._handle),
                              dummy_data='NRZ')
        else:
            return 'AUTO'

    @signal_type.setter
    def signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if type is not 'AUTO, 'NRZ' or 'PAM4'
        """
        value = value.upper()
        if value not in ['AUTO', 'NRZ', 'PAM4']:
            raise ValueError("Please specify either 'AUTO', 'NRZ' or 'PAM4'")
        elif value == 'AUTO':
            self._write(':{}:SIGNal:TYPE:{} ON'.format(self._handle, value),
                        dummy_data='AUTO')
        else:
            self._write(':{}:SIGNal:TYPE:AUTO OFF'.format(self._handle, value))
            self._write(':{}:SIGNal:TYPE {}'.format(self._handle, value))

    def save_cgsx(self, filename):
        """
        Save a CGSX memory file to the PC running CLI.

        :param filename: path and file e. Path is relative to PC running CLI.
        :type filename: str
        :raise NotSupportedError: exception if scope is not in 'EYE' mode
        """
        if self._display_memory.scope_mode == 'EYE':

            orig = self._interface.visa_handle.read_termination
            self._interface.visa_handle.read_termination = None

            # Dummy file saved on scope before transferring it to PC
            scope_path = 'D:\\User Files\\Screen Images\\test_cgsx.cgsx'
            try:
                self._write(':{}:DISPlay ON'.format(self._handle))

                self._write(':DISK:EYE:FNAMe  "{}"'.format(scope_path))
                self._write(':DISK:EYE:SAVE:SOURce {}'.format(self._handle))
                self._write(':DISK:EYE:SAVE')
                self._write(':DISK:EYE:FNAMe:AUPDate')
                self._read('*OPC?')
            except Exception as e:
                err_msg = 'EXCEPTION: ' + str(e.args)
                self.logger.warning(err_msg)
                self._write("*CLS")
                self._write(':DISK:EYE:FNAMe  "{}"'.format(scope_path))
                self._write(':DISK:EYE:SAVE:SOURce {}'.format(self._handle))
                self._write(':DISK:EYE:SAVE')
                self._write(':DISK:EYE:FNAMe:AUPDate')
                self._read('*OPC?')

            data = self._interface.visa_handle.query_binary_values(':DISK:BFILE? "' + scope_path + '"', datatype='s')

            if not filename.endswith('.cgsx'):
                filename += '.cgsx'

            fh = open(filename, 'wb')
            fh.write(data[0])
            fh.close()
            self.logger.info("Image saved to {}".format(os.path.realpath(fh.name)))

            self._interface.visa_handle.read_termination = orig
        else:
            raise NotSupportedError("Saving a CGSX file requires scope to be in 'EYE' mode.")

    def save_wf(self, filename, holes_tolerance=None):
        """
        Save a waveform memory file to the PC running CLI.

        :param filename: path and file e. Path is relative to PC running CLI.
        :type filename: str
        :param holes_tolerance: number of holes that need to be captured in the waveform before saving
        :type holes_tolerance: int
        """

        orig = self._interface.visa_handle.read_termination
        self._interface.visa_handle.read_termination = None

        # Dummy file saved on scope before transferring it to PC
        scope_path = 'D:\\User Files\\Screen Images\\test_wfmx.wfmx'
        if isinstance(holes_tolerance, int):
            while int(self._read(':WAVeform:XYFormat:POINts:HOLes?')) > holes_tolerance:
                self.sleep(0.5)
        try:
            self._write(':DISK:WAVeform:FNAMe  "{}"'.format(scope_path))
            self._write(':{}:DISPlay ON'.format(self._handle))
            self._write(':DISK:WAVeform:SAVE:SOURce {}'.format(self._handle))
            self._write(':DISK:WAVeform:SAVE')
            self._write(':DISK:WAVeform:FNAMe:AUPDate')
            self._read('*OPC?')
        except Exception as e:
            err_msg = 'EXCEPTION: ' + str(e.args)
            self.logger.warning(err_msg)
            self._write("*CLS")
            self._write(':DISK:WAVeform:FNAMe  "{}"'.format(scope_path))
            self._write(':{}:DISPlay ON'.format(self._handle))
            self._write(':DISK:WAVeform:SAVE:SOURce {}'.format(self._handle))
            self._write(':DISK:WAVeform:SAVE')
            self._write(':DISK:WAVeform:FNAMe:AUPDate')
            self._read('*OPC?')

        data = self._interface.visa_handle.query_binary_values(':DISK:BFILE? "' + scope_path + '"', datatype='s')

        if not filename.endswith('.wfmx'):
            filename += '.wfmx'

        fh = open(filename, 'wb')
        fh.write(data[0])
        fh.close()
        self.logger.info("Image saved to {}".format(os.path.realpath(fh.name)))

        self._interface.visa_handle.read_termination = orig


class Keysight86100XSingleElectricalModule(Keysight86100XElectricalModule):
    """
    Keysight 86100X common Single Channel
    """
    CAPABILITY = {'software_delay': {'min': -10e-9, 'max': 10e-9},
                  'skew': {'min': -1, 'max': 1},
                  'bandwidth': [50e9, 70e9]}

    def __init__(self, module_id=None, module_option=None, channel_number=None, handle=None,
                 pam=None, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param module_id: module slot index
        :type module_id: int
        :param module_option: available added options for module
        :type module_option: str
        :param channel_number: channel index
        :type channel_number: int or str
        :param handle: channel handle (e.g 'CHAN1A')
        :type handle: str
        :param pam: flag to specify pam license available for this module
        :type pam: bool
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, module_option=module_option,
                         channel_number=channel_number, handle=handle,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.osc = Keysight86100XOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                         self._display_memory, interface, dummy_mode)
        self.eye = Keysight86100XEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                self._display_memory, interface, dummy_mode)
        self.jitter = Keysight86100XJitterMeasurement(self._module_id, self._channel_number, self._handle,
                                                      self._display_memory, interface, dummy_mode)
        self.mask_test = Keysight86100XEyeMaskTest(self._module_id, self._channel_number, self._handle,
                                                   self._display_memory, interface, dummy_mode)
        for i in range(1, 5, 1):
            self.histogram.append(Keysight86100XHistogram(i, self._module_id, self._channel_number, self._handle,
                                                          self._display_memory, interface, dummy_mode))
        if pam:
            self.pam_eye = Keysight86100XPAMEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                           self._display_memory, interface, dummy_mode)
            self.pam_osc = Keysight86100XPAMOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                                    self._display_memory, interface, dummy_mode)

    @property
    def attenuation(self):
        """
        Disable or Enable attenuation

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":CHAN{}{}:ATTenuator:STATe?".format(self._module_id,
                                                                           self._channel_number))]

    @attenuation.setter
    def attenuation(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':CHAN{}{}:ATTenuator:STATe {}'.format(self._module_id,
                                                               self._channel_number,
                                                               input_dict[value]))

    @property
    def bandwidth(self):
        """
        Specify channel bandwidth in GHz

        :value: - 50e9
                - 70e9
        :type: float
        :raise ValueError: exception if bandwidth is not '50.0E+9' or '70.0E+9'
        """
        return float(self._read(":CHAN{}{}:BANDwidth:FREQuency?".format(
            self._module_id, self._channel_number)))

    @bandwidth.setter
    def bandwidth(self, value):
        """
        :type value: float
        :raise ValueError: exception if bandwidth is not '50.0E+9' or '70.0E+9'
        """
        if value not in self.CAPABILITY['bandwidth']:
            raise ValueError('Please specify either 50e9 or 70e9')
        else:
            self._write(':CHAN{}{}:BANDwidth:FREQuency {}'.format(self._module_id,
                                                                  self._channel_number,
                                                                  value))

    @property
    def skew(self):
        """
        Specify channel hardware skew

        :value: skew between 0s and 1s
        :type: float
        :raise ValueError: exception if skew is not between -1s and 1s
        """
        return float(self._read(':CHAN{}{}:SKEW?'.format(self._module_id, self._channel_number)))

    @skew.setter
    def skew(self, value):
        """
        :type value: float
        :raise ValueError: exception if skew is not between -1s and 1s
        """
        if self.CAPABILITY['skew']['min'] <= value <= self.CAPABILITY['skew']['max']:
            self._write(':CHAN{}{}:SKEW {}'.format(self._module_id,
                                                   self._channel_number,
                                                   value))
        else:
            raise ValueError('Please specify skew is between {}s and {}s'.format(
                self.CAPABILITY['skew']['min'], self.CAPABILITY['skew']['max']))

    def set_attenuation(self, level=0, unit='DB'):
        """
        Set the channel attenuation

        :param level: attenuation level
        :type level: float
        :param unit: attenuation unit: 'DB' or 'RATIO'
        :type unit: str
        :raise ValueError: exception if unit is not 'DB' or 'RATIO'
        """
        unit = unit.upper()
        if unit == 'DB':
            self._write(':CHAN{}{}:ATTenuator:STATe ON'.format(self._module_id,
                                                               self._channel_number))
            self._write(':CHAN{}{}:ATTenuator:DECibels {}'.format(self._module_id,
                                                                  self._channel_number, level))
        elif unit == 'RATIO':
            self._write(':CHAN{}{}:ATTenuator:STATe ON'.format(self._module_id,
                                                               self._channel_number))
            self._write(':CHAN{}{}:ATTenuator:RATio {}'.format(self._module_id,
                                                               self._channel_number, level))
        else:
            raise ValueError("Incorrect Attenunation unit, only db and ratio are accepted")


class Keysight86100XDiffElectricalModule(Keysight86100XElectricalModule):
    """
    Keysight 86118A Module
    """
    CAPABILITY = {'software_delay': {'min': -10e-9, 'max': 10e-9},
                  'skew': {'min': -1, 'max': 1}}

    def __init__(self, module_id=None, module_option=None, channel_number=None, handle=None,
                 pam=None, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param module_id: module slot index
        :type module_id: int
        :param module_option: available added options for module
        :type module_option: str
        :param channel_number: channel index
        :type channel_number: int or str
        :param handle: channel handle (e.g 'CHAN1A')
        :type handle: str
        :param pam: flag to specify pam license available for this module
        :type pam: bool
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, module_option=module_option,
                         channel_number=channel_number, handle=handle,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.osc = Keysight86100XOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                         self._display_memory, interface, dummy_mode)
        self.eye = Keysight86100XEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                self._display_memory, interface, dummy_mode)
        self.jitter = Keysight86100XJitterMeasurement(self._module_id, self._channel_number, self._handle,
                                                      self._display_memory, interface, dummy_mode)
        self.mask_test = Keysight86100XEyeMaskTest(self._module_id, self._channel_number, self._handle,
                                                   self._display_memory, interface, dummy_mode)
        for i in range(1, 5, 1):
            self.histogram.append(Keysight86100XHistogram(i, self._module_id, self._channel_number, self._handle,
                                                          self._display_memory, interface, dummy_mode))
        if pam:
            self.pam_eye = Keysight86100XPAMEyeMeasurement(self._module_id, self._channel_number, self._handle,
                                                           self._display_memory, interface, dummy_mode)
            self.pam_osc = Keysight86100XPAMOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                                    self._display_memory, interface, dummy_mode)

    @property
    def mode(self):
        """
        Specify signal mode

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
        :type: str
        :raise ValueError: exception if input is not "SINGLE" or "DIFFERENTIAL"
        """
        output_dict = {'0': 'SINGLE', 'OFF': 'SINGLE', '1': 'DIFFERENTIAL', 'ON': 'DIFFERENTIAL',
                       'DUMMY_DATA': 'SINGLE'}
        return output_dict[self._read(":{}:DMODe?".format(self._handle))]

    @mode.setter
    def mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not "SINGLE" or "DIFFERENTIAL"
        """
        value = value.upper()
        input_dict = {'DIFFERENTIAL': 'ON', 'SINGLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "SINGLE" or "DIFFERENTIAL"')
        else:
            self._write(':{}:DMODe {}'.format(self._handle, input_dict[value]))

    @property
    def scale_tracking(self):  # TODO: Add Polling
        """
        Disable or Enable scale tracking

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":{}:DSTR?".format(self._handle))]

    @scale_tracking.setter
    def scale_tracking(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':{}:DSTR {}'.format(self._handle, input_dict[value]))

    def deskew(self):
        """
        Auto differential deskew
        """
        self._write(":{}:DESKew".format(self._handle))
