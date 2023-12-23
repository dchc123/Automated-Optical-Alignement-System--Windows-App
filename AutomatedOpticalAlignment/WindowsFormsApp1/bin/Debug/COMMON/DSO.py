# -*- coding: cp1252 -*-
import VISARW
import time


class DSO:

    DSOCount = 0

    def __init__(self,model,add):
        self.model = model
        self.add = add
        DSO.DSOCount += 1

    def displayCount(self):
        print("DSO count %d" % DCO.DCOCount)

    def RESET(self):
        VISARW.write(self.add, ("*RST"))

    def CLEAR_STATUS(self):
        VISARW.write(self.add, ("*CLS"))

    def AUT(self):
        VISARW.write(self.add,("*AUT"))

    def CHANNEL(self,channel):                          # view channel
        if self.model in( "KMSOX3104T", "54832D"):
        #if self.model == "KMSOX3104T":
            VISARW.write(self.add,(":VIEW CHAN%d" %channel))

    def INPUT(self,channel,Parameter):
        if self.model == "54832D":
            VISARW.write(self.add,(":CHAN%d:INP %s" %(channel,Parameter))) # <parameter> The parameters available in
            # this command for Infiniium: [DC, DC50, AC]

    def OFFSET(self,channel,offset):
        if self.model == "54832D":
            VISARW.write(self.add,(":CHAN%s:OFFS %s" %(channel,offset))) # offset in Volts

    def BLANK_CHANNEL(self,channel):
        if self.model in( "KMSOX3104T", "54832D"):
        #if self.model == "KMSOX3104T":
            VISARW.write(self.add,(":BLANK CHANnel%d" %channel))
    
    def ACQUISITION(self,mode):
        if self.model == "54832D":
            VISARW.write(self.add,(":ACQ:MODE %s" %mode)) #acquisition mode {RTIMe|{ETIMe|REPetitive}|PDETect|HRESolution | SEGMented}

    def AVERAGING(self,mode,count): #mode= 'ON'/'OFF' , count= 2,4,16,...
        if self.model == "54832D":
            VISARW.write(self.add,(":ACQ:AVER %s" %mode)) #
            VISARW.write(self.add,(":ACQ:AVER:COUN %s" %str(count)))

    def RUN_CONTROL(self,control):          #control = [RUN , STOP , SINGLE]
        if self.model in( "KMSOX3104T", "54832D"):
            VISARW.write(self.add,(":%s" %control))

    def CLEAR_DISPLAY(self):        #clears the diplay
        if self.model == "54832D":
            VISARW.write(self.add,(":CDIS"))
                    
    def FREQ(self,channel):
        if self.model in( "KMSOX3104T", "54832D"):
        #if self.model == "KMSOX3104T":
            VISARW.write(self.add,(":MEASURE:SOURCE CHANNEL%s" %(channel)))
            time.sleep(0.5)
            freq1 = VISARW.read(self.add,(":MEASURE:FREQUENCY?"))
            return freq1
        
    def DUTYCYCLE(self,channel):
        if self.model in( "KMSOX3104T", "54832D"):
            dutyc =VISARW.read(self.add,(":MEASure:DUTYcycle? CHANNEL%s" %(channel)))
            return dutyc
        
    def TRISE(self,channel):
        if self.model in( "KMSOX3104T", "54832D"):
            VISARW.write(self.add,(":MEASURE:SOURCE CHANNEL%s" %(channel)))
            time.sleep(0.5)
            trise = VISARW.read(self.add,(":MEASURE:RISETIME?"))
            return trise
        
    def TFALL(self,channel):
        if self.model in( "KMSOX3104T", "54832D"):
            VISARW.write(self.add,(":MEASURE:SOURCE CHANNEL%s" %(channel)))
            time.sleep(0.5)
            tfall = VISARW.read(self.add,(":MEASURE:FALLTIME?"))
            return tfall

    def GET_VTOP(self,source = 'CHAN1'): #source = [CHAN1,2,3,4|FUNC1,2,3,4|WMEM]
        if self.model == "54832D":
            vtop = VISARW.read(self.add,(":MEAS:VTOP? %s" %source))
            return vtop

    def GET_VBASE(self,source = 'CHAN1'): #source = [CHAN1,2,3,4|FUNC1,2,3,4|WMEM]
        if self.model == "54832D":
            vbase = VISARW.read(self.add,(":MEAS:VBASE? %s" %source))
            return vbase

    def TIMESCALEDIV(self,sPerDiv):
        if self.model in( "KMSOX3104T", "54832D"):
            VISARW.write(self.add,(":TIMebase:SCALe %s" %(sPerDiv)))
            time.sleep(0.1)

    def TIMEDELAY(self,delay):
        if self.model in( "KMSOX3104T", "54832D"):
        #if self.model == "KMSOX3104T":
            VISARW.write(self.add,(":TIM:POS %s" %delay))
            time.sleep(0.1)
	
    def VOLTSCALEDIV(self,channel,vPerDiv):
        if self.model in( "KMSOX3104T", "54832D"):
        #if self.model == "KMSOX3104T":
            VISARW.write(self.add,(":CHANnel%s:SCAL %s" %(channel,vPerDiv)))
            time.sleep(0.1)
            
    def TRIGGER_SETUP(self,channel,slope,level,sweep):  #Slope= POSITIVE or NEGATIVE
        if self.model == "KMSOX3104T":
            VISARW.write(self.add,(":TRIG:EDGE:SOUR CHAN%s" %(channel)))
            VISARW.write(self.add,(":TRIGger:SLOPe %s" %(slope)))
            VISARW.write(self.add,(":TRIG:EDGE:level %s" %(level)))
            time.sleep(0.1)
        if self.model == "54832D":
            VISARW.write(self.add,(":TRIG:MODE EDGE"))
            VISARW.write(self.add,(":TRIG:EDGE:SOUR CHAN%s" %channel))
            VISARW.write(self.add,(":TRIG:EDGE:SLOP %s" %slope))
            VISARW.write(self.add,(":TRIG:LEVEL CHAN%s,%s" %(channel,level)))
            VISARW.write(self.add,(":TRIG:SWE %s" %sweep)) #{AUTO|TRIGgered|SINGle}
            time.sleep(0.1)
            
    def MARKERSOURCE(self,xy,source): # source = [CHAN1,2,3,4 | FUNC1,2,3,4]
        if self.model in( "KMSOX3104T", "54832D"):
            VISARW.write(self.add,(":MARKer:X%dY%dsource %s" %(xy,xy,source)))

    def MARKERMODE(self,mode):
        if self.model in( "KMSOX3104T", "54832D"):
        #if self.model == "KMSOX3104T":
            VISARW.write(self.add,(":MARKer:MODE %s" %mode))
            #mode = OFF | MEASurement | MANual | WAVeform | BINary | HEX
            
    def XDELTA(self):
        if self.model in( "KMSOX3104T", "54832D"):
        #if self.model == "KMSOX3104T":
            xdelta = float(VISARW.read(self.add,(":MARK:XDEL?")))
        return xdelta

    def MARKER_X_POS(self,x,position_in_s):
        if self.model in( "KMSOX3104T", "54832D"):
        #if self.model == "KMSOX3104T":
            VISARW.write(self.add,(":MARK:X%dPosition %s" %(x,position_in_s)))
            time.sleep(0.001)
            x_pos = float(VISARW.read(self.add,(":MARKer:X%dposition?" %x)))
            x_pos = float(VISARW.read(self.add,(":MARKer:X%dposition?" %x)))
            time.sleep(0.001)
            y_pos = float(VISARW.read(self.add,(":MARKer:Y%dposition?" %x)))
            y_pos = float(VISARW.read(self.add,(":MARKer:Y%dposition?" %x)))
            return x_pos,y_pos
            #x1_pos, y1_pos = DSO1.MARKER_X_POS(1,3) //format for calling this function 

            
    #----------------------- FUNCTION commands --------------------------#
        
    # Creates and displays the function
    def SET_FUNCTION(self,number,kind,oper1='CHAN1',oper2='CHAN2'): # number = ['1','2','3','4']
        if self.model == "54832D":                              # type = ['ADD','AVERAGE','DIVIDE','INVERT','MAX','MIN',
            if kind == 'ADD': #the algebraic sum of the two operands [oper1] and [oper2]
                VISARW.write(self.add,(":FUNC%s:ADD %s,%s" %(number,oper1,oper2)))
            elif kind == 'AVERAGE': #averages the operand [oper1] based on the number of specified averages [oper2].
                if oper2 =='CHAN2': 
                    oper2 = 5 #default averages value: 5 
                VISARW.write(self.add,(":FUNC%s:AVER %s,%s" %(number,oper1,oper2)))
            elif kind == 'DIVIDE': #divides the first operand by the second operand
                VISARW.write(self.add,(":FUNC%s:DIV %s,%s" %(number,oper1,oper2)))
            elif kind == 'INVERT': #inverts the defined operand’s [oper1] waveform by multiplying by -1
                VISARW.write(self.add,(":FUNC%s:INV %s" %(number,oper1)))
            elif kind == 'MAX': #computes the maximum of each time bucket for the defined operand’s waveform [oper1]
                VISARW.write(self.add,(":FUNC%s:MAX %s" %(number,oper1)))
            elif kind == 'MIN': #computes the minimum of each time bucket for the defined operand’s waveform [oper1]
                VISARW.write(self.add,(":FUNC%s:MIN %s" %(number,oper1)))
            elif kind == 'SMOOTH': #assigns the smoothing operator to the operand [oper1] with the number of specified smoothing points [oper2]
                if oper2 =='CHAN2':
                    oper2 = 5 #default averages value: 5 
                VISARW.write(self.add,(":FUNC%s:SMO %s,%s" %(number,oper1,oper2)))
            elif kind == 'SUBTRACT': #algebraically subtracts the second operand [oper2] from the first operand [oper1]
                VISARW.write(self.add,(":FUNC%s:SUBT %s,%s" %(number,oper1,oper2)))
            VISARW.write(self.add,(":FUNC%s:DISP ON" %number)) # displays the function as well

    def FUNC_RANGE(self,number,range):
        if self.model == "54832D":
            VISARW.write(self.add,(":FUNC%s:RANG %s" %(number,range)))

    def FUNC_OFFSET(self,number,offset):
        if self.model == "54832D":
            VISARW.write(self.add,(":FUNC%s:OFFS %s" %(number,offset)))

    def DISP_FUNC(self,number,mode):
        if self.model == "54832D":
            VISARW.write(self.add,(":FUNC%s:DISP %s" %(number,mode)))
#added by KD
    def PWIDTH(self,channel):
        if self.model in( "KMSOX3104T", "54832D"):
            pwidth =VISARW.read(self.add,(":MEASure:PWIDth? CHANNEL%s" %(channel)))
            return pwidth
    def NWIDTH(self,channel):
        if self.model in( "KMSOX3104T", "54832D"):
            nwidth =VISARW.read(self.add,(":MEASure:NWIDth? CHANNEL%s" %(channel)))
            return nwidth

    def GET_VMAX(self,source = 'CHAN1'): #source = [CHAN1,2,3,4|FUNC1,2,3,4|WMEM]
        if self.model == "54832D":
            vmax = VISARW.read(self.add,(":MEAS:VMAX? %s" %source))
            return vmax
