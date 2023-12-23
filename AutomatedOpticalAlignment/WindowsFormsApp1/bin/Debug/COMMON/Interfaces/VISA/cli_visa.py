"""
| $Revision:: 279799                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-25 20:17:49 +0100 (Wed, 25 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Source for the extended APIs:
Rohde & Schwarz: 6. Measurement Synchronization
https://www.rohde-schwarz.com/us/driver-pages/remote-control/measurements-synchronization_231248.html

"""
import time
import pyvisa as visa
from pyvisa.resources.messagebased import MessageBasedResource  # Used for typing
from COMMON.Interfaces.Base.base_equipment_interface import BaseEquipmentInterface


class CLIVISA(BaseEquipmentInterface):
    """
    CLI Visa driver
    """
    def __init__(self, address=None, **kwargs):
        """
        Initialize instance

        :param address: communication interface address
        :type address: str
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(**kwargs)
        self.address = address
        self.visa_handle = None
        """:type: MessageBasedResource"""

    def _stb_polling(self, exception_msg, timeout):
        """
        STB polling loop internal function

        :param exception_msg: message to raise exception with
        :type exception_msg: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        :raise RuntimeError: when it times out
        """
        start = time.time()
        # STB polling loop
        while True:
            stb = self.visa_handle.read_stb()
            if (stb & self.stb_event_mask) > 0:
                break

            elapsed = time.time() - start
            if elapsed > timeout:
                raise RuntimeError(exception_msg)
            else:
                # Progressive delay
                if elapsed > 0.01:
                    if elapsed > 0.1:
                        if elapsed > 1:
                            if elapsed > 10:
                                time.sleep(0.5)
                            else:
                                time.sleep(0.1)
                        else:
                            time.sleep(0.01)
                    else:
                        time.sleep(0.001)

    def close(self):
        """
        Close visa connection
        """
        self.visa_handle.close()

    def error_checking(self):
        """
        This function calls reads error queries and raises exception if any error occurred

        :raise RuntimeError: for detected errors
        """
        if not self.error_check_supported:
            return

        errors = []

        # check error bit
        if self.stb_polling_supported:
            stb = int(self.visa_handle.query('*STB?'))
            if (stb & self.stb_error_mask) == 0:
                return    # no error flagged return early

        # check for error messages
        while True:
            response = self.visa_handle.query('SYST:ERR?')
            if '"no error"' in response.lower():
                break
            errors.append(response)
            if len(errors) > 50:
                # safety stop
                errors.append('Cannot clear the error queue')
                break

        # raise if errors
        if errors:
            raise RuntimeError(errors)

    def open(self, address=None):
        """
        Opens visa connection

        :param address: communication interface address
        :type address: str
        """
        if address:
            self.address = address
        if self.address is None:
            raise RuntimeError("Attempted to open interface without an address")

        try:
            self.visa_handle = visa.ResourceManager().open_resource(self.address)
        except:
            self.visa_handle = visa.ResourceManager("@py").open_resource(self.address)

    def query(self, message):
        """
        Send a message through visa, and return results

        :param message: data to write
        :type message: str
        :return: data returned
        :rtype: str
        """
        return self.visa_handle.query(message)

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
        self.visa_handle.query('*ESR?')
        full_cmd = message + ';*OPC'
        self.visa_handle.discard_events(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_ALL_MECH)
        self.visa_handle.enable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_QUEUE)
        self.visa_handle.write(full_cmd)
        self.visa_handle.wait_on_event(visa.constants.VI_EVENT_SERVICE_REQ, timeout*1000)  # timeout in ms
        self.visa_handle.disable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_QUEUE)
        self.visa_handle.query('*ESR?')

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
        self.visa_handle.write(message)
        exception_msg = 'Querying with OPCsync - Timeout occured. Message: "{}", timeout {}s'.format(message, timeout)
        self._stb_polling(exception_msg, timeout)
        response = self.visa_handle.read()
        return response

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
        self.visa_handle.query('*ESR?')
        full_cmd = message + ';*OPC'
        self.visa_handle.write(full_cmd)
        exception_msg = 'Querying with OPCsync - Timeout occured. Message: "{}", timeout {}s'.format(message, timeout)
        self._stb_polling(exception_msg, timeout)
        response = self.visa_handle.read()
        self.visa_handle.query('*ESR?')
        return response

    def read(self):
        """
        Read a response

        :return: data returned
        :rtype: str
        """
        return self.visa_handle.read()

    def write(self, message):
        """
        Write data through visa.

        :param message: data to write
        :type message: str
        """
        self.visa_handle.write(message)

    def write_with_srq_sync(self, message, timeout):
        """
        This function sends a command with and waits for the service request event

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        self.visa_handle.query('*ESR?')
        full_cmd = message + ';*OPC'
        self.visa_handle.discard_events(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_ALL_MECH)
        self.visa_handle.enable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_QUEUE)
        self.visa_handle.write(full_cmd)
        self.visa_handle.wait_on_event(visa.constants.VI_EVENT_SERVICE_REQ, timeout*1000)  # timeout in ms
        self.visa_handle.disable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_QUEUE)
        self.visa_handle.query('*ESR?')

    def write_with_stb_poll(self, message, timeout):
        """
        This function queries instrument with basic STB polling

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        self.visa_handle.write(message)
        exception_msg = 'Writing with OPCsync - Timeout occured. Command: "{}", timeout {}s'.format(message, timeout)
        self._stb_polling(exception_msg, timeout)

    def write_with_stb_poll_sync(self, message, timeout):
        """
        This function queries instrument with STB polling synchronization mechanism

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        self.visa_handle.query('*ESR?')
        full_cmd = message + ';*OPC'
        self.visa_handle.write(full_cmd)
        exception_msg = 'Writing with OPCsync - Timeout occured. Command: "{}", timeout {}s'.format(message, timeout)
        self._stb_polling(exception_msg, timeout)
        self.visa_handle.query('*ESR?')
