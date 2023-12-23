"""
| $Revision:: 282512                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-09-20 23:14:19 +0100 (Thu, 20 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Description: Copy & Paste the description from the Procedure class here to allow users to quickly identify what the
procedure does.

"""
from COMMON.Procedures.base_procedure import BaseProcedure, BaseProcedureInputsContainer


# TODO: Update ProcedureArguments class to include procedure specific arguments
class ProcedureArguments(BaseProcedureInputsContainer):
    """
    Data Object that holds all of your procedure specific arguments.

    Add items such as variables and test conditions here. Set them to
    a value of None to indicate that they are required items.

    Usage:
    self.sj_frequency = 80e6
    self.sweep_type = 'Binary'
    """
    def __init__(self):
        super().__init__()
        # TODO: Insert required procedure variables here
        # self.sj_frequency = 80e6

    # TODO: Add checks for arguments to ensure they are of the required type/value
    def _check_requirements(self):
        """
        Use this to check argument types and values.

        Usage:
        if type(self.sj_frequency) is not int:
            Raise TypeError
        """
        pass


# TODO: Update ProcedureResources class to include procedure specific resources
class ProcedureResources(BaseProcedureInputsContainer):
    """
    Data Object that holds all of your procedure specific resources.
    Add items such as equipment and devices here. Set them to
    a value of None to indicate that they are required items.

    Usage:
    self.input_bert = BERT()
    self.output_bert = BERT()
    self.scope = Scope()
    """
    def __init__(self):
        super().__init__()
        # TODO: Insert required procedure equipment/devices here
        # self.input_bert = AnritsuMP1800()

    # TODO: Add checks for resources to ensure they are of the required type/value
    def _check_requirements(self):
        """
        Use this to check resource types and values.

        Usage:
        if type(self.input_bert) is not BaseBert:
            Raise TypeError
        """
        pass


# TODO: Rename procedure class to match desired procedure name
class ProcedureName(BaseProcedure):
    def __init__(self):
        """
        Add a description of what this procedure does here.

        :returns: a dictionary containing the following keys: 'Key1', 'Key2'
        """
        super().__init__()
        self.resources = ProcedureResources()
        """:type: ProcedureResources"""
        self.arguments = ProcedureArguments()
        """:type: ProcedureArguments"""

    # TODO: Add logic to deal with setup logic
    def setup(self):
        """
        Method used for setup config.
        """
        pass

    # TODO: Add logic that should run prior to the procedure executing
    def pre_main(self):
        """
        Method used for pre-main configuration.
        """
        pass

    # TODO: Add procedure logic
    def main(self):
        """
        Method used for core procedure logic. Run the test by calling [ProcedureName].run()
        """
        # Add results using:
        # self.data.add('Value', 32, 'MHz')
        pass

    # TODO: Add logic that should run after the test finished executing
    def post_main(self):
        """
        Method used for post-main configuration.
        """
        pass

    #TODO: Add clean-up logic
    def clean_up(self):
        """
        Method used to perform procedure clean-up.
        """
        pass
