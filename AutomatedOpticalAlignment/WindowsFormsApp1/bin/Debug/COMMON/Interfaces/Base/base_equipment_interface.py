"""
| $Revision:: 280004                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-07-27 18:32:23 +0100 (Fri, 27 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from abc import ABC
from abc import abstractmethod
import logging
from COMMON.Utilities.logging_ext import create_stream_handler


class BaseEquipmentInterface(ABC):
    """
    Base Equipment Interface from which all equipment interface should be derived from
    """
    def __init__(self, name=None, **kwargs):
        """
        Initialize instance

        :param name: communication interface name
        :type name: str
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        # error check for unused key word arguments
        if len(kwargs) > 0:
            raise RuntimeWarning("Unused keyword arguments at most base class: {}".format(kwargs))
        super().__init__()

        # if a name isn't supplied, use class definition name
        if name:
            self._name = name
        else:
            self._name = type(self).__name__

        self.error_check_supported = True
        self.stb_polling_supported = True
        self.stb_error_mask = 0x04
        self.stb_event_mask = 0x20

        # assign a standard logger to each item using device name
        # TODO: [sfarsi] multiple objects with same name, will tunnel to same logger!
        self.logger = logging.getLogger(self.name)
        create_stream_handler()

    @property
    def name(self):
        """
        :value: object name
        :type: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        :type value: str
        """
        self._name = value
        self.logger.name = value  # Update object's logger name to match object name

    @abstractmethod
    def close(self):
        """
        INTERNAL
        Close interface connection.
        """
        pass

    @abstractmethod
    def error_checking(self):
        """
        This function calls reads error queries and raises exception if any error occurred

        :raise RuntimeError: for detected errors
        """
        pass

    @abstractmethod
    def open(self, address=None):
        """
        Opens connection.

        :param address: communication interface address
        :type address: str
        """
        pass

    @abstractmethod
    def query(self, message):
        """
        Send a message and return results

        :param message: data to write
        :type message: str
        :return: data returned
        :rtype: str
        """
        pass

    @abstractmethod
    def query_with_srq_sync(self, message, timeout):
        """
        This function sends a command with and waits for the service request event

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        :return: data returned
        :rtype: str
        """
        pass

    @abstractmethod
    def query_with_stb_poll(self, message, timeout):
        """
        This function queries instrument with basic STB polling

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        :return: data returned
        :rtype: str
        """
        pass

    @abstractmethod
    def query_with_stb_poll_sync(self, message, timeout):
        """
        This function queries instrument with STB polling synchronization mechanism

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        :return: data returned
        :rtype: str
        """
        pass

    @abstractmethod
    def read(self):
        """
        Read a response

        :return: data returned
        :rtype: str
        """
        pass

    @abstractmethod
    def write(self, message):
        """
        Write data.

        :param message: data to write
        :type message: str
        """
        pass

    @abstractmethod
    def write_with_srq_sync(self, message, timeout):
        """
        This function sends a command with and waits for the service request event

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        pass

    @abstractmethod
    def write_with_stb_poll(self, message, timeout):
        """
        This function queries instrument with basic STB polling

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        pass

    @abstractmethod
    def write_with_stb_poll_sync(self, message, timeout):
        """
        This function queries instrument with STB polling synchronization mechanism

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        pass