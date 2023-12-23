"""
| $Revision:: 282699                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-10-04 18:29:51 +0100 (Thu, 04 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from abc import abstractmethod
from CLI.Equipment.RFSwitch.base_rf_switch import BaseRFSwitch
from CLI.Interfaces.VISA.cli_visa import CLIVISA


class Keysight876XX(BaseRFSwitch):

    # Concrete implementation of Keysight876XX should implement custom _ROUTE_MAP variable
    # Follow the format -> { 'port': front panel button }
    _ROUTE_MAP = {}
    _CAPABILITY = {
        '11713C': {'slots': ['x', 'y'], 'banks': ['1', '2']},
        '11713B': {'slots': ['x', 'y'], 'banks': ['1']}
                   }

    def __init__(self, address, slot, bank, interface=None, dummy_mode=False, **kwargs):
        """
        Base Keysight876XX class that all concrete Keysight87XX drivers should be derived from.

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
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, slot=slot, bank=bank, interface=interface, dummy_mode=dummy_mode, **kwargs)

    def _configure_interface(self):
        """
        Configures the interface to disable error checking and polling
        """
        if isinstance(self._interface, CLIVISA):
            self._interface.error_check_supported = False
            self._interface.stb_polling_supported = False

    def _configure(self):
        # Get the switch driver model. Setting it to model 11713C if it's dummy mode
        if not self.dummy_mode:
            self._driver_model = self.identity['model']
        else:
            self._driver_model = '11713C'

        #  Type & value check slot, changing it to lower-case if it's a str
        if isinstance(self._slot, str):
            self._slot = self._slot.lower()
            if self._slot not in self._CAPABILITY[self._driver_model]['slots']:
                raise ValueError('Unsupported slot! Must be one of {0}!'
                                 .format(self._CAPABILITY[self._driver_model]['slots']))
        else:
            raise TypeError('Slot must be a str!')

        # Type & value check bank
        if isinstance(self._bank, str):
            if self._bank not in self._CAPABILITY[self._driver_model]['banks']:
                raise ValueError('Switch driver model {0} only supports banks {1}.'.
                                 format(self._driver_model, self._CAPABILITY[self._driver_model]['banks']))
        else:
            raise TypeError('Bank must be a str!')

    @property
    def driver_model(self):
        """
        ***READ-ONLY***

        :return: the model of the switch driver
        :rtype: str
        """
        return self._driver_model

    @property
    def slot(self):
        """
        **READ-ONLY**

        :return: slot in which the switch is installed
        :rtype: int or str
        """
        return self._slot

    @property
    def bank(self):
        """
        **READ-ONLY**

        :return: bank in which the switch resides
        :rtype: int or str
        """
        return self._bank

    def open_all(self):
        """
        Opens all relays in the switch
        """
        if self.slot == 'x':
            self._write('ROUTe:OPEn (@{0}01,{0}02,{0}03,{0}04,{0}09)'.format(self.bank))
        elif self.slot == 'y':
            self._write(':ROUTe:OPEn (@{0}05,{0}06,{0}07,{0}08,{0}00)'.format(self.bank))

    def close_all(self):
        """
        Closes all relays in the device
        """
        if self.slot == 'x':
            self._write(':ROUTe:CLOSe (@{0}01,{0}02,{0}03,{0}04,{0}09)'.format(self.bank))
        elif self.slot == 'y':
            self._write(':ROUTe:CLOSe (@{0}05,{0}06,{0}07,{0}08,{0}00)'.format(self.bank))

    def _slot_map(self, port):
        """
        Retrieves the appropriate driver pins to toggle and adjusts it if the switch is installed in slot Y

        :param port: the port to open
        :type port: str
        :return: the driver value to toggle to close the given port
        :rtype: int
        """
        # Ensure the switch contains the port the user has selected
        if port not in self._ROUTE_MAP.keys():
            raise ValueError('Switch does not contain a port {0}'.format(port))
        # Get the route that we will connect
        path = self._ROUTE_MAP[port]
        # If the route is none then the port is connected by opening all ports otherwise identify which path to close
        if path is not None:
            # If the slot is Y, the path is offset by 4 and switch 0 is used instead of 9
            if self.slot == 'y':
                if path == 9:
                    path = 0
                else:
                    path += 4
        return path

    def route_path(self, in_port, out_port=None):
        """
        Connects the input port to the output port. Setting out_port to None causes the method to connect the input port
        to the common port, ignoring the out_port argument completely.

        :param in_port: the port to connect to the output port
        :type in_port: str
        :param out_port: the port to connect the input port to
        :type out_port: str
        """
        if not isinstance(in_port, str):
            raise TypeError('In_port must be of type str!')
        if out_port is not None:
            self.logger.warning('Out port is set to a value but is not used by Keysight 876XX switches. '
                                'Value will be ignored!')
        # Get the currently connected port and don't do anything if the port is already connected
        current_port = self.path_status['in_port']
        if in_port != current_port:
            # Get the route that we will connect
            path = self._slot_map(in_port)
            # Open all paths to ensure we are starting fresh
            self.open_all()
            # If path is not None, write the command
            if path is not None:
                self._write(':ROUTe:CLOSe (@{0}0{1})'.format(self.bank, path))
        else:
            self.logger.info('Port {0} already connected. Routing bypassed to preserve switch life.'.format(in_port))

    @property
    @abstractmethod
    def path_status(self):
        """
        Returns the current path connection status in a dictionary with the format {in_port: port, out_port: port}

        :return: dictionary with the current connection status
        :rtype: dict
        """
        # Needs to be implemented in concrete switch as closed path is dependent on specific switch positions
        pass

    @property
    def bank_voltage(self):
        """
        Returns the voltage of the bank in which the switch resides.

        :return: voltage of the bank
        :rtype: str
        """
        return self._read(':CONFigure:BANK{0}?'.format(self.bank)).strip().replace('P', '')

    @bank_voltage.setter
    def bank_voltage(self, value):
        """
        Set the voltage of the bank in which the switch resides.

        :param value: voltage to set
        :type value: int or float
        """
        if not isinstance(value, int) and not isinstance(value, float):
            raise TypeError('Bank voltage must be an int or float!')
        # Convert the int or float to a bank voltage SCPI value
        bank_voltages = {0: 'OFF', 5: 'P5v', 15: 'P15v', 24: 'P24v'}
        if value not in bank_voltages.keys():
            bank_voltage = 'USER'
            self.logger.warning('Bank voltage set to User defined value: {0}V! '
                                'Setting may conflict with switch connected in adjacent slot!'.format(value))
        else:
            bank_voltage = bank_voltages[value]
            self.logger.warning('Bank voltage set to {0}V. '
                                'Setting may conflict with switch connected in adjacent slot!'.format(value))
        # Write the command
        self._write('CONFigure:BANK{0} {1}'.format(self.bank, bank_voltage))

    @property
    def ttl_mode(self):
        """
        ***READ-ONLY***

        :return: whether TTL Mode is enabled
        :rtype: bool
        """
        read_value =  self._read('CONFigure:BANK{0}:TTL?'.format(self.bank)).strip()
        if read_value == '1':
            return True
        else:
            return False

    @ttl_mode.setter
    def ttl_mode(self, value):
        """
        Sets the TTL mode On or Off

        :param value: whether TTL mode is on or off
        :type value: bool
        """
        # Check the type of value. Property supports both str an int. If str, set value to lowercase
        if not isinstance(value, bool):
            raise TypeError('TTL Mode must be of type bool (either True or False)!')
        # Create a dictionary of TTL Mode enable options:
        ttl_enable_options = {True: 'ON', False: 'OFF'}
        # Write the command
        self._write('CONFigure:BANK{0}:TTL {1}'.format(self.bank, ttl_enable_options[value]))

    @property
    def relay_cycles(self):
        """
        Returns the number of relay cycles for each relay in the switch

        :return: a list of relay cycles
        :rtype: list
        """
        cycles = None
        if self.slot == 'x':
            cycles = self._read(':DIAGnostic:RELay:CYCles? (@{0}01,{0}02,{0}03,{0}04,{0}09)'.format(self.bank))
        elif self.slot == 'y':
            cycles = self._read(':DIAGnostic:RELay:CYCles? (@{0}05,{0}06,{0}07,{0}08,{0}00)'.format(self.bank))
        return cycles.strip().split(',')

    def clear_relay_cycles(self):
        """
        Clears the relay cycles of all relays in the switch
        """
        if self.slot == 'x':
            self._write(':DIAGnostic:RELay:CLEAr (@{0}01,{0}02,{0}03,{0}04,{0}09)'.format(self.bank))
        elif self.slot == 'y':
            self._write(':DIAGnostic:RELay:CLEAr (@{0}05,{0}06,{0}07,{0}08,{0}00)'.format(self.bank))
