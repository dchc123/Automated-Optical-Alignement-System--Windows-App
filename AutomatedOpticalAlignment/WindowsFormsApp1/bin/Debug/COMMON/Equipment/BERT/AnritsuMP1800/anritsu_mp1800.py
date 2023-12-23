"""
| $Revision:: 283530                                   $:  Revision of last commit
| $Author:: wleung@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-11-12 20:05:11 +0000 (Mon, 12 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

The Anritsu MP1800 has multiple configurations depending on the modules connected,
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

For the top level API: See :py:class:`Equipment.BERT.AnritsuMP1800.anritsu_mp1800.AnritsuMP1800`
::

    >>> from CLI.Equipment.BERT.AnritsuMP1800.anritsu_mp1800 import AnritsuMP1800
    >>> bert = AnritsuMP1800('GPIB1::23::INSTR')
    >>> bert.connect()
    >>> bert.clock_frequency
    0
    >>> bert.clock_frequency = 100000000
    >>> bert.clock_frequency
    100000000

For the Error Detector API: See :py:mod:`Equipment.BERT.AnritsuMP1800.ed`

For the Pattern Generator API: See :py:mod:`Equipment.BERT.AnritsuMP1800.ppg`

For the Jitter Module API: See :py:mod:`Equipment.BERT.AnritsuMP1800.jitter`
"""
from CLI.Utilities.custom_exceptions import NotSupportedError
from CLI.Interfaces.Socket.cli_socket import CLISocket
from CLI.Equipment.BERT.base_bert import BaseBERT
from CLI.Utilities.custom_structures import CustomList

from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_mu183020a import AnritsuMU183020AChannel
from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_muxed_ppg import AnritsuMuxedMP1800PPG
from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_mu183040a import AnritsuMU183040AChannel
from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_mu183040b import AnritsuMU183040BChannel
from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_demuxed_ed import AnritsuDemuxedED
from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_mu181500b import AnritsuMU181500B
from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_mp1800_ed import AnritsuMP1800ED
from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_mp1800_ppg import AnritsuMP1800PPG
from CLI.Equipment.BERT.AnritsuMP1800.Modules.anritsu_mp1800_jitter import AnritsuMP1800Jitter


