"""
| $Revision:: 284096                                   $:  Revision of last commit
| $Author:: abouchar@SEMNET.DOM                        $:  Author of last commit
| $Date:: 2018-11-27 12:59:28 +0000 (Tue, 27 Nov 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

For the top level API: See :py:class:`.KeysightN5227A`
::

    >>> from CLI.Equipment.VNA.KeysightN5227A.keysight_n5227a import KeysightN5227A
    >>> VNA = KeysightN5227A('GPIB1::23::INSTR')
    >>> VNA.connect()
    >>> VNA.port_power_coupling = "ENABLE"
    >>> VNA.trigger()
    >>> VNA.new_trace(2,1)
    >>> VNA.select_trace("S21")
    >>> VNA.new_trace(3,1)
    Note that 'new_trace' keeps the last created trace in memory, and uses it if none are provided for other functions
    >>> VNA.delete_trace()
    >>> VNA.save_snp(1,"C:\data\test")
    >>> 'C:\data\test.s1p'
    >>> VNA.save_snp([1,2,3],"C:\data\test")
    >>> 'C:\data\test.s3p'
    >>> VNA.delete_trace("_all_")

For frequency API:
:py:class:`.KeysightN5227AFrequency`
::

    >>> VNA.frequency.start = 100000000
    >>> VNA.frequency.start
    100000000.0

For GuidedCal API:
:py:class:`.KeysightN5227AGuidedCal`
::

    >>> VNA.guided_cal.initiate()
    >>> VNA.guided_cal.number_of_steps
    5
    >>> VNA.guided_cal.select_cal_kit(1, "N4691-60004 ECal")
    >>> VNA.guided_cal.select_connector_type(1, "1.85 mm female")
    >>> VNA.guided_cal.step_description(2)
    'Connect APC 7 Open to port3'
    >>> VNA.guided_cal.measure(3)
    >>> VNA.guided_cal.save("C:\data\Calfile.cal")

For marker API:
:py:class:`.KeysightN5227AMarker`
::

    >>> VNA.marker[1].state = "ENABLE"
    >>> VNA.marker[1].x = 10000000000
    >>> VNA.marker[1].y
    -3.456
    >>> VNA.marker[1].search_target = -4.4
    >>> VNA.marker[1].search('TARG')
    >>> VNA.marker[1].x
    1000000

For port API:
:py:class:`.KeysightN5227APort`
::

    >>> VNA.port[1].rf_power = 1.1
    >>> VNA.port[1].rf_power
    1.1

For sweep API:
:py:class:`.KeysightN5227ASweep`
::

    >>> VNA.sweep.if_bandwidth = 10000
    >>> VNA.sweep.if_bandwidth
    10000

For reference marker API:
:py:class:`.KeysightN5227ARefMarker`
::

    >>> VNA.refmarker.state = "ENABLE"
    >>> VNA.refmarker
    'ENABLE'
    >>> VNA.refmarker.y
    -4.0

"""
import os
from ....Utilities.custom_structures import CustomList
from ..base_vna import BaseVNA
from ..base_vna import BaseVNABlock
from ..base_vna import BaseVNAFrequencyBlock
from ..base_vna import BaseVNAMarkerBlock
from ..base_vna import BaseVNAPortBlock
from ....Interfaces.VISA.cli_visa import CLIVISA


