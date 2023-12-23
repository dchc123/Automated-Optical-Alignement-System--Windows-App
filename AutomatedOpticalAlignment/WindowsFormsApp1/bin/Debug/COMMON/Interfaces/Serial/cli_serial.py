import time
import minimalmodbus
from COMMON.Interfaces.Base.base_equipment_interface import BaseEquipmentInterface


class CliSerial(BaseEquipmentInterface):
    """
    CLI serial interface driver
    """
    COMMANDS = {'Model': 0,
                'SN1': 1, 'SN2': 1,
                'Software_Number': 3, 'Software_Revision': 4,
                'setpoint': 300, 'DUT_temp': 108, 'Air_temp': 104, 'Nosel_temp': 100}

    def __init__(self, address=None, baud_rate=9600, **kwargs):
        """
        Initialize instance

        :param address: communication interface address
        :type address: str
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(**kwargs)
        self.address = address
        self.serial_handle = None
        self.baud_rate = baud_rate

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

        self.serial_handle = minimalmodbus.Instrument(self.address, 1)
        self.serial_handle.serial.baudrate = self.baud_rate
        time.sleep(0.1)

    def close(self):
        """
        Close visa connection
        """
        # self.serial_handle.close()
        pass

    def query(self, message):
        """
        translates GPIB query messages, sends message through minimalmodbus, and return results

        :param message: data to write
        :type message: str
        :return: data returned
        :rtype: str
        """
        number_of_decimals = 1
        signed = True
        if message == "?TD":
            parameter = self.COMMANDS['DUT_temp']
        elif message == "?TA":
            parameter = self.COMMANDS['Nosel_temp']
        elif message == "?SP":
            parameter = self.COMMANDS['setpoint']
        elif message == "*IDN?":
            return_val = "SP Scientific,"
            parameter = self.COMMANDS['Model']
            return_val += f"0x{self.serial_handle.read_register(parameter):04X}"
            return_val += ","
            time.sleep(0.1)
            parameter = self.COMMANDS['SN1']
            return_val += f"0x{self.serial_handle.read_register(parameter):04X}"
            time.sleep(0.1)
            parameter = self.COMMANDS['SN2']
            return_val += f"{self.serial_handle.read_register(parameter):04X}"
            return_val += ","
            time.sleep(0.1)
            parameter = self.COMMANDS['Software_Number']
            return_val += f"0x{self.serial_handle.read_register(parameter):04X}"
            time.sleep(0.1)
            parameter = self.COMMANDS['Software_Revision']
            return_val += f"REV 0x{self.serial_handle.read_register(parameter):04X}"
            time.sleep(0.01)
            return return_val
        else:
            raise NotImplementedError(f"CLI serial driver can't handle a '{message}' query yet")

        return_val = self.serial_handle.read_register(parameter, number_of_decimals, signed=signed)
        time.sleep(0.1)

        return return_val

    def read(self):
        """
        Read a response

        :return: data returned
        :rtype: str
        """
        raise NotImplementedError("use query on serial comms")

    def error_checking(self):
        """
        This function calls reads error queries and raises exception if any error occurred

        :raise RuntimeError: for detected errors
        """
        if not self.error_check_supported:
            return

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
        raise NotImplementedError("query_with_srq_sync not valid for serial comms")

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
        raise NotImplementedError("query_with_stb_poll not valid for serial comms")

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
        raise NotImplementedError("query_with_stb_poll_sync not valid for serial comms")

    def write(self, message):
        """
        Write data through visa.

        :param message: data to write
        :type message: str
        """
        number_of_decimals = 1
        signed = True
        if message.startswith("SP "):
            register = self.COMMANDS['setpoint']
            value = float(message[3:])
        else:
            raise NotImplementedError(f"no serial write methode implemented to deal with {message}")

        self.serial_handle.write_register(register, value, number_of_decimals, signed=signed)
        time.sleep(0.1)

    def write_with_srq_sync(self, message, timeout):
        """
        This function sends a command with and waits for the service request event

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        raise NotImplementedError("write_with_srq_sync not valid for serial comms")

    def write_with_stb_poll(self, message, timeout):
        """
        This function queries instrument with basic STB polling

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        raise NotImplementedError("write_with_stb_poll not valid for serial comms")

    def write_with_stb_poll_sync(self, message, timeout):
        """
        This function queries instrument with STB polling synchronization mechanism

        :param message: data to write
        :type message: str
        :param timeout: period in s to raise error if no response
        :type timeout: int
        """
        raise NotImplementedError("write_with_stb_poll_sync not valid for serial comms")
