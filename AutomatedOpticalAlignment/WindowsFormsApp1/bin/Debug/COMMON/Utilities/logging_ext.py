"""
| $Revision:: 279502                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-18 21:31:20 +0100 (Wed, 18 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Collection of logging library extensions
"""
import re
import logging
from functools import wraps


# New logging levels
LOG_VERBOSE_LEVEL = 5


def create_stream_handler(log_level='INFO'):
    if logging.root.hasHandlers():
        return  # do nothing

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    sh = logging.StreamHandler()
    sh.name = 'CLIStream'
    formatter = logging.Formatter(fmt='{levelname:10}{name}.{funcName}: {message}', style='{')
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)


class _AttributeAccessLogging:
    """
    Global flag to enable/disable auto-logging of CLI object attributes
    using @cli_property and @cli_method decorators
    """
    enabled = True


def log_method_access(method):
    """
    Custom decorator to auto log method/function access.


    :param method: method to be decorated
    :type method: function
    """
    @wraps(method)
    def log_method_access_wrapper(*args, **kwargs):
        if _AttributeAccessLogging.enabled:
            self = args[0]  # Reference to calling instance

            parameters = ""
            for arg in args:
                if arg == self:
                    continue

                # Add a comma if the parameters string is not empty
                if parameters:
                    parameters += ", "

                parameters += str(arg)

            for kwarg in kwargs.keys():
                # Add a comma if the parameters string is not empty
                if parameters:
                    parameters += ", "

                parameters += f"{kwarg}={kwargs[kwarg]}"

            try:
                return_string = ''

                ret = method(*args, **kwargs)  # Method call

                if ret is not None:
                    return_string = f" --> {ret}"

                self.logger.log(LOG_VERBOSE_LEVEL, f"{method.__name__}({parameters.strip()}){return_string}")

            except Exception as e:
                self.logger.log(LOG_VERBOSE_LEVEL, f"{method.__name__}({parameters.strip()})")
                raise e
        else:
            ret = method(*args, **kwargs)

        return ret

    return log_method_access_wrapper


class log_property_access(property):
    """
    Emulate PyProperty_Type() in Objects/descrobject.c
    https://docs.python.org/2/howto/descriptor.html#properties

    Added logging features to original class

    **NOTE**: the class name doesn't follow coding guidelines, because this class is meant to
    be used as a decorator, and decorators use small_with_underscore convention
    """
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return_value = self.fget(obj)
        if _AttributeAccessLogging.enabled:
            call = re.search("<function\s([A-Za-z0-9_.]+) at .+>", str(self.fget))
            call = call.group(1)
            obj.logger.log(LOG_VERBOSE_LEVEL, f"{call} --> {return_value}")
        return return_value

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        if _AttributeAccessLogging.enabled:
            call = re.search("<function\s([A-Za-z0-9_.]+) at .+>", str(self.fset))
            call = call.group(1)
            obj.logger.log(LOG_VERBOSE_LEVEL, f"{call} <-- {value}")
        self.fset(obj, value)
