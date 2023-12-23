"""
Arroyo 5300 TEC controller
# address = ASRL1::INSTR for COM1 on Windows
::
>>> from COMMON.Equipment.TemperatureUnit.Arroyo53XX.arroyo_5300 import Arroyo5300
>>> tu = Arroyo5300(address="ASRL/dev/ttyUSB0::INSTR")
>>> tu.connect()
>>> tu.thermocouple_temperature
25.0
>>> # tu.setpoint = 40
>>> tu.setpoint
40.0
>>> tu.output
'DISABLE'
>>> tu.pid
[1.2, 0.0001, 0.0]
>>> tu.pid = [1.2, 0.0001, 0.0]
>>> # tu.output = "ENABLE"
>>> # tu.set_and_soak(setpoint=40, soak=5, temp_error=2.0)

"""


from COMMON.Equipment.TemperatureUnit.Arroyo53XX.arroyo_53xx import Arroyo53XX
from COMMON.Interfaces.VISA.cli_visa import CLIVISA


class Arroyo5300(Arroyo53XX):
    """
    Driver for Arroyo 5300 TEC controller
    """
    CAPABILITY = {'temperature': {'min': -99, 'max': 250}}

    def __init__(self, address, temp_limit='high', interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param temp_limit: the type of victim
        :type temp_limit: str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode,
                         temp_limit=temp_limit, **kwargs)
