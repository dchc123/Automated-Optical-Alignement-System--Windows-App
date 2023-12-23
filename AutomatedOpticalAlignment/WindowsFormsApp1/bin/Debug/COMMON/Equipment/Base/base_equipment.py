"""
| $Revision:: 282872                                   $:  Revision of last commit
| $Author:: sgotic@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-10-16 15:38:00 +0100 (Tue, 16 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
import inspect
import logging
import time
from abc import ABC
from COMMON.Interfaces.Base.base_equipment_interface import BaseEquipmentInterface  # Used for typing
from COMMON.Interfaces.VISA.cli_visa import CLIVISA
from COMMON.Utilities.attribute_collector import AttributeCollectorMixin
from COMMON.Utilities.logging_ext import create_stream_handler
from COMMON.Utilities.setattr_mod import BlockSetattrMixin


class _BaseEquipmentCommon(ABC, BlockSetattrMixin, AttributeCollectorMixin):
    """
    Common equipment attributes
    """
    def __init__(self, interface, dummy_mode, name=None, **kwargs):
        """
        Initialize instance

        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param name: driver name that defaults to class name
        :type name: str
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(object_type=_BaseEquipmentCommon,
                         child_type=_BaseEquipmentCommon, ignore_keys=('dummy_mode', 'name'), ignore_private=True,
                         **kwargs)

        self._dummy_mode_dict = {}
        self._interface = interface

        # if a name isn't supplied, use class definition name
        if name:
            self._name = name
        else:
            self._name = type(self).__name__

        self.dummy_mode = dummy_mode

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

    def _read(self, message=None, type_='basic', dummy_type=None, dummy_data=None, timeout=60):
        """
        INTERNAL
        Generic method for reads form interface

        :param message: OPTIONAL message for the read
        :type message: None or str
        :param type_: extended read types
         - 'basic'
         - 'stb_poll_sync'
         - 'srq_sync'
        :type: str
        :param dummy_type: specific dummy type, in case it can't be extracted from docstring
         - 'int'   = 1
         - 'float' = 1.0
         - 'str'   = 'DUMMY_DATA'
         - 'dict'  = {0: 'DUMMY_DATA', 1: 'DUMMY_DATA'}
         - 'list'  = [0, 1]
        :type dummy_type: str
        :param dummy_data: specific dummy data
        :type dummy_data: Any
        :param timeout: time in s to complete read, otherwise raise exception
        :type timeout: int
        :return: return data from interface
        :rtype: str
        :raise TypeError: when supplied message is missing '?' character
        """
        if message is not None and '?' not in message:
            raise TypeError("The read request message must contain '?' character")

        if not self.dummy_mode:
            if message is None:
                data = self._interface.read()
            elif type_ == 'basic':
                data = self._interface.query(message)
            elif type_ == 'stb_poll':
                data = self._interface.query_with_stb_poll(message, timeout=timeout)
            elif type_ == 'stb_poll_sync':
                data = self._interface.query_with_stb_poll_sync(message, timeout=timeout)
            elif type_ == 'srq_sync':
                data = self._interface.query_with_srq_sync(message, timeout=timeout)
            else:
                raise TypeError("Invalid read type: {}".format(type_))
            self._interface.error_checking()
        else:
            stack = inspect.stack()
            property_name = stack[1][3]
            doc_string = getattr(type(self), property_name).__doc__
            return_dict = {
                'int': 1, 'float': 1.0, 'str': 'DUMMY_DATA',
                'dict': {0: 'DUMMY_DATA', 1: 'DUMMY_DATA'}, 'list': [0, 1]
            }

            # If property was set by the user during the dummy_mode session, then return that.
            if property_name in self._dummy_mode_dict.keys():
                data = self._dummy_mode_dict[property_name]
            # elif use a generic statement that was supplied by the user
            elif dummy_data is not None:
                data = dummy_data
            # Else get a generic statement based on user type
            elif dummy_type is not None:
                data = return_dict[dummy_type]
            # Else get a generic statement based on docstring :type:
            elif ':type:' in doc_string:
                doc_string_type_split = doc_string.split(':type:')
                return_type = doc_string_type_split[1].split(':raise')[0].strip()
                data = return_dict[return_type]
            else:
                data = 'DUMMY_DATA'

        return data

    def _write(self, message, type_='basic', dummy_data=None, timeout=60):
        """
        INTERNAL
        Generic method for writes to interface

        :param message: message to write
        :type message: str
        :param type_: extended read types
         - 'basic'
         - 'stb_poll_sync'
         - 'srq_sync'
        :type type_: str
        :param dummy_data: specific dummy data
        :type dummy_data: Any
        :param timeout: time in s to complete read, otherwise raise exception
        :type timeout: int
        """
        if not self.dummy_mode:
            if type_ == 'basic':
                self._interface.write(message)
            elif type_ == 'stb_poll':
                self._interface.write_with_stb_poll(message, timeout=timeout)
            elif type_ == 'stb_poll_sync':
                self._interface.write_with_stb_poll_sync(message, timeout=timeout)
            elif type_ == 'srq_sync':
                self._interface.write_with_srq_sync(message, timeout=timeout)
            else:
                raise TypeError("Invalid query type: {}".format(type_))
            self._interface.error_checking()
        else:
            stack = inspect.stack()
            property_name = stack[1][3]
            key = '{}'.format(property_name)
            split_message = message.split()

            if dummy_data is not None:
                value = dummy_data
            elif len(split_message) > 1:
                value = split_message[-1]
            else:
                self.logger.debug('DEV: property type is not defined in the docstring')
                value = 'DUMMY_DATA'
            self._dummy_mode_dict.update({key: value})

    def sleep(self, seconds):
        """
        Delay execution for a given number of seconds. Skipped if in dummy more.
        The argument may be a floating point number for subsecond precision

        :param seconds: time to sleep
        :type seconds: int or float
        """
        if not self.dummy_mode:
            self.logger.debug("Sleeping for {} seconds".format(seconds))
            time.sleep(seconds)
        else:
            self.logger.debug("DUMMY MODE: Skipping sleep for {} seconds".format(seconds))

    @property
    def interface(self):
        return self._interface


