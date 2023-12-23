"""
| $Revision:: 280883                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-08-08 13:53:32 +0100 (Wed, 08 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.custom_exceptions import NotSupportedError
from ..base_multimeter import BaseMultimeter
from ..base_multimeter import BaseMultimeterMeasurementBlock


class Keysight344XXX(BaseMultimeter):
    """
    Keysight 344XXX common multimeter driver
    """

    CAPABILITY = {'current_ac_range': {'min': None, 'max': None},
                  'current_dc_range': {'min': None, 'max': None},
                  'resistance_2w_range': {'min': None, 'max': None},
                  'resistance_4w_range': {'min': None, 'max': None},
                  'volt_ac_range': {'min': None, 'max': None},
                  'volt_dc_range': {'min': None, 'max': None}}

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
        self.current_ac = Keysight344XXXMeasurementBlock(type_="CURRent", meas_type_=":AC",
                                                         meas_range_=self.CAPABILITY['current_ac_range'],
                                                         interface=interface, dummy_mode=dummy_mode)
        self.voltage_ac = Keysight344XXXMeasurementBlock(type_="VOLTage", meas_type_=":AC",
                                                         meas_range_=self.CAPABILITY['volt_ac_range'],
                                                         interface=interface, dummy_mode=dummy_mode)
        self.current_dc = Keysight344XXXMeasurementBlock(type_="CURRent", meas_type_=":DC",
                                                         meas_range_=self.CAPABILITY['current_dc_range'],
                                                         interface=interface, dummy_mode=dummy_mode)
        self.voltage_dc = Keysight344XXXMeasurementBlock(type_="VOLTage", meas_type_=":DC",
                                                         meas_range_=self.CAPABILITY['volt_dc_range'],
                                                         interface=interface, dummy_mode=dummy_mode)
        self.resistance_2w = Keysight344XXXMeasurementBlock(type_="RESistance", meas_type_="",
                                                            meas_range_= self.CAPABILITY['resistance_2w_range'],
                                                            interface=interface, dummy_mode=dummy_mode)
        self.resistance_4w = Keysight344XXXMeasurementBlock(type_="FRESistance", meas_type_="",
                                                            meas_range_=self.CAPABILITY['resistance_4w_range'],
                                                            interface=interface, dummy_mode=dummy_mode)


class Keysight344XXXMeasurementBlock(BaseMultimeterMeasurementBlock):
    """
    Keysight 344XXX common multimeter Measurement Block
    """
    CAPABILITY = {'nplc_values': [None]}

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
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._type = type_
        self._meas_type = meas_type_
        self._meas_mode = 'AUTO'
        self._range_min = meas_range_['min']
        self._range_max = meas_range_['max']

    @property
    def value(self):
        """
        **READONLY**

        :value: measured instantaneous voltage/current/resistance (V,A,Ohm)
        :type: float
        """
        if self._meas_mode == 'AUTO':
            return float(self._read("MEAS:%s%s?" % (self._type, self._meas_type),
                                    type_='stb_poll_sync'))
        else:
            manual_range = self.range
            manual_resolution = self._resolution
            return float(self._read("MEAS:%s%s? %s,%s" %
                                    (self._type, self._meas_type, manual_range, manual_resolution),
                                    type_='stb_poll_sync'))

    @property
    def meas_mode(self):
        """
        Measurement mode

        :value: - 'AUTO'
                - 'MANUAL'
        :type: str
        :raise ValueError: Exception if value is 'AUTO' or 'MANUAL'

        """
        return self._meas_mode

    @meas_mode.setter
    def meas_mode(self, value):
        """
        :type value: str
        :raise ValueError: Exception if value is 'AUTO' or 'MANUAL'
        """
        value = value.upper()
        input_list = ['AUTO', 'MANUAL']
        if value not in input_list:
            raise ValueError('Please specify either %s' % input_list)
        else:
            self._meas_mode = value
            self.logger.info('Multimeter has changed to {} measurement mode.'
                             .format(value.lower()))

    @property
    def nplc(self):
        """
        :value: Power line cycles per integration
        :type: float
        :raise ValueError: Exception if value is not valid entry.
        :raise NotSupportedError: Exception when trying to use NPLC for AC measurements
        """
        if self._meas_type == ':AC':
            raise NotSupportedError('AC measurements do not support nplc setting.')
        else:
            return float(self._read("%s%s:NPLCycles?" % (self._type, self._meas_type)))

    @nplc.setter
    def nplc(self, value):
        """
        :type value: float
        :raise ValueError: Exception if nplc value is not a valid entry.
        :raise NotSupportedError: Exception when trying to use NPLC for AC measurements
        """
        nplc_values = self.CAPABILITY['nplc_values']

        if value not in nplc_values:
            raise ValueError('Invalid nplc setting. Select one of the following values : %s'
                             % nplc_values)
        else:
            if self._meas_type == ':AC':
                raise NotSupportedError('AC measurements do not support nplc setting.')
            else:
                self._write("%s%s:NPLCycles %s" % (self._type, self._meas_type, value))
                self._meas_mode = 'MANUAL'
                self.logger.info('Multimeter has changed to manual measurement mode.')

    @property
    def range(self):
        """
        Equipment will select best range for value provided.
        Getting range will return high end of currently active measurement range.

        :value: measurement range (V,A,Ohm)
        :type: float
        :raise ValueError: Exception if range value is invalid
        """
        return float(self._read("%s%s:RANGe?" % (self._type, self._meas_type)))

    @range.setter
    def range(self, value):
        """
        :type value: float
        :raise ValueError: Exception if range value is invalid
        """
        if not (self._range_min <= value <= self._range_max):
            raise ValueError("%s range is invalid. See valid entries/range.(min:%s|max:%s)"
                             % (self._type.capitalize(), self._range_min, self._range_max))

        self._write("%s%s:RANGe %s" % (self._type, self._meas_type, value))
        self._meas_mode = 'MANUAL'
        self.logger.info('Multimeter has changed to manual measurement mode.')

    @property
    def _resolution(self):
        """
        **READONLY**

        :value: measurement resolution
        :type: float
        """
        return float(self._read("%s%s:RESolution?" % (self._type, self._meas_type)))
