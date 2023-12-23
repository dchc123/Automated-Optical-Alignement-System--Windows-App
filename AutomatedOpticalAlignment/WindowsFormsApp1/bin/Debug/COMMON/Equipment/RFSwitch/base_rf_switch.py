"""
| $Revision:: 282826                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-10-12 21:26:12 +0100 (Fri, 12 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from abc import abstractmethod
from CLI.Equipment.Base.base_equipment import BaseEquipment


class BaseRFSwitch(BaseEquipment):
    def __init__(self, address, slot, bank, interface=None, dummy_mode=False, **kwargs):
        """
        BaseRFSwitch class that all RF switch drivers should be derived from.

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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._slot = slot
        ''':type: str'''
        self._bank = bank
        ''':type: str'''
        self._driver_model = None
        ''':type: str'''

    @property
    @abstractmethod
    def driver_model(self):
        """
        ***READ-ONLY***

        :return: the model of the switch driver
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def slot(self):
        """
        ***READ-ONLY***

        :return: the slot in which the switch is installed
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def bank(self):
        """
        ***READ-ONLY***

        :return: the bank in which the switch resides
        :rtype: str
        """
        pass

    @abstractmethod
    def open_all(self):
        """
        Opens all paths in the switch
        """
        pass

    @abstractmethod
    def close_all(self):
        """
        Closes all paths in a device
        """
        pass

    # TODO: Discuss naming of function
    @abstractmethod
    def route_path(self, in_port, out_port=None):
        """
        Connects the input port to the output port. Setting out_port to None causes the method to connect the input port
        to the common port, ignoring the out_port argument completely.

        :param in_port: the port to connect to the output port
        :type in_port: str
        :param out_port: the port to connect the input port to
        :type out_port: str
        """
        pass

    # TODO: Discuss where switch aliasing goes: driver or bench
    @property
    @abstractmethod
    def path_status(self):
        """
        Returns the current path connection status in a dictionary with the format {in_port: port, out_port: port}

        :return: dictionary with the current connection status
        :rtype: dict
        """
        pass

    @property
    @abstractmethod
    def bank_voltage(self):
        """
        Returns the voltage of the bank in which the switch resides.

        :return: voltage of the bank
        :rtype: int or float or str
        """
        pass

    @bank_voltage.setter
    @abstractmethod
    def bank_voltage(self, value):
        """
        Set the voltage of the bank in which the switch resides.

        :param value: voltage to set
        :type value: int or float
        """
        pass

    @property
    @abstractmethod
    def ttl_mode(self):
        """
        ***READ-ONLY***

        :return: whether TTL Mode is enabled
        :rtype: bool
        """
        pass

    @ttl_mode.setter
    @abstractmethod
    def ttl_mode(self, value):
        """
        Sets the TTL mode On or Off

        :param value: whether TTL mode is on or off
        :type value: bool
        """
        pass

    @property
    @abstractmethod
    def relay_cycles(self):
        """
        Returns the number of relay cycles for each relay in the switch

        :return: a list of relay cycles
        :rtype: list
        """
        pass

    @abstractmethod
    def clear_relay_cycles(self):
        """
        Clears the relay cycles of all relays in the switch
        """
        pass



















