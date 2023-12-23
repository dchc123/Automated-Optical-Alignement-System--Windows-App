"""
| $Revision:: 278787                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-03 01:43:55 +0100 (Tue, 03 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Collection of custom exceptions
"""


class NotSupportedError(Exception):
    """
    An exception indicating that an instrument does not support the requested function
    """
