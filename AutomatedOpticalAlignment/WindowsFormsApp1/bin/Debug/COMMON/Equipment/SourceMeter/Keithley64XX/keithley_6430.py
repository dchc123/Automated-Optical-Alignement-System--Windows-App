"""
| $Revision:: 282440                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-09-18 16:50:44 +0100 (Tue, 18 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keithley2400`

::
    >>> from CLI.Equipment.SourceMeter.Keithley64XX.keithley_6430 import Keithley6430
    >>> smu = Keithley6430('GPIB0::24::INSTR')
    >>> smu.connect()

For Channel block level API:
:py:class:`.Keithley2400Channel`

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
from CLI.Equipment.SourceMeter.Keithley24XX.keithley_24xx import Keithley24XX
from CLI.Equipment.SourceMeter.Keithley24XX.keithley_24xx import Keithley24XXChannel
from CLI.Equipment.SourceMeter.Keithley24XX.keithley_24xx import Keithley24XXSourceParentBlock
from CLI.Equipment.SourceMeter.Keithley24XX.keithley_24xx import Keithley24XXMeasureParentBlock
from CLI.Equipment.SourceMeter.Keithley24XX.keithley_24xx import Keithley24XXSourceVoltageBlock
from CLI.Equipment.SourceMeter.Keithley24XX.keithley_24xx import Keithley24XXSourceCurrentBlock
from CLI.Equipment.SourceMeter.Keithley24XX.keithley_24xx import Keithley24XXMeasureBlock


class Keithley6430(Keithley24XX):
    """
    Keithley 6430 Source Meter
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
        """:type: list of Keithley6430Channel"""

        self.channel.append(Keithley6430Channel(channel_number=1, interface=interface, dummy_mode=dummy_mode))


class Keithley6430Channel(Keithley24XXChannel):
    """
    Keithly6430 Channel Sub Block
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
        self.source = Keithley6430SourceParentBlock(channel_number=channel_number, interface=interface,
                                                    dummy_mode=dummy_mode)
        self.measure = Keithley6430MeasureParentBlock(channel_number=channel_number, interface=interface,
                                                      dummy_mode=dummy_mode)


class Keithley6430SourceParentBlock(Keithley24XXSourceParentBlock):
    """
       Keithly6430 Source Mode Sub Block
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

        self.voltage = Keithley6430SourceVoltageBlock(channel_number=channel_number, type_='voltage',
                                                      interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley6430SourceCurrentBlock(channel_number=channel_number, type_='current',
                                                      interface=interface, dummy_mode=dummy_mode)


class Keithley6430MeasureParentBlock(Keithley24XXMeasureParentBlock):
    """
       Keithly6430 Source Mode Sub Block
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

        self.voltage = Keithley6430MeasureBlock(channel_number=channel_number, type_='voltage',
                                                interface=interface, dummy_mode=dummy_mode)
        self.current = Keithley6430MeasureBlock(channel_number=channel_number, type_='current',
                                                interface=interface, dummy_mode=dummy_mode)
        self.resistance = Keithley6430MeasureBlock(channel_number=channel_number, type_='resistance',
                                                   interface=interface, dummy_mode=dummy_mode)


class Keithley6430SourceVoltageBlock(Keithley24XXSourceVoltageBlock):
    """
    Keithley6430 Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 5e-6, 'warn': 21, 'max': 210}},
                  'current': {'source': {'min': 50e-12, 'warn': 0.0105, 'max': 1.05}}
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


class Keithley6430SourceCurrentBlock(Keithley24XXSourceCurrentBlock):
    """
    Keithley6430 Sub Block
    """
    CAPABILITY = {'voltage': {'source': {'min': 5e-6, 'warn': 21, 'max': 210}},
                  'current': {'source': {'min': 50e-12, 'warn': 0.0105, 'max': 1.05}}
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


class Keithley6430MeasureBlock(Keithley24XXMeasureBlock):
    """
    Keithley6430 Resistance Sub Block
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
