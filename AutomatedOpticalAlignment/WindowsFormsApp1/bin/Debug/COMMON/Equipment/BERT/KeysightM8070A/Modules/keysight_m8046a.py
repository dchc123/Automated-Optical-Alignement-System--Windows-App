"""
| $Revision:: 282004                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-08-30 14:55:09 +0100 (Thu, 30 Aug 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from .keysight_m80xxx_ed import KeysightM80XXXED


class KeysightM8046A(KeysightM80XXXED):
    """
    Keysight BERT Error Detector channel class that all ED channels should be derived from
    """
    def __init__(self, module_id, channel_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param module_id: module identification string
        :type module_id: int
        :param channel_number: number targeting channel
        :type channel_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(module_id=module_id, channel_number=channel_number,
                         interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def equalization(self):
        """
        Current equalizer setting. '0' = No Equalization '55' corresponds to 5.1dB of
        trace loss nyquist for fBaud = 32GHz according to the datasheet for 26GBaud PAM4.

        :value: Current equalizer setting
        :type: int
        :raise ValueError: exception if value is not between 0 and 55
        """
        return int(float(self._read(":INPut:EQUalization:PRESet:Level? 'M{}.DataIn'".format(self._module_id))))

    @equalization.setter
    def equalization(self, value):
        """
        :type value: int
        :raise ValueError: exception if value is not between 0 and 55
        """
        # User manual states range to be 0-120. 0-55 is for PAM4 signals. If this setting is eventually needed for NRZ,
        # code can be updated but it is currently unlikely to happen.
        if not (0 <= value <= 55):
            raise ValueError("The equalization setting must be between 0 and 55.")
        self._write(":INPut:EQUalization:PRESet:LEVel 'M{}.DataIn', {}".format(self._module_id, value))
