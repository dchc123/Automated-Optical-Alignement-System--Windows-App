.. COMMON Drivers documentation master file, created by
   sphinx-quickstart on Mon Nov 20 15:39:50 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. Custom tags for space
.. |vspace| raw:: latex

   \vspace{5mm}

.. |br| raw:: html

   <br />

Welcome to COMMON User Documentation!
=============================================

Introduction
------------
This document captures each COMMON object's user APIs and their definitions. The COMMON objects are
partitioned into these categories:

* Bench Abstraction
* Equipment Drivers
* Device Drivers
* Standard Procedures
* Interface Drivers
* Mainframe Drivers
* Utilities

Examples
^^^^^^^^
Below is a sample Object definition with its API listings. It comes with descriptive names to
assist in reading:

.. container:: toggle

    .. container:: header

        **[_Show/Hide Code_]**

    |vspace| |br|

    .. automodule:: sample_module
        :noindex:
        :members:
        :undoc-members:
        :show-inheritance:

    |vspace| |br|
    A property API is accessed just like a basic attribute or variable. The position of equal
    sign determines if a value is assigned to, or read from a property

    .. code-block:: python

        from  from sample_module import ClassName

        # Creating instance of class
        sample = ClassName(init_arg1='init_value')

        # Assigning value to property
        sample.property1 = 'value'

        # Read value form property
        data = sample.property1

    |vspace| |br|
    **NOTE: Some properties are read-only, and if user attempts to write to them, an 'AttributeError'
    is raised.**

    When using a method API, it is highly recommended to use arguments with their keywords instead of
    relying on each argument's position. This significantly improves backwards compatibility and
    code readability

    .. code-block:: python

        from sample_module import ClassName

        # Good practice
        sample1 = ClassName(init_arg1='init_value')
        sample1.method1(arg1='value')

        # Bad practice
        sample2 = ClassName('init_value')
        sample2.method1('value')

|vspace| |br|

COMMON Version
----------------
.. toctree::

    COMMON.version

Equipment Drivers
-----------------
.. toctree::
    :maxdepth: 2

    COMMON.Equipment

Device Drivers
--------------
.. toctree::
    :maxdepth: 2

    COMMON.Device

Standard Procedures
-------------------
*Coming Soon*

.. toctree::
    :maxdepth: 2

    COMMON.Procedures

Interface Drivers
-----------------
.. toctree::
    :maxdepth: 2

    COMMON.Interfaces

Mainframe Drivers
-----------------
.. toctree::
    :maxdepth: 2

    COMMON.Mainframes

Benches
-------
.. toctree::
    :maxdepth: 2

    COMMON.Benches

Utilities
---------
.. toctree::
    :maxdepth: 2

    COMMON.Utilities

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
