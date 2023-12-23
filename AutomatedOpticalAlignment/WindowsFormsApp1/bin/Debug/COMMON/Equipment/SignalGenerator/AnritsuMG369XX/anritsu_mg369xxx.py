"""
| $Revision:: 283841                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-21 18:27:35 +0000 (Wed, 21 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Equipment.SignalGenerator.base_signal_generator import BaseSignalGenerator


class AnritsuMG369XXX(BaseSignalGenerator):
    """
    Anritsu MG369XXX Signal Generator
    """
    CAPABILITY = {'amplitude': {'min': None, 'max': None},
                  'frequency': {'min': None, 'max': None}}

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
        self._frequency = None
        self._amplitude = None
        self._output = None

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        super()._configure_interface()
        self._interface.stb_polling_supported = False
        # TODO: Investigate way to do error checking
        self._interface.error_check_supported = False

    @property
    def amplitude(self):
        """
        Signal Amplitude
        :value: amplitude in dBm
        :type: float
        """
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        """
        if self.CAPABILITY['amplitude']['min'] <= value <= self.CAPABILITY['amplitude']['max']:
            self._amplitude = value
            if not self.dummy_mode:
                self._interface.write("L0 {} DM".format(int(value)))
        else:
            raise ValueError('Please specify an amplitude between {} and {}'.format(
                self.CAPABILITY['amplitude']['min'], self.CAPABILITY['amplitude']['max']))

    @property
    def frequency(self):
        """
        Signal Frequency

        :value: frequency in Hz
        :type: int
        """
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        """
        :type value: int
        """
        if self.CAPABILITY['frequency']['min'] <= value <= self.CAPABILITY['frequency']['max']:
            self._frequency = value
            if not self.dummy_mode:
                self._interface.write("CF1 {} HZ".format(int(value)))
        else:
            raise ValueError('Please specify a frequency between {} and {}'.format(
                self.CAPABILITY['frequency']['min'], self.CAPABILITY['frequency']['max']))

    @property
    def output(self):
        """
        Disable or Enable signal generator output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        return self._output

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'ENABLE': 'RF1', 'DISABLE': 'RF0'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._output = value
            if not self.dummy_mode:
                self._interface.write('{}'.format(input_dict[value]))


