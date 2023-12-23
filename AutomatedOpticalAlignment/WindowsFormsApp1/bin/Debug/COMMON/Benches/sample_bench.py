from CLI.Benches.base_bench import BaseBench
from CLI.Devices.GN2104X.gn2104 import GN2104
from CLI.Equipment.PowerSupply.KeysightE36XXX.keysight_e3646a import KeysightE3646A


class SampleBench(BaseBench):
    def __init__(self, dummy_mode=False):
        """
        Initialize instance

        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        """
        super().__init__(dummy_mode=dummy_mode)

        self.dut = GN2104(interface_address=103, device_address=44, dummy_mode=dummy_mode)
        self.ps = KeysightE3646A(address="GPIB0::5::INSTR", dummy_mode=dummy_mode)

    def aliases(self):
        """
        VIRTUAL FUNCTION
        Users can create aliases for resources or their sub-components.
        Automatically called by connect after all resources have been connected.
        Must be used when aliasing sub-components of dynamic resources
        """
        self.vcc = self.ps  # can have multiple references to same resource
        self.vccl = self.ps.channel[1]  # creating aliases for sub-components
        self.vcch = self.vcc.channel[2]  # creating aliases for sub-components
