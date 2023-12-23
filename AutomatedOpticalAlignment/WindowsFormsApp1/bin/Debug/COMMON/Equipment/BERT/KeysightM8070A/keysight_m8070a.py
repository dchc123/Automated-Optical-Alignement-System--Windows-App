"""
| $Revision:: 283010                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-23 14:50:04 +0100 (Tue, 23 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

The Keysight M8070 has multiple configurations depending on the modules connected,
therefore it is dynamically configured upon connection. The following modules
are supported:

+---------------------+------------+------------------+--------------+
| ED                  | Jitter     | PPG              | Synthesizer  |
+=====================+============+==================+==============+
| MU182040A (Demuxed) | MU181500B  | MU182020A (Muxed)| MU181000A    |
+---------------------+------------+------------------+--------------+
| MU183040A           |            | MU183020A        |              |
+---------------------+------------+------------------+--------------+
| MU183040B           |            |                  |              |
+---------------------+------------+------------------+--------------+

For the top level API: See :py:class:`Equipment.BERT.KeysightM8070A.keysight_m8070a.KeysightM8070A`
::

    >>> from CLI.Equipment.BERT.KeysightM8070A.keysight_m8070a import KeysightM8070A
    >>> bert = KeysightM8070A('GPIB1::23::INSTR')
    >>> bert.connect()
    >>> bert.clock_frequency
    0
    >>> bert.clock_frequency = 100000000
    >>> bert.clock_frequency
    100000000
    >>> bert.global_output = 'ENABLE'

For the Error Detector API: See :py:mod:`Equipment.BERT.KeysightM8070A.Modules.keysight_m80xxx_ed`

For the Pattern Generator API: See :py:mod:`Equipment.BERT.KeysightM8070A.Modules.keysight_m80xxx_ppg`

For the Jitter Module API: See :py:mod:`Equipment.BERT.KeysightM8070A.Modules.keysight_m80xxx_jitter`
"""
import re
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Equipment.BERT.base_bert import BaseBERT
from CLI.Utilities.custom_structures import CustomList
from CLI.Equipment.BERT.KeysightM8070A.Modules.keysight_m8045a import KeysightM8045A
from CLI.Equipment.BERT.KeysightM8070A.Modules.keysight_m8045a_jitter import KeysightM8045AJitter
from CLI.Equipment.BERT.KeysightM8070A.Modules.keysight_m8046a import KeysightM8046A
from CLI.Equipment.BERT.KeysightM8070A.Modules.keysight_m80xxx_ppg import KeysightM80XXXPPG
from CLI.Equipment.BERT.KeysightM8070A.Modules.keysight_m80xxx_jitter import KeysightM80XXXJitter
from CLI.Equipment.BERT.KeysightM8070A.Modules.keysight_m80xxx_ed import KeysightM80XXXED


