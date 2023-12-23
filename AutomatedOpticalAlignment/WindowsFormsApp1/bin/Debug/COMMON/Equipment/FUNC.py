import VISARW
import time

class FUNC:

    FUNCcount = 0

    def __init__(self,model,add):
        self.model = model
        self.add = add
        FUNC.FUNCcount += 1

    def displayCount(self):
        print("FUNC count %d" % FUNC.FUNCcount)

    def RESET(self):
        VISARW.write(self.add,("*RST"))
        return VISARW.write(self.add,(";*OPC?"))

    def AUT(self):
        VISARW.write(self.add,("*AUT"))

    def TRG(self):
        VISARW.write(self.add,("*TRG"))

    def OPC(self):
        return VISARW.write(self.add,(";*OPC?"))

    def PULSE(self,Period,Hilevel,LoLevel,Width,EdgeTime):
        if self.model == "33220A":
            VISARW.write(self.add,("function PULSe"))
            time.sleep(0.1)
            VISARW.write(self.add,("pulse: period %s" %(Period)))
            time.sleep(0.1)
            VISARW.write(self.add,("PULSe:width %s" %(Width)))
            time.sleep(0.1)
            VISARW.write(self.add,("voltage:low %s" %(LoLevel)))
            time.sleep(0.1)
            VISARW.write(self.add,("voltage:high %s" %(Hilevel)))
            time.sleep(0.1)
            VISARW.write(self.add,("FUNCtion:PULSe:TRANsition %s" %(EdgeTime)))

    def SQUARE(self,DutyCycl,Hilevel,LoLevel,Freq):
        if self.model == "33220A":
            VISARW.write(self.add,("FUNC SQU"))
            time.sleep(0.1)
            VISARW.write(self.add,("FUNC:SQU:DCYC %s" %(DutyCycl)))
            time.sleep(0.1)
            VISARW.write(self.add,("FREQ %s" %(Freq)))
            time.sleep(0.1)
            VISARW.write(self.add,("VOLT:HIGH %s" %(Hilevel)))
            time.sleep(0.1)
            VISARW.write(self.add,("VOLT:LOW %s" %(LoLevel)))
            time.sleep(0.1)

    def ARB(self,Hilevel,LoLevel,frequency,values):
        if self.model == "33220A":
            # output the user funtion defined above
            VISARW.write(self.add,("FUNC:SHAPe USER"))
            # use byte SWAP
            VISARW.write(self.add,("FORM:BORD SWAP"))
            VISARW.write(self.add,("OUTPut:LOAD INF"))
            # define low and high Voltage
            # the low voltage will be output with a dac value of -8192
            VISARW.write(self.add,("VOLT:LOW %s" %(LoLevel)))
            # the high voltage will be output with a value of +8192
            VISARW.write(self.add,("VOLT:HIGH %s" %(Hilevel)))
            # define the frequency of the waveform
            VISARW.write(self.add,("OUTPut:LOAD INF"))
            VISARW.write(self.add,("FREQuency %s" %(frequency)))
            # define the arb user waveform
            val_string = ""
            for val in values:
                val_string += ", %s" %(val)
            # print("DATA:DAC VOLATILE, #%s%s" %(len(str(len(values)*2)),len(values)*2))
            print("DATA VOLATILE%s" %(val_string))
            # VISARW.write(self.add,("DATA:DEL VOLATILE"))
            # VISARW.write(self.add,("DATA:DAC VOLATILE, #%s%s" %(len(str(len(values))),len(values))))
            VISARW.write(self.add,("DATA VOLATILE%s" %(val_string)))
            print("wrote data:dac volitile. %s" %(self.OPC()))
            # use the VOLATILE waveform
            # VISARW.write(self.add,("DATA:COPY tims, VOLATILE"))
            VISARW.write(self.add,("FUNC:USER VOLATILE"))
            print("wrote FUNC:USER VOLATILE. %s" %(self.OPC()))
            print("FUNC:USER? %s" %(VISARW.read(self.add,("FUNC:USER?"))))
            print("DATA:CATalog? %s" %(VISARW.read(self.add,("DATA:CATalog?"))))
            print("DATA:ATTRibute:POINts? VOLATILE %s" %(VISARW.read(self.add,("DATA:ATTRibute:POINts? VOLATILE"))))

    def UPDATE_ARB_VALUES(self,values):
        if self.model == "33220A":
            # define the arb user waveform
            val_string = ""
            for val in values:
                val_string += ", %s" %(val)
            # print("DATA:DAC VOLATILE, #%s%s" %(len(str(len(values)*2)),len(values)*2))
            print("DATA VOLATILE%s" %(val_string))
            # VISARW.write(self.add,("DATA:DEL VOLATILE"))
            # VISARW.write(self.add,("DATA:DAC VOLATILE, #%s%s" %(len(str(len(values))),len(values))))
            VISARW.write(self.add,("DATA VOLATILE%s" %(val_string)))
            print("wrote data:dac volitile. %s" %(self.OPC()))


    def DC(self,offset):    # funtion mode: DC
        if self.model == "33220A":
            VISARW.write(self.add,("FUNC DC"))
            VISARW.write(self.add,("VOLT:OFFS %s" %offset))
            time.sleep(0.1)

    def VOFFSET(self,offset):
        if self.model == "33220A":
            VISARW.write(self.add,("VOLT:OFFS %s" %offset))
            time.sleep(0.1)

    def BURSTMODE_TRIG(self,no_of_cycles):
        if self.model == "33220A":
            VISARW.write(self.add,("BURS:NCYC %s" %(no_of_cycles)))
            time.sleep(0.1)
            VISARW.write(self.add,("BURSt:MODE TRIGgered"))
            time.sleep(0.1)
            VISARW.write(self.add,("BURSt:STATE ON"))
            time.sleep(0.1)

    def TRIGGER(self, source="Immediate"):
        if self.model == "33220A":
            if (source == "Immediate"):
                VISARW.write(self.add,("TRIG:SOUR IMM"))
                VISARW.write(self.add,("OUTPUT OFF"))
                # time.sleep(0.1)
            elif (source == "External"):
                # triggered from an external source (back off )
                VISARW.write(self.add,("TRIG:SOUR EXT"))
                #VISARW.write(self.add,("TRIG:SLOP POS"))
            elif (source == "Bus"):
                VISARW.write(self.add,("TRIG:SOUR BUS"))


    def OUTPUT(self,state,load=50,polarity="NORMal"):
        if self.model == "33220A":
            VISARW.write(self.add,("OUTPut:POLarity %s" %(polarity)))
            VISARW.write(self.add,("OUTPut:LOAD %s" %(load)))
            # polarity is either NORMal or INVerted
            VISARW.write(self.add,("OUTPUT %s" %(state)))
            #time.sleep(0.1)

    def HiZLoad(self):
        if self.model == "33220A":
            VISARW.write(self.add,("OUTP:LOAD INF"))
            time.sleep(0.1)

    def Load50(self):
        if self.model == "33220A":
            VISARW.write(self.add,("OUTPut:LOAD 50"))
            time.sleep(0.1)
