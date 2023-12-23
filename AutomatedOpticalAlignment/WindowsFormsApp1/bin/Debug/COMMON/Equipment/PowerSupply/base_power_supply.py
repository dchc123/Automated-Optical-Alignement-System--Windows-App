"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Equipment.Base.base_equipment import BaseEquipment
from COMMON.Equipment.Base.base_equipment import BaseEquipmentBlock
from COMMON.Utilities.custom_structures import CustomList


class BasePowerSupply(BaseEquipment):
    """
    Base Power Supply class that all Power Supply should be derived from.
    """
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
        self.channel = CustomList()
        """:type: list of BasePowerSupplyChannel"""

    @property
    def global_output(self):
        """
        Enable state of the global output state. This is a single global setting that
        supersedes all output states of channel class
        :py:attr:`Equipment.base_power_supply.BasePowerSupplyChannel.output`

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        raise NotImplementedError

    @global_output.setter
    def global_output(self, value):
        """
        :type value: str
        """
        raise NotImplementedError


class BasePowerSupplyChannel(BaseEquipmentBlock):
    """
    Base power supply output channel class that all power supply channels should be derived from.
    """
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
        self.voltage = None
        """:type: BasePowerSupplyVoltBlock"""
        self.current = None
        """:type: BasePowerSupplyCurrBlock"""

    @property
    def output(self):
        """
        Enable state of the channel output

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
    def power(self):
        """
        READONLY

        :value: measured power in W
        :type: float
        """
        raise NotImplementedError


class BasePowerSupplyVoltBlock(BaseEquipmentBlock):
    """
    Base sub block for grouping voltage specific properties
    """
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

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous voltage in V
        :type: float
        """
        raise NotImplementedError

    @property
    def protection_level(self):
        """
        :value: voltage protection level
        :type: float
        """
        raise NotImplementedError

    @protection_level.setter
    def protection_level(self, value):
        """
        :type value: float
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


class BasePowerSupplyCurrBlock(BaseEquipmentBlock):
    """
    Base sub block for grouping current specific properties
    """
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

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous current in A
        :type: float
        """
        raise NotImplementedError

    @property
    def setpoint(self):
        """
        :value: current level setting in A
        :type: float
        """
        raise NotImplementedError

    @setpoint.setter
    def setpoint(self, value):
        """
        :type value: float
        """
        raise NotImplementedError

