"""
| $Revision:: 282861                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-10-15 22:36:13 +0100 (Mon, 15 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Equipment.Base.base_equipment import BaseEquipment
from COMMON.Equipment.Base.base_equipment import BaseEquipmentBlock
from COMMON.Utilities.custom_structures import CustomList


class BaseSourceMeter(BaseEquipment):
    """
    Base Source Meter class that all Source Meter should be derived from.
    """
    def __init__(self, address, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of BaseSourceMeterChannel"""

class BaseSourceMeterChannel(BaseEquipmentBlock):
    """
    Base source meter output channel class that all source meter channels should be derived from.
    """
    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = None
        self.source = None
        """:type: BaseSourceMeterSourceParentBlock"""
        self.measure = None
        """:type: BaseSourceMeterMeasureParentBlock"""

    @property
    def output(self):
        """
        Disable or Enable source meter output

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @output.setter
    def output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def remote_sensing(self):
        """
        Disable or Enable four wire sensing

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @remote_sensing.setter
    def remote_sensing(self, value):
        """
        :type value: str
        """
        raise NotImplementedError

    @property
    def terminal_select(self):
        """
        Select FRONT or REAR terminals on source meter

        :value: - 'FRONT'
                - 'REAR'
        :type: str
        """
        raise NotImplementedError

    @terminal_select.setter
    def terminal_select(self, value):
        """
        :type value: str
        :raise ValueError: exception if value is not FRONT/REAR
        """
        raise NotImplementedError


class BaseSourceMeterSourceParentBlock(BaseEquipmentBlock):
    """
    Base sub block for grouping source specific properties
    """
    CAPABILITY = None

    def __init__(self, interface, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = None
        self._type = None
        self.voltage = None
        """:type: BaseSourceMeterSourceVoltageBlock"""
        self.current = None
        """:type: BaseSourceMeterSourceCurrentBlock"""


class BaseSourceMeterMeasureParentBlock(BaseEquipmentBlock):
    """
    Base sub block for grouping source specific properties
    """
    CAPABILITY = None

    def __init__(self, interface, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = None
        self._type = None
        self.voltage = None
        """:type: BaseSourceMeterMeasureBlock"""
        self.current = None
        """:type: BaseSourceMeterMeasureBlock"""
        self.resistance = None
        """:type: BaseSourceMeterMeasureBlock"""


class BaseSourceMeterSourceVoltageBlock(BaseEquipmentBlock):
    """
    Base sub block for grouping source specific properties
    """
    CAPABILITY = None

    def __init__(self, interface, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = None
        self._type = None

    @property
    def _source_mode(self):
        """
        **READONLY**
        Private:
        Stores which mode of operation the source meter is in

        :value: - 'VOLT'
                - 'CURR'
        :type: str
        """
        raise NotImplementedError

    @property
    def compliance_current(self):
        """
        Voltage/Current limit

        :value: limit for voltage/current compliance
        :type: float
        """
        raise NotImplementedError

    @compliance_current.setter
    def compliance_current(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def range(self):
        """
        Voltage/Current setpoint range
        :value: setpoint source range
        :type: float
        """
        raise NotImplementedError

    @range.setter
    def range(self, value):
        """"
        :type value: float or str
        """
        raise NotImplementedError

    @property
    def setpoint(self):
        """
        :value: voltage/current level setting in V/A
        :type: float
        """
        raise NotImplementedError

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        """
        raise NotImplementedError


class BaseSourceMeterSourceCurrentBlock(BaseEquipmentBlock):
    """
    Base sub block for grouping source specific properties
    """
    CAPABILITY = None

    def __init__(self, interface, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = None
        self._type = None

    @property
    def _source_mode(self):
        """
        **READONLY**
        Private:
        Stores which mode of operation the source meter is in

        :value: - 'VOLT'
                - 'CURR'
        :type: str
        """
        raise NotImplementedError

    @property
    def compliance_voltage(self):
        """
        Voltage/Current limit

        :value: limit for voltage/current compliance
        :type: float
        """
        raise NotImplementedError

    @compliance_voltage.setter
    def compliance_voltage(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def range(self):
        """
        Voltage/Current setpoint range
        :value: setpoint source range
        :type: float
        """
        raise NotImplementedError

    @range.setter
    def range(self, value):
        """"
        :type value: float or str
        """
        raise NotImplementedError

    @property
    def setpoint(self):
        """
        :value: voltage/current level setting in V/A
        :type: float
        """
        raise NotImplementedError

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        """
        raise NotImplementedError


class BaseSourceMeterMeasureBlock(BaseEquipmentBlock):
    """
    Base sub block for grouping measurement specific properties
    """
    def __init__(self, interface, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._channel_number = None
        self._type = None

    @property
    def range(self):
        """
        Voltage/Current measurement range
        :value: range for voltage/current measurement
        :type: float
        """
        raise NotImplementedError

    @range.setter
    def range(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous voltage/current in V/A
        :type: float
        """
        raise NotImplementedError
