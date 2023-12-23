''' PSU Class - Provides interface to PSU modules

#Rev 1.0 Initial relase
#Rev 1.1 added support for E3631A
Rev 01.02.00.00 adding support for N7600
Date : 05/05/17

---
Version Notes

01.02.00.00 - Added support for N6700:
    
    __init__ : Added the module parameter as optional, this is used to define which N6700 module is being initialised
    show_module : Prints the module capability i.e Voltage & Current.  Only supports N6732B & N6762A
'''

from COMMON.Equipment import VISARW
import time

# Constants
CLASS_VERSION = "01.02.00.02"
CLASS_DATE = "05 MAY 17"
CLASS_AUTHOR = "Paul Martin"

class PSU:

    PSUcount = 0

    def __init__(self,model,add,module=0):
        self.model = model
        self.add = add
        PSU.PSUcount += 1
        self.module = int(module)
#        print("----------\nPSU Class Version : %s\nPSU Class Date :%s\n"
#             %(CLASS_VERSION, CLASS_DATE))
        if self.model == "N6700":
            # ENSURE OUTPUT COUPLING IS OFF
            #print ("PSU Model N6700 : OUTPUT COUPLING DISABLED")
            VISARW.write(self.add,("OUTP:COUP OFF"))
            if self.module < 1 or self.module > 4:
                print("===  Error  ===\nModel set to N6700\nModule MUST be set to either 1, 2, 3 or 4")


    def displayCount(self):
        print("PSU count %d" % PSU.PSUcount)

    def ON(self):
        if self.model == "K2400":
            VISARW.write(self.add,(":OUTP:STAT 1"))
        elif self.model == "E3640A":
            VISARW.write(self.add,(":OUTP:STAT 1"))
        elif self.model == "6624_1":
            VISARW.write(self.add,("OUT 1,1"))
        elif self.model == "6624_2":
            VISARW.write(self.add,("OUT 2,1"))
        elif self.model == "6624_3":
            VISARW.write(self.add,("OUT 3,1"))
        elif self.model == "6624_4":
            VISARW.write(self.add,("OUT 4,1"))
        elif self.model == "E3631A_6V":
            VISARW.write(self.add,("OUTP:STAT ON"))
        elif self.model == "E3631A_25V":
            VISARW.write(self.add,("OUTP:STAT ON"))
        elif self.model == "N6700":
            if self.module > 0 and self.module < 5:
                VISARW.write(self.add,("OUTP:STAT 1, (@" + str(self.module) + ")"))
            else:
                print("Illegal setting of module parameter, current setting %s" % (self.module))

        else:
            print ("No function defined for this model")

    def OFF(self):
        if self.model == "K2400":
            VISARW.write(self.add,(":OUTP:STAT 0"))
        elif self.model == "E3640A":
            VISARW.write(self.add,(":OUTP:STAT 0"))
        elif self.model == "6624_1":
            VISARW.write(self.add,("OUT 1,0"))
        elif self.model == "6624_2":
            VISARW.write(self.add,("OUT 2,0"))
        elif self.model == "6624_3":
            VISARW.write(self.add,("OUT 3,0"))
        elif self.model == "6624_4":
            VISARW.write(self.add,("OUT 4,0"))
        elif self.model == "E3631A_6V":
            VISARW.write(self.add,("OUTP:STAT OFF"))
        elif self.model == "E3631A_25V":
            VISARW.write(self.add,("OUTP:STAT OFF"))
        elif self.model == "N6700":
            if self.module > 0 and self.module < 5:
                VISARW.write(self.add,("OUTP:STAT 0, (@" + str(self.module) + ")"))
            else:
                print("Illegal setting of module parameter, current setting %s" % (self.module))
        else:
            print ("No function defined for this model")

    def Vset(self,volts):
        if self.model == "K2400":
            VISARW.write(self.add,(":SOUR:VOLT %s" %volts))
        elif self.model == "E3640A":
            VISARW.write(self.add,(":VOLT %s" %volts))
        elif self.model == "6624_1":
            VISARW.write(self.add,("VSET 1,%s" %volts))
        elif self.model == "6624_2":
            VISARW.write(self.add,("VSET 2,%s" %volts))
        elif self.model == "6624_3":
            VISARW.write(self.add,("VSET 3,%s" %volts))
        elif self.model == "6624_4":
            VISARW.write(self.add,("VSET 4,%s" %volts))
        elif self.model == "E3631A_6V":
            VISARW.write(self.add,("INST P6V"))
            VISARW.write(self.add,(":VOLT %s" %volts))
        elif self.model == "E3631A_25V":
            VISARW.write(self.add,("INST P25V"))
            VISARW.write(self.add,(":VOLT %s" %volts))
        elif self.model == "N6700":
            if self.module > 0 and self.module < 5:
                VISARW.write(self.add,(":VOLT %s, (@%s)" % (volts,self.module)))
            else:
                print("Illegal setting of module parameter, current setting %s" % (self.module))
        else:
            print ("No function defined for this model : %s" % self.model)

    def Iset(self,curr):
        if self.model == "K2400":
            VISARW.write(self.add,(":SENS:CURR:PROT %s" %curr))
        elif self.model == "6624_1":
            VISARW.write(self.add,("ISET 1,%s" %curr))
        elif self.model == "6624_2":
            VISARW.write(self.add,("ISET 2,%s" %curr))
        elif self.model == "6624_3":
            VISARW.write(self.add,("ISET 3,%s" %curr))
        elif self.model == "6624_4":
            VISARW.write(self.add,("ISET 4,%s" %curr))
        elif self.model == "E3640A":
            VISARW.write(self.add,(":CURR %s" %curr))
        elif self.model == "E3631A_6V":
            VISARW.write(self.add,("INST P6V"))
            VISARW.write(self.add,(":CURR %s" %curr))
        elif self.model == "E3631A_25V":
            VISARW.write(self.add,("INST P25V"))
            VISARW.write(self.add,(":CURR %s" %curr))
        elif self.model == "N6700":
            if self.module > 0 and self.module < 5:          
                VISARW.write(self.add,(":CURR %s, (@%s)" % (curr,self.module)))
            else:
                print("Illegal setting of module parameter, current setting %s" % (self.module))
        else:
            print ("No function defined for this model")


    def Init(self,volts,curr,state):
        #state = ON or OFF
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
        elif self.model == "E3640A":
            VISARW.write(self.add,":*RST")
            time.sleep(1)
            VISARW.write(self.add,(":VOLT %s" %volts))
            VISARW.write(self.add,(":CURR %s" %curr))
            if state == "ON":
                VISARW.write(self.add,(":OUTP:STAT 1"))
            else:
                VISARW.write(self.add,(":OUTP:STAT 0"))
            x = VISARW.read(self.add,("MEAS:CURR?"))
        elif self.model == "6624_1":
            VISARW.write(self.add,("OUT 1,0"))
            VISARW.write(self.add,("ISET 1,%s" %curr))
            VISARW.write(self.add,("VSET 1,%s" %volts))
            if state == "ON":
                VISARW.write(self.add,("OUT 1,1"))
            else:
                VISARW.write(self.add,("OUT 1,0"))
        elif self.model == "6624_2":
            VISARW.write(self.add,("OUT 2,0"))
            VISARW.write(self.add,("ISET 2,%s" %curr))
            VISARW.write(self.add,("VSET 2,%s" %volts))
            if state == "ON":
                VISARW.write(self.add,("OUT 2,1"))
            else:
                VISARW.write(self.add,("OUT 2,0"))
        elif self.model == "6624_3":
            VISARW.write(self.add,("OUT 3,0"))
            VISARW.write(self.add,("ISET 3,%s" %curr))
            VISARW.write(self.add,("VSET 3,%s" %volts))
            if state == "ON":
                VISARW.write(self.add,("OUT 3,1"))
            else:
                VISARW.write(self.add,("OUT 3,0"))
        elif self.model == "6624_4":
            VISARW.write(self.add,("OUT 4,0"))
            VISARW.write(self.add,("ISET 4,%s" %curr))
            VISARW.write(self.add,("VSET 4,%s" %volts))
            if state == "ON":
                VISARW.write(self.add,("OUT 4,1"))
            else:
                VISARW.write(self.add,("OUT 4,0"))
        elif self.model == "E3631A_6V":
            #VISARW.write(self.add,":*RST")
            time.sleep(1)
            VISARW.write(self.add,("INST P6V"))
            VISARW.write(self.add,(":VOLT %s" %volts))
            VISARW.write(self.add,(":CURR %s" %curr))
        elif self.model == "E3631A_25V":
            #VISARW.write(self.add,":*RST")
            time.sleep(1)
            VISARW.write(self.add,("INST P25V"))
            VISARW.write(self.add,(":VOLT %s" %volts))
            VISARW.write(self.add,(":CURR %s" %curr))
        elif self.model == "N6700":
            if self.module > 0 and self.module < 5:
                VISARW.write(self.add,("OUTP:STAT 0, (@" + str(self.module) + ")"))
                VISARW.write(self.add,(":CURR %s, (@%s)" % (curr,self.module)))
                VISARW.write(self.add,(":VOLT %s, (@%s)" % (volts,self.module)))
                if state == "ON":
                    VISARW.write(self.add,("OUTP:STAT 1, (@" + str(self.module) + ")"))
                else:
                    VISARW.write(self.add,("OUTP:STAT 0, (@" + str(self.module) + ")"))
            else:
                print("Illegal setting of module parameter, current setting %s" % (self.module))
        else:
            print ("No function defined for this model")

    def Iread(self):
        if self.model == "K2400":
            str = VISARW.read(self.add,(":MEAS:CURR?"))
            split = (str.split(','))
            curr = split[1]
        elif self.model == "E3640A":
            curr = VISARW.read(self.add,(":MEAS:CURR?"))
        elif self.model == "6624_1":
            curr = VISARW.read(self.add,("IOUT? 1"))
        elif self.model == "6624_2":
            curr = VISARW.read(self.add,("IOUT? 2"))
        elif self.model == "6624_3":
            curr = VISARW.read(self.add,("IOUT? 3"))
        elif self.model == "6624_4":
            curr = VISARW.read(self.add,("IOUT? 4"))
        elif self.model == "N6700":
            if self.module >= 1 and self.module <=4:          
                curr = VISARW.read(self.add,("MEAS:CURR? (@%s)") % (self.module))
            else:
                print("Illegal setting of module parameter, current setting %s" % (self.module))
        else:
            print ("No function defined for this model")
        return curr

    def show_module(self):
        ''' Method to show the model of the PSU module installed at the initialised address
        '''
        if self.model == "N6700":
            if self.module > 0 and self.module < 5:
                module_type = VISARW.read(self.add,("SYST:CHAN:MOD? (@" + str(self.module) + ")"))
                print("PSU module at address : %s is %s" % (self.add,module_type))
                if module_type == 'N6732B':
                    print("\tCapability : 8V 6.25A 50W")
                elif module_type == 'N6762A':
                    print("\tCapability : 50V 3A 100W")
                else:
                    print("\tCapability : Plese refer to user documentation.")                
        else:
             print ("No function defined for this model")
                
