"""
Author:: tbrooks@semtech.com
"""
from COMMON.Equipment.RealtimeScope.KeysightMSOSXXXX.keysight_msosxxxx import KeysightMSOSXXXX, KeysightMSOSXXXXChannel, \
    KeysightMSOSXXXXProbe, KeysightMSOSXXXXTrigger, KeysightMSOSXXXXDigitalChannel, KeysightMSOSXXXXFunction


class KeysightMXRXXXX(KeysightMSOSXXXX):
    """
    Driver for Keysight MXR series scopes is based on S series driver
    """
    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)


class KeysightMXRXXXXChannel(KeysightMSOSXXXXChannel):
    """
    Keysight MXR series Channel driver Based on S series channel driver
    """
    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)


class KeysightMXRXXXXProbe(KeysightMSOSXXXXProbe):
    """
    Keysight MXR series Probe driver Based on S series Probe driver
    """
    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)


class KeysightMXRXXXXTrigger(KeysightMSOSXXXXTrigger):
    """
    Keysight MXR Series trigger driver Based on S series trigger driver
    """
    def __init__(self, interface, dummy_mode, **kwargs):
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)


class KeysightMXRXXXXDigitalChannel(KeysightMSOSXXXXDigitalChannel):
    """
    Keysight MXR series Digital Channel driver Based on S series Digital Channel driver
    """
    def __init__(self, channel_number, interface, dummy_mode, **kwargs):
        super().__init__(channel_number=channel_number, interface=interface, dummy_mode=dummy_mode, **kwargs)


class KeysightMXRXXXXFunction(KeysightMSOSXXXXFunction):
    """
    Function block based on S Series function block
    """

    def __init__(self,  function_number, interface, dummy_mode, **kwargs):
        super().__init__(function_number=function_number, interface=interface, dummy_mode=dummy_mode, **kwargs)
