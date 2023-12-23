"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keithley2010`
::

    >>> from CLI.Equipment.Multimeter.Keithley20XX.keithley_2010 import Keithley2010
    >>> mm = Keithley2010('GPIB1::7::INSTR')
    >>> mm.connect()

For measurement block level API: :py:class:`.Keithley2010AMeasurementBlock`
::

    >>> mm.ac_current.value
    1.0
    >>> mm.resistance_4w.range = 150
    'Multimeter has changed to manual measurement mode.'
    >>> mm.resistance_4w.value
    145.5
    >>> mm.resistance_4w.meas_mode
    'MANUAL'
    >>> mm.resistance_4w.meas_mode = 'AUTO'
    >>> mm.dc_current.value
    0.4125
    >>> mm.voltage_dc.range = 1
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from .keithley_20xx import Keithley20XX
from .keithley_20xx import Keithley20XXMeasurementBlock


class Keithley2010(Keithley20XX):
    """
    Keithley 2010 multimeter driver
    """

    CAPABILITY = {'current_ac_range': {'min': 0, 'max': 3.1},
                  'current_dc_range': {'min': 0, 'max': 3.1},
                  'resistance_2w_range': {'min': 0, 'max': 120000000},
                  'resistance_4w_range': {'min': 0, 'max': 120000000},
                  'volt_ac_range': {'min': 0, 'max': 757.5},
                  'volt_dc_range': {'min': 0, 'max': 1010}}

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param meas_range_: minimum ans maximum values for range
        :type meas_range_: dict of str
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
        self.current_ac = Keithley2010AMeasurementBlock(type_="CURRent", meas_type_=":AC",
                                                        meas_range_=self.CAPABILITY['current_ac_range'],
                                                        interface=interface, dummy_mode=dummy_mode)
        self.voltage_ac = Keithley2010AMeasurementBlock(type_="VOLTage", meas_type_=":AC",
                                                        meas_range_=self.CAPABILITY['volt_ac_range'],
                                                        interface=interface, dummy_mode=dummy_mode)
        self.current_dc = Keithley2010AMeasurementBlock(type_="CURRent", meas_type_=":DC",
                                                        meas_range_=self.CAPABILITY['current_dc_range'],
                                                        interface=interface, dummy_mode=dummy_mode)
        self.voltage_dc = Keithley2010AMeasurementBlock(type_="VOLTage", meas_type_=":DC",
                                                        meas_range_=self.CAPABILITY['volt_dc_range'],
                                                        interface=interface, dummy_mode=dummy_mode)
        self.resistance_2w = Keithley2010AMeasurementBlock(type_="RESistance", meas_type_="",
                                                           meas_range_= self.CAPABILITY['resistance_2w_range'],
                                                           interface=interface, dummy_mode=dummy_mode)
        self.resistance_4w = Keithley2010AMeasurementBlock(type_="FRESistance", meas_type_="",
                                                           meas_range_=self.CAPABILITY['resistance_4w_range'],
                                                           interface=interface, dummy_mode=dummy_mode)


class Keithley2010AMeasurementBlock(Keithley20XXMeasurementBlock):
    """
    Keithley 2010 multimeter Measurement Block
    """
    CAPABILITY = {'nplc_values': {'min': 0.01, 'max': 10}}

    def __init__(self, type_, meas_type_, meas_range_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param meas_type_: select between AC/DC for voltage and current (resistance is blank)
        :type meas_type_: str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(type_=type_, meas_type_=meas_type_, meas_range_=meas_range_,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

