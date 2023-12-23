"""
| $Revision:: 279036                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-10 17:01:00 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Equipment.Base.base_equipment import BaseEquipment
from CLI.Equipment.Base.base_equipment import BaseEquipmentBlock


class BaseOpticalSwitch(BaseEquipment):
    """
    Base Optical Switch class that all Optical Switches should be derived from.
    """

    CAPABILITY = {'channel': None}

    def __init__(self, address, interface, dummy_mode, **kwargs):
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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)


class BaseOpticalSwitchChannel(BaseEquipmentBlock):
    """
    Base Optical Switch channel class that all Optical Switches channels should be derived from.
    """

    CAPABILITY = {'in_ports': [None], 'out_ports': [None]}

    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._state_dict = {}

    def add_state(self, keyword, in_port, out_port):
        """
        Creates a dictionary in the following format :
        {'key1': [input, output], 'key2': [input, output]}

        :param keyword: keyword that describes switch state
        :type keyword: str
        :param in_port:
        :type in_port: int or str
        :param out_port:
        :type out_port: int or str
        :returns:
        """
        self._state_dict.update({keyword: [in_port, out_port]})

    def auto_states(self):
        """
        Automatically creates a state dictionary, iterating between in_port and out_port:
        {'state_1_1': [input1, output1], 'state_1_2':
        [input1, output2], 'state_2_1': [input2, output1]}
        """
        in_ports = self.CAPABILITY['in_ports']
        out_ports = self.CAPABILITY['out_ports']

        for in_port in in_ports:
            for out_port in out_ports:
                self.add_state('state_%s_%s' % (in_port, out_port), in_port, out_port)

    def close_state(self, keyword):
        """
        Closes ports associated to the keyword state. This method call :
        :py:class:`.route`

        :param keyword: switch state descriptor
        :type keyword: str
        :raise ValueError: value error if state dict is empty or keyword is not a valid state
        """
        if self._state_dict:
            if keyword not in self._state_dict.keys():
                raise ValueError("State '%s' is not a valid keyword" % keyword)
            else:
                self.close(self._state_dict[keyword][0], self._state_dict[keyword][1])
        else:
            raise ValueError("No states have been created")

    @property
    def current_routing(self):
        """
        READONLY

        Returns currently connected paths in a list of lists.
        Length of list depends on switch Capability.

        :value: [[in_port, out_port], [in_port2, out_port2]] currently closed
        :type: list of list
        """
        raise NotImplementedError

    def delete_state(self, keyword):
        """
        Deletes a state entry if 'keyword' exists. If keyword is '_all_', all entries are deleted.

        :param keyword: switch state descriptor
        :type keyword: str
        :raise ValueError: value error if state dict is empty or keyword is not a valid state
        """
        if self._state_dict:
            if keyword == '_all_':
                self._state_dict.clear()
            else:
                if keyword in self._state_dict.keys():
                    del self._state_dict[keyword]
                else:
                    raise ValueError("State '%s' is not a valid keyword" % keyword)
        else:
            raise ValueError("No states have been created")

    def close(self, in_port, out_port):
        """
        Connects switch in_port to out_port

        :param in_port:
        :type in_port: int or str
        :param out_port:
        :type out_port: int or str
        """
        raise NotImplementedError

    def states(self, keyword='_all_'):
        """
        Returns  [in_port, out_port] of 'keyword' state. If keyword is '_all_', returns the full
        state dictionary in this format : {'key1': [input1, output1], 'key2': [input2, output2]}

        :param keyword: switch state descriptor
        :type keyword: str
        :return: dictionary of all states or list of requested state
        :rtype: dict or list
        :raise ValueError: value error if state dict is empty
        """
        if self._state_dict:
            if keyword == '_all_':
                return self._state_dict
            else:
                return self._state_dict[keyword]
        else:
            raise ValueError("No states have been created")