class KeysightN5227A(BaseVNA):
    """
    Driver for Keysight N5227A VNA
    """
    CAPABILITY = {'markers': 10, 'number_of_ports': 4}

    def __init__(self, address, interface=None, dummy_mode=False, **kwargs):
        """
        Initialize instance

        :param address: the address that corresponds to this equipment
        :type address: int or str
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        if interface is None:
            interface = CLIVISA()
        super().__init__(address=address, interface=interface, dummy_mode=dummy_mode, **kwargs)
        self.frequency = KeysightN5227AFrequency(interface=interface, dummy_mode=dummy_mode)
        self.guided_cal = KeysightN5227AGuidedCal(interface=interface, dummy_mode=dummy_mode)
        self.ref_marker = KeysightN5227ARefMarker(interface=interface, dummy_mode=dummy_mode)
        self.sweep = KeysightN5227ASweep(interface=interface, dummy_mode=dummy_mode)
        #  measurement_name is the last created or selected trace
        self.measurement_name = None

        self.marker = CustomList()
        """:type: list of KeysightN5227AMarker"""
        self.port = CustomList()
        """:type: list of KeysightN5227APort"""

        # Keysight N5227A supports 9 markers
        for i in range(1, 10):
            self.marker.append(KeysightN5227AMarker(marker_number=i, interface=interface, dummy_mode=dummy_mode))
        # Keysight N5227A has 4 ports
        for i in range(1, 5):
            self.port.append(KeysightN5227APort(port_number=i, interface=interface, dummy_mode=dummy_mode))

    @property
    def correction_state(self):
        """
        Disable or Enable correction

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read("SENSe:CORRection:STATe?", dummy_data='0').upper()]

    @correction_state.setter
    def correction_state(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'DISABLE': '0',  'ENABLE': '1'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("SENSe:CORRection:STATe %s" % input_dict[value])

    @property
    def get_names_prameters(self):
        """
        Gets all current measurement names and parameters

        :return: returns dictionary containing 2 lists : measurement names and parameters
        :rtype: dict
        """
        csv_string = self._read("calculate:parameter:catalog:extended?").strip().strip('"')

        names_params_list = csv_string.split(",")
        measurement_names = []
        parameters = []

        for i in range(len(names_params_list)):
            if i % 2 == 0:  # check if number is even or odd
                measurement_names.append(names_params_list[i])
            else:
                parameters.append(names_params_list[i])
        return {"measurement_names": measurement_names, "parameters": parameters}

    @property
    def port_power_coupling(self):
        """
        Port RF power coupling state

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
        return output_dict[self._read("SOURce:POWer:COUPle?", dummy_data='0')]

    @port_power_coupling.setter
    def port_power_coupling(self, value):
        """
        :type value: str
        :raise ValueError: value error if input is not 'ENABLE'/'DISABLE'
        """
        value = value.upper()
        input_dict = {'ENABLE': '1', 'DISABLE': '0'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            self._write("SOURce:POWer:COUPle %s" % input_dict[value])

    def apply_calset(self, calset, apply_stimulus=True):
        """
        Selects a calset and turns on correction

        :param calset: calset name
        :type calset: str
        :param apply_stimulus: change stimulus to match those of selected cal set
        :type apply_stimulus: bool
        """
        self._write('SENSe:CORRection:CSET:ACTIvate "%s",%s' % (calset, int(apply_stimulus)))
        self.correction_state = 'ENABLE'

    def delete_markers(self):
        """
        Deletes all markers on the currently selected trace
        """
        self._write("CALCulate:MEASure:MARKer:AOFF")

    def delete_trace(self, measurement_name=None):
        """
        Deletes 1 or all S-parameter measurement trace(s). To delete all traces, specify '_all_' as measurement_name.

        :param measurement_name: measurement name
        :type measurement_name: str
        :raise ValueError: exception if there are no recent measurements in memory,
         or passed measurement name is invalid.
        """
        if measurement_name is None:
            if self.measurement_name is None:
                raise ValueError('There are no recently create measurements to select. Please specify a valid name.')
            else:
                measurement_name = self.measurement_name
                self.measurement_name = None

        if measurement_name == '_all_':
            self._write("CALC:PAR:DEL:ALL", dummy_data="1")
            self.measurement_name = None
        else:
            if measurement_name not in self.get_names_prameters['measurement_names']:
                raise ValueError('%s is not a valid measurement name to delete' % measurement_name)
            else:
                self._write("calculate:parameter:delete '%s'" % measurement_name, dummy_data="1")

    def get_data(self, measurement_name=None, data_type='FDATA'):
        """
        Returns selected measurement data, depending on data type requested.

        :param measurement_name: measurement name
        :type measurement_name: str
        :param data_type: data type to be returned
        :type data_type: str
        :return: data
        :rtype: csv
        :raise ValueError: exception if data_type is not 'FDATA', 'RDATA', 'SDATA', 'FMEM', 'SMEM', 'SDIV'
        """

        input_list = ['FDATA', 'RDATA', 'SDATA', 'FMEM', 'SMEM', 'SDIV']
        if data_type not in input_list:
            raise ValueError('%s is not a valid data type' % data_type)
        else:
            self.select_trace(measurement_name)
            return self._read('CALCulate1:DATA? {}'.format(data_type))

    def measure_x_bandwidth(self, measurement_name=None, marker_no=9, x=-3, ref_freq=1e8):
        """
        Measures the bandwidth on parameter, starting at ref and at x dB

        :param measurement_name: measurement name to make bandwidth measurement on (ex: "CH1_S21_1")
        :type measurement_name: str
        :param marker_no: marker to be used for bandwidth measurement
        :type marker_no: int
        :param x: number of "dB" for bandwidth measurement
        :type x: float
        :param ref_freq: frequency value to set reference marker, default to 100MHz
        :type ref_freq: float
        :return: measured bandwidth (Hz)
        :rtype: float
        :raise ValueError: exception if there are no recent measurements in memory,
         or passed measurement name is invalid.
        """

        if measurement_name is None:
            if self.measurement_name is None:
                raise ValueError('There are no recently create measurements to select. Please specify valid name.')
            else:
                measurement_name = self.measurement_name

        measurement_names = self.get_names_prameters["measurement_names"]
        if measurement_name not in measurement_names:
            raise ValueError("Parameter %s was not found" % measurement_name)

        self.select_trace(measurement_name)

        marker_previous = self.marker[marker_no].state
        ref_marker_previous = self.ref_marker.state

        self.ref_marker.state = "ENABLE"
        self.marker[marker_no].state = "ENABLE"
        self.ref_marker.x = ref_freq
        self.marker[marker_no].x = ref_freq
        self.marker[marker_no].delta_state = "ENABLE"
        self.marker[marker_no].search_target = x
        self.marker[marker_no].search('RTAR')
        bandwidth = self.marker[marker_no].x

        self.marker[marker_no].state = marker_previous
        self.ref_marker.state = ref_marker_previous

        return bandwidth

    def new_trace(self, out_port, in_port, measurement_name=None):
        """
        Creates and displays a new S-parameter measurement trace.
        Function returns measurement name. If a measurement name is passed, a trace number will be
        appended to ensure it's uniqueness.
        Else, it will be defined as : "CH1_S[out_port][in_port]_[trace_number]"

        :param in_port: input port of measurement
        :type in_port: str or int
        :param out_port: output port of measurement
        :type out_port: str or int
        :param measurement_name: measurement name
        :type measurement_name: str
        :return: constructed measurement name to use in 'select_trace' or 'delete_trace' methods (ex: CH1_21_2)
        :rtype: str
        """
        in_port = str(in_port)
        out_port = str(out_port)

        trace_number = int(self._read("DISPlay:WINDow:TRACe:NEXT?", dummy_data='1'))

        if measurement_name is not None:
            self.measurement_name = measurement_name + "_" + str(trace_number)
        else:
            self.measurement_name = "CH1_S" + out_port + in_port + "_" + str(trace_number)

        parameter = "'S" + out_port + "_" + in_port + "'"
        self._write("CALC:PAR:EXT %s, %s" % ("'" + self.measurement_name + "'", parameter), dummy_data='1')
        self._write("display:window:trace%s:feed %s" % (trace_number, "'" + self.measurement_name + "'"),
                    dummy_data='1')

        return self.measurement_name

    def save_snp(self, ports, filename, blocking=True):
        """
        Saves snp data file. File name must not have extension.

        :param ports: single port or list containing port numbers to save
        :type ports: int or list of int
        :param filename: path and file name. Path is relative to VNA PC
        :type filename: str
        :param blocking: blocking call
        :type blocking: bool
        :return: Returns the file path with the extension
        :rtype: str
        """

        orig = self._interface.visa_handle.read_termination
        self._interface.visa_handle.read_termination = None

        temp_dir = 'D:\\tempdir'
        self._write(":MMEMory:MDIRectory '{}'".format(temp_dir))
        temp_fname = temp_dir + '\\temp_file'

        if isinstance(ports, int):
            ports = [ports]
        port_str = ','.join(map(str, ports))
        ext = ".s%sp" % len(ports)
        temp_fname = temp_fname + ext
        filename = filename + ext

        if blocking:
            self._write("CALCulate1:MEASure:DATA:SNP:PORTs:SAVE '%s','%s'" %
                        (port_str, temp_fname), type_='stb_poll_sync')
        else:
            self._write("CALCulate1:MEASure:DATA:SNP:PORTs:SAVE '%s','%s'" % (port_str, temp_fname))

        self._write(':FORMat:DATA ASCII,0')

        # Example returned from ":MMEMory:TRANsfer?" :
        # #210ABCDE+WXYZ<nl><end>
        # Where:
        # # - always sent before definite block data
        # 2 - specifies that the byte count is two digits (2)
        # 10 - specifies the number of data bytes that will follow, not counting <NL><END>
        # ABCDE+WXYZ - 10 digits of data
        # <NL><END> - always sent at the end of block data

        self._interface.write(":MMEMory:TRANsfer? '{}'".format(temp_fname))
        # Throwing away '#' and calculating amount of bytes to read
        bytes_to_read = int(self._interface.visa_handle.read_bytes(int(self._interface.visa_handle.read_bytes(2)[1:2])))
        data = self._interface.visa_handle.read_bytes(bytes_to_read)
        # read and discard termination character
        self._interface.visa_handle.read_bytes(1)

        fh = open(filename, "wb")
        fh.write(data)
        self.logger.info("File saved to {}".format(os.path.realpath(fh.name)))
        fh.close()
        # delete temp file to clean up
        self._write(":MMEMory:DELete '{}'".format(temp_fname))

        self._interface.visa_handle.read_termination = orig

        return filename

    # could be used eventually if needed.
    # def save_picture_vna(self, file, blocking=True):
    #     """
    #     Saves a picture of the network analyzer screen. File name must not have extension.
    #
    #     :param file: path and file name. Path is relative to VNA PC
    #     :type file: str
    #     :param blocking: blocking call
    #     :type blocking: bool
    #     :return: Returns the file path with the extension
    #     :rtype: str
    #     """
    #
    #     file = file + ".png"
    #     if blocking:
    #         self._write("HCOPy:FILE '%s'" % file, type_='stb_poll_sync')
    #     else:
    #         self._write("HCOPy:FILE '%s'" % file)
    #
    #     return file

    def save_picture(self, filename):
        """
        Saves a picture of the network analyzer screen to the PC running CLI.
        Saves as a .png file.

        :param filename: path and file name. Path is relative to PC running CLI.
        :type filename: str
        """

        orig = self._interface.visa_handle.read_termination
        self._interface.visa_handle.read_termination = None

        image_data = self._interface.visa_handle.query_binary_values('HCOPY:SDUMP:DATA?', datatype='s')
        if not filename.endswith('.png'):
            filename += '.png'
        fh = open(filename, "wb")
        fh.write(image_data[0])
        self.logger.info("Image saved to {}".format(os.path.realpath(fh.name)))
        fh.close()

        self._interface.visa_handle.read_termination = orig

    def select_trace(self, measurement_name=None):
        """
        Selects an S-parameter measurement traces. measurement_name is constructed and returned in "new_trace" method
        :py:class:`.new_trace`

        :param measurement_name: measurement name
        :type measurement_name: str
        :raise ValueError: exception if there are no recent measurements in memory,
         or passed measurement name is invalid.
        """
        if measurement_name is None:
            if self.measurement_name is None:
                raise ValueError('There are no recently create measurements to select. Please specify a valid name.')
            else:
                measurement_name = self.measurement_name

        if measurement_name not in self.get_names_prameters['measurement_names']:
            raise ValueError('%s is not a valid measurement name to select' % measurement_name)
        else:
            self._write("calculate:parameter:select '%s'" % measurement_name)
            self.measurement_name = measurement_name

    def trigger(self, blocking=True):
        """
        Triggers a single measurement sweep. Sweep takes variable amount of time to complete. Once
        completed, you can make measurements on the available traces.

        :param blocking: blocking call
        :type blocking: bool
        """
        if blocking:
            self._write("SENSe:SWEep:MODE SINGle", type_='stb_poll_sync')
        else:
            self._write("SENSe:SWEep:MODE SINGle")


class KeysightN5227AFrequency(BaseVNAFrequencyBlock):
    """
    Keysight N5227A Frequency driver
    """

    CAPABILITY = {'frequency_range': {'min': 1e7, 'max': 70e9}}

    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def start(self):
        """
        :value: start frequency (Hz)
        :type: float
        :raise ValueError: Exception if range value is invalid
        """
        return float(self._read("SENSe:FREQuency:STARt?", dummy_data=1e5))
    
    @start.setter
    def start(self, value):
        """
        :type value: float
        :raise ValueError: Exception if range value is invalid
        """

        range_min = self.CAPABILITY['frequency_range']['min']
        range_max = self.CAPABILITY['frequency_range']['max']

        if range_min <= value <= range_max:
            self._write("SENSe:FREQuency:STARt %s" % value)
        else:
            raise ValueError("%s is an invalid start frequency entry. See valid range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))
        
    @property
    def stop(self):
        """
        :value: stop frequency (Hz)
        :type: float
        :raise ValueError: Exception if range value is invalid
        """
        return float(self._read("SENSe:FREQuency:STOP?", dummy_data=5e10))

    @stop.setter
    def stop(self, value):
        """
        :type value: float
        :raise ValueError: Exception if range value is invalid
        """
        range_min = self.CAPABILITY['frequency_range']['min']
        range_max = self.CAPABILITY['frequency_range']['max']

        if range_min <= value <= range_max:
            self._write("SENSe:FREQuency:STOP %s" % value)
        else:
            raise ValueError("%s is an invalid stop frequency entry. See valid range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))

    @property
    def span(self):
        """
        :value: frequency span (Hz)
        :type: float
        """
        return float(self._read("SENSe:FREQuency:SPAN?", dummy_data=5e10))

    @span.setter
    def span(self, value):
        """
        :type value: float
        """
        self._write("SENSe:FREQuency:SPAN %s" % value)

    @property
    def center(self):
        """
        :value: center frequency (Hz)
        :type: float
        :raise ValueError: Exception if range value is invalid
        """
        return float(self._read("SENSe:FREQuency:CENTer?", dummy_data=5e9))

    @center.setter
    def center(self, value):
        """
        :type value: float
        :raise ValueError: Exception if range value is invalid
        """
        range_min = self.CAPABILITY['frequency_range']['min']
        range_max = self.CAPABILITY['frequency_range']['max']

        if range_min <= value <= range_max:
            self._write("SENSe:FREQuency:CENTer %s" % value)
        else:
            raise ValueError("%s is an invalid center frequency entry. See valid range."
                             "(min:%s|max:%s)" % (value, range_min, range_max))


class KeysightN5227AGuidedCal(BaseVNABlock):
    """
    Keysight N5227A Guided Calibration diver
    """

    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def number_of_steps(self):
        """
        ***READONLY***
        Returns number of steps for selected calibration

        :value: number of steps
        :type: int
        """
        return int(self._read("SENSe:CORRection:COLLect:GUIDed:STEPs?"))

    def available_cal_kits(self, conn_type):
        """
        ***READONLY***
        Returns available cal kit for selected connector type

        :param conn_type: connector type
        :type conn_type: str
        :returns: available cal kits for selected connector type
        :rtype: list of str
        """
        return self._read("SENSe:CORRection:COLLect:GUIDed:CKIT:CATalog? '%s'" % conn_type,
                          dummy_data="N4691-60004 ECal,N4691-60001 ECal").split(",")

    @property
    def available_connector_type(self):
        """
        ***READONLY***
        Returns connector types available to select

        :value: Available connector types
        :type: list of str
        """
        return self._read("SENSe:CORRection:COLLect:GUIDed:CONNector:CATalog?",
                          dummy_data="1.85 mm female,2.92 mm male").split(",")

    def step_description(self, step_number):
        """
        Returns description of "step_number" calibration step

        :param step_number: number of current calibration step
        :type step_number: int
        :return: step description
        :rtype: str
        """
        return self._read("SENSe:CORRection:COLLect:GUIDed:DESCription? %s" % step_number,
                          dummy_data='Connect APC 7 Open to port3')

    def initiate(self):
        """
        Initiate guided calibration
        """
        self._write("SENSe:CORRection:COLLect:GUIDed:INITiate")

    def measure(self, step_number):
        """
        Measure given calibration step

        :param step_number: number of current calibration step
        :type step_number: int
        """
        self._write("SENSe:CORRection:COLLect:GUIDed:ACQuire STAN%s" % step_number, type_='stb_poll_sync')

    def select_cal_kit(self, port_number, cal_kit):
        """
        Select cal kit to be used in guided calibration.
        For available cal kit selection, see this property :
        :py:class:`.available_cal_kits`

        :param port_number: port number
        :type port_number: int
        :param cal_kit: calibration kit used
        :type cal_kit: str
        """
        self._write("SENSe:CORRection:COLLect:GUIDed:CKIT:PORT%s '%s'" % (port_number, cal_kit))

    def select_connector_type(self, port_number, conn_type):
        """
        Select connector type to be used in guided calibration.
        For available cal kit selection, see this property :
        :py:class:`.available_connector_type`

        :param port_number: port number
        :type port_number: int
        :param conn_type: connector type
        :type conn_type: str
        """
        self._write("SENSe:CORRection:COLLect:GUIDed:CONN:PORT%s '%s'" % (port_number, conn_type))

    def save(self, path_filename=None):
        """
        Save guided calibration results

        :param path_filename: path of location to save file, with ".cal" extension
        :type path_filename: str
        """
        self._write("SENSe:CORRection:COLLect:GUIDed:SAVE:CSET", type_='stb_poll_sync')
        if path_filename is not None:
            self._write("MMEMory:STORe '%s'" % path_filename, type_='stb_poll_sync')


class KeysightN5227AMarker(BaseVNAMarkerBlock):
    """
    Keysight N5227A Marker driver
    """
    CAPABILITY = {
        'search_functions': ['MAX', 'MIN', 'RPE', 'LPE', 'NPE', 'TARG', 'LTAR', 'RTAR', 'COMP']
    }

    def __init__(self, marker_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param marker_number: the marker number
        :type marker_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._marker_number = marker_number

    @property
    def _selected_trace(self):
        """
        ***READONLY***
        Returns True if a trace is selected, else returns false

        :value: selected
        :type: bool
        """
        if self._read("calculate:parameter:select?").strip('"'):
            return True
        else:
            return False

    @property
    def delta_state(self):
        """
        Disable or Enable delta marker state.
        Specifies whether marker is relative to the Reference marker or absolute

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        :raise ValueError: exception if marker is not enabled.
        """
        if self.state == 'ENABLE':
            output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
            return output_dict[self._read("CALCulate:MARKer%s:DelTa?" % self._marker_number, dummy_data='OFF').upper()]
        else:
            raise ValueError('Marker %s is not enabled.' % self._marker_number)

    @delta_state.setter
    def delta_state(self, value):
        """
        :type value: str
        :raise ValueError: value error if input is not 'ENABLE'/'DISABLE'
        """
        value = value.upper()
        input_dict = {'DISABLE': '0', 'ENABLE': '1'}
        if value not in input_dict.keys():
            raise ValueError('Please specify either "ENABLE" or "DISABLE"')
        else:
            if value == 'ENABLE':
                self._write("CALCulate:MARKer:REFerence:STATe 1")
            self._write("CALCulate:MARKer%s:DELTa %s" % (self._marker_number, input_dict[value]))

    @property
    def state(self):
        """
        Disable or Enable marker

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        if self._selected_trace:
            output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
            return output_dict[self._read("CALCulate:MARKer%s?" % self._marker_number, dummy_data='OFF').upper()]
        else:
            raise ValueError('No traces are selected')

    @state.setter
    def state(self, value):
        """
        :type value: str
        """
        value = value.upper()
        input_dict = {'DISABLE': '0',  'ENABLE': '1'}
        if self._selected_trace:
            if value not in input_dict.keys():
                raise ValueError('Please specify either "ENABLE" or "DISABLE"')
            else:
                self._write("CALCulate:MARKer%s %s" % (self._marker_number, input_dict[value]))
        else:
            raise ValueError('No traces are selected')

    @property
    def search_target(self):
        """
        Target value (y) for specified marker, when doing target searches ('TARG', 'LTAR', 'RTAR').

        :value: search marker (y axis) target value
        :type: float
        """
        return float(self._read("CALCulate:MARKer%s:TARGet:VALue?" % self._marker_number))

    @search_target.setter
    def search_target(self, value):
        """
        :type value: float
        """
        self._write("CALCulate:MARKer%s:TARGet:VALue %s" % (self._marker_number, value))

    @property
    def x(self):
        """
        :value: x
        :type: float
        :raise ValueError: exception if marker is not enabled.
        """
        if self.state == 'ENABLE':
            return float(self._read("CALCulate:MARKer%s:x?" % self._marker_number))
        else:
            raise ValueError('Marker %s is not enabled.' % self._marker_number)

    @x.setter
    def x(self, value):
        """
        :type value: float
        """
        self.state = 'ENABLE'
        self._write("CALCulate:MARKer%s:x %s" % (self._marker_number, value))

    @property
    def y(self):
        """
        READONLY

        :value: y
        :type: float
        :raise ValueError: exception if marker is not enabled.
        """
        if self.state == 'ENABLE':
            return float(self._read("CALCulate:MARKer%s:y?" % self._marker_number).split(',')[0])
        else:
            raise ValueError('Marker %s is not enabled.' % self._marker_number)

    def search(self, function):
        """
        Executes selected search function

        :param function: - 'MAX' - finds the highest value
                         - 'MIN' - finds the lowest value
                         - 'RPE' - finds the next valid peak to the right
                         - 'LPE' - finds the next valid peak to the left
                         - 'NPE' - finds the next highest value among the valid peaks
                         - 'TARG' - finds the target value to the right,wraps around left
                         - 'LTAR' - finds the next target value to the left of the marker
                         - 'RTAR' - finds the next target value to the right of the marker
                         - 'COMP' - finds the compression level on a power-swept S21 trace.
        :type function: str
        :raise ValueError: value error if function is not defined
        """
        input_list = self.CAPABILITY['search_functions']
        if function not in input_list:
            raise ValueError('Please a function in this list %s' % input_list)
        else:
            self._write("CALCulate:MARKer%s:FUNCtion:EXECute %s" % (self._marker_number, function))


class KeysightN5227APort(BaseVNAPortBlock):
    """
    Keysight N5227A Port driver
    """

    CAPABILITY = {'rf_power': {'min': -30, 'max': 30}}

    def __init__(self, port_number, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param port_number: the port number of the VNA
        :type port_number: int
        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)
        self._port_number = port_number

    @property
    def rf_power(self):
        """
        :value: Port RF power level (dBm)
        :type: float
        :raise ValueError: Exception if range value is invalid
        """
        return float(self._read(":SOURce:POW%s?" % self._port_number, dummy_data="1dBm")
                     .strip(" dBm"))

    @rf_power.setter
    def rf_power(self, value):
        """
        :type: float
        :raise ValueError: Exception if range value is invalid
        """
        range_min = self.CAPABILITY['rf_power']['min']
        range_max = self.CAPABILITY['rf_power']['max']

        if range_min <= value <= range_max:
            self._write(":SOURce:POW%s %s" % (self._port_number, value), dummy_data=str(value))
        else:
            raise ValueError("%s is an invalid RF Power entry. See valid range.(min:%s|max:%s)"
                             % (value, range_min, range_max))


class KeysightN5227ARefMarker(BaseVNABlock):
    """
    Keysight N5227A Reference marker driver
    """

    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def _selected_trace(self):
        """
        ***READONLY***
        Returns True if a trace is selected, else returns false

        :value: selected
        :type: bool
        """
        if self._read("calculate:parameter:select?").strip('"'):
            return True
        else:
            return False

    @property
    def state(self):
        """
        Disable or Enable the reference marker

        :value: - 'DISABLE'
                - 'ENABLE'
        :type: str
        """
        if self._selected_trace:
            output_dict = {'0': 'DISABLE', '1': 'ENABLE'}
            return output_dict[self._read("CALCulate:MARKer:REFerence:STATe?", dummy_data='0').upper()]
        else:
            raise ValueError('No traces are selected')

    @state.setter
    def state(self, value):
        """
        :type value: str
        """
        input_dict = {'DISABLE': '0',  'ENABLE': '1'}
        value = value.upper()
        if self._selected_trace:
            if value not in input_dict.keys():
                raise ValueError('Please specify either "ENABLE" or "DISABLE"')
            else:
                self._write("CALCulate:MARKer:REFerence:STATe %s" % (input_dict[value]))
        else:
            raise ValueError('No traces are selected')

    @property
    def x(self):
        """
        :value: x
        :type: float
        :raise ValueError: exception if reference marker is not enabled.
        """
        if self.state == 'ENABLE':
            return float(self._read("CALCulate:MARKer:REFerence:X?"))
        else:
            raise ValueError('Reference marker is not enabled')

    @x.setter
    def x(self, value):
        """
        :type: float
        """
        self.state = 'ENABLE'
        self._write("CALCulate:MARKer:REFerence:X %s" % value)

    @property
    def y(self):
        """
        READONLY

        :value: y
        :type: float
        :raise ValueError: exception if reference marker is not enabled.
        """
        if self.state == 'ENABLE':
            return float(self._read("CALCulate:MARKer:REFerence:Y?").split(',')[0])
        else:
            raise ValueError('Reference marker is not enabled')


class KeysightN5227ASweep(BaseVNABlock):
    """
    Keysight N5227A Sweep driver
    """

    CAPABILITY = {'if_bandwidth': {'min': 1, 'max': 15e6}}

    def __init__(self, interface, dummy_mode, **kwargs):
        """
        Initialize instance

        :param interface: interface to equipment
        :type interface: BaseEquipmentInterface
        :param dummy_mode: specifies whether or not the driver is in dummy mode
        :type dummy_mode: bool
        :param kwargs: arbitrary keyword arguments
        :type kwargs: dict
        """
        super().__init__(interface=interface, dummy_mode=dummy_mode, **kwargs)

    @property
    def points(self):
        """
        :value: number of data points for the measurement
        :type: int
        """
        return int(float(self._read("SENSe:SWEep:POINts?")))

    @points.setter
    def points(self, value):
        """
        :type value: int
        """
        self._write("SENSe:SWEep:POINts %s" % value)

    @property
    def step_size(self):
        """
        :value: frequency step size (Hz)
        :type: int
        """
        return int(float(self._read("SENSe:SWEep:STEP?")))

    @step_size.setter
    def step_size(self, value):
        """
        :type value: int
        """
        self._write("SENSe:SWEep:STEP %s" % value)

    @property
    def if_bandwidth(self):
        """
        When setting IF Bandwidth, VNA chooses closest available value.

        :value: IF bandwidth (Hz)
        :type: int
        :raise ValueError: Exception if range value is invalid
        """
        return int(float(self._read("SENSe:BANDwidth:RESolution?")))

    @if_bandwidth.setter
    def if_bandwidth(self, value):
        """
        :type value: int
        :raise ValueError: Exception if range value is invalid
        """
        range_min = self.CAPABILITY['if_bandwidth']['min']
        range_max = self.CAPABILITY['if_bandwidth']['max']

        if range_min <= value <= range_max:
            self._write("SENSe:BANDwidth:RESolution %s" % value)
        else:
            raise ValueError("%s is an invalid IF Bandwidth entry. See valid range.(min:%s|max:%s)"
                             % (value, range_min, range_max))

