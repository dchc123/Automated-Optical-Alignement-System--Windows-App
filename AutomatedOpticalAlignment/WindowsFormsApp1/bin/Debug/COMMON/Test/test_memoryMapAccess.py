from unittest import TestCase, expectedFailure
from unittest.mock import patch, mock_open, call

from COMMON.Device.memory_map_access import MemoryMapAccess
from collections import OrderedDict
import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestMemoryMapAccess(TestCase):

    @expectedFailure
    def test_table(self):
        self.fail()

    @expectedFailure
    def test_get_reg(self):
        self.fail()

    @expectedFailure
    def test__get_addr(self):
        self.fail()

    @expectedFailure
    def test_set_reg(self):
        self.fail()

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    def test_pw3(self, mock_interface):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'chip_sequences': {'PASSWORD_LEVEL_3': {'PWE_2': 0x59,
                                                                                           'PWE_3': 0xAB,
                                                                                           'PWE_1': 0x1D,
                                                                                           'PWE_0': 0x6E}},
                                                   'test_signals': {}}
            self.mm = MemoryMapAccess(mock_interface)

            expected = OrderedDict([('PWE_3', 0xAB),
                                    ('PWE_2', 0x59),
                                    ('PWE_1', 0x1D),
                                    ('PWE_0', 0x6E)])
            self.assertIs(dict, type(self.mm.pw3))
            self.assertSequenceEqual(expected, self.mm.pw3)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    def test_soft_reset(self, mock_interface):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'chip_sequences': {'SOFT_RESET': {'PWE_2': 0x2C,
                                                                                     'PWE_3': 0x5D,
                                                                                     'PWE_1': 0x6A,
                                                                                     'TABLE_SEL': 0x8B,
                                                                                     'PWE_0': 0xC9}},
                                                   'test_signals': {}}

            self.mm = MemoryMapAccess(mock_interface)
            expected = OrderedDict([('PWE_3', 0x5D),
                                    ('PWE_2', 0x2C),
                                    ('PWE_1', 0x6A),
                                    ('PWE_0', 0xC9),
                                    ('TABLE_SEL', 0x8B)])

            self.assertSequenceEqual(expected, self.mm.soft_reset)
            self.assertIs(dict, type(self.mm.soft_reset))

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    def test_save_all_settings(self, mock_interface):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'bit_field': {'bf0': {'POR': 0,
                                                                         'register': 'REG_0',
                                                                         'justification': 0,
                                                                         'length': 8,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 'bf1': {'POR': 0,
                                                                         'register': 'REG_1',
                                                                         'justification': 0,
                                                                         'length': 4,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 'bf2': {'POR': 0,
                                                                         'register': 'REG_1',
                                                                         'justification': 4,
                                                                         'length': 4,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 },
                                                   'memory_map': {'TABLE_SEL': {'deviceID': 0xa2,
                                                                                'table': 'Not_tabled',
                                                                                'offset': 0x7f},
                                                                  'REG_0': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x0},
                                                                  'REG_1': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x1},
                                                                  'REG_2': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x2},
                                                                  },
                                                   'test_signals': {}
                                                   }
            self.mm = MemoryMapAccess(mock_interface)
            mock_interface.read.side_effect = [0x81, 0x54, 0x32, 0x1D]
            m_open = mock_open()
            with patch('COMMON.Device.memory_map_access.open', m_open):
                self.mm.save_settings('settings.txt')
            m_open.assert_called_once_with('settings.txt', 'w')
            handle = m_open()
            handle.write.assert_has_calls([call('TABLE_SEL: 0x81\n'), call('REG_0: 0x54\n'), call('REG_1: 0x32\n'),
                                           call('REG_2: 0x1D\n')])

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    def test_save_specified_settings(self, mock_interface):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'bit_field': {'bf0': {'POR': 0,
                                                                         'register': 'REG_0',
                                                                         'justification': 0,
                                                                         'length': 8,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 'bf1': {'POR': 0,
                                                                         'register': 'REG_1',
                                                                         'justification': 0,
                                                                         'length': 4,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 'bf2': {'POR': 0,
                                                                         'register': 'REG_1',
                                                                         'justification': 4,
                                                                         'length': 4,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 },
                                                   'memory_map': {'TABLE_SEL': {'deviceID': 0xa2,
                                                                                'table': 'Not_tabled',
                                                                                'offset': 0x7f},
                                                                  'REG_0': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x0},
                                                                  'REG_1': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x1},
                                                                  'REG_2': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x2},
                                                                  },
                                                   'test_signals': {}
                                                   }
            self.mm = MemoryMapAccess(mock_interface)
            mock_interface.read.side_effect = [0x54, 0x32, 0x1D]
            m_open = mock_open()
            with patch('COMMON.Device.memory_map_access.open', m_open):
                self.mm.save_settings('settings.txt', ['bf0', 'bf2', 'REG_2'])
            m_open.assert_called_once_with('settings.txt', 'w')
            handle = m_open()
            handle.write.assert_has_calls([call('bf0: 0x54\n'), call('bf2: 0x03\n'), call('REG_2: 0x1D\n')])

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    def test_load_settings(self, mock_interface):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'bit_field': {'bf0': {'POR': 0,
                                                                         'register': 'REG_0',
                                                                         'justification': 0,
                                                                         'length': 8,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 'bf1': {'POR': 0,
                                                                         'register': 'REG_1',
                                                                         'justification': 0,
                                                                         'length': 4,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 'bf2': {'POR': 0,
                                                                         'register': 'REG_1',
                                                                         'justification': 4,
                                                                         'length': 4,
                                                                         'write_access': 'n/a',
                                                                         },
                                                                 },
                                                   'memory_map': {'TABLE_SEL': {'deviceID': 0xa2,
                                                                                'table': 'Not_tabled',
                                                                                'offset': 0x7f},
                                                                  'REG_0': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x0},
                                                                  'REG_1': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x1},
                                                                  'REG_2': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x2},
                                                                  },
                                                   'test_signals': {}
                                                   }
            self.mm = MemoryMapAccess(mock_interface)

            # https://stackoverflow.com/questions/24779893/customizing-unittest-mock-mock-open-for-iteration
            m_open = mock_open(read_data='bf0: 0x54\nbf2: 3\nREG_2: 0x1D\nnon_existent_bf: 2\n')
            m_open.return_value.__iter__ = lambda self: self
            m_open.return_value.__next__ = lambda self: next(iter(self.readline, ''))
            with captured_output() as (out, err):
                with patch('COMMON.Device.memory_map_access.open', m_open):
                    settings = self.mm.load_settings('settings.txt')
            output = out.getvalue().strip()
            self.assertEqual('could not find register non_existent_bf in memory map', output)
            m_open.assert_called_once_with('settings.txt', 'r')
            expected_settings = {'bf0': 0x54, 'bf2': 0x3, 'REG_2': 0x1D}
            self.assertEqual(expected_settings, settings)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    def test_get_non_default_values(self, mock_interface):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'bit_field': {'non_writable_reg': {'POR': 0,
                                                                                      'register': 'REG_0',
                                                                                      'justification': 4,
                                                                                      'length': 1,
                                                                                      'write_access': 'n/a',
                                                                                      },
                                                                 'None_writable': {'POR': 0,
                                                                                   'register': 'REG_1',
                                                                                   'justification': 3,
                                                                                   'length': 1,
                                                                                   'write_access': None,
                                                                                   },
                                                                 'cond_writable': {'POR': 0,
                                                                                   'register': 'REG_1',
                                                                                   'justification': 3,
                                                                                   'length': 1,
                                                                                   'write_access': 'cond',
                                                                                   },
                                                                 'all_writable': {'POR': 0,
                                                                                  'register': 'REG_1',
                                                                                  'justification': 4,
                                                                                  'length': 1,
                                                                                  'write_access': 'ALL',
                                                                                  },
                                                                 'pw0_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 0,
                                                                                  'length': 1,
                                                                                  'write_access': 'PW0',
                                                                                  },
                                                                 'pw1_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 4,
                                                                                  'length': 2,
                                                                                  'write_access': 'pw1',
                                                                                  },
                                                                 'pw2_writable': {'POR': 1,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 1,
                                                                                  'length': 1,
                                                                                  'write_access': 'pw2',
                                                                                  },
                                                                 'pw3_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 2,
                                                                                  'length': 1,
                                                                                  'write_access': 'pw3',
                                                                                  },
                                                                 'unexpected_writable': {'POR': 0,
                                                                                         'register': 'REG_2',
                                                                                         'justification': 5,
                                                                                         'length': 1,
                                                                                         'write_access': 'huh?',
                                                                                         },
                                                                 },
                                                   'memory_map': {'TABLE_SEL': {'deviceID': 0xa2,
                                                                                'table': 'Not_tabled',
                                                                                'offset': 0x7f},
                                                                  'REG_0': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x0},
                                                                  'REG_1': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x1},
                                                                  'REG_2': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x2},
                                                                  },
                                                   'test_signals': {}}
            mock_interface.read.side_effect = [0, 1 << 4, 0, 2 << 4, 0, 1 << 2]
            self.mm = MemoryMapAccess(mock_interface)
            expected = {'all_writable': 1, 'pw1_writable': 2, 'pw2_writable': 0, 'pw3_writable': 1}
            with captured_output() as (out, err):
                self.assertEqual(expected, self.mm.get_non_default_values())
            output = out.getvalue().strip()
            self.assertEqual('......\n4 non default writable registers', output)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    def test_get_non_default_values_from_table_81(self, mock_interface):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'bit_field': {'non_writable_reg': {'POR': 0,
                                                                                      'register': 'REG_0',
                                                                                      'justification': 4,
                                                                                      'length': 1,
                                                                                      'write_access': 'n/a',
                                                                                      },
                                                                 'cond_writable': {'POR': 0,
                                                                                   'register': 'REG_1',
                                                                                   'justification': 3,
                                                                                   'length': 1,
                                                                                   'write_access': 'cond',
                                                                                   },
                                                                 'all_writable': {'POR': 0,
                                                                                  'register': 'REG_1',
                                                                                  'justification': 4,
                                                                                  'length': 1,
                                                                                  'write_access': 'ALL',
                                                                                  },
                                                                 'pw0_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 0,
                                                                                  'length': 1,
                                                                                  'write_access': 'PW0',
                                                                                  },
                                                                 'pw1_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 4,
                                                                                  'length': 2,
                                                                                  'write_access': 'pw1',
                                                                                  },
                                                                 'pw2_writable': {'POR': 1,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 1,
                                                                                  'length': 1,
                                                                                  'write_access': 'pw2',
                                                                                  },
                                                                 'pw3_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 2,
                                                                                  'length': 1,
                                                                                  'write_access': 'pw3',
                                                                                  },
                                                                 'unexpected_writable': {'POR': 0,
                                                                                         'register': 'REG_2',
                                                                                         'justification': 5,
                                                                                         'length': 1,
                                                                                         'write_access': 'huh?',
                                                                                         },
                                                                 },
                                                   'memory_map': {'TABLE_SEL': {'deviceID': 0xa2,
                                                                                'table': 'Not_tabled',
                                                                                'offset': 0x7f},
                                                                  'REG_0': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x0},
                                                                  'REG_1': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x1},
                                                                  'REG_2': {'deviceID': 0xa2,
                                                                            'table': 0x80,
                                                                            'offset': 0x2},
                                                                  },
                                                   'test_signals': {}}
            mock_interface.read.side_effect = [0, 1 << 4]
            self.mm = MemoryMapAccess(mock_interface)
            expected = {'all_writable': 1}
            with captured_output() as (out, err):
                self.assertEqual(expected, self.mm.get_non_default_values([0x81]))
            output = out.getvalue().strip()
            self.assertEqual('..\n1 non default writable register', output)

    @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    def test_get_non_default_values_ignores_tb_and_fsc(self, mock_interface):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'bit_field': {'non_writable_reg': {'POR': 0,
                                                                                      'register': 'REG_0',
                                                                                      'justification': 4,
                                                                                      'length': 1,
                                                                                      'write_access': 'n/a',
                                                                                      },
                                                                 'cond_writable': {'POR': 0,
                                                                                   'register': 'REG_1',
                                                                                   'justification': 3,
                                                                                   'length': 1,
                                                                                   'write_access': 'cond',
                                                                                   },
                                                                 'all_writable': {'POR': 0,
                                                                                  'register': 'REG_1',
                                                                                  'justification': 4,
                                                                                  'length': 1,
                                                                                  'write_access': 'ALL',
                                                                                  },
                                                                 'pw0_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 0,
                                                                                  'length': 1,
                                                                                  'write_access': 'PW0',
                                                                                  },
                                                                 'pw1_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 4,
                                                                                  'length': 2,
                                                                                  'write_access': 'pw1',
                                                                                  },
                                                                 'pw2_writable': {'POR': 1,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 1,
                                                                                  'length': 1,
                                                                                  'write_access': 'pw2',
                                                                                  },
                                                                 'pw3_writable': {'POR': 0,
                                                                                  'register': 'REG_2',
                                                                                  'justification': 2,
                                                                                  'length': 1,
                                                                                  'write_access': 'pw3',
                                                                                  },
                                                                 'tb_writable': {'POR': 0,
                                                                                 'register': 'REG_3',
                                                                                 'justification': 2,
                                                                                 'length': 1,
                                                                                 'write_access': 'pw3',
                                                                                 },
                                                                 'fsc_writable': {'POR': 0,
                                                                                  'register': 'REG_3',
                                                                                  'justification': 1,
                                                                                  'length': 1,
                                                                                  'write_access': 'pw3',
                                                                                  },
                                                                 'unexpected_writable': {'POR': 0,
                                                                                         'register': 'REG_2',
                                                                                         'justification': 5,
                                                                                         'length': 1,
                                                                                         'write_access': 'huh?',
                                                                                         },
                                                                 },
                                                   'memory_map': {'TABLE_SEL': {'deviceID': 0xa2,
                                                                                'table': 'Not_tabled',
                                                                                'offset': 0x7f},
                                                                  'REG_0': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x0},
                                                                  'REG_1': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x1},
                                                                  'REG_2': {'deviceID': 0xa2,
                                                                            'table': 0x81,
                                                                            'offset': 0x2},
                                                                  'REG_3': {'deviceID': 0xf0,
                                                                            'table': 0,
                                                                            'offset': 0x2},
                                                                  },
                                                   'test_signals': {}}
            mock_interface.read.side_effect = [0, 1 << 4, 0, 2 << 4, 0, 1 << 2]
            self.mm = MemoryMapAccess(mock_interface)
            expected = {'all_writable': 1, 'pw1_writable': 2, 'pw2_writable': 0, 'pw3_writable': 1}
            with captured_output() as (out, err):
                self.assertEqual(expected, self.mm.get_non_default_values())
            output = out.getvalue().strip()
            self.assertEqual('......\n4 non default writable registers', output)

    def test__get_dig_debug_signals(self):
        with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
            mock_storable.retrieve.return_value = {'test_signals': {'DIG_DEBUG_TX_ENABLE_SEL': {'address': 0x12,
                                                                                                'fromXLS':
                                                                                                    'tx_enable'},
                                                                    'DIG_DEBUG_APD_PWM_SEL': {'address': 0x13,
                                                                                              'fromXLS': 'apd_pwm'},

                                                                    }}
            self.mm = MemoryMapAccess('mock_interface')
            expected = {'tx_enable': 0x12,
                        'apd_pwm': 0x13}
            self.assertDictEqual(expected, self.mm.dig_debug)

    # @patch('COMMON.Interfaces.USBtoI2C.i2c_win32.Usb2I2c')
    # def test_chip_name(self, mock_interface):
    #     with patch('COMMON.Device.memory_map_access.storable') as mock_storable:
    #         mock_storable.retrieve.return_value = {'bit_field': {},
    #                                                'memory_map': {'TABLE_SEL': {'deviceID': 0xa2,
    #                                                                             'table': 'Not_tabled',
    #                                                                             'offset': 0x7f},
    #                                                               'CHIP_NAME_0': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x80},
    #                                                               'CHIP_NAME_1': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x81},
    #                                                               'CHIP_NAME_2': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x82},
    #                                                               'CHIP_NAME_3': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x83},
    #                                                               'CHIP_NAME_4': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x84},
    #                                                               'CHIP_NAME_5': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x85},
    #                                                               'CHIP_NAME_6': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x86},
    #                                                               'CHIP_NAME_7': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x87},
    #                                                               'CHIP_NAME_8': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x88},
    #                                                               'CHIP_NAME_9': {'deviceID': 0xa2,
    #                                                                               'table': 0xFF,
    #                                                                               'offset': 0x89},
    #                                                               'INTERNAL_VERSION_0': {'deviceID': 0xa2,
    #                                                                                      'table': 0xFF,
    #                                                                                      'offset': 0x8A},
    #                                                               'INTERNAL_VERSION_1': {'deviceID': 0xa2,
    #                                                                                      'table': 0xFF,
    #                                                                                      'offset': 0x8B},
    #                                                               },
    #                                                'test_signals': {}
    #                                                }
    #         self.mm = MemoryMapAccess(mock_interface)
    #         mock_interface.read.side_effect = [0x47, 0x4E, 0x32, 0x38, 0x4C, 0x39, 0x36, 0x5F, 0x41, 0x30, 0x5F, 0x30]
    #         expected_string = 'GN28L96_A0_0'
    #         self.assertEqual(expected_string, self.mm.chip_name)
