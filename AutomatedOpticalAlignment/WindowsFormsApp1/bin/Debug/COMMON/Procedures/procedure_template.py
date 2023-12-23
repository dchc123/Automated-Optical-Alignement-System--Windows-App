"""
| $Revision:: 282512                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-09-20 23:14:19 +0100 (Thu, 20 Sep 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Description:

"""
from COMMON.Procedures.base_procedure import BaseProcedure, BaseProcedureInputsContainer


class ProcedureArguments(BaseProcedureInputsContainer):
    def __init__(self):
        super().__init__()

    def _check_requirements(self):
        pass


class ProcedureResources(BaseProcedureInputsContainer):
    def __init__(self):
        super().__init__()

    def _check_requirements(self):
        pass


class ProcedureName(BaseProcedure):
    def __init__(self):
        super().__init__()
        self.resources = ProcedureResources()
        """:type: ProcedureResources"""
        self.arguments = ProcedureArguments()
        """:type: ProcedureArguments"""

    def setup(self):
        pass

    def pre_main(self):
        pass

    def main(self):
        pass

    def post_main(self):
        pass

    def clean_up(self):
        pass
