from __future__ import absolute_import, division, print_function, unicode_literals # for python 3 compatibility
import ctypes
import time

i2cDll = ctypes.CDLL("T:/Characterisation/PYTHON/COMMON/USBtoI2C.dll")
# i2cDll = ctypes.CDLL("C:/Python/USBtoI2C.dll")
VENDORID = 4292
PRODUCTID = 34006

def clearI2cBus():
    handle = i2cDll.CreateMe_USB()
    e = i2cDll.EnumeratesDevices_USB(handle,VENDORID,PRODUCTID)
    c = i2cDll.Connect_USB(handle,0)
    s = i2cDll.GetSerialNum_USB(handle)
    i2cDll.ClearBus_USB(handle)
    i2cDll.Disconnect_USB(handle)
    i2cDll.DestroyMe_USB(handle)


def Write(add,reg,data):
    handle = i2cDll.CreateMe_USB()
    data_in = ctypes.c_int()
    e = i2cDll.EnumeratesDevices_USB(handle,VENDORID,PRODUCTID)
    c = i2cDll.Connect_USB(handle,0)
    s = i2cDll.GetSerialNum_USB(handle)
    #data_in.value = data
    data_in.value = int(data)
    time.sleep(0.05)
    w = i2cDll.Write1_USB(handle,add,reg,1,ctypes.byref(data_in))
    i2cDll.Disconnect_USB(handle)
    i2cDll.DestroyMe_USB(handle)

def BlockWrite(add,reg,*data):
    handle = i2cDll.CreateMe_USB()
    # data_struct = ctypes.c_int * len(data)
    e = i2cDll.EnumeratesDevices_USB(handle,VENDORID,PRODUCTID)
    c = i2cDll.Connect_USB(handle,0)
    s = i2cDll.GetSerialNum_USB(handle)
    # data_in.value = data
    # check that data is an array of integers with max size = 255
    # if a list of bytes is passed to us, write block data,
    if isinstance(data[0], tuple) or isinstance(data[0], list):
        vals = data[0]
    else:
        vals = data

    # print("data ", data, data_struct)
    data_in = (ctypes.c_ubyte * len(vals))(*vals ) # initialis a ctypes C_int array of length of the data passed to it, with the values pre populated
    #time.sleep(0.05)
    w = i2cDll.Write1_USB(handle,add,reg,len(vals),ctypes.byref(data_in))
    i2cDll.Disconnect_USB(handle)
    i2cDll.DestroyMe_USB(handle)
    return w

def Read(add,reg):
    handle = i2cDll.CreateMe_USB()
    data_out = ctypes.c_ubyte()
    e = i2cDll.EnumeratesDevices_USB(handle,VENDORID,PRODUCTID)
    c = i2cDll.Connect_USB(handle,0)
    s = i2cDll.GetSerialNum_USB(handle)
    r = i2cDll.Read1_USB(handle,add,reg,1,ctypes.byref(data_out))
    time.sleep(0.05)
    x = (data_out.value)
    i2cDll.Disconnect_USB(handle)
    i2cDll.DestroyMe_USB(handle)
    return x

def BlockRead(add,reg,length):
    handle = i2cDll.CreateMe_USB()
    data_out = (ctypes.c_ubyte * length)(*list())
    e = i2cDll.EnumeratesDevices_USB(handle,VENDORID, PRODUCTID)
    c = i2cDll.Connect_USB(handle,0)
    s = i2cDll.GetSerialNum_USB(handle)
    r = i2cDll.Read1_USB(handle,add,reg,length,ctypes.byref(data_out))
    #x = (data_out.value)
    i2cDll.Disconnect_USB(handle)
    i2cDll.DestroyMe_USB(handle)
    return list(data_out)
