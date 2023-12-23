"""
| $Revision:: 283620                                   $:  Revision of last commit
| $Author:: lagapie@SEMNET.DOM                         $:  Author of last commit
| $Date:: 2018-11-14 18:43:13 +0000 (Wed, 14 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Mainframes.Keysight816XX.keysight_8163x import Keysight8163X
from CLI.Utilities.custom_structures import CustomList
from ..base_optical_switch import BaseOpticalSwitch
from ..base_optical_switch import BaseOpticalSwitchChannel


class Keysight8159XX(BaseOpticalSwitch):
    """
    Keysight 8159XX optical switch common driver
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
            interface = Keysight8163X()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._slot_number = slot_number
        self.channel = CustomList()
        """:type: list of Keysight8159XXChannel"""
        self.channel.append(Keysight8159XXChannel(channel_number=1, slot_number=slot_number, interface=interface,
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
        Switches channels to default. Done for all channels on the module.
        """
        for channel in self.channel:
            channel.close(1, 1)

class Keysight8159XXChannel(BaseOpticalSwitchChannel):
    """
    Keysight 8159XX optical switch channel
    """

    CAPABILITY = {'in_ports': [None], 'out_ports': [None]}

    def __init__(self, channel_number, slot_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: channel number of the switch
        :type channel_number: int
        :param slot_number: slot number of the module
        :type slot_number: int
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

