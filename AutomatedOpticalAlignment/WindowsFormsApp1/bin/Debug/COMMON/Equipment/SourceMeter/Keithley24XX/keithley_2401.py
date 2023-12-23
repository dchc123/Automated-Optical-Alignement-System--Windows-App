"""
| $Revision:: 283320                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-11-01 17:16:36 +0000 (Thu, 01 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keithley2401`

::
    >>> from CLI.Equipment.SourceMeter.Keithley24XX.keithley_2401 import Keithley2401
    >>> smu = Keithley2401('GPIB0::24::INSTR')
    >>> smu.connect()

For Channel block level API:
:py:class:`.Keithley2401Channel`

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


class Keithley2401(Keithley24XX):
    """
    Keithley 2401 Source Meter
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
        """:type: list of Keithley2401Channel"""

        self.channel.append(Keithley2401Channel(channel_number=1, interface=interface, dummy_mode=dummy_mode))


class Keithley2401Channel(Keithley24XXChannel):
    """
    Keithly2400 Channel Sub Block
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
        self.source = Keithley2401SourceParentBlock(channel_number=channel_number, interface=interface,
                                                    dummy_mode=dummy_mode)
        self.measure = Keithley2401MeasureParentBlock(channel_number=channel_number, interface=interface,
                                                      dummy_mode=dummy_mode)


class Keithley2401SourceParentBlock(Keithley24XXSourceParentBlock):
    """
   Keithly2401 Source Mode Sub Block
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

        self.voltage = Keithley2401SourceVoltageBlock(channel_number=channel_number, type_='voltage',
                                                      interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley2401SourceCurrentBlock(channel_number=channel_number, type_='current',
                                                      interface=interface, dummy_mode=dummy_mode)


class Keithley2401MeasureParentBlock(Keithley24XXMeasureParentBlock):
    """
       Keithly2401 Source Mode Sub Block
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

        self.voltage = Keithley2401MeasureBlock(channel_number=channel_number, type_='voltage',
                                                interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley2401MeasureBlock(channel_number=channel_number, type_='current',
                                                interface=interface, dummy_mode=dummy_mode)
        self.resistance = Keithley2401MeasureBlock(channel_number=channel_number, type_='resistance',
                                                   interface=interface, dummy_mode=dummy_mode)


class Keithley2401SourceVoltageBlock(Keithley24XXSourceVoltageBlock):
    """
    Keithley2401 Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 5e-6, 'warn': 21, 'max': 210}},
                  'current': {'source': {'min': 50e-12, 'warn': 0.105, 'max': 1.05}}
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


class Keithley2401SourceCurrentBlock(Keithley24XXSourceCurrentBlock):
    """
    Keithley2401 Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 5e-6, 'warn': 21, 'max': 210}},
                  'current': {'source': {'min': 50e-12, 'warn': 0.105, 'max': 1.05}}
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


class Keithley2401MeasureBlock(Keithley24XXMeasureBlock):
    """
    Keithley2401 Resistance Sub Block
    """
    CAPABILITY = {'voltage': {'measure': {'min': 1e-6, 'max': 211}},
                  'current': {'measure': {'min': 10e-12, 'max': 1.055}},
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
