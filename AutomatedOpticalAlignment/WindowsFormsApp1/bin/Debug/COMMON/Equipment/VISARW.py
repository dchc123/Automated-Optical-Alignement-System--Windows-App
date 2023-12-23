'''VISARW - Provides VISA Read and Write functions

Requires pyVISA

Version : 00.00.00.00 - Intital functional version
Version : 00.01.00.00 - read_timeout added. Function exposes the VISA timeout parameter to support long reads
'''

import visa
import time
try:
    rm = visa.ResourceManager()
except:
    rm = visa.ResourceManager('@py')

def read(add,data):
    try:
        inst = rm.open_resource(add, write_termination='\n')
        time.sleep(0.01)
        #return( (inst.query(data)).strip('\n') )
        rdata = (inst.query(data))
        #return rdata
        return rdata.strip('\n')
        #return( (inst.query(data)).strip('\n') )
        time.sleep(0.01)
    except:
        print("VISA ERROR")
        return("9E99")

def write(add,data):
    try:
        inst = rm.open_resource(add, write_termination='\n')
        inst.write(data)
        time.sleep(0.01)
    except:
        print("VISA ERROR")

def read_timeout(add,data,timeout=2.0):
    ''' VISA read function which exposes the timeout parameter

    The timeout value is used for the specific read, then returned to the original value'''
    try:
        inst = rm.open_resource(add, write_termination='\n')
        time.sleep(0.01)
        original_timeout = inst.timeout
        inst.timeout = float(timeout)
        time.sleep(0.01)
        rdata = (inst.query(data))
        time.sleep(0.01)
        inst.timeout = float(original_timeout)
        return rdata.strip('\n')
        time.sleep(0.01)
    except:
        print("VISA ERROR")
        return("9E99")
