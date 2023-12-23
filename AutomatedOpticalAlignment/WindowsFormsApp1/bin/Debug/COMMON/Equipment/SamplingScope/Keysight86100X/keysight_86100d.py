"""
| $Revision:: 279062                                   $:  Revision of last commit
| $Author:: ael-khouly@SEMNET.DOM                      $:  Author of last commit
| $Date:: 2018-07-10 19:29:10 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API:
See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86100x.Keysight86100X`
::

    >>> from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x import Keysight86100X
    >>> scope = Keysight86100X('GPIB1::23::INSTR')
    >>> scope.connect()
    >>> scope.auto_scale()
    >>> scope.mode
    'OSC'
    >>> scope.mode = 'EYE'

For acquisition limits API:
See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86100x.Keysight86100XLimit`
::

    >>> scope.limit.set_limit(number=10000, limit_type='SAMPLE')
    >>> scope.limit.state
    'DISABLE'
    >>> scope.limit.state = 'ENABLE'

For trigger API:
See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86100x.Keysight86100XTrigger`
::

    >>> scope.trigger.mode = 'EDGE'
    >>> scope.trigger.level
    2e-2
    >>> scope.trigger.level = 2.4e-3
    >>> scope.trigger.pattern_lock = 'ENABLE'

For timebase API:
See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86100x.Keysight86100XTimebase`
::

    >>> scope.timebase.reference = 'LEFT'
    >>> scope.timebase.units = 'SECONDS'
    >>> scope.timebase.position
    1.72e-10
    >>> scope.timebase.position = 2e-10
    >>> scope.timebase.scale = 17e-12

For Precision Timebase API:
See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86107a.Keysight86107A`
::

    >>> scope.precision_timebase.state = 'ENABLE'
    >>> scope.precision_timebase.ref_clock_frequency
    100000.0
    >>> scope.precision_timebase.ref_clock_frequency = 1e7
    >>> scope.precision_timebase.reset_time_reference()

For Internal Precision Timebase API:
See :py:class:`Equipment.SamplingScope.Keysight86100X.keysight_86100d.Keysight86100D`
::

    >>> scope.int_precision_timebase.state = 'ENABLE'
    >>> scope.int_precision_timebase.ref_clock_frequency
    100000.0
    >>> scope.int_precision_timebase.ref_clock_frequency = 1e7
    >>> scope.int_precision_timebase.reset_time_reference()

For Electrical Modules API:
See :py:mod:`Equipment.SamplingScope.Keysight86100X.Modules.keysight_electrical_module`
::

    >>> scope.elec[1].mode
    'SINGLE'
    >>> scope.elec[1].mode = 'DIFFERENTIAL'
    # Note that you can access channels by an int index or by their display names
    >>> scope.elec['1A'].mode
    'DIFFERENTIAL'
    >>> scope.mode = 'OSC'
    >>> scope.elec[1].mode = 'SINGLE'
    >>> scope.elec[1].osc.avg
    0.5
    >>> scope.mode = 'EYE'
    >>> scope.elec[1].eye.amplitude
    1.0
    >>> scope.elec[1].mask_test.load('MASK_PATH')
    >>> scope.elec[1].histogram[1].state = 'ENABLE'
    >>> scope.elec[1].histogram[1].placement = 'TOP'

For Optical Modules API:
See :py:mod:`Equipment.SamplingScope.Keysight86100X.Modules.keysight_optical_module`
::

    >>> scope.mode = 'OSC'
    >>> scope.opt[1].osc.avg
    0.5
    >>> scope.mode = 'EYE'
    >>> scope.opt[1].eye.amplitude
    1.0
    >>> scope.opt[1].mask_test.load('MASK_PATH')
    >>> scope.opt[1].histogram[1].state = 'ENABLE'
    >>> scope.opt[1].histogram[1].placement = 'TOP'
"""
from CLI.Interfaces.VISA.cli_visa import CLIVISA
from CLI.Equipment.SamplingScope.Keysight86100X.keysight_86100x import Keysight86100X


class Keysight86100D(Keysight86100X):
    """
    Keysight86100D Scope driver
    """
    def __init__(self, address, chassis_ip=None, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._chassis_ip = chassis_ip

    def connect(self):
        super().connect()
        if self._chassis_ip:
            self._write('RDCA:CONN:MODE COMP')
            self._write('RDCA:CONN:HOST "{}"'.format(self._chassis_ip))
            self._write('RDCA:CONNect "{}"'.format(self._chassis_ip))
            self._configure()

    def disconnect(self):
        super().disconnect()
        if self._chassis_ip:
            self._write('RDCA:DISConnect')

