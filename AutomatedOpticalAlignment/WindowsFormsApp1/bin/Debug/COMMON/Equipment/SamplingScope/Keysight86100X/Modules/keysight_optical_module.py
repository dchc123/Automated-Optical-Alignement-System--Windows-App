"""
| $Revision:: 283782                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-20 16:46:38 +0000 (Tue, 20 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------
"""

from CLI.Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module import Keysight86100XElectricalModule
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XOpticalEyeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XJitterMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XEyeMaskTest
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XHistogram
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks  import Keysight86100XOpticalOscilloscopeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XPAMEyeMeasurement
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x_blocks import Keysight86100XPAMOscilloscopeMeasurement
from CLI.Utilities.custom_exceptions import NotSupportedError
from decimal import Decimal


class Keysight86100XOpticalModule(Keysight86100XElectricalModule):
    """
    Keysight 86105D Module
    """
    CAPABILITY = {'software_delay': {'min': -10e-9, 'max': 10e-9},
                  'wavelength': [850, 1310, 1550]}

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
        super().__init__(module_id=module_id, module_option=module_option,
                         channel_number=channel_number, handle=handle,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def filter_state(self):
        """
        Disable or Enable optical filter

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE', 'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(":CHAN{}{}:FILTer?".format(self._module_id, self._channel_number))]

    @filter_state.setter
    def filter_state(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':CHAN{}{}:FILTer {}'.format(self._module_id, self._channel_number, input_dict[value]))

    @property
    def filter_bandwidth(self):
        """
        Specify optical channel filter bandwidth in Hz

        :value: bandwidth
        :type: float
        :raise ValueError: exception if bandwidth is not a valid input
        """
        if self.sirc_filter_state == 'ENABLE':
            return float(self._read(':CHAN{}{}:SIRC:FBANDwidth?'.format(self._module_id, self._channel_number)))
        else:
            return float(self._read(":CHAN{}{}:FSELect:BANDwidth?".format(self._module_id, self._channel_number)))

    @filter_bandwidth.setter
    def filter_bandwidth(self, value):
        """
        :type value: float
        :raise ValueError: exception if bandwidth is not a valid input
        """
        if self.sirc_filter_state == 'ENABLE':
            self._write(':CHAN{}{}:SIRC:FBANDwidth {}'.format(self._module_id, self._channel_number, value))
        else:
            input_list = self._read(':CHAN{}{}:FSEL:BAND:VSET?'.format(self._module_id, self._channel_number)).split(',')
            input_list = [float(x.strip('"')) for x in input_list]
            if value not in input_list:
                raise ValueError("Please specify {}".format(input_list))
            else:
                self._write(':CHAN{}{}:FSELect:BANDwidth {}'.format(self._module_id, self._channel_number, value))

    @property
    def filter_rate(self):
        """
        Specify optical channel filter rate in Baud

        :value: rate in baud
        :type: float
        :raise ValueError: exception if rate is not a valid input
        """
        if self.sirc_filter_state == 'ENABLE':
            return float(self._read(':CHAN{}{}:SIRC:FRATe?'.format(self._module_id, self._channel_number)))
        else:
            return float(self._read(":CHAN{}{}:FSELect:RATe?".format(self._module_id, self._channel_number)))

    @filter_rate.setter
    def filter_rate(self, value):
        """
        :type value: float
        :raise ValueError: exception if rate is not a valid input
        """
        if self.sirc_filter_state == 'ENABLE':
            self._write(':CHAN{}{}:SIRC:FRATe {}'.format(self._module_id, self._channel_number, value))
        else:
            input_list = self._read(':CHAN{}{}:FSEL:RAT:VSET?'.format(self._module_id, self._channel_number)).split(',')
            input_list = [float(x.strip('"')) for x in input_list]
            if value not in input_list:
                raise ValueError("Please specify {}".format(input_list))
            else:
                self._write(':CHAN{}{}:FSELect:RAT {}'.format(self._module_id, self._channel_number, value))

    @property
    def mode(self):
        """
        Specify signal mode

        :value: - 'DIFFERENTIAL'
                - 'SINGLE'
        :type: str
        :raise ValueError: exception if input is not "SINGLE" or "DIFFERENTIAL"
        """
        raise NotSupportedError('Optical channel does not support differential mode')

    @mode.setter
    def mode(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not "SINGLE" or "DIFFERENTIAL"
        """
        raise NotSupportedError('Optical channel does not support differential mode')

    @property
    def sirc_filter_state(self):
        """
        Disable or Enable SIRC filter

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE', 'DUMMY_DATA': 'DISABLE'}
        # To catch if option is not present.
        try:
            return output_dict[self._read(":CHAN{}{}:SIRC?".format(self._module_id, self._channel_number))]
        except:
            return 'DISABLE'

    @sirc_filter_state.setter
    def sirc_filter_state(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(':CHAN{}{}:SIRC {}'.format(self._module_id, self._channel_number, input_dict[value]))

    @property
    def wavelength(self):
        """
        Specify channel wavelength in meter

        :value: wavelength in nm
        :type: int
        """
        return float(self._read(":CHAN{}{}:WAVelength:VALue?".format(
            self._module_id, self._channel_number)))*1e9

    @wavelength.setter
    def wavelength(self, value):
        """
        :type value: int
        """
        if value in self.CAPABILITY['wavelength']:
            self._write(':CHAN{}{}:WAVelength:VALue {:.2E}'.format(
                self._module_id, self._channel_number, Decimal(value*1e-9)))
        else:
            raise ValueError('Please specify one of the following values {}'.format(
                self.CAPABILITY['wavelength']))


class Keysight86100XSingleOpticalModule(Keysight86100XOpticalModule):
    """
    Keysight 86118A Single Channel
    """
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
        self.osc = Keysight86100XOpticalOscilloscopeMeasurement(self._module_id, self._channel_number, self._handle,
                                                                self._display_memory, interface, dummy_mode)
        self.eye = Keysight86100XOpticalEyeMeasurement(self._module_id, self._channel_number, self._handle,
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

