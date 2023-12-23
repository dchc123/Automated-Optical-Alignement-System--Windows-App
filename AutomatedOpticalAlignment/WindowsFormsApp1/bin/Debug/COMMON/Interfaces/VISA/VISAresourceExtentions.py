"""
| $Revision:: 278787                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-03 01:43:55 +0100 (Tue, 03 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

PyVISA Visa.Resource class extension methods and 2 new exception types

Source:
Rohde & Schwarz: 6. Measurement Synchronization
https://www.rohde-schwarz.com/us/driver-pages/remote-control/measurements-synchronization_231248.html

Version 1.0.0
- Initial version
"""
import os
import time
import visa


class InstrumentErrorException(Exception):
    def __init__(self, errors):
        message = ''
        if errors is not None and len(errors) > 0:
            message = '\n'.join(errors)
        super().__init__(message)


class InstrumentTimeoutException(Exception):
    def __init__(self, message):
        super().__init__(message)


def ext_clear_status(device):
    """
    Clears the instrument io buffers and status
    """
    device.clear()
    device.query('*CLS;*OPC?')


visa.Resource.ext_clear_status = ext_clear_status


def ext_check_error_queue(device, stb_polling):
    """
    Function implemented as defined in the Instrument Error Checking chapter
    """
    errors = []

    if stb_polling:
        stb = int(device.query('*STB?'))
        if (stb & 4) == 0:
            return errors

    while True:
        response = device.query('SYST:ERR?')
        if '"no error"' in response.lower():
            break
        errors.append(response)
        if len(errors) > 50:
            # safety stop
            errors.append('Cannot clear the error queue')
            break
    if len(errors) == 0:
        return None
    else:
        return errors


visa.Resource.ext_check_error_queue = ext_check_error_queue


def ext_wait_for_opc(device):
    """
    This function waits until the instrument responds that the operation is complete
    """
    device.query('*OPC?')


visa.Resource.ext_wait_for_opc = ext_wait_for_opc


def ext_error_checking(device, stb_polling):
    """
    This function calls ReadErrorQueue and raise InstrumentErrorException if any error occurred
    If you want to only check for error without generating the exception, use the
    ext_check_error_queue() function
    """
    errors = device.ext_check_error_queue(stb_polling)
    if errors is not None and len(errors) > 0:
        raise InstrumentErrorException(errors)


visa.Resource.ext_error_checking = ext_error_checking


def ext_query_bin_data_to_file(device, query, pc_file_path):
    """
    This function queries a binary data from the instrument and writes them to a file on your PC
    """
    file_data = device.query_binary_values(query, datatype='s')[0]
    new_file = open(pc_file_path, "wb")
    new_file.write(file_data)
    new_file.close()


visa.Resource.ext_query_bin_data_to_file = ext_query_bin_data_to_file


def ext_send_pc_file_data_to_instrument(device, command, pc_file_path, send_lf_at_the_end=False):
    """
    This function sends a binary data from a PC file to the instrument
    """
    device.send_end = False

    chunk_size = 1000000  # Transfer is done by 1MB chunks
    pc_file = open(pc_file_path, "rb")
    length = os.path.getsize(pc_file_path)
    length_string = str(length)
    len_of_length = len(length_string)
    if len_of_length < 10:
        header = '#{0}{1}'.format(len_of_length, length)
    else:
        header = '#({0})'.format(length)

    command += header
    device.send_end = False
    device.write_raw(command)
    while length > 0:
        if length > chunk_size:
            chunk = pc_file.read(chunk_size)
            device.write_raw(chunk)
            length -= chunk_size
        else:
            chunk = pc_file.read(length)
            length = 0
            if send_lf_at_the_end is True:
                device.write_raw(chunk)
                device.send_end = True
                device.write_raw('\n')
            else:
                device.send_end = True
                device.write_raw(chunk)

    pc_file.close()


visa.Resource.ext_send_pc_file_data_to_instrument = ext_send_pc_file_data_to_instrument


