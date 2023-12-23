"""
| $Revision:: 279026                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-10 16:20:17 +0100 (Tue, 10 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from .base_laser import BaseLaser


class BaseTunableLaser(BaseLaser):
    """
    Base Tunable Laser class that all Tunable Lasers should be derived from.
    """
    def __init__(self, address, interface, dummy_mode, **kwargs):
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
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def wavelength(self):
        """
        Wavelength of output signal

        :value: wavelength (nm)
        :type: float
        """
        raise NotImplementedError

    @wavelength.setter
    def wavelength(self, value):
        """
        :type value: float
        """
        raise NotImplementedError
