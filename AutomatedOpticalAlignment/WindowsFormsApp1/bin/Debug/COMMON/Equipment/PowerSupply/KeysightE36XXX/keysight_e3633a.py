"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.KeysightE3633A`
::

    >>> from CLI.Equipment.PowerSupply.KeysightE36XXX.keysight_e3633a import KeysightE3633A
    >>> ps = KeysightE3633A('GPIB1::23::INSTR')
    >>> ps.connect()

For channel level API:
:py:class:`.KeysightE3633AChannel`
::

    >>> ps.channel[1].voltage.setpoint = 5
    >>> ps.channel[1].voltage.setpoint
    5
    >>> ps.channel[1].voltage.value
    5.0012
    >>> ps.channel[1].current.value
    0.102
    >>> ps.channel[1].voltage.limit = 10
    >>> ps.channel[1].voltage.setpoint =11
    >>> ps.channel[1].voltage.protection_tripped
    True
    >>> ps.channel[1].voltage.setpoint = 9
    >>> ps.channel[1].voltage.clear_protection()
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_structures import CustomList
from .keysight_e36xxx import _KeysightE36XXXMemory
from .keysight_e36xxx import KeysightE36XXX
from .keysight_e36xxx import KeysightE36XXXChannel
from .keysight_e36xxx import KeysightE36XXXVoltBlock
from .keysight_e36xxx import KeysightE36XXXCurrBlock


class KeysightE3633A(KeysightE36XXX):
    """
    Keysight E3633A power supply driver.
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
        """:type: list of KeysightE3633AChannel"""
        self._memory = _KeysightE36XXXMemory(interface=interface, dummy_mode=dummy_mode)
        self.channel.append(KeysightE3633AChannel(channel_number=1, memory=self._memory,
                                                  interface=interface, dummy_mode=dummy_mode))


class KeysightE3633AChannel(KeysightE36XXXChannel):
        """
        Keysight E3633A Channel
        """

        def __init__(self, channel_number, memory, interface, dummy_mode, **kwargs):
            """
            Initialize instance

            :param channel_number: number targeting channel
            :type channel_number: int
            :param memory: shared memory container for all sub-blocks
            :type memory: _KeysightE36XXXMemory
            :param interface: interface to equipment
            :type interface: BaseEquipmentInterface
            :param dummy_mode: specifies whether or not the driver is in dummy mode
            :type dummy_mode: bool
            :param kwargs: arbitrary keyword arguments
            :type kwargs: dict
            """
            super().__init__(channel_number=channel_number, memory=memory,
                             interface=interface, dummy_mode=dummy_mode, **kwargs)

            temp_range_values = {"ALL": ['P8V', 'P20V', 'LOW', 'HIGH'],
                                 "LOW": ['P8V', 'LOW'], "HIGH": ['P20V', 'HIGH']}
            volt_threshold = 8.24
            curr_threshold = 10.30
            self.voltage = KeysightE3633AVoltBlock(channel_number=channel_number, range_values=temp_range_values,
                                                   range_threshold=volt_threshold, memory=memory,
                                                   interface=interface, dummy_mode=dummy_mode,
                                                   name=self.name + 'VoltageMeasure')
            self.current = KeysightE3633ACurrBlock(channel_number=channel_number, range_values=temp_range_values,
                                                   range_threshold=curr_threshold, memory=memory,
                                                   interface=interface, dummy_mode=dummy_mode,
                                                   name=self.name + 'CurrentMeasure')


class KeysightE3633AVoltBlock(KeysightE36XXXVoltBlock):
    """
    Keysight E3633A voltage sub block
    """
    CAPABILITY = {'voltage': {'min': 0.0, 'max': 20.6}}

    def __init__(self, channel_number, range_values, range_threshold, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param range_values: range values to use for error checking and range change
        :type range_values: dict
        :param range_threshold: voltage range threshold
        :type range_threshold: float
        :param memory: shared memory container for all sub-blocks
        :type memory: _KeysightE36XXXMemory
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, range_values=range_values, range_threshold=range_threshold,
                         memory=memory, interface=interface, dummy_mode=dummy_mode, **kwargs)


class KeysightE3633ACurrBlock(KeysightE36XXXCurrBlock):
    """
    Keysight E3633A current sub block
    """
    CAPABILITY = {'current': {'min': 0.0, 'max': 20.6}}

    def __init__(self, channel_number, range_values, range_threshold, memory, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param range_values: range values to use for error checking and range change
        :type range_values: dict
        :param range_threshold: current range threshold
        :type range_threshold: float
        :param memory: shared memory container for all sub-blocks
        :type memory: _KeysightE36XXXMemory
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, range_values=range_values, range_threshold=range_threshold,
                         memory=memory, interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def ocp(self):
        """
        Current protection state

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        self._memory.channel = self._channel_number
        return output_dict[self._read('CURRent:PROTection:STATe?', dummy_data='0').strip()]

    @ocp.setter
    def ocp(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        self._memory.channel = self._channel_number
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("CURRent:PROTection:STATe %s" % input_dict[value])

    @property
    def protection_level(self):
        """
        :value: Current protection level
        :type: float
        """
        self._memory.channel = self._channel_number
        return float(self._read("CURRent:PROTection:LEVel?"))

    @protection_level.setter
    def protection_level(self, value):
        """
        :type value: float
        """
        self._memory.channel = self._channel_number
        self._write("CURRent:PROTection:LEVel %s" % value)

    @property
    def protection_tripped(self):
        """
        **READONLY**
        Over current protection. Returns True if protection is tripped

        :value: ocp tripped
        :type: bool
        """

        return bool(int(self._read("CURRent:PROTection:TRIPped?", dummy_type="int")))

    def clear_protection(self):
        """
        Clears the protection status triggered by an over current.
        Condition generating the fault must be removed in order for clear to take effect.
        """

        self._write("CURRENT:PROTection:CLEar")

        if self.protection_tripped:
            self.logger.warning('Condition generating the issue has not been addressed. Please address condition, then '
                                'clear protection flag.')
