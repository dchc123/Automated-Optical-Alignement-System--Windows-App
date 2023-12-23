from __future__ import absolute_import, division, print_function, unicode_literals # for python 3 compatibility

from gpiozero import OutputDevice, DigitalInputDevice

PINS = {           # hedder pin number
    'BEN':7,       # 26
    'TX_DIS':18,   # 12
    'TX_FAULT': 17 # 13
    }

class BEN(OutputDevice):
    """
    extends :class:`OutpuDevice` and represents BEN on and off

    :param int pin:
        The GPIO pin which the BEN is attached to. See :ref:`pin-numbering` for
        valid pin numbers.

    :param bool active_high:
        If ``True`` (the default), BEN will operate normally with the
        circuit described above. If ``False`` you should wire the cathode to
        the GPIO pin, and the anode to a 3V3 pin (via a limiting resistor).

    :param bool initial_value:
        If ``False`` (the default), BEN will be off initially.  If
        ``None``, BEN will be left in whatever state the pin is found in
        when configured for output (warning: this can be on).  If ``True``, BEN
        will be switched on initially.


    """
    def __init__(
            self, pin=PINS['BEN'], active_high=True, initial_value=False,
            pin_factory=None):
        super(BEN, self).__init__(pin, active_high, initial_value, pin_factory=pin_factory)

class TX_DIS(OutputDevice):
    """
    extends :class:`OutpuDevice` and represents TX_DIS on and off

    :param int pin:
        The GPIO pin which the TX_DIS is attached to. See :ref:`pin-numbering` for
        valid pin numbers. defaults to header pin number 12 gpio pin 18

    :param bool active_high:
        If ``True`` (the default), TX_DIS will operate normally with the
        circuit described above. If ``False`` you should wire the cathode to
        the GPIO pin, and the anode to a 3V3 pin (via a limiting resistor).

    :param bool initial_value:
        If ``False`` (the default), TX_DIS will be off initially.  If
        ``None``, TX_DIS will be left in whatever state the pin is found in
        when configured for output (warning: this can be on).  If ``True``, TX_DIS
        will be switched on initially.


    """
    def __init__(
            self, pin=PINS['TX_DIS'], active_high=True, initial_value=False,
            pin_factory=None):
        super(TX_DIS, self).__init__(pin, active_high, initial_value, pin_factory=pin_factory)

class TX_FAULT(DigitalInputDevice):
    """Extends :class:`DigitalInputDevice` and represents TX_FAULT."""
    def __init__(self, pin=PINS['TX_FAULT'], active_high=True, pin_factory=None, pull_up=True):
        super(TX_FAULT, self).__init__(pin, pull_up, pin_factory=pin_factory)


if __name__ == "__main__":
    import time, datetime
    ben = BEN()
    tx_dis = TX_DIS(initial_value=False)
    tx_sd = DigitalInputDevice(5) # pin 29
    hi_time = 0
    def say_hello():
        hi_time = datetime.datetime.now()
        print("tx_sd went high at %s" % hi_time)
    tx_sd.when_activated = say_hello

    ben_on_time = datetime.datetime.now()
    print("BEN on at %s" % (ben_on_time))
    # turn ben on
    ben.on()
    time.sleep(1)
    # turn ben off
    print("ben on to tx_sd high = %s" % (hi_time-ben_on_time))
    ben.off()
    tx_dis.on()
    time.sleep(0.001)
    tx_dis.off()
    time.sleep(1)
