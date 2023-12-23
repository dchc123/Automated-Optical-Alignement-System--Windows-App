"""
| $Revision:: 279036                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-10 17:01:00 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Equipment.SignalGenerator.base_signal_generator import BaseSignalGenerator


class AgilentE44XXX(BaseSignalGenerator):
    """
    Agilent E442XX Signal Generator
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

    @property
    def amplitude(self):
        """
        Signal Amplitude.

        :value: amplitude in dBm
        :type: float
        :raise ValueError: exception if input is not between -135dBm and 20dBm
        """
        return float(self._read(":POW:LEV:IMM:AMPL?"))

    @amplitude.setter
    def amplitude(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is not between -135dBm and 20dBm
        """
        if self.CAPABILITY['amplitude']['min'] <= value <= self.CAPABILITY['amplitude']['max']:
            self._write(":POW:LEV:IMM:AMPL %s" % value)
        else:
            raise ValueError('Please specify an amplitude between {} and {}'.format(
                self.CAPABILITY['amplitude']['min'], self.CAPABILITY['amplitude']['max']))

    @property
    def frequency(self):
        """
        Signal Frequency

        :value: frequency in Hz
        :type: float
        :raise ValueError: exception if input is not between 100KHz and 4GHz
        """
        freq = float(self._read(":FREQ:FIX?"))
        if freq is None:
            raise ValueError("Frequency is not set")
        else:
            return freq

    @frequency.setter
    def frequency(self, value):
        """
        :type value: float
        :raise ValueError: exception if input is not between 100KHz and 4GHz
        """
        if self.CAPABILITY['frequency']['min'] <= value <= self.CAPABILITY['frequency']['max']:
            self._write(":FREQ:FIX %s" % value)
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
        output_dict = {
            'ON': 'ENABLE', '1': 'ENABLE',
            'OFF': 'DISABLE', '0': 'DISABLE'
        }
        return output_dict[self._read(":OUTP:STAT?", dummy_data='OFF')]

    @output.setter
    def output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError("Please specify either 'ENABLE' or 'DISABLE'")
        else:
            self._write(":OUTP:STAT %s" % input_dict[value])






