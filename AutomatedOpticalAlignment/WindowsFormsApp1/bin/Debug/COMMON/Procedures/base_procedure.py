"""
| $Revision:: 282866                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-10-16 13:33:33 +0100 (Tue, 16 Oct 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

Top level Procedure functionality
"""
# Imports
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum


class ProcedureState(Enum):
    """
    Enum that represents the states a procedure can be in at any given time.

    States:
    NOT_STARTED: Procedure has been instantiated but not run.
    NONE_CHECK: Procedure is running the _check_for_none() functions
    REQUIREMENT_CHECK: Procedure is running the _check_requirements() functions
    PRE_TEST: Procedure is running the _pre-test() function
    TEST: Procedure is running the _main() function
    POST_TEST: Procedure is running the _post_main() function()
    COMPLETED: Procedure has completed successfully
    """
    NOT_STARTED = 0
    NONE_CHECK = 1
    REQUIREMENT_CHECK = 2
    SETUP = 3
    PRE_MAIN = 4
    MAIN = 5
    POST_MAIN = 6
    CLEAN_UP = 7
    COMPLETED = 8


class ProcedureData:
    """
    Data Object used to store procedure results.
    """
    def __init__(self):
        self._data_container = {}
        self._data_type = {}

    def add(self, name, value, units=None):
        """
        Creates a new entry in the data container.

        :param name: name or description of the data point being entered
        :type name: str
        :param value: value of the data point
        :type value: float or str or list or tuple
        :param units: units of the value being entered. If none are provided, defaults to 'None'
        :type units: str
        :raise ValueError: exception if the keyword[name] already exist in the dictionary
        """
        if name in self._data_container.keys():
            raise ValueError("{} already exists in the data dictionary.".format(name))
        else:
            self._data_container.update({name: {'value': value, 'units': units}})
            if isinstance(value, list):
                data_type = 'list'
            elif isinstance(value, tuple):
                data_type = 'tuple'
            else:
                data_type = 'single'
            self._data_type.update({name: data_type})
            # TODO: more options can be adder later if needed (support for dictionaries, sets...etc)

    def append(self, name, value, units=None):
        """
        Appends value to data entry associated to 'name' if it already exists, else it creates it (add).
        Appending creates a list of 'data_type". (list of lists, list of single values, list of tuples)

        :param name: name or description of the data point being entered
        :type name: str
        :param value: value of the data point
        :type value: float or str or list or tuple
        :param units: units of the value being entered. If none are provided, defaults to 'None'
        :type units: str
        :raise ValueError: exception if units are not the same as previously added units,
         or appending to a different data type
        """
        if name in self._data_container.keys():

            if self._data_container[name]['units'] == units:
                if isinstance(value, list):  # Enters to check if appending a list to another list or not
                    if self._data_type[name] == 'list':
                        if isinstance(self._data_container[name]['value'][0], list):
                            self._data_container[name]['value'].append(value)
                        else:
                            self._data_container.update(
                                {name: {'value': [self._data_container[name]['value'], value], 'units': units}})
                    else:
                        raise ValueError("Cannot append list to a {}.". format(self._data_type[name]))
                elif isinstance(value, tuple):  # Enters to check if appending a tuple to another tuple or not
                    if self._data_type[name] == 'tuple':
                        if isinstance(self._data_container[name]['value'][0], tuple):
                            self._data_container[name]['value'].append(value)
                        else:
                            self._data_container.update(
                                {name: {'value': [self._data_container[name]['value'], value], 'units': units}})
                    else:
                        raise ValueError("Cannot append tuple to a {}.".format(self._data_type[name]))
                else:   # Enters to check if appending a single value to other single values
                    if self._data_type[name] == 'single':
                        if isinstance(self._data_container[name]['value'], list):
                            self._data_container[name]['value'].append(value)
                        else:
                            self._data_container.update(
                                {name: {'value': [self._data_container[name]['value'], value], 'units': units}})
                    else:
                        raise ValueError("Cannot append a single value to a {}.".format(self._data_type[name]))
            else:
                raise ValueError("Cannot append data with different units than previous units.")

        else:
            self.add(name, value, units)

    def clear(self):
        """
        Clears the data container
        """
        self._data_container.clear()
        self._data_type.clear()

    def delete(self, name):
        """
        Deletes 'name' entry from the data container if it exists

        :param name: name or description of the data to be deleted
        :type name: str
        """
        if name in self._data_container.keys():
            del self._data_container[name]
            del self._data_type[name]

    def get(self):
        """
        :return: collected data dictionary
        :rtype: dict
        """
        return self._data_container.copy()


