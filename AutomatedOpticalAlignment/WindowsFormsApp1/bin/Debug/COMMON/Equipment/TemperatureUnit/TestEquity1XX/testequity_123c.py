"""
| $Revision:: 282825                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-10-12 21:24:43 +0100 (Fri, 12 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`Equipment.TemperatureUnit.TestEquity1XX.testequity_123c`
::

    >>> from CLI.Equipment.TemperatureUnit.TestEquity1XX.testequity_123c import TestEquity123C
    >>> tu = TestEquity123C('GPIB1::23::INSTR')
    >>> tu.connect()
    >>> tu.unit_temperature
    25.0
    >>> tu.setpoint = 100
    >>> tu.setpoint
    100.0
"""
from .testequity_1xx import TestEquity10X
from COMMON.Interfaces.VISA.cli_visa import CLIVISA


class TestEquity123C(TestEquity10X):
    """
    Driver for Test Equity 123C
    """

    CAPABILITY = {'temperature': {'min': -68, 'max': 175}}

    def __init__(self, address, temp_limit='high', f4t=False, interface=None, dummy_mode=False, **kwargs):
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
        super().__init__(address=address, f4t=f4t, interface=interface, dummy_mode=dummy_mode,
                         temp_limit=temp_limit, **kwargs)

