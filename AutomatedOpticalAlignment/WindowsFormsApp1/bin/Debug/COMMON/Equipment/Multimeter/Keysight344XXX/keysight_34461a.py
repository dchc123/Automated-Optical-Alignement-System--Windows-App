"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.Keysight34461A`
::

    >>> from CLI.Equipment.Multimeter.Keysight344XXX.keysight_34461a import Keysight34461A
    >>> mm = Keysight34461A('TCPIP0::10.14.1.127::inst0::INSTR')
    >>> mm.connect()

For measurement block level API: :py:class:`.Keysight34461AMeasurementBlock`
::

    >>> mm.ac_current.value
    1.0
    >>> mm.dc_voltage.nplc = 5.0
    'Multimeter has changed to manual measurement mode.'
    >>> mm.dc_voltage.nplc
    5.0
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
from .keysight_344xxx import Keysight344XXX
from .keysight_344xxx import Keysight344XXXMeasurementBlock


class Keysight34461A(Keysight344XXX):
    """
    Keysight 34461A multimeter driver
    """
    CAPABILITY = {'current_ac_range': {'min': 0, 'max': 10},
                  'current_dc_range': {'min': 0, 'max': 10},
                  'resistance_2w_range': {'min': 0, 'max': 100000000},
                  'resistance_4w_range': {'min': 0, 'max': 100000000},
                  'volt_ac_range': {'min': 0, 'max': 750},
                  'volt_dc_range': {'min': 0, 'max': 1000}}

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
        self.current_ac = Keysight34461AMeasurementBlock(type_="CURRent", meas_type_=":AC",
                                                         meas_range_=self.CAPABILITY['current_ac_range'],
                                                         interface=interface, dummy_mode=dummy_mode)
        self.voltage_ac = Keysight34461AMeasurementBlock(type_="VOLTage", meas_type_=":AC",
                                                         meas_range_=self.CAPABILITY['volt_ac_range'],
                                                         interface=interface, dummy_mode=dummy_mode)
        self.current_dc = Keysight34461AMeasurementBlock(type_="CURRent", meas_type_=":DC",
                                                         meas_range_=self.CAPABILITY['current_dc_range'],
                                                         interface=interface, dummy_mode=dummy_mode)
        self.voltage_dc = Keysight34461AMeasurementBlock(type_="VOLTage", meas_type_=":DC",
                                                         meas_range_=self.CAPABILITY['volt_dc_range'],
                                                         interface=interface, dummy_mode=dummy_mode)
        self.resistance_2w = Keysight34461AMeasurementBlock(type_="RESistance", meas_type_="",
                                                            meas_range_= self.CAPABILITY['resistance_2w_range'],
                                                            interface=interface, dummy_mode=dummy_mode)
        self.resistance_4w = Keysight34461AMeasurementBlock(type_="FRESistance", meas_type_="",
                                                            meas_range_=self.CAPABILITY['resistance_4w_range'],
                                                            interface=interface, dummy_mode=dummy_mode)


class Keysight34461AMeasurementBlock(Keysight344XXXMeasurementBlock):
    """
    Keysight 34461A multimeter Measurement Block
    """
    CAPABILITY = {'nplc_values': [0.02, 0.2, 1, 10, 100]}

    def __init__(self, type_, meas_type_, meas_range_, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param type_: measurement type, also prefix to be used for SCPI commands
        :type type_: str
        :param meas_type_: select between AC/DC for voltage and current (resistance is blank)
        :type meas_type_: str
        :param meas_range_: minimum ans maximum values for range
        :type meas_range_: dict of str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(type_=type_, meas_type_=meas_type_, meas_range_=meas_range_,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def range(self):
        """
        Equipment will select best range for value provided.
        Getting range will return high end of currently active measurement range.

        :value: measurement range (V,A,Ohm)
        :type: float
        :raise ValueError: Exception if range value is invalid
        """
        return super().range

    @range.setter
    def range(self, value):
        """
        :type value: float
        :raise ValueError: Exception if range value is invalid
        """
        if self._type == 'CURRent':
            if not (self._range_min <= value <= self._range_max):
                raise ValueError("%s range is invalid. See valid entries/range.(min:%s|max:%s)"
                                 % (self._type.capitalize(), self._range_min, self._range_max))
            else:
                if value < 3:
                    self._write("CURRent%s:TERMinals 3" % self._meas_type)
                    self._write("CURRent%s:RANGe %s" % (self._meas_type, value))
                    self.logger.info(
                        'For range < 3A, cables need to be connected to 3A terminal.')
                elif value >= 3:
                    self._write("CURRent%s:TERMinals 10" % self._meas_type)
                    self.logger.info('For range > 3A, cables need to be connected to 10A terminal.'
                                     'Range is forced to 10A range.')
            self._meas_mode = 'MANUAL'
            self.logger.info('Multimeter has changed to manual measurement mode.')
        else:
            super(Keysight34461AMeasurementBlock, self.__class__).range.fset(self, value)
