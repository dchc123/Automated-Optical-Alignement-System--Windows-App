"""
| $Revision:: 280255                                   $:  Revision of last commit
| $Author:: mwiendels@SEMNET.DOM                       $:  Author of last commit
| $Date:: 2018-07-30 14:59:47 +0100 (Mon, 30 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from ..KeysightN67XXX.keysight_n670xx import KeysightN670XX


class KeysightN6700B(KeysightN670XX):
    """
    Keysight N6700B 4 channel power supply chassis driver.
    """
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

    @property
    def coupling_state(self):
        """
        State of the output channel coupling

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read(':OUTP:COUP:STAT?'.strip(), dummy_data='0')]

    @coupling_state.setter
    def coupling_state(self, value):
        """
        :type value: str
        :raise ValueError: exception if input is not ENABLE/DISABLE
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write(":OUTP:COUP:STAT %s" % input_dict[value])

    @property
    def output_coupling(self):
        """
        Selects which channels are coupled together and coupling will be enabled if supported.
        If an empty list is specified, they are all uncoupled and if supported coupling will be disabled

        :value: list of channels to couple. ex [1,2]
        :type: list of int
        """
        return super().output_coupling

    @output_coupling.setter
    def output_coupling(self, value):
        """
        :type value: list of int
        :raise ValueError: exception if input is not list of int
        """
        if not value:
            self.coupling_state = 'DISABLE'
        else:
            self.coupling_state = 'ENABLE'
        self._write(":OUTP:COUP:CHAN %s" % ','.join(map(str, value)))
