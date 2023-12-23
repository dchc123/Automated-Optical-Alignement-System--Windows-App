"""
| $Revision:: 282699                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-10-04 18:29:51 +0100 (Thu, 04 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.RFSwitch.Keysight876XX.keysight_876XX import Keysight876XX


class Keysight8769M(Keysight876XX):
    """
    Keysight 8769M Switch Driver
    """
    # Route map must be a dict of { 'port': front panel button }
    _ROUTE_MAP = {'1': 4, '2': 2, '3': 3, '4': 1, '5': 9, '6': None}

    def __init__(self, address, slot, bank, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance.

        :param address: address of the switch
        :type address: int or str
        :param slot: the driver slot in which the switch is installed
        :type slot: str
        :param bank: the bank in which the switch is located
        :type bank: str
        :param interface: the interface used to communicate to the switch
        :type interface: BaseEquipmentInterface
        :param dummy_mode: whether or not the switch is operating in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(address=address, slot=slot, bank=bank, interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def path_status(self):
        """
        Returns the current path connection status in a dictionary with the format {in_port: port, out_port: port}

        :return: dictionary with the current connection status
        :rtype: dict
        """
        path_map = {'in_port': None, 'out_port': 'common'}
        if self.slot == 'x':
            read_status = self._read(':ROUTe:CLOSe? (@{0}01,{0}02,{0}03,{0}04,{0}09)'
                                     .format(self.bank)).strip().split(',')
        else:
            read_status = self._read(':ROUTe:CLOSe? (@{0}05,{0}06,{0}07,{0}08,{0}00)'
                                     .format(self.bank)).strip().split(',')
        # If nothing is closed, port 6 is connected
        if '1' not in read_status:
            path_map['in_port'] = '6'
        # Identify which port is connected to the common port. This will identify the relay
        # closest to common that is closed. i.e. if all relays are closed, Port 1 is open.
        else:
            if read_status[3] == '1':
                path_map['in_port'] = '1'
            elif read_status[1] == '1':
                path_map['in_port'] = '2'
            elif read_status[2] == '1':
                path_map['in_port'] = '3'
            elif read_status[0] == '1':
                path_map['in_port'] = '4'
            elif read_status[4] == '1':
                path_map['in_port'] = '5'
        return path_map