class BaseEquipment(_BaseEquipmentCommon):
    """
    All equipment drivers are derived from this class. It contains all base method
    prototypes that must be implemented by all drivers
    """
    def __init__(self, address, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param address: the GPIB, USB, or TCP/IP address that corresponds to this equipment
        :type address: int or str
        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

        self._address = address
        self._interface_connected = False
        self._configured = False

    @property
    def identity(self):
        """
        **READONLY**
        Retrieve equipment identity. Also retrieve modules and options properties
        if available

        :value: identity
        :type: dict
        """
        idn_data = self._read("*IDN?", dummy_data='{a},{b},{b},{b}'.format(a=self.name, b='DUMMY_DATA'))
        idn_data = idn_data.split(',')

        data = {
            'manufacturer': idn_data[0].strip(),
            'model': idn_data[1].strip(),
            'serial': idn_data[2].strip(),
            'firmware': idn_data[3].strip()
        }

        if hasattr(self, 'modules'):
            data['modules'] = self.modules
        if hasattr(self, 'options'):
            data['options'] = self.options

        for key, value in data.items():
            self.logger.debug("{}: {}".format(key.upper(), value))

        return data

    def _configure(self):
        """
        INTERNAL, VIRTUAL
        Perform driver configuration, such as mapping of physical features to
        specific implementation classes
        """
        pass

    def _configure_interface(self):
        """
        INTERNAL
        Configure the interface for this driver
        """
        if isinstance(self._interface, CLIVISA):
            self._interface.visa_handle.read_termination = '\n'
        self._interface.write('*CLS')
        self._interface.write('*ESE 1')

    def connect(self):
        """
        Connect through interface
        """
        self._unblock_setattr()
        if not self.dummy_mode and not self._interface_connected:
            if self._interface is None:
                raise RuntimeError("Missing communication interface")
            self._interface.open(address=self._address)
            self._configure_interface()
            self._interface_connected = True
        if not self._configured:
            self._configure()
            self._configured = True
        self._block_setattr()

    def disconnect(self):
        """
        Disconnect interface
        """
        if not self.dummy_mode and self._interface_connected:
            self._interface.close()
            self._interface_connected = False

    def reset(self):
        """
        Perform equipment reset, to put device in known preset state
        """
        if not self.dummy_mode:
            self._write("*RST", type_='stb_poll_sync')


class BaseEquipmentBlock(_BaseEquipmentCommon, BlockSetattrMixin, AttributeCollectorMixin):
    """
    All equipment driver sub blocks are derived from this class. It contains all base method
    prototypes that must be implemented by all drivers
    """
    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: communication interface
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