def ext_copy_pc_file_to_instrument(device, pc_file_path, instr_file_path,
                                   send_lf_at_the_end=False):
    """
    This function transfers a file from the PC file to the instrument
    """
    command = ':MMEM:DATA \'{0}\','.format(instr_file_path)
    device.ext_send_pc_file_data_to_instrument(command, pc_file_path, send_lf_at_the_end)


visa.Resource.ext_copy_pc_file_to_instrument = ext_copy_pc_file_to_instrument


def ext_write_with_stb_poll_sync(device, cmd, timeout_ms):
    """
    This function writes a command with STB polling synchronization mechanism
    """
    device.query('*ESR?')
    full_cmd = cmd + ';*OPC'
    device.write(full_cmd)
    exception_msg = 'Writing with OPCsync - Timeout occured. Command: "{}", timeout {} ' \
                    'ms'.format(cmd, timeout_ms)
    _stb_polling(device, exception_msg, timeout_ms)
    device.query('*ESR?')


visa.Resource.ext_write_with_stb_poll_sync = ext_write_with_stb_poll_sync


def _stb_polling(device, exception_msg, timeout_ms):
    """
    STB polling loop internal function
    """
    timeout_secs = timeout_ms / 1000
    start = time.time()
    # STB polling loop
    while True:
        stb = device.read_stb()
        if (stb & 32) > 0:
            break

        elapsed = time.time() - start
        if elapsed > timeout_secs:
            raise InstrumentTimeoutException(exception_msg)
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


def ext_query_with_stb_poll_sync(device, query, timeout_ms):
    """
    This function queries instrument with STB polling synchronization mechanism
    """
    device.query('*ESR?')
    full_cmd = query + ';*OPC'
    device.write(full_cmd)
    exception_msg = 'Querying with OPCsync - Timeout occured. Query: "{}", timeout {} ' \
                    'ms'.format(query, timeout_ms)
    _stb_polling(device, exception_msg, timeout_ms)
    response = device.read()
    device.query('*ESR?')
    return response


visa.Resource.ext_query_with_stb_poll_sync = ext_query_with_stb_poll_sync


def ext_write_with_srq_sync(device, cmd, timeout_ms):
    """
    This function sends a command with and waits for the service request event
    """
    device.query('*ESR?')
    full_cmd = cmd + ';*OPC'
    device.discard_events(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_ALL_MECH)
    device.enable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_QUEUE)
    device.write(full_cmd)
    device.wait_on_event(visa.constants.VI_EVENT_SERVICE_REQ, timeout_ms)
    device.disable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_QUEUE)
    device.query('*ESR?')


visa.Resource.ext_write_with_srq_sync = ext_write_with_srq_sync


def ext_query_with_srq_sync(device, cmd, timeout_ms):
    """
    This function sends a query, waits for the service request event and then reads the response
    """
    device.query('*ESR?')
    full_cmd = cmd + ';*OPC'
    device.discard_events(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_ALL_MECH)
    device.enable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_QUEUE)
    device.write(full_cmd)
    device.wait_on_event(visa.constants.VI_EVENT_SERVICE_REQ, timeout_ms)
    device.disable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_QUEUE)
    response = device.read()
    device.query('*ESR?')
    return response


visa.Resource.ext_query_with_srq_sync = ext_query_with_srq_sync


def ext_write_with_srq_event(device, cmd, handler):
    """
    This function sends a command with the registration of the service request handler
    """
    device.query('*ESR?')
    full_cmd = cmd + ';*OPC'
    device.discard_events(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_ALL_MECH)
    try:
        device.uninstall_handler(visa.constants.VI_EVENT_SERVICE_REQ, handler)
    except visa.UnknownHandler:
        pass

    device.install_handler(visa.constants.VI_EVENT_SERVICE_REQ, handler)
    device.enable_event(visa.constants.VI_EVENT_SERVICE_REQ, visa.constants.VI_HNDLR, 0)
    device.write(full_cmd)


visa.Resource.ext_write_with_srq_event = ext_write_with_srq_event
