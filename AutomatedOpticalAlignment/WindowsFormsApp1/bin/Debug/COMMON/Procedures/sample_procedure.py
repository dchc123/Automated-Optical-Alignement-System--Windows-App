"""
| $Revision:: 282512                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-09-20 23:14:19 +0100 (Thu, 20 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Description: This procedure powers up an auxiliary supply and measures the idle power of a connected device.

"""
from COMMON.Procedures.base_procedure import BaseProcedure, BaseProcedureInputsContainer
from COMMON.Equipment.PowerSupply.base_power_supply import BasePowerSupply


class ProcedureArguments(BaseProcedureInputsContainer):
    """
    Data Object that holds all of your procedure specific arguments.

    Add items such as variables and test conditions here. Set them to
    a value of None to indicate that they are required items.
    """
    def __init__(self):
        super().__init__()
        self.averages = 1

    def _check_requirements(self):
        """
        Use this to check argument types and values.
        """
        if not isinstance(self.averages, int):
            raise TypeError('Averages must be of type int!')


class ProcedureResources(BaseProcedureInputsContainer):
    """
    Data Object that holds all of your procedure specific resources.
    Add items such as equipment and devices here. Set them to
    a value of None to indicate that they are required items.
    """
    def __init__(self):
        super().__init__()
        self.supply = None
        ''':type: BasePowerSupply'''
        self.channel_number = None
        ''':type: int'''

    def _check_requirements(self):
        """
        Use this to check resource types and values.
        """
        if not isinstance(self.supply, BasePowerSupply):
            raise TypeError('Supply must be of type BasePowerSupply!')
        if not isinstance(self.channel_number, int):
            raise TypeError('Channel number must be of type int')


class SampleProcedure(BaseProcedure):
    def __init__(self):
        """
        This procedure powers up an auxiliary supply and measures the idle power of a connected device.

        :returns: a dictionary containing the following keys: 'AveragePower', 'PowerList'
        """
        super().__init__()
        self.resources = ProcedureResources()
        """:type: ProcedureResources"""
        self.arguments = ProcedureArguments()
        """:type: ProcedureArguments"""

    def setup(self):
        """
        Method used for setup config.
        """
        # Configure the voltage & current before powering on
        self.resources.supply.channel[self.resources.channel_number].voltage.setpoint = 5
        self.resources.supply.channel[self.resources.channel_number].current.setpoint = 0.5

    def pre_main(self):
        """
        Method used for pre-main configuration.
        """
        # Turn the supply on
        self.resources.supply.channel[self.resources.channel_number].output = 'ENABLE'

    def main(self):
        """
        Method used for core procedure logic. Run the test by calling [ProcedureName].run()
        """
        # Display a message to inform the user that the procedure main is running:
        print('{time}: Procedure is running main.'.format(time=self.utilities.get_timestamp()))

        total_power = 0
        # Grab the power values n-times
        for i in range(0, self.arguments.averages):
            current_reading = self.resources.supply.channel[self.resources.channel_number].power
            total_power += current_reading
            # For each iteration, append the current power reading to the data object. Object will automatically create
            # a list for the data.
            self.data.append('PowerList', current_reading, 'W')

        # Complete the average by dividing by n
        total_power = total_power / self.arguments.averages

        # Store the averaged result
        self.data.add('AveragePower', total_power, 'W')  # Added single float value to the data container

    def post_main(self):
        """
        Method used for post-main configuration.
        """
        # Turn off the supply
        self.resources.supply.channel[self.resources.channel_number].output = 'DISABLE'

    def clean_up(self):
        """
        Method used to perform procedure clean-up.
        """
        # Set the supply channel voltage & current to 0 to avoid any accidents.
        self.resources.supply.channel[self.resources.channel_number].voltage.setpoint = 0
        self.resources.supply.channel[self.resources.channel_number].current.setpoint = 0
