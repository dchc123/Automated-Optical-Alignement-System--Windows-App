import ctypes
from unittest import TestCase, expectedFailure
from unittest.mock import patch, MagicMock, Mock
import logging
from testfixtures import log_capture

from COMMON.Interfaces.USBtoI2C.i2c_win32 import Usb2I2c

import sys
from contextlib import contextmanager
from io import StringIO
import re


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestUsb2I2c(TestCase):

    def setUp(self):
        self.c = Usb2I2c()

    def test_identity(self):
        Usb2I2c.connections_info = {'number_of_dongles': 0}
        self.assertEqual({'number_of_dongles': 0}, self.c.identity)

    def test_close_dummy_mode(self):
        self.c.interface_connected = True
        self.c.dummy_mode = True
        self.assertEqual(self.c.interface_connected, True)
        self.c.close()
        self.assertEqual(self.c.interface_connected, False)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_close(self, mock_dll):
        self.c.interface_connected = True
        Usb2I2c.connections_info['handle'] = 25
        Usb2I2c.connections_info['connected'] = True
        mock_dll.Connected_USB.side_effect = [1,0]
        self.c.close()
        mock_dll.Connected_USB.assert_called_with(25)
        self.assertEqual(mock_dll.Connected_USB.call_count, 2)
        mock_dll.Disconnect_USB.assert_called_once_with(25)
        self.assertFalse(self.c.interface_connected)
        self.assertEqual(Usb2I2c.connections_info, {})

    @log_capture()
    def test_close_when_interface_closed_already(self, log):
        self.c.interface_connected = False
        self.c.close()
        log.check(('Usb2I2c', 'INFO', 'Attempted to close a connection that is already closed'),)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    @log_capture()
    def test_close_when_dll_disconnected(self, log, mock_dll):
        self.c.interface_connected = True
        Usb2I2c.connections_info['handle'] = 25
        mock_dll.Connected_USB.return_value = 0
        self.c.close()
        mock_dll.Connected_USB.assert_called_once_with(25)
        log.check(('Usb2I2c', 'INFO', 'Attempted to close a connection where dll reports connection closed'),)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_clr_dll(self, mock_dll):
        Usb2I2c.connections_info['handle'] = 25
        Usb2I2c.connections_info['connected'] = False
        self.c.interface_connected = False
        mock_dll.DestroyMe_USB.return_value = 1
        mock_dll.Connected_USB.return_value = 0
        self.c.clear_dll()
        mock_dll.DestroyMe_USB.assert_called_once_with(25)
        mock_dll.Connected_USB.assert_called_once_with(25)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_clr_dll_when_interface_open(self, mock_dll):
        Usb2I2c.connections_info['handle'] = 25
        Usb2I2c.connections_info['connected'] = True
        mock_dll.Connected_USB.return_value = 1
        self.c.interface_connected = True
        with (self.assertRaisesRegex(RuntimeError, 'Tried to destroy DLL instance without closing the connection')):
            self.c.clear_dll()
        mock_dll.Connected_USB.assert_called_once_with(25)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_clr_dll_without_handle(self, mock_dll):
        Usb2I2c.connections_info['handle'] = None
        self.c.interface_connected = True
        with (self.assertRaisesRegex(RuntimeError, 'Tried to destroy DLL instance without a handle!')):
            self.c.clear_dll()
        mock_dll.called_once()

    def test_clr_dll_without_dll(self):
        with (self.assertRaisesRegex(RuntimeError, 'Tried to destroy DLL instance without loading dll!')):
            self.c.clear_dll()

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_open(self, mock_dll):
        self.assertFalse(self.c.interface_connected)
        Usb2I2c.connections_info = {}
        handle = 25
        mock_dll.CreateMe_USB.return_value = handle
        mock_dll.EnumeratesDevices_USB.return_value = 1
        mock_dll.ListDevices_USB.return_value = 1
        mock_dll.Connect_USB.return_value = 1
        self.assertFalse(mock_dll.EnumeratesDevices_USB.called)
        self.c.open()
        mock_dll.Connect_USB.assert_called_once_with(25, 0)
        expected_connection_info = dict(number_of_dongles=1, serial_numbers=[0], index=0, handle=25,
                                        connected=True)
        self.assertDictEqual(expected_connection_info, Usb2I2c.connections_info)
        self.assertTrue(self.c.interface_connected)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_open_error(self, mock_dll):
        self.assertFalse(self.c.interface_connected)
        self.c.address = 3
        handle = 25
        mock_dll.CreateMe_USB.return_value = handle
        mock_dll.EnumeratesDevices_USB.return_value = 1
        mock_dll.ListDevices_USB.return_value = 1
        mock_dll.Connect_USB.return_value = -7
        self.assertFalse(mock_dll.EnumeratesDevices_USB.called)
        with self.assertRaisesRegex(RuntimeError, 'failed to connect to dongle index 3. Returned -7 - INVALID_ADDRESS'):
            self.c.open()
        mock_dll.Connect_USB.assert_called_once_with(25, 3)
        expected_connection_info = dict(number_of_dongles=1, serial_numbers=[0], index=None, handle=25,
                                        connected=False)
        self.assertDictEqual(expected_connection_info, Usb2I2c.connections_info)
        self.assertFalse(self.c.interface_connected)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_open_with_no_dongles_connected(self, mock_dll):
        self.assertFalse(self.c.interface_connected)
        handle = 25
        mock_dll.CreateMe_USB.return_value = handle
        mock_dll.EnumeratesDevices_USB.return_value = 0
        mock_dll.ListDevices_USB.return_value = 1
        self.assertFalse(mock_dll.EnumeratesDevices_USB.called)
        with self.assertRaisesRegex(IOError, 'No USBtoI2C dongles connected - Check power and USB connection?'):
            self.c.open()
        self.assertFalse(self.c.interface_connected)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_open_with_dongle_disconnected(self, mock_dll):
        self.assertFalse(self.c.interface_connected)
        handle = 25
        mock_dll.CreateMe_USB.return_value = handle
        mock_dll.EnumeratesDevices_USB.return_value = 0
        mock_dll.ListDevices_USB.return_value = 1
        Usb2I2c.connections_info['number_of_dongles'] = 0
        self.assertFalse(mock_dll.EnumeratesDevices_USB.called)
        with self.assertRaisesRegex(IOError, 'No USBtoI2C dongles connected - Check power and USB connection?'):
            self.c.open()

    def test_open_dummy_mode(self):
        self.assertFalse(self.c.interface_connected)
        self.c.dummy_mode = True
        self.c.open()
        self.assertTrue(self.c.interface_connected)

    def test_load_dll(self):
        self.assertEqual(Usb2I2c.dll, None)
        self.c.load_dll()
        self.assertIsInstance(Usb2I2c.dll, ctypes.CDLL)

    def test_scan(self):
        with patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll', create=True) as _mock_dll:
            handle = 25
            _mock_dll.CreateMe_USB.return_value = handle
            _mock_dll.EnumeratesDevices_USB.return_value = 1
            _mock_dll.ListDevices_USB.return_value = 1
            self.assertFalse(_mock_dll.EnumeratesDevices_USB.called)
            self.c.load_dll()
            # we expect a dictionary that identifies each dongle attached.
            # The driver seems to be written in such a way that it is not possible to connect to 2 devices at the
            # same time. We have a handle to the driver, we then enumerate connected devices.
            # When we connect to one of these devices we can address the handle to the driver but not specify the
            # connection, therefore we cannot communicate concurrently with a second device.
            # Comparing to other i2c_2_USB drivers, enumerating devices can happen without a handle. A handle is
            # associated with a USB device
            expected_connection_info = {'number_of_dongles': 1, 'serial_numbers': [0], 'index': None,
                                        'handle': handle, 'connected': False}
            # If we were able to communicate to multiple devices in parallel, we would expect to have a dictionary of
            # dictionaries, or at least a list of dictionaries eg:
            # expected_connection_info = {0: {'Handle': None, 'serial_num': 123, 'connected': False},
            #                             1: {'Handle': None, 'serial_num': 456, 'connected': False},}

            self.assertDictEqual(expected_connection_info, self.c.scan())
            # we expect to enumerate Devices
            _mock_dll.EnumeratesDevices_USB.assert_called_once_with(handle, self.c.VENDORID, self.c.PRODUCTID)
            _mock_dll.ListDevices_USB.assert_called_once()

    def test_scan_2_dongles(self):
        with patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll', create=True) as _mock_dll:
            handle = 25
            _mock_dll.CreateMe_USB.return_value = handle
            _mock_dll.EnumeratesDevices_USB.return_value = 2
            _mock_dll.ListDevices_USB.return_value = 1
            self.assertFalse(_mock_dll.EnumeratesDevices_USB.called)
            self.c.load_dll()
            # we expect a dictionary that identifies each dongle attached.
            # The driver seems to be written in such a way that it is not possible to connect to 2 devices at the
            # same time. We have a handle to the driver, we then enumerate connected devices.
            # When we connect to one of these devices we can address the handle to the driver but not specify the
            # connection, therefore we cannot communicate concurrently with a second device.
            # Comparing to other i2c_2_USB drivers, enumerating devices can happen without a handle. A handle is
            # associated with a USB device
            expected_connection_info = {'number_of_dongles': 2, 'serial_numbers': [0, 1], 'index': None,
                                        'handle': handle, 'connected': False}
            # If we were able to communicate to multiple devices in parallel, we would expect to have a dictionary of
            # dictionaries, or at least a list of dictionaries eg:
            # expected_connection_info = {0: {'Handle': None, 'serial_num': 123, 'connected': False},
            #                             1: {'Handle': None, 'serial_num': 456, 'connected': False},}

            with captured_output() as (out, err):
                self.assertDictEqual(expected_connection_info, self.c.scan())
            output = out.getvalue().strip()
            self.assertEqual(output, '2 dongles were found - using 1st dongle')
            # we expect to enumerates Devices
            _mock_dll.EnumeratesDevices_USB.assert_called_once_with(handle, self.c.VENDORID, self.c.PRODUCTID)
            _mock_dll.ListDevices_USB.assert_called_once()
            # we aught to indicate that there are more that 1 dongles.

    def test_scan_no_dongles(self):
        with patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll') as _mock_dll:
            handle = 25
            _mock_dll.CreateMe_USB.return_value = handle
            _mock_dll.EnumeratesDevices_USB.return_value = 0
            with self.assertRaisesRegex(IOError, 'No USBtoI2C dongles connected - Check power and USB connection?'):
                self.c.scan()

    def test_scan_dll_not_loaded(self):
        self.c.dll = None
        with patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll') as _mock_dll:
            handle = 25
            _mock_dll.CreateMe_USB.return_value = handle
            _mock_dll.EnumeratesDevices_USB.return_value = 1
            _mock_dll.ListDevices_USB.return_value = 1
            self.assertFalse(_mock_dll.EnumeratesDevices_USB.called)
            # we expect a dictionary that identifies each dongle attached.
            # The driver seems to be written in such a way that it is not possible to connect to 2 devices at the
            # same time. We have a handle to the driver, we then enumerates connected devices.
            # When we connect to one of these devices we can address the handle to the driver but not specify the
            # connection, therefore we cannot communicate concurrently with a second device.
            # Comparing to other i2c_2_USB drivers, enumerating devices can happen without a handle. A handle is
            # associated with a USB device
            expected_connection_info = {'number_of_dongles': 1, 'serial_numbers': [0], 'index': None,
                                        'handle': handle, 'connected': False}
            # If we were able to communicate to multiple devices in parallel, we would expect to have a dictionary of
            # dictionaries, or at least a list of dictionaries eg:
            # expected_connection_info = {0: {'Handle': None, 'serial_num': 123, 'connected': False},
            #                             1: {'Handle': None, 'serial_num': 456, 'connected': False},}

            self.assertDictEqual(expected_connection_info, self.c.scan())
            # we expect to enumerate Devices
            _mock_dll.EnumeratesDevices_USB.assert_called_once_with(handle, self.c.VENDORID, self.c.PRODUCTID)
            _mock_dll.ListDevices_USB.assert_called_once()

    def test_read_no_addresses(self):
        """We need device ID and memory address to read"""
        with self.assertRaises(TypeError):
            self.c.read(device_address=None, memory_address=4)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_read(self, mock_dll):
        self.c._i2c_read = MagicMock(name='_i2c_read', return_value=[4])
        mock_dll.CreateMe_USB.return_value = 25
        mock_dll.EnumeratesDevices_USB.return_value = 1
        mock_dll.Connect_USB.return_value = 1
        self.assertEqual(4, self.c.read(0x2, 0x3))
        self.c._i2c_read.assert_called_once_with(device_address=2, memory_address=3, length=1)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_read_block(self, mock_dll):
        self.c._i2c_read = MagicMock(name='_i2c_read', return_value=[4, 5, 6])
        mock_dll.CreateMe_USB.return_value = 25
        mock_dll.EnumeratesDevices_USB.return_value = 1
        mock_dll.Connect_USB.return_value = 1
        self.assertListEqual([4, 5, 6], self.c.read(0x2, 0x3, 3))
        self.c._i2c_read.assert_called_once_with(device_address=2, memory_address=3, length=3)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test__i2c_read(self, mock_dll):
        mock_dll.Read1_USB.return_value = 1  # good status
        Usb2I2c.connections_info['handle'] = 25
        self.assertEqual([0], self.c._i2c_read(2, 3, 1))
        mock_dll.Read1_USB.called_once()

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test__i2c_read_block(self, mock_dll):
        mock_dll.Read1_USB.return_value = 1  # good status
        Usb2I2c.connections_info['handle'] = 25
        self.assertEqual([0, 0, 0, 0], self.c._i2c_read(2, 3, 4))
        mock_dll.Read1_USB.called_once()

    @log_capture()
    def test_write_without_open(self, log):
        self.c._i2c_write_no_ack = MagicMock(name='_i2c_write')
        self.c.open = MagicMock(name='open')
        self.c.write(0x2, 0x3, 0x4)
        self.c.open.assert_called_once_with()
        self.c._i2c_write_no_ack.assert_called_once_with(device_address=2, memory_address=3, data=4)
        log.check(('Usb2I2c', 'WARNING', 'Attempting to write without opening a connection with the dongle. Connecting '
                                         'to dongle at index 0...'), )

    @log_capture()
    def test_read_without_open(self, log):
        self.c._i2c_read = MagicMock(name='_i2c_read', return_value=[4])
        self.c.open = MagicMock(name='open')
        self.assertEqual(4, self.c.read(0x2, 0x3))
        self.c.open.assert_called_once_with()
        self.c._i2c_read.assert_called_once_with(device_address=2, memory_address=3, length=1)
        log.check(('Usb2I2c', 'WARNING', 'Attempting to read without opening a connection with the dongle. Connecting '
                                         'to dongle at index 0...'), )

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_write(self, mock_dll):
        self.c._i2c_write_no_ack = MagicMock(name='_i2c_write')
        mock_dll.CreateMe_USB.return_value = 25
        mock_dll.EnumeratesDevices_USB.return_value = 1
        mock_dll.Connect_USB.return_value = 1
        self.c.write(0x2, 0x3, 0x4)
        self.c._i2c_write_no_ack.assert_called_once_with(device_address=2, memory_address=3, data=4)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_write_block(self, mock_dll):
        self.c._i2c_write_no_ack = MagicMock(name='_i2c_write')
        mock_dll.CreateMe_USB.return_value = 25
        mock_dll.EnumeratesDevices_USB.return_value = 1
        mock_dll.Connect_USB.return_value = 1
        self.c.write(0x2, 0x3, [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7])
        self.c._i2c_write_no_ack.assert_called_once_with(device_address=2, memory_address=3, data=[0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7])

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test__i2c_write(self, mock_dll):
        mock_dll.PageWrite_USB.return_value = 1
        Usb2I2c.connections_info['handle'] = 25
        self.c._i2c_write(2, 3, 5)
        mock_dll.PageWrite_USB.assert_called_once()

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test__i2c_write_block(self, mock_dll):
        mock_dll.PageWrite_USB.return_value = 1
        Usb2I2c.connections_info['handle'] = 25
        expected_list = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7]
        self.c._i2c_write(2, 3, expected_list)
        mock_dll.PageWrite_USB.assert_called_once()
        kall = mock_dll.PageWrite_USB.call_args
        a, kwa = kall
        listp = ctypes.POINTER(ctypes.c_ubyte*8)
        returned_list = list(ctypes.cast(a[4], listp)[0])
        self.assertEqual(expected_list, returned_list)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test__i2c_write_big_block_without_wait_for_ack(self, mock_dll):
        """check that 16 bytes get broken up into 2 8 byte writes, using Write1_USB"""
        mock_dll.Write1_USB.return_value = 1
        Usb2I2c.connections_info['handle'] = 25
        expected_list = [ 0x0,  0x1,  0x2,  0x3,  0x4,  0x5,  0x6,  0x7,
                         0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]
        self.c._i2c_write_no_ack(2, 3, expected_list)
        self.assertEqual(2, mock_dll.Write1_USB.call_count)
        kall_list = mock_dll.Write1_USB.call_args_list
        for i, kall in enumerate(kall_list):
            a, kwa = kall
            listp = ctypes.POINTER(ctypes.c_ubyte*8)
            returned_list = list(ctypes.cast(a[4], listp)[0])
            self.assertEqual(expected_list[i*8:i*8+8], returned_list)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test__i2c_write_big_block_with_wait_for_ack(self, mock_dll):
        """check that 16 bytes (or more than 8 bytes) get written seamlessly by PageWrite_USB.
        The firmware handles wait for ack between 8 byte pages"""
        mock_dll.PageWrite_USB.return_value = 1
        Usb2I2c.connections_info['handle'] = 25
        expected_list = [ 0x0,  0x1,  0x2,  0x3,  0x4,  0x5,  0x6,  0x7,
                         0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17]
        self.c._i2c_write(2, 3, expected_list)
        self.assertEqual(1, mock_dll.PageWrite_USB.call_count)
        a, kwa = mock_dll.PageWrite_USB.call_args
        listp = ctypes.POINTER(ctypes.c_ubyte*16)  # declare a pointer to an array of 16 unsigned bytes
        # using the address of the list that was sent to PageWrite_usb, convert the contents to a list
        returned_list = list(ctypes.cast(a[4], listp)[0])
        self.assertEqual(expected_list, returned_list)

    def test_write_no_addresses(self):
        """We need device ID and memory address to read"""
        with self.assertRaises(TypeError):
            self.c.write(device_address=None, memory_address=2, data=[123])

    def test_reset(self):
        with patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll') as _mock_dll:
            _mock_dll.Reset_USB.return_value = 1
            self.assertFalse(_mock_dll.Reset_USB.called)
            self.assertEqual(1, self.c.reset())
            self.assertTrue(_mock_dll.Reset_USB.called)

    @log_capture()
    def test_reset_fail(self, log):
        with patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll') as _mock_dll:
            _mock_dll.Reset_USB.return_value = -10
            self.assertFalse(_mock_dll.Reset_USB.called)
            self.assertEqual(-10, self.c.reset())
            self.assertTrue(_mock_dll.Reset_USB.called)
        log.check(('Usb2I2c', 'WARNING', 'Reset_USB returned error: -10 - HANDLE_ERROR'),)

    def test_reset_dummy_mode(self):
        self.c.dummy_mode = True
        # assert success
        self.assertEqual(1, self.c.reset())

    def test_interface_speed(self):
        self.c._interface_speed = 234
        self.assertEqual(234, self.c.interface_speed)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_set_interface_speed(self, mock_dll):
        mock_dll.SetBusSpeed_USB.return_value = 1
        Usb2I2c.connections_info['handle'] = 23
        self.c.interface_speed = 300
        mock_dll.SetBusSpeed_USB.called_once_with(23, 300)
        self.assertEqual(300, self.c.interface_speed)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_set_interface_speed_invalid_speed(self, mock_dll):
        mock_dll.SetBusSpeed_USB.return_value = 1
        Usb2I2c.connections_info['handle'] = 23
        with self.assertRaises(ValueError):
            self.c.interface_speed = 30000

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c.dll')
    def test_set_interface_speed_ioerror(self, mock_dll):
        mock_dll.SetBusSpeed_USB.return_value = -5  # not connected
        Usb2I2c.connections_info['handle'] = 23
        with self.assertRaises(IOError):
            self.c.interface_speed = 300

    def test_gpio_voltage_level(self):
        with self.assertRaises(NotImplementedError):
            self.c.gpio_voltage_level

    def test_interface_mode(self):
        with self.assertRaises(NotImplementedError):
            self.c.interface_mode

    def test_interface_type(self):
        with self.assertRaises(NotImplementedError):
            self.c.interface_type
