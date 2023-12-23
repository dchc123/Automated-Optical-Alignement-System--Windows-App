''' SMU Class - Provides interface to SMU modules

Version : 01.00.00.03
Date : 22/05/17

---
Version notes

01.00.00.03 - Added the following functions

    SetSENSCurrentRange : Sets the measurement current range
    SetFilter : Configure the Filter (average) function
'''

# import os
# os.chdir("C:/PYTHON")
from COMMON.Equipment import VISARW
import time

# Constants
CLASS_VERSION = "01.00.00.03"
CLASS_DATE = "22 MAY 17"
CLASS_AUTHOR = ""

class SMU:

    SMUcount = 0

    def __init__(self,model,add):
        self.model = model
        self.add = add
        SMU.SMUcount += 1

    def displayCount(self):
        print("SMU count %d" % SMU.SMUcount)

    def ON(self):
        if self.model == "K2400":
            VISARW.write(self.add,(":OUTP:STAT 1"))
        else:
            print ("No function defined for this model")

    def OFF(self):
        if self.model == "K2400":
            VISARW.write(self.add,(":OUTP:STAT 0"))
        else:
            print ("No function defined for this model")

    def Vset(self,volts):
        if self.model == "K2400":
            VISARW.write(self.add,(":SOUR:VOLT %s" %volts))
        else:
            print ("No function defined for this model")

    #THIS COMMAND SETS THE PROTECTION VOLTAGE (a.k.a Cmpl voltage) NOT THE SOURCE VOLTAGE
    def Vset_Cmpl(self,volts):
        if self.model == "K2400":
            VISARW.write(self.add,(":SENS:VOLT:PROT %s" %volts))
        else:
            print ("No function defined for this model")



    #THIS COMMAND SETS THE PROTECTION CURRENT NOT THE SOURCE CURRENT
    def IsetP(self,curr):
        if self.model == "K2400":
            VISARW.write(self.add,(":SENS:CURR:PROT %s" %curr))
            #VISARW.write(self.add,(":SOUR:CURR %s" %curr))
        else:
            print ("No function defined for this model")

    #THIS COMMAND SETS THE SOURCE CURRENT
    def Iset(self,curr):
        if self.model == "K2400":
            VISARW.write(self.add,(":SOUR:CURR %s" %curr))
        else:
            print ("No function defined for this model")

    def InitVsource(self,volts,curr,state):
        if self.model == "K2400":
            VISARW.write(self.add,":*RST")
            time.sleep(1)
            VISARW.write(self.add,(":SOUR:FUNC VOLT"))
            VISARW.write(self.add,(":SOUR:VOLT %s" %volts))
            VISARW.write(self.add,":SENS:CURR:RANG 1")
            VISARW.write(self.add,(":SENS:CURR:PROT %s" %curr))
            if state == "ON":
                VISARW.write(self.add,(":OUTP:STAT 1"))
            else:
                VISARW.write(self.add,(":OUTP:STAT 0"))
            VISARW.write(self.add,":INIT")
        else:
            print ("No function defined for this model")

    def InitIsource(self,volts,curr,state):
        if self.model == "K2400":
            VISARW.write(self.add,":*RST")
            time.sleep(1)
            VISARW.write(self.add,(":SOUR:FUNC CURR"))
            VISARW.write(self.add,(":SOUR:CURR %s" %curr))
            VISARW.write(self.add,":SENS:VOLT:RANG 10")
            VISARW.write(self.add,":SOUR:CURR:RANG 10e-3")
            VISARW.write(self.add,(":SENS:VOLT:PROT %s" %volts))
            if state == "ON":
                VISARW.write(self.add,(":OUTP:STAT 1"))
            else:
                VISARW.write(self.add,(":OUTP:STAT 0"))
            VISARW.write(self.add,":INIT")
        else:
            print ("No function defined for this model")

    def Iread(self):
        if self.model == "K2400":
            for i in range(25):
                string = VISARW.read(self.add,(":MEAS:CURR?"))
                i=i+1
                if string != "9E99" and string != "":
                    break
			#string = VISARW.read(self.add,(":MEAS:CURR?"))
            split = (string.split(','))
            curr = split[1]
        else:
            print ("No function defined for this model")
        return curr

    def Vread(self):
        if self.model == "K2400":
            string = VISARW.read(self.add,(":MEAS:VOLT?"))
            split = (string.split(','))
            volts = split[0]
        else:
            print ("No function defined for this model")
        return volts

    def IreadR(self):
        if self.model == "K2400":
            string = VISARW.read(self.add,(":READ?"))
            split = (string.split(','))
            curr = split[1]
        else:
            print ("No function defined for this model")
        return curr

    def SetSENSCurrentRange(self,set_range=0.1):
        ''' Method to set the current range used for current readings'''
        if self.model == "K2400":
            VISARW.write(self.add,(":SENS:CURR:RANG %s" % (set_range)))
        else:
            print ("No function defined for this model")

    def SetFilter(self,state="OFF",filt_type="MOV",filt_count=10):
        if self.model == "K2400":
            if state == "ON":
                VISARW.write(self.add,(":SENS:AVER ON"))
            else:
                VISARW.write(self.add,(":SENS:AVER OFF"))

            if filt_type == "MOV":
                VISARW.write(self.add,(":SENS:AVER:TCON MOV"))
            elif filt_type == "REP":
                VISARW.write(self.add,(":SENS:AVER:TCON REP"))
            else:
                print ("Invalid filt_type parameter setting : %s" % (filt_type))

            VISARW.write(self.add,(":SENS:AVER:COUN %s" % (filt_count)))

        else:
            print ("No function defined for this model")

    def LOCAL_mode(self):  # set Keithey to Local mode #
        if self.model == "K2400":
            VISARW.write(self.add,(":SYST:KEY 23"))
        else:
            print ("No function defined for this model")