class BaseProcedureInputsContainer(ABC):
    """
    Base procedure data container class that all procedure containers should be derived from.
    """
    def __init__(self):
        pass

    @abstractmethod
    def _check_requirements(self):
        """
        Contains checks to ensure variables contained within the data object are of the correct type and value.
        """
        pass

    def _check_for_none(self):
        """
        Uses reflection to get a list of variables in the data container and checks to ensure none of them are set
        to None. Raises a ValueError exception if a None variable is encountered.
        """
        variables = vars(self)
        for variable_key, variable_value  in variables.items():
            if not variable_key.startswith('_'):
                if variable_value is None:
                    raise ValueError('Required procedure variable "{0}" has not been set!'
                                     .format(variable_key))


class ProcedureUtilities:
    def __init__(self):
        '''
        Utilities class to house common helper functions to be used in procedures.
        '''
        pass

    def get_timestamp(self):
        """
        Builds a common timestamp string that can be used across all procedures.
        :return: timestamp string in the format YYYY_mm_dd_HH_MM_SS
        :rtype: str
        """
        return datetime.now().strftime('%Y_%m_%d_%H_%M_%S')


class BaseProcedure(ABC):
    """
    Base procedure class that all procedures should be derived from.
    """
    def __init__(self, name=None):
        if name is None:
            self._name = type(self).__name__
        else:
            self._name = name
        self.resources = None
        self.arguments = None
        self.data = ProcedureData()
        self._state = ProcedureState.NOT_STARTED
        self.logger = logging.getLogger(self._name)
        self.utilities = ProcedureUtilities()

    @property
    def name(self):
        """
        ***READONLY***
        :return: returns the name of the procedure
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Sets the name of the procedure.

        :param value: name of the procedure
        :type value: str
        """
        if not isinstance(value, str):
            raise TypeError('Procedure name must be a str!')
        else:
            self._name = value

    @property
    def state(self):
        """
        ***READONLY***

        :return: returns the state of the procedure
        :rtype: any
        """
        return self._state

    def check_requirements(self):
        """
        Calls the _check_requirements methods in the resources and arguments objects that exist within the procedure.
        """
        self.resources._check_requirements()
        self.arguments._check_requirements()

    def check_for_none(self):
        """
        Calls the _check_for_none methods in the resources and arguments objects that exist within the procedure.
        """
        self.resources._check_for_none()
        self.arguments._check_for_none()

    @abstractmethod
    def setup(self):
        """
        Abstract method for the setup method that runs before the pre_main method.
        """
        pass

    @abstractmethod
    def pre_main(self):
        """
        Abstract method for the pre-main method that runs before the main method.
        """
        pass

    @abstractmethod
    def main(self):
        """
        Abstract method for the main method that runs after the pre-main method and before the post-main method
        """
        pass

    @abstractmethod
    def post_main(self):
        """
        Abstract method for the post_main method that runs after the main method has finished executing.
        """
        pass

    @abstractmethod
    def clean_up(self):
        """
        Abstract method for the clean-up method that runs after the post main method.
        """
        pass

    def run(self, run_setup=True, run_pre_main=True, run_post_main=True, run_clean_up=True):
        """
        Executes the procedure.

        Note that all previous run data will be overwritten.
        :param run_setup: whether the setup method should be run before pre_main is executed.
        :type run_setup: bool
        :param run_pre_main: whether the pre-test method should be run before the test is executed.
        :type run_pre_main: bool
        :param run_post_main: whether the post-test method should be run after the test has finished executing.
        :type run_post_main: bool
        :param run_clean_up: whether the clean_up method is run after the post_main method
        :type run_clean_up: bool
        """
        # Clear data object to ensure it's empty
        self.data.clear()
        # Ensure data objects contain no None variables
        self._state = ProcedureState.NONE_CHECK
        self.check_for_none()
        # Ensure data objects contain variables of correct value and type
        self._state = ProcedureState.REQUIREMENT_CHECK
        self.check_requirements()
        # Run setup if requested
        if run_setup:
            self._state = ProcedureState.SETUP
            self.setup()
        # Run pre-test if requested
        if run_pre_main:
            self._state = ProcedureState.PRE_MAIN
            self.pre_main()
        # Run the core procedure logic
        self._state = ProcedureState.MAIN
        self.main()
        # Run post-test if requested
        if run_post_main:
            self._state = ProcedureState.POST_MAIN
            self.post_main()
        # Run clean-up if requested
        if run_clean_up:
            self._state = ProcedureState.CLEAN_UP
            self.clean_up()
        # Set procedure state to completed
        self._state = ProcedureState.COMPLETED
