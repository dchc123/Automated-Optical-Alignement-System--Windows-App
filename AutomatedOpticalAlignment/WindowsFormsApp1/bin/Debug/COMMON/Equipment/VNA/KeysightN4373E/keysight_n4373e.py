"""
| $Revision:: 280392                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-31 01:14:44 +0100 (Tue, 31 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------


Before using this driver, the "SCPI server" needs to be running on the VNA.
Please make sure to test the connection before using driver.

For the top level API: See :py:class:`.KeysightN4373E`
::

    >>> from CLI.Equipment.VNA.KeysightN4373E.keysight_n4373e import KeysightN4373E
    >>> LCA = KeysightN4373E('TCPIP0::192.168.1.204::5026::SOCKET')
    >>> LCA.connect()
    >>> LCA.optical_power = 3
    >>> LCA.modulator_bias_mode('EVER')
    >>> LCA.wavelength = 1310
    >>> LCA.source = 'INTERNAL'
    >>> LCA.wavelength
    1310
    >>> LCA.measurement_mode('SING')
    >>> LCA.init_measurement('OE')
    >>> LCA.trigger()
"""
from CLI.Equipment.Base.base_equipment import BaseEquipment
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_exceptions import NotSupportedError


class KeysightN4373E(BaseEquipment):
    """
    Keysight N4373E LCA driver
    """
    CAPABILITY = {'optical_power': {'min': -1, 'max': 5}}

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

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        if isinstance(self._interface, CLIVISA):
            self._interface.visa_handle.read_termination = '\n'
        self._interface.write('*CLS')

        self._interface.stb_polling_supported = False

    def _opc_polling_lca(self):
        """
        Implemented since the LCA is not 100% compliant to SCPI standard
        """
        if not self.dummy_mode:
            opc = '0'
            while opc != '1':
                self.sleep(0.05)
                opc = self._read('*OPC?')

    @property
    def forward_rf_power(self):
        """
        :value: forward RF power
        :type: float
        """
        return float(self._read(":RF:POWer:FWD?"))

    @forward_rf_power.setter
    def forward_rf_power(self, value):
        """
        :type value: float
        """
        self._write(":RF:POWer:FWD %s" % value)

    @property
    def laser_output(self):
        """
        Enable state of the laser output.

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'LaserOff': 'DISABLE', 'LaserOn': 'ENABLE', '0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read(':SOURce:STATe?', dummy_data='LaserOff')]

    @laser_output.setter
    def laser_output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":SOURce:STATe %s" % input_dict[value])

    @property
    def measurement_mode(self):
        """
        This parameter is only applied when 'init_measurement' is sent.

        :value: - 'SING' - Single ended
                - 'DIFF' - Differential
        :type: str
        :raise ValueError: value error if input is not 'SING'/'DIFF'
        """
        output_dict = {'SingleEnded': 'SING', 'Differential': 'DIFF'}
        return output_dict[self._read(":PARameter:MEASurement:MODE?", dummy_data="SING")]

    @measurement_mode.setter
    def measurement_mode(self, value):
        """
        :type value: str
        :raise ValueError: value error if input is not 'SING'/'DIFF'
        """
        input_list = ['SING', 'DIFF']
        value = value.upper()
        if value not in input_list:
            raise ValueError("Please specify either 'SING' or 'DIFF'")
        else:
            self._write(":PARameter:MEASurement:MODE %s" % value)

    @property
    def modulator_bias_mode(self):
        """
        How often a modulator bias voltage optimization will be performed.
        This parameter is only applied when 'init_measurement' is sent.

        :value: - 'CONT' - Continuous
                - 'EVER' - Every Sweep
                - 'ONCE' - Once
        :type: str
        """
        output_dict = {'EverySweep': 'EVER', 'Continuous': 'CONT', 'Once': 'ONCE'}
        return output_dict[self._read(":PARameter:MODUlator:BIAS:MODE?", dummy_data="EverySweep")]

    @modulator_bias_mode.setter
    def modulator_bias_mode(self, value):
        """
        :type value: str
        :raise ValueError: value error if input is not 'CONT', 'EVER' or 'ONCE'
        """
        input_list = ['CONT', 'EVER', 'ONCE']
        value = value.upper()
        if value not in input_list:
            raise ValueError("Please specify either 'CONT', 'EVER' or 'ONCE'")
        else:
            self._write(":PARameter:MODUlator:BIAS:MODE %s" % value)

    @property
    def optical_power(self):
        """
        This parameter is only applied when 'init_measurement' is sent.

        :value: Optical power output (dBm)
        :type: float
        """
        return float(self._read(":PARameter:OPTical:OUTput:POWer?"))

    @optical_power.setter
    def optical_power(self, value):
        """
        :type value: float
        :raise ValueError: Exception if range value is invalid
        """
        range_min = self.CAPABILITY['optical_power']['min']
        range_max = self.CAPABILITY['optical_power']['max']

        if range_min <= value <= range_max:
            self._write(":PARameter:OPTical:OUTput:POWer %s" % value)
        else:
            raise ValueError("%s is an invalid optical power entry. See valid range.(min:%s|max:%s)"
                             % (value, range_min, range_max))

    def reset(self):
        """
        Perform equipment reset, to put device in known preset state
        """
        raise NotSupportedError("%s does not support reset command" % self.name)

    @property
    def source(self):
        """
        Changes the source to internal or external.
        This parameter is only applied when 'init_measurement' is sent.

        :value: - 'INTERNAL'
                - 'EXTERNAL'
        :type: str
        :raise ValueError: exception if input is not INTERNAL/EXTERNAL
        """
        output_dict = {'0': 'INTERNAL', '1': 'EXTERNAL'}
        return output_dict[self._read(':PARameter:SOURce:EXTernal?', dummy_data='0')]

    @source.setter
    def source(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not INTERNAL/EXTERNAL
        """
        input_dict = {'EXTERNAL': '1', 'INTERNAL': '0'}
        value = value.upper()
        if value not in input_dict.keys():
            raise ValueError('Please specify either "INTERNAL" or "EXTERNAL"')
        else:
            self._write(":PARameter:SOURce:EXTernal %s" % input_dict[value])

    @property
    def wavelength(self):
        """
        This parameter is only applied when 'init_measurement' is sent.

        :value: wavelength of optical source (nm)
        :type: int
        :raise ValueError: Exception if source is set to external
        """
        output_dict = {'1550': 1550, '1310': 1310}
        wav = self._read(":PARameter:WAVelength?", dummy_data='1310')
        if wav == '0':          # Temporary fix to prevent errors, wavelength in remote operation defaults to 0
            self.wavelength = 1310
            return output_dict[self._read(":PARameter:WAVelength?", dummy_data='1310')]
        else:
            return output_dict[wav]

    @wavelength.setter
    def wavelength(self, value):
        """
        :type value: int
        :raise ValueError: Exception if source is set to external
        """
        if self.source == 'EXTERNAL':
            raise ValueError("Cannot set wavelength when source is set to EXTERNAL")
        else:
            input_list = [1310, 1550]
            if value not in input_list:
                raise ValueError("Please specify either 1310 or 1550")
            else:
                self._write(":PARameter:WAVelength %s" % value)

    def abort_measurement(self):
        """
        Aborts a measurement in progress
        """
        self._write(":MEAS:ABOR")

    def init_measurement(self, meas_type, cal_file=None, blocking=True):
        """
        Initiates a measurement in the specified type. Following this command, a trigger is needed.
        If a calibration file is being passed, it will be used and loaded.

        :param meas_type:   - 'EE' - Electrical to Electrical measurement
                            - 'EO' - Electrical to Optical measurement
                            - 'OE' - Optical to Electrical measurement
                            - 'OO' - Optical to Optical measurement
        :type meas_type: str
        :param cal_file: path and filename of calibration file
        :type cal_file: str
        :param blocking: blocking call
        :type blocking: bool
        :raise ValueError: value error if input is not 'EE', 'EO', 'OE' or 'OO'
        """
        input_list = ['EE', 'EO', 'OE', 'OO']
        meas_type = meas_type.upper()

        if meas_type not in input_list:
            raise ValueError('Please select a measurement type from this list %s' % input_list)
        else:
            temp = self.wavelength  # Temporary fix to prevent errors, wavelength in remote operation defaults to 0
            if cal_file is None:
                self._write(":MEASurement:INITialize:%s" % meas_type)
            else:
                self._write(":LOAD:%s:CAL:NAME '%s'" % (meas_type, cal_file))

        if blocking:
            self._opc_polling_lca()

    def trigger(self, mode='SINGLE', blocking=True):
        """
        LCA triggers a sweep on the VNA. Sweep takes variable amount of time to complete. Once
        completed, you can make measurements on the available traces.

        :param mode: - 'SINGLE'
                     - 'CONTINUOUS'
        :type mode: str
        :param blocking: blocking call ('SINGLE' mode only)
        :type blocking: bool
        :raise ValueError: value error if input is not 'SINGLE'/'CONTINUOUS'
        """
        mode = mode.upper()
        if mode == 'SINGLE':
            self._write(":MEAS:STAR SINGle")
            if blocking:
                self._opc_polling_lca()
        elif mode == 'CONTINUOUS':
            self._write(":MEAS:STAR CONT")
        else:
            raise ValueError("Please specify either 'SINGLE' or 'CONTINUOUS'")







