"""
| $Revision:: 282440                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-09-18 16:50:44 +0100 (Tue, 18 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keithley2612B`

::
    >>> from CLI.Equipment.SourceMeter.Keithley26XX.keithley_2612b import Keithley2612B
    >>> smu = Keithley2612B('GPIB0::24::INSTR')
    >>> smu.connect()

For Channel block level API:
:py:class:`.Keithley2612BChannel`

::
    >>> smu.channel[1].terminal_select = "FRONT"
    >>> smu.channel[1].remote_sensing = "ENABLE"
    >>> smu.channel[1].output = "ENABLE"

    >>> smu.channel[1].source.voltage.setpoint = 3.3
    >>> smu.channel[1].source.current.compliance_limit = 0.5
    >>> smu.channel[1].measure.current.range = "AUTO"
    >>> smu.channel[1].measure.current.range = 100e-3
    >>> smu.channel[1].measure.current.value
    0.095
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_structures import CustomList
from .keithley_26xx import Keithley26XX
from .keithley_26xx import Keithley26XXChannel
from .keithley_26xx import Keithley26XXSourceParentBlock
from .keithley_26xx import Keithley26XXMeasureParentBlock
from .keithley_26xx import Keithley26XXSourceVoltageBlock
from .keithley_26xx import Keithley26XXSourceCurrentBlock
from .keithley_26xx import Keithley26XXMeasureBlock


class Keithley2612B(Keithley26XX):
    """
    Keithley 2612B Source Meter
    """

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
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
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.channel = CustomList()
        """:type: list of Keithley2612BChannel"""

        self.channel.append(Keithley2612BChannel(channel_number=1, interface=interface, dummy_mode=dummy_mode))


class Keithley2612BChannel(Keithley26XXChannel):
    """
    Keithly2612B Channel Sub Block
    """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)

        self._channel_number = channel_number
        self.source = Keithley2612BSourceParentBlock(channel_number=channel_number, interface=interface,
                                                     dummy_mode=dummy_mode)
        self.measure = Keithley2612BMeasureParentBlock(channel_number=channel_number, interface=interface,
                                                       dummy_mode=dummy_mode)


class Keithley2612BSourceParentBlock(Keithley26XXSourceParentBlock):
    """
       Keithly2612B Source Mode Sub Block
       """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)

        self.voltage = Keithley2612BSourceVoltageBlock(channel_number=channel_number, type_='voltage',
                                                       interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley2612BSourceCurrentBlock(channel_number=channel_number, type_='current',
                                                       interface=interface, dummy_mode=dummy_mode)


class Keithley2612BMeasureParentBlock(Keithley26XXMeasureParentBlock):
    """
       Keithly2400 Source Mode Sub Block
       """

    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: Any
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)

        self.voltage = Keithley2612BMeasureBlock(channel_number=channel_number, type_='voltage',
                                                 interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley2612BMeasureBlock(channel_number=channel_number, type_='current',
                                                 interface=interface, dummy_mode=dummy_mode)
        self.resistance = Keithley2612BMeasureBlock(channel_number=channel_number, type_='resistance',
                                                    interface=interface, dummy_mode=dummy_mode)


class Keithley2612BSourceVoltageBlock(Keithley26XXSourceVoltageBlock):
    """
    Keithley2612B Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 1e-6, 'warn': 20, 'max': 202}},
                  'current': {'source': {'min': 1e-12, 'warn': 0.101, 'max': 1.515}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param current_type: select between AC/DC
        :type current_type: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, type_=type_,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._type = type_


class Keithley2612BSourceCurrentBlock(Keithley26XXSourceCurrentBlock):
    """
    Keithley2612B Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 1e-6, 'warn': 20, 'max': 202}},
                  'current': {'source': {'min': 1e-12, 'warn': 0.101, 'max': 1.515}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param current_type: select between AC/DC
        :type current_type: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, type_=type_,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._type = type_


class Keithley2612BMeasureBlock(Keithley26XXMeasureBlock):
    """
    Keithley2612B Resistance Sub Block
    """
    CAPABILITY = {'voltage': {'measure': {'min': 1e-6, 'max': 204}},
                  'current': {'measure': {'min': 1e-12, 'max': 1.53}},
                  'resistance': {'measure': {'min': 100e-6, 'max': 211e6}}
                  }

    def __init__(self, channel_number, type_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param current_type: select between AC/DC
        :type current_type: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(channel_number=channel_number, type_=type_,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._type = type_