class AnritsuMP1800(BaseBERT):
    """
    Driver for Anritsu MP1800 Series BERT
    """
    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        AnritsuMP1800 initialization

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param name: (default: "AnritsuMP1800") object name for logging purposes
         object for identification purposes
        :param dummy_mode: (default: False) specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        """
        if interface is None:
            interface = CLISocket()
        super().__init__(address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._synthesizer_module_id = None

        self.ppg = CustomList()
        """:type: list of AnritsuMP1800PPG"""
        self.ed = CustomList()
        """:type: list of AnritsuMP1800ED"""
        self.jitter = CustomList()
        """:type: list of AnritsuMP1800Jitter"""

    def _configure(self):
        """
        Queries the hardware to determine its configuration and configures the driver accordingly.
        """

        modules = self.modules

        # Add more checks as drivers for more modules are developed
        # Assumption being made here that there is at most 1 synthesizer module in chassis
        if "MU181000A" in modules:
            self._synthesizer_module_id = modules["MU181000A"][0]
            del modules["MU181000A"]

        if "MU183020A" in modules:
            for module_id in modules["MU183020A"]:
                self.ppg.append(AnritsuMU183020AChannel(module_id=module_id, channel_number=1,
                                                        synth_mod_id=self._synthesizer_module_id,
                                                        interface=self._interface, dummy_mode=self.dummy_mode))
            del modules["MU183020A"]

        if "MU183040A" in modules:
            for module_id in modules["MU183040A"]:
                self.ed.append(AnritsuMU183040AChannel(module_id=module_id, channel_number=1,
                                                       interface=self._interface, dummy_mode=self.dummy_mode))
            del modules["MU183040A"]

        if "MU183040B" in modules:
            for module_id in modules["MU183040B"]:
                self.ed.append(AnritsuMU183040BChannel(module_id=module_id, channel_number=1,
                                                       interface=self._interface, dummy_mode=self.dummy_mode))
            del modules["MU183040B"]

        if "MU181500B" in modules:
            for module_id in modules["MU181500B"]:
                self.jitter.append(AnritsuMU181500B(module_id=module_id, channel_number=1,
                                                    synth_mod_id=self._synthesizer_module_id,
                                                    interface=self._interface, dummy_mode=self.dummy_mode))
            del modules["MU181500B"]

        # Assumptions are being made here... if a MUX module is present, assume that there are
        # exactly two MU181020B PPGs in the chassis and are both connected to the MUX.
        if "MU182020A" in modules:
            self.ppg.append(AnritsuMuxedMP1800PPG(ppg1_module_id=modules["MU181020B"][0],
                                                  ppg2_module_id=modules["MU181020B"][1],
                                                  mux_module_id=modules["MU182020A"][0],
                                                  interface=self._interface, dummy_mode=self.dummy_mode))
            del modules["MU182020A"]

        # Assumptions are being made here... if a DEMUX module is present, assume that there are
        # exactly two MU181040B EDs in the chassis and are both connected to the DEMUX.
        if "MU182040A" in modules:
            self.ed.append(AnritsuDemuxedED(ed1_module_id=modules["MU181040B"][0],
                                            ed2_module_id=modules["MU181040B"][1],
                                            demux_module_id=modules["MU182040A"][0],
                                            interface=self._interface, dummy_mode=self.dummy_mode))
            del modules["MU182040A"]

        if modules:
            for module in modules.keys():
                if module != 'NONE':
                    self.logger.error('%s is not a supported module' % module)

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
        return int(self._read(':OUTPut:CLOCk:FREQuency?'))*1000

    @clock_frequency.setter
    def clock_frequency(self, value):
        """
        :type value: int
        :raise ValueError: exception if frequency not between 100MHz and 12500MHz
        """
        if self._synthesizer_module_id is None:
            raise NotSupportedError('Synthesizer module cannot be detected')
        elif 12500000 < value < 100000000:
            raise ValueError('Clock frequency valid between 100MHz and 12500Mhz')
        else:
            self._write(":MODule:ID %s" % self._synthesizer_module_id)
            self._write(":OUTPut:CLOCk:FUNit kHz")
            frequency_khz = round(float(value) / 1000.0)
            self._write(":OUTPut:CLOCk:FREQuency %d" % frequency_khz)

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
        output_dict = {'0': 'DISABLE', 'OFF': 'DISABLE', '1': 'ENABLE', 'ON': 'ENABLE',
                       'DUMMY_DATA': 'DISABLE'}
        return output_dict[self._read(':SOURce:OUTPut:ASET?')]

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
            self._write(":SOURce:OUTPut:ASET %s" % input_dict[value])

    @property
    def identity(self):
        """
        **READONLY**
        Retrieve equipment identity. Also retrieve modules and options properties
        if available. This overrides the parent property because Anritsu doesn't return firmware.

        :value: identity
        :type: dict
        """
        idn_data = self._read("*IDN?", dummy_data='{a},{b},{b},{b}'.format(a=self.name, b='DUMMY_DATA'))
        idn_data = idn_data.split(',')

        data = {
            'manufacturer': idn_data[0].strip(),
            'model': idn_data[1].strip(),
            'serial': idn_data[2].strip()
        }

        if hasattr(self, 'modules'):
            data['modules'] = self.modules
        if hasattr(self, 'options'):
            data['options'] = self.options

        for key, value in data.items():
            self.logger.debug("{}: {}".format(key.upper(), value))

        return data

    @property
    def modules(self):
        """
        **READONLY**

        :value: returns a dictionary of all modules and module ids connected
        :type: dict
        """
        # Create a dict with module names as keys and a list of module numbers as the value
        modules = {}
        dummy_modules = ['MU181000A, 1', 'MU183020A, 2', 'MU183040A, 3', 'MU181500B, 4',
                         'NONE, 5', 'NONE, 6']
        for module_id in range(1, 7):
            module_name = self._read(":SYSTEM:MODULE? %d" % module_id,
                                     dummy_data=dummy_modules[module_id-1]).split(',')[0]
            if module_name in modules.keys():
                modules[module_name] = modules[module_name] + [module_id]
            else:
                modules[module_name] = [module_id]
        return modules
