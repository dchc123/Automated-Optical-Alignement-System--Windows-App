"""
| $Revision:: 283708                                   $:  Revision of last commit
| $Author:: lagapie@SEMNET.DOM                         $:  Author of last commit
| $Date:: 2018-11-16 18:15:08 +0000 (Fri, 16 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Mainframes.YokogawaAQ221X .yokogawa_aq221x import YokogawaAQ221X
from CLI.Utilities.custom_structures import CustomList
from ..base_optical_switch import BaseOpticalSwitch
from ..base_optical_switch import BaseOpticalSwitchChannel


class YokogawaAQ2200_4XX(BaseOpticalSwitch):
    """
    Yokogawa AQ2200-4XX optical switch common driver
    """

    CAPABILITY = {'channel': None}

    def __init__(self, address, slot_number, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address of the mainframe controlling this module
        :type address: int or str
        :param slot_number: slot number of the module
        :type slot_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = YokogawaAQ221X()
        self.interface = interface
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._slot_number = slot_number
        self.channel = CustomList()
        """:type: list of Yokogawa AQ2200_4XX Channel """
        self.channel.append(YokogawaAQ2200_4XXChannel(channel_number=1, slot_number=slot_number, interface=interface,
                                                      dummy_mode=dummy_mode))

    @property
    def identity(self):
        """
        **READONLY**
        Retrieve module identity.

        :value: identity
        :type: dict
        """
        idn_data = self._read(":SLOT{}:IDN?".format(self._slot_number),
                              dummy_data='{a},{b},{b},{b}'.format(a=self.name, b='DUMMY_DATA'))
        idn_data = idn_data.split(',')
        data = {
            'manufacturer': idn_data[0],
            'model': idn_data[1],
            'serial': idn_data[2],
            'firmware': idn_data[3]
        }
        for key, value in data.items():
            self.logger.debug("{}: {}".format(key.upper(), value))
        return data

    def reset(self):
        """
        Custom reset that only performs on current slot.
        Switches channels to default.
        """
        for channel in self.channel:
            channel.close(1, 1)

    def connect(self):
        """
        Connect to slot and verify compatibility.
        """
        super().connect()
        slots = self.interface.slots()
        if self._slot_number > slots:
            self.disconnect()
            raise ValueError("%s is an invalid SLOT number. Choose a slot between 1 and %s. Disconnecting..."
                             % (self._slot_number, slots))
        for channel in self.channel:
            channel._module_options()



class YokogawaAQ2200_4XXChannel(BaseOpticalSwitchChannel):
    """
    Yokogawa AQ2200-4XX optical switch channel
    """

    CAPABILITY = {'in_ports': [None],
                  'out_ports': [None],
                  'optical_fiber_type': [None],
                  'wavelength_range': {'min': None, 'max': None},
                  }

    def __init__(self, channel_number, slot_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the switch
        :type channel_number: int
        :param slot_number: slot number of the module
        :type slot_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = channel_number
        self._slot_number = slot_number

    @property
    def current_routing(self):
        """
        READONLY

        Returns currently connected paths in a list of lists.
        Length of list depends on switch Capability.

        :value: [[in_port, out_port], [in_port2, out_port2]] currently closed
        :type: list of list
        :raise ValueError: Exception if port combination is invalid
        """
        temp = self._read("ROUTe%s:CHANnel%s?" % (self._slot_number, self._channel_number),
                          dummy_data='1,2;2,1').strip().replace('A', '1').replace('B', '2')

        return [x.split(',') for x in temp.split(";")]

    def close(self, in_port, out_port):
        """
        Connects switch in_port to out_port

        :param in_port:
        :type in_port: int or str
        :param out_port:
        :type out_port: int or str
        :raise ValueError: Exception if port combination is invalid
        """
        in_dict = {1: 'A', 2: 'B'}    # Modules requires letters. User only uses numbers.

        if in_port in self.CAPABILITY['in_ports'] and out_port in self.CAPABILITY['out_ports']:
            self._write("ROUTe%s:CHANnel%s %s,%s"
                        % (self._slot_number, self._channel_number, in_dict[in_port], out_port))
        else:
            raise ValueError("Port combination not valid. "
                             "See supported ports. in_ports: %s , out_ports: %s "
                             % (self.CAPABILITY['in_ports'], self.CAPABILITY['out_ports']))

    def _module_options(self):
        """
        Retrieve the module options and populate some of the capability fields.
        """
        module_opt = str(self._read(":SLOT%s:OPT?" % self._slot_number, dummy_data="800NM-1370NM")).split(",")
        model_suffix = module_opt[0].split("-")
        if model_suffix[1] == "04":
            self.CAPABILITY['in_ports'] = [1]
            self.CAPABILITY['out_ports'] = [1, 2, 3, 4]
        elif model_suffix[1] == "08":
            self.CAPABILITY['in_ports'] = [1]
            self.CAPABILITY['out_ports'] = [1, 2, 3, 4, 5, 6, 7, 8]
        elif model_suffix[1] == "16":
            self.CAPABILITY['in_ports'] = [1]
            self.CAPABILITY['out_ports'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        elif model_suffix[1] == "21":
            self.CAPABILITY['in_ports'] = [1, 2]
            self.CAPABILITY['out_ports'] = [1, 2]
        elif model_suffix[1] == "22":
            self.CAPABILITY['in_ports'] = [1, 2]
            self.CAPABILITY['out_ports'] = [1, 2]
        else:
            raise ValueError("Unexpected Optical Switch Port Configuration. Please verify User manual! ")
        if model_suffix[2] == "SA":
            self.CAPABILITY['optical_fiber_type'] = "SMF"
        elif model_suffix[2] == "G5":
            self.CAPABILITY['optical_fiber_type'] = "MMF (GI 50/125)"
        elif model_suffix[2] == "G6":
            self.CAPABILITY['optical_fiber_type'] = "MMF (GI 62.5/125)"
        else:
            raise ValueError("Unexpected Optical Switch Optical Fiber Type. Please verify User manual! ")
        wl_range = module_opt[6].split("/")
        self.CAPABILITY['wavelength_range']['min'] = float(wl_range[0].rstrip("NM"))
        self.CAPABILITY['wavelength_range']['max'] = float(wl_range[1].rstrip("NM"))
