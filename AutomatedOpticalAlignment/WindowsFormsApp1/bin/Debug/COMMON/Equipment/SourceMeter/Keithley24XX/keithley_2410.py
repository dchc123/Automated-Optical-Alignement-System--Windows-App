"""
| $Revision:: 283320                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-11-01 17:16:36 +0000 (Thu, 01 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keithley2410`

::
    >>> from CLI.Equipment.SourceMeter.Keithley24XX.keithley_2410 import Keithley2410
    >>> smu = Keithley2410('GPIB0::24::INSTR')
    >>> smu.connect()

For Channel block level API:
:py:class:`.Keithley2410Channel`

::
    >>> smu.channel[1].terminal_select = "FRONT"
    >>> smu.channel[1].remote_sensing = "ENABLE"
    >>> smu.channel[1].output = "ENABLE"

    >>> smu.channel[1].source.voltage.setpoint = 3.3
    >>> smu.channel[1].source.current.compliance_voltage = 0.5
    >>> smu.channel[1].measure.current.range = "AUTO"
    >>> smu.channel[1].measure.current.range = 100e-3
    >>> smu.channel[1].measure.current.value
    0.095
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Utilities.custom_structures import CustomList
from .keithley_24xx import Keithley24XX
from .keithley_24xx import Keithley24XXChannel
from .keithley_24xx import Keithley24XXSourceParentBlock
from .keithley_24xx import Keithley24XXMeasureParentBlock
from .keithley_24xx import Keithley24XXSourceVoltageBlock
from .keithley_24xx import Keithley24XXSourceCurrentBlock
from .keithley_24xx import Keithley24XXMeasureBlock


class Keithley2410(Keithley24XX):
    """
    Keithley 2410 Source Meter
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
        """:type: list of Keithley2410Channel"""

        self.channel.append(Keithley2410Channel(channel_number=1, interface=interface, dummy_mode=dummy_mode))


class Keithley2410Channel(Keithley24XXChannel):
    """
    Keithly2410 Channel Sub Block
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
        self.source = Keithley2410SourceParentBlock(channel_number=channel_number, interface=interface,
                                                    dummy_mode=dummy_mode)
        self.measure = Keithley2410MeasureParentBlock(channel_number=channel_number, interface=interface,
                                                      dummy_mode=dummy_mode)


class Keithley2410SourceParentBlock(Keithley24XXSourceParentBlock):
    """
       Keithly2410 Source Mode Sub Block
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

        self.voltage = Keithley2410SourceVoltageBlock(channel_number=channel_number, type_='voltage',
                                                      interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley2410SourceCurrentBlock(channel_number=channel_number, type_='current',
                                                      interface=interface, dummy_mode=dummy_mode)


class Keithley2410MeasureParentBlock(Keithley24XXMeasureParentBlock):
    """
       Keithly2410 Source Mode Sub Block
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

        self.voltage = Keithley2410MeasureBlock(channel_number=channel_number, type_='voltage',
                                                interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley2410MeasureBlock(channel_number=channel_number, type_='current',
                                                interface=interface, dummy_mode=dummy_mode)
        self.resistance = Keithley2410MeasureBlock(channel_number=channel_number, type_='resistance',
                                                   interface=interface, dummy_mode=dummy_mode)


class Keithley2410SourceVoltageBlock(Keithley24XXSourceVoltageBlock):
    """
    Keithley2410 Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 5e-6, 'warn': 21, 'max': 1100}},
                  'current': {'source': {'min': 50e-12, 'warn': 0.021, 'max': 1.05}}
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


class Keithley2410SourceCurrentBlock(Keithley24XXSourceCurrentBlock):
    """
    Keithley2410 Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 5e-6, 'warn': 21, 'max': 1100}},
                  'current': {'source': {'min': 50e-12, 'warn': 0.021, 'max': 1.05}}
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


class Keithley2410MeasureBlock(Keithley24XXMeasureBlock):
    """
    Keithley2410 Resistance Sub Block
    """
    CAPABILITY = {'voltage': {'measure': {'min': 1e-6, 'max': 1100}},
                  'current': {'measure': {'min': 10e-12, 'max': 1.05}},
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