class KeysightM8070A(BaseBERT):
    """
    Driver for KeysightM8070A Bert
    """
    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        AnritsuMP1800 initialization

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: (default: False) specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.ppg = CustomList()
        """:type: list of KeysightM80XXXPPG"""
        self.ed = CustomList()
        """:type: list of KeysightM80XXXED"""
        self.jitter = CustomList()
        """:type: list of KeysightM80XXXJitter"""
        self.jitter_clk = KeysightM80XXXJitter(module_id='clk',
                                               channel_number='clk',
                                               interface=self._interface,
                                               dummy_mode=self.dummy_mode)

    @property
    def clock_frequency(self):
        """
        BERT clock frequency. This is the preferred property for setting a clock
        frequency. Even if the actual commands are sent to a PPG or jitter module, they'll be
        masked by this generic method.

        :value: desired clock frequency in Hz
        :type: int
        :raise ValueError: exception if frequency not between 100MHz and 12500MHz
        """
        return self.ppg[1].frequency

    @clock_frequency.setter
    def clock_frequency(self, value):
        """
        :type value: int
        :raise ValueError: exception if frequency not between 100MHz and 12500MHz
        """
        self.ppg[1].frequency = value

    @property
    def global_ed_signal_type(self):
        """
        Signal type

        :value: - 'NRZ'
                - 'PAM4'
        :type: str
        :raise ValueError: exception if type is not NRZ or PAM4
        """
        return self.ed[1].signal_type

    @global_ed_signal_type.setter
    def global_ed_signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if type is not NRZ or PAM4
        """
        value = value.upper()
        if value not in ['NRZ', 'PAM4']:
            raise ValueError('Please specify type either as "NRZ" or "PAM4"')

        scpi_string = ''
        for ed in self.ed:
            scpi_string += ":DATA:LINecoding 'M{}.DataIn', {};".format(ed._module_id, value)
        self._write(scpi_string)

    @property
    def global_ppg_signal_type(self):
        """
        Signal type

        :value: - 'NRZ'
                - 'PAM4'
        :type: str
        :raise ValueError: exception if type is not NRZ or PAM4
        """
        return self.ppg[1].signal_type

    @global_ppg_signal_type.setter
    def global_ppg_signal_type(self, value):
        """
        :type value: str
        :raise ValueError: exception if type is not NRZ or PAM4
        """
        value = value.upper()
        if value not in ['NRZ', 'PAM4']:
            raise ValueError('Please specify type either as "NRZ" or "PAM4"')

        scpi_string = ''
        for ppg in self.ppg:
            scpi_string += ":DATA:LINecoding 'M{m}.DataOut1', {v}; " \
                           ":DATA:LINecoding 'M{m}.DataOut2', {v};".format(m=ppg._module_id, v=value)
        self._write(scpi_string)

    @property
    def global_output(self):
        """
        Enable state of the global data and clock output. This is a single global setting that
        supersedes all output states of specialized classes such as
        :py:attr:`Equipment.base_bert.BaseBERTPatternGenerator.data_output`

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE'}
        return output_dict[self._read('OUTPut:GLOBal? "M1.System"', dummy_data='OFF')]

    @global_output.setter
    def global_output(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': 'ON', 'DISABLE': 'OFF'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("OUTPut:GLOBal 'M1.System', {}".format(input_dict[value]))

    @property
    def modules(self):
        """
        **READONLY**

        :value: returns a dictionary of all modules and module ids connected
        :type: dict
        """
        modules_dict = {}
        pattern = re.compile(u'\(M(.*?),.*?\)')
        opt_string = self._read("*OPT?", dummy_data='dummy')
        split_opt_string = re.findall(pattern, opt_string)
        modules = [e.split("-") for e in split_opt_string]

        if self.dummy_mode:
            modules = [0, 'M8045A'], [1, 'M8046A'], [2, 'M8046A']

        for element in modules:
            module_id = int(element[0])
            module_name = element[1]

            if module_id not in modules_dict.keys():
                modules_dict[module_id] = module_name
            else:
                raise ValueError(f'Repeated module ID value : {module_id} ')

        return modules_dict

    def _configure(self):
        """
        Queries the hardware to determine its configuration and configures the driver accordingly.
        """

        modules = self.modules
        for module_id, module_name in modules.items():
            if module_name == "M8045A":
                for i in [1, 2]:
                    self.ppg.append(KeysightM8045A(module_id=module_id,
                                                   module_name=module_name,  #TODO: temporary fix for capability
                                                   channel_number=i,
                                                   interface=self._interface,
                                                   dummy_mode=self.dummy_mode))
                    self.jitter.append(KeysightM8045AJitter(module_id=module_id,
                                                            channel_number=i,
                                                            interface=self._interface,
                                                            dummy_mode=self.dummy_mode))

            elif module_name == "M8046A":
                self.ed.append(KeysightM8046A(module_id=module_id,
                                              channel_number=1,
                                              interface=self._interface,
                                              dummy_mode=self.dummy_mode))

            else:
                if module_name != 'NONE':
                    self.logger.error('%s is not a supported module' % module_name)

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        super()._configure_interface()
        self._interface.visa_handle.timeout = 20000
