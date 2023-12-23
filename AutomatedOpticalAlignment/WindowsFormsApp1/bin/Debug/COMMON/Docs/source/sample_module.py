"""
OPTIONAL Module docstring at the top of the file 'sample_moudle'.
Module usage example::

    >>> from sample_module import ClassName
    >>> sample = ClassName(init_arg1='init_value')
    >>> sample.inst_attr1 = 'value'
    >>> sample.inst_attr2
    'default_value'
"""
from sample_parent_module import ParentClass


class ClassName(ParentClass):
    """
    Class documentation string
    """
    def __init__(self, init_arg1, init_arg2="default_value", **init_remaining_keyword_args):
        """
        OPTIONAL Initialization docstring. It is appended to class docstring in documents
        when available.

        :param init_arg1: initialization argument 1
        :type init_arg1: int
        :param init_arg2: initialization argument 2
        :type init_arg2: str
        :param init_remaining_keyword_args: arbitrary keyword arguments
        :type init_remaining_keyword_args: dict
        """
        super().__init__(**init_remaining_keyword_args)
        self.inst_attr1 = init_arg1
        """Instance Attribute 1 documentation string"""
        self.inst_attr2 = init_arg2
        """Instance Attribute 2 documentation string"""

    @property
    def property1(self):
        """
        Property 1 documentation string

        :value: list or description of possible property 1 values
        :type: <type>
        :raise <ExceptionType>: short explanation for why exception was raised
        """
        return

    @property1.setter
    def property1(self, value):
        """
        :type value: <type>
        :raise <ExceptionType>: raise exception type for corresponding condition in error
        """
        pass

    def method1(self, arg1, arg2="default_value"):
        """
        Method 1 documentation string

        :param arg1: input argument 1 description
        :type arg1: <type>
        :param arg2: input argument 2 description
        :type arg2: <type>
        :return: return data description
        :rtype: <type>
        :raise <ExceptionType1>: short explanation for why exception type 1 was raised
        :raise <ExceptionType2>: short explanation for why exception type 2 was raised
        """
        pass
