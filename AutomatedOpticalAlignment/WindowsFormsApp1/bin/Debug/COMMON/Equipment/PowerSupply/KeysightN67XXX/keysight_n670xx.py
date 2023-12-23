"""
| $Revision:: 281242                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-08-13 15:13:48 +0100 (Mon, 13 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Utilities.custom_structures import CustomList
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from ..base_power_supply import BasePowerSupply
from ..KeysightN67XXX.Modules.keysight_n67xxx import KeysightN67XXXChannel
from ..KeysightN67XXX.Modules.keysight_n6731b import KeysightN6731BChannel
from ..KeysightN67XXX.Modules.keysight_n6732b import KeysightN6732BChannel
from ..KeysightN67XXX.Modules.keysight_n6734b import KeysightN6734BChannel
from ..KeysightN67XXX.Modules.keysight_n6741b import KeysightN6741BChannel
from ..KeysightN67XXX.Modules.keysight_n6742b import KeysightN6742BChannel
from ..KeysightN67XXX.Modules.keysight_n6751a import KeysightN6751AChannel
from ..KeysightN67XXX.Modules.keysight_n6761a import KeysightN6761AChannel
from ..KeysightN67XXX.Modules.keysight_n6762a import KeysightN6762AChannel


class KeysightN670XX(BasePowerSupply):
    """
    Keysight N670XX 4 channel power supply chassis driver.
    """
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
        """:type: list of KeysightN67XXXChannel"""

    @property
    def modules(self):
        """
        **READONLY**

        :value: returns a dict of dict of all psu mdules connected. (chan, model, option)
        :rtype: dict
        """
        # Create a dict with channel number as keys
        # and an other dict of module name/options as the value
        modules_and_options = {}
        dummy_options = ['', '', '054', '054']
        dummy_modules = 'chan 1:N6732B;chan 2:N6732B;chan 3:N6761A;chan 4:N6762A'

        temp = self._read("*RDT?", dummy_data=dummy_modules)
        channels = [x.strip('chan ').split(':') for x in temp.split(";")]
        for index, channel in enumerate(channels):
            option = self._read('SYSTem:CHANnel:OPTion? (@%s)' % channel[0],
                                dummy_data=dummy_options[index])
            modules_and_options[int(channel[0])] = {'module_name': channel[1],
                                                    'module_option': option}

        return modules_and_options

    def _configure(self):
        """
        Queries the hardware to determine its configuration and configures the drivers accordingly.
        """

        modules_options = self.modules

        for chan in modules_options.keys():

            if "N6731B" in modules_options[chan]['module_name']:
                self.channel.append(KeysightN6731BChannel(
                    channel_number=chan, channel_options=modules_options[chan]['module_option'],
                    interface=self._interface, dummy_mode=self.dummy_mode))

            elif "N6732B" in modules_options[chan]['module_name']:
                self.channel.append(KeysightN6732BChannel(
                    channel_number=chan, channel_options=modules_options[chan]['module_option'],
                    interface=self._interface, dummy_mode=self.dummy_mode))

            elif "N6734B" in modules_options[chan]['module_name']:
                self.channel.append(KeysightN6734BChannel(
                    channel_number=chan, channel_options=modules_options[chan]['module_option'],
                    interface=self._interface, dummy_mode=self.dummy_mode))

            elif "N6741B" in modules_options[chan]['module_name']:
                self.channel.append(KeysightN6741BChannel(
                    channel_number=chan, channel_options=modules_options[chan]['module_option'],
                    interface=self._interface, dummy_mode=self.dummy_mode))

            elif "N6742B" in modules_options[chan]['module_name']:
                self.channel.append(KeysightN6742BChannel(
                    channel_number=chan, channel_options=modules_options[chan]['module_option'],
                    interface=self._interface, dummy_mode=self.dummy_mode))

            elif "N6751A" in modules_options[chan]['module_name']:
                self.channel.append(KeysightN6751AChannel(
                    channel_number=chan, channel_options=modules_options[chan]['module_option'],
                    interface=self._interface, dummy_mode=self.dummy_mode))

            elif "N6761A" in modules_options[chan]['module_name']:
                self.channel.append(KeysightN6761AChannel(
                    channel_number=chan, channel_options=modules_options[chan]['module_option'],
                    interface=self._interface, dummy_mode=self.dummy_mode))

            elif "N6762A" in modules_options[chan]['module_name']:
                self.channel.append(KeysightN6762AChannel(
                    channel_number=chan, channel_options=modules_options[chan]['module_option'],
                    interface=self._interface, dummy_mode=self.dummy_mode))

            else:
                if modules_options[chan]['module_name'] != 'Not Present':
                    self.logger.error('%s is not a supported module'
                                      % modules_options[chan]['module_name'])

    @property
    def output_coupling(self):
        """
        Selects which channels are coupled together and coupling will be enabled if supported.
        If an empty list is specified, they are all uncoupled and if supported coupling will be disabled

        :value: list of channels to couple. ex [1,2]
        :type: list of int
        """
        return self._read(":OUTP:COUP:CHAN?")

    @output_coupling.setter
    def output_coupling(self, value):
        """
        :type value: list of int
        :raise ValueError: exception if input is not list of int
        """
        self._write((":OUTP:COUP:CHAN %s" % ','.join(map(str, value))))
