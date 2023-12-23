# -*- coding: cp1252 -*-
''' DCA functions

Version : 01.04.00.00
Date : 22/05/18

---
Version notes

01.00.00.00 - ADDED the following functions

   VPP Measure : Measure the Peak to Peak Voltage
   GET_RESULT : Read the results from the measurements configured on screen
   LOAD_FILE : Load a set up file.  NOTE the file needs to be resident on the DCA
   GET_AVG_POWER : Read Average Power
   SET_MEAS_SOURCE : Configure the measurement source to a specific channel

01.01.00.00 - ADDED the following functions

   Marker functions

01.03.00.00 - ADDED precision timebase module support and functions

01.04.00.00 - ADDED EYE/MASK mode commands and functions
'''

import sys
import VISARW
import time

class DCA:

    DCAcount = 0

    def __init__(self,model,add):
        self.model = model
        self.add = add
        DCA.DCAcount += 1

    def displayCount(self):
        print("DCA count %d" % DCA.DCAcount)

    def RESET(self):
        if self.model in( "86100C", "86100D"):
            VISARW.write(self.add,("*RST"))
            time.sleep(3)
        else:
            print ("No function defined for this model")

    def CLS(self): #clears device status and errors
        if self.model in( "86100C", "86100D"):
            VISARW.write(self.add,("*CLS"))
        else:
            print ("No function defined for this model")

    def LOAD_SETUP(self,num):
        if self.model in( "86100C", "86100D"):
            VISARW.write(self.add,(":REC:SET %s" %num))
        else:
            print ("No function defined for this model")

    def AUT(self):              #AUTOSCALE
        if self.model in ("86100C", "86100D"):
            #response = VISARW.read_timeout(self.add,":AUT;*OPC?",20000)
            VISARW.write(self.add,(":AUT"))
            time.sleep(3)
        else:
            print ("No function defined for this model")

    def CLR_DISPLAY(self):
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,":CDIS") # clears the present display
        else:
            print ("No function defined for this model")

    def RUN(self):
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":RUN")) # runs acquisition
        else:
            print ("No function defined for this model")

    def STOP(self):
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":STOP")) # stops acquisition on all channels
        else:
            print ("No function defined for this model")

    def SYSTEM_MODE(self,mode):
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":SYST:MODE %s" %mode)) # {EYE | OSCilloscope | TDR | JITTer}
            time.sleep(0.1)
            VISARW.write(self.add,("*CLS"))
            if mode == "JITT" or "JITTer":
                time.sleep(6)
                VISARW.write(self.add,(":DISP:JITT:SHAD 1"))# PUTS HISTOGRAM WINDOW "ON"
                time.sleep(3)
                VISARW.write(self.add,(":DISP:JITT:SHAD 0"))# PUTS HISTOGRAM WINDOW "OFF"
        else:
            print ("No function defined for this model")

    def PERSISTENCE(self,mode): # {MINimum | INFinite | <persistence_value> in secs| CGRade | GSCale}
        if self.model in ("86100C", "86100D"):  # only oscilloscope system mode supports all of them
            VISARW.write(self.add,(":DISP:PERS %s" %mode)) 
        else:
            print ("No function defined for this model")

    def DISP_CHAN(self,channel,mode):
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?"))
            if sysmode == 'EYE':
                VISARW.write(self.add,(":CHAN%s:DISP %s,APP" %(channel,mode))) # channel and {ON | OFF} and append it to already displayed channels
            else:
                VISARW.write(self.add,(":CHAN%s:DISP %s" %(channel,mode))) # channel and {ON | OFF}
        else:
            print ("No function defined for this model")

    def CHANNEL_ATTEN(self,channel,atten,units):
        '''channel attenuation factor (i.e. to compensate for external attenuation)'''
        if self.model in ("86100C", "86100D"):  
            VISARW.write(self.add,(":CHAN%s:PROB %s,%s" %(channel,atten,units))) # channel_No , atten_value, [DEC|RAT]
        else:
            print ("No function defined for this model")

    def CHANNEL_BW(self,channel,bw='MID',): #channel bandwidth ['LOW','MID','HIGH']
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":CHAN%s:BAND %s" %(str(channel),bw))) # channel_No , mode
        else:
            print ("No function defined for this model")
    
    def CHANNEL_FILTER(self,channel,mode='ON',filterset=1): #channel filter 'ON'/'OFF' and filter select [1-XX]
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":CHAN%s:FILT %s" %(str(channel),mode))) # channel_No , mode
            VISARW.write(self.add,(":CHAN%s:FSEL FILT%s" %(str(channel),str(filterset)))) # channel_No , filterset
        else:
            print ("No function defined for this model")

    def CHANNEL_WAVELENGTH(self,channel,wave):
        '''Optical channel wavelength select [WAV1,WAV2,WAV3,USER]
            for 850,1310,1550nm and user calibrated respectively'''
        if self.model in ("86100C", "86100D"):  
            VISARW.write(self.add,(":CHAN%s:WAV %s" %(str(channel),wave))) # channel_No , wavelength setting
        else:
            print ("No function defined for this model")
    
    def DISP_FUNC(self,function,mode):
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?"))
            if sysmode == 'EYE':
                VISARW.write(self.add,(":FUNC%s:DISP %s,APP" %(function,mode))) # Function and {ON | OFF} and append it to already displayed channels
            else:
                VISARW.write(self.add,(":FUNC%s:DISP %s" %(function,mode))) # Function and {ON | OFF}
        else:
            print ("No function defined for this model")

    def AVERAGING(self,mode,count):                     #not for use when in JITTER MODE
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":ACQ:AVER %s" %mode))   # {ON | OFF}
            VISARW.write(self.add,(":ACQ:COUN %s" %str(count)))  # integer from 1 to 8192
        else:
            print ("No function defined for this model")

    def VSCALE(self,channel,value):         
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":CHAN%s:SCAL %s" %(channel,value))) #channel No and vertical scale in Volts
        else:
            print ("No function defined for this model")    
    
    def VOFFSET(self,channel,value):         
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":CHAN%s:OFFS %s" %(channel,value))) #channel No and offset value in Volts
        else:
            print ("No function defined for this model") 


    #------------- Histogram Commands ---------------------------------

    def SET_HISTOGRAM(self,axis,source,X1,Y1,X2,Y2):         
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":HIST:AXIS %s" %axis)) #axis type: {VERTical | HORizontal}
            VISARW.write(self.add,(":HIST:SOUR %s" %source)) #source type: {CHANnel<N> | FUNCtion<N> | RESPonse<N> | CGMemory}
            VISARW.write(self.add,(":HIST:WIND:BORD ON"))
            VISARW.write(self.add,(":HIST:WIND:X1P %s" %X1)) # the window coordinates
            VISARW.write(self.add,(":HIST:WIND:Y1P %s" %Y1))
            VISARW.write(self.add,(":HIST:WIND:X2P %s" %X2))
            VISARW.write(self.add,(":HIST:WIND:Y2P %s" %Y2))
            time.sleep(1)
            VISARW.write(self.add,(":HIST:MODE ON"))
        else:
            print ("No function defined for this model")


    def GET_HIST_DATA(self):    #returns the mean, std deviation, peak-to-peak, and the peak position
        if self.model in ("86100C", "86100D"):
            mean = VISARW.read(self.add,(":MEAS:HIST:MEAN?"))
            stddev = VISARW.read(self.add,(":MEAS:HIST:STDD?"))
            p_p = VISARW.read(self.add,(":MEAS:HIST:PP?"))
            pposition = VISARW.read(self.add,(":MEAS:HIST:PPOS?"))
        else:
            print ("No function defined for this model")
        return mean,stddev,p_p,pposition

    # --------------------------------------------------------------------

    def SET_TIMESCALE(self,value):         
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":TIM:SCAL %s" %value))  #set timescale (in sec/div)
        else:
            print ("No function defined for this model")

    def SET_DELAY(self,value):         
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":TIM:POS %s" %value))   #set time delay (in sec)
        else:
            print ("No function defined for this model")

    def GET_VAMP(self,source='CHAN1',query=1):              #returns the V amplitude of the selected source (OSC mode)
        if self.model in ("86100C", "86100D"):              #query=0 sets the V_amp measurement in DCA screen
            if query ==1:                                   # source = <CHAN1/2/3/4, FUNC1/2/3/4>
                VAMP = VISARW.read(self.add,(":MEAS:VAMP? %s" %source))
            else:
                VISARW.write(self.add,(":MEAS:VAMP %s" %source))
                VAMP = 0
        else:
            print ("No function defined for this model")
        return VAMP

    def GET_VBASE(self,source='CHAN1'):                     #returns the V base of selected channel
        if self.model in ("86100C", "86100D"):              # source = <CHAN1/2/3/4, FUNC1/2/3/4>
            VBASE = VISARW.read(self.add,(":MEAS:VBAS? %s" %source))
        else:
            print ("No function defined for this model")
        return VBASE

    def GET_VAVG(self,source='CHAN1'):              #returns the average Voltage of selected channel
        if self.model in ("86100C", "86100D"):      # source = <CHAN1/2/3/4, FUNC1/2/3/4>
            VAVG = VISARW.read(self.add,(":MEAS:VAV? DISP,%s" %source))
        else:
            print ("No function defined for this model")
        return VAVG

    def GET_VPP(self,source='CHAN1'):                             #returns the Peak to Peak Voltage of selected channel
        if self.model in ("86100C", "86100D"):
            VPP = VISARW.read(self.add,(":MEAS:VPP? %s" %source))
        else:
            print ("No function defined for this model")
        return VPP

    def GET_TOP(self,source):                             #returns the VTOP of selected source
        if self.model in ("86100C", "86100D"):
            VTOP = VISARW.read(self.add,(":MEAS:VTOP? %s" %source))
        else:
            print ("No function defined for this model")
        return VTOP

    def GET_VMAX(self,source='CHAN1'):                  #returns the VMAX of selected source
        if self.model in ("86100C", "86100D"):          # source = <CHAN1/2/3/4, FUNC1/2/3/4>
            VTOP = VISARW.read(self.add,(":MEAS:VMAX? %s" %source))
        else:
            print ("No function defined for this model")
        return VTOP

    def GET_RISETIME(self,source='CHAN1',query=1):
        #returns the rise time of selected source
        #query=0 sets the rise time measurement in DCA screen
        # source = <CHAN1/2/3/4 | FUNC1/2/3/4 | RESP<N> | WMEM<N> >
        if self.model in ("86100C", "86100D"):          
            if query == 1:
                RT = VISARW.read(self.add,(":MEAS:RIS? %s" %source))
            else:
                VISARW.write(self.add,(":MEAS:RIS %s" %source))
                RT = 0
        else:
            print ("No function defined for this model")
        return RT

    def GET_FALLTIME(self,source='CHAN1',query=1):
        #returns the fall time of selected source
        #query=0 sets the fall time measurement in DCA screen
        # source = <CHAN1/2/3/4 | FUNC1/2/3/4 | RESP<N> | WMEM<N> >
        if self.model in ("86100C", "86100D"):          
            if query == 1:
                FT = VISARW.read(self.add,(":MEAS:FALL? %s" %source))
            else:
                VISARW.write(self.add,(":MEAS:FALL %s" %source))
                FT = 0
        else:
            print ("No function defined for this model")
        return FT
    
    def GET_RAW_RESULTS(self):                  #returns the full RAW result list for upto 4 measurements
        results = ""
        if self.model in ("86100C", "86100D"):
            results = VISARW.read(self.add,("MEAS:RES?"))
        else:
            print ("No function defined for this model")
        return results

    def GET_RESULT(self,measurement='1',parameter='curr'):
        #returns the SELECTED result (measurement and parameter) out of the full raw result list
        #structure: measurement = [1|2|3|4] , parameter = [curr|mean|std_dev|min|max]
        raw_results = result = ""                           
        param = select = 0
        if self.model in ("86100C", "86100D"):
            if parameter == 'curr':
                param = 1
            elif parameter == 'mean':
                param = 4
            elif parameter == 'std_dev':
                param = 5
            elif parameter == 'min':
                param = 2
            elif parameter == 'max':
                param = 3
            else:
                print ("---- Error: Invalid parameter value ----")
                result = 9.99999e37

            if measurement == '1':
                select = 0 + param
            elif measurement == '2':
                select = 7 + param
            elif measurement == '3':
                select = 14 + param
            elif measurement == '4':
                select = 21 + param
            else:
                print ("---- Error: Invalid measurement value ----")
                result = 9.99999e37
            
            raw_results = str(VISARW.read(self.add,("MEAS:RES?")))
            split = raw_results.split(',')

            if select < len(split):
                result = split[select]
            else:
                print ("--- Error: Attempting to access a measurement that does not exist ---")
                result = 9.99999e37
        else:
            print ("No function defined for this model")
        return result

    def LOAD_FILE(self,file_name,delay=5):              #loads a config file
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,("DISK:LOAD \"%s\"" %(file_name))) # i.e.: D:\User Files\setups\gc1904_IMOD.set
            time.sleep(delay)
        else:
            print ("No function defined for this model")

    def GET_AVG_POWER(self,units="DEC",query=1):
        ''' Read the AVERAGE POWER of the active source.

        Valid UNITS : DEC = dBm, WATT = Watts'''

        if self.model in ("86100C", "86100D"):
            if query == 1:
                AVG_POWER = VISARW.read(self.add,("MEAS:APOW? %s" %(units)))
            else:
                VISARW.write(self.add,("MEAS:APOW %s" %(units)))
                AVG_POWER = 0
        else:
            print ("No function defined for this model")
        return AVG_POWER

    def AVG_PWR_CORRECTION(self,mode="ON"):
        ''' Applies dark calibration data to Average Power measurements
            Valid input : ON or OFF '''

        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,("MEAS:APOW:CORR %s" %mode))
        else:
            print ("No function defined for this model")

    def SET_MEAS_SOURCE(self,source=1):
        ''' Select the measurement source channel.

        Valid source : 1, 2, 3 or 4'''
        
        if self.model in ("86100C", "86100D"):
            if source > 0 and source < 5:
                VISARW.write(self.add,(":MEAS:SOUR CHAN%s" %(source)))
            else:
                print ("Invalid SOURCE setting [%s], valid settings 1, 2, 3 or 4" % source)
        else:
            print ("No function defined for this model")

    #----------------- Trigger commands -----------------------------------------------------
    def TRIGG_BITRATE(self,bitrate):
        #i.e. bitrate autodetect 'OFF' or bitrate = 1E9 or 2.5E9
        #defines the bitrate of the trigger pattern
        if self.model in ("86100C", "86100D"):
            if bitrate == 'AUT':
                VISARW.write(self.add,(":TRIG:BRAT:AUT 1"))
            else:
                VISARW.write(self.add,(":TRIG:BRAT:AUT 0"))
                VISARW.write(self.add,(":TRIG:BRAT %s" %(bitrate)))
        else:
            print ("No function defined for this model")

    def TRIGG_DIVRATIO(self,ratio):
        #Sets the data-to-clock divide ratio used by pattern lock trigger mode.
        #use 'AUT' for autodetect or integers: 1,2,4,5,8,10,15,16,20,25,30,32,35,40,45,50,64,66,100,128
        if self.model in ("86100C", "86100D"):
            if ratio == 'AUT':
                VISARW.write(self.add,(":TRIG:DCDR:AUT 1"))
            else:
                VISARW.write(self.add,(":TRIG:DCDR:AUT 0"))
                VISARW.write(self.add,(":TRIG:DCDR %s" %(ratio)))
        else:
            print ("No function defined for this model")
    
    def TRIGG_PLOCK(self,plock):      # plock = 'ON'/'OFF' #enables/disables pattern lock
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":TRIG:PLOC %s" %(plock)))
        else:
            print ("No function defined for this model")
    
    def TRIGG_PLENGTH(self,p_length):
        #sets the length of the pattern used in pattern lock trigger mode or 'AUT' for autodetecting the pattern length
        # <p_length> is an integer value in the range of 1 to 215 in jitter mode and 1 to 223 in the other instrument modes
        if self.model in ("86100C", "86100D"):   
            if p_length == 'AUT':          
                VISARW.write(self.add,(":TRIG:PLEN:AUT 1"))
            else:
                VISARW.write(self.add,(":TRIG:PLEN:AUT 0"))
                VISARW.write(self.add,(":TRIG:PLEN %s" %(p_length)))
        else:
            print ("No function defined for this model")

    def TRIGG_SLOPE(self,slope):    # slope = 'POS'/'NEG' #sets the slope of the edge on which to trigger
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":TRIG:SLOP %s" %slope))
        else:
            print ("No function defined for this model")

    def TRIGG_BW(self,option):   #Bandwidth = {LOW | HIGH | DIV} #LOW= Filtered (DC-100MHz), 
        if self.model in ("86100C", "86100D"):                   #HIGH= Standard (DC-3.2GHz)
            VISARW.write(self.add,("TRIG:BWL %s" %option))       #DIV= Divided (3-13GHz)   
        else:
            print ("No function defined for this model")

    def TRIGG_SOURCE(self,source):   # source =  {FPANel | FRUN | LMODule | RMODule}
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,("TRIG:SOUR %s" %source))
        else:
            print ("No function defined for this model")

    def TRIGG_GATED(self,gated):      # 'ON'/'OFF' #Enables or disables the ability of the instrument to respond to trigger inputs
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,("TRIG:GAT %s" %gated))
        else:
            print ("No function defined for this model")
    #-----------------------------------------------------------------------------

    def FUNCTION(self,number=1,func='ADD',oper1='CHAN1',oper2='CHAN2'):      # e.g. FUNCTION(1,ADD,CHAN1,CHAN2)
        if self.model in ("86100C", "86100D"):
            if func   == 'ADD':         #A function that adds source 1 to source 2, point by point, and places the result in the selected function waveform.
                VISARW.write(self.add,(":FUNC%s:ADD %s,%s" %(number,oper1,oper2)))
            elif func == 'DIFF':        #A function that differentiates source 1 and places the result in the selected function waveform
                VISARW.write(self.add,(":FUNC%s:DIFF %s" %(number,oper1)))
            elif func == 'INV':         #A function that inverts the defined operand's waveform by multiplying by –1.
                VISARW.write(self.add,(":FUNC%s:INV %s" %(number,oper1)))
            elif func == 'MULT':        #A function that multiplies source 1 by source 2, point by point, and places the result in the function waveform.
                VISARW.write(self.add,(":FUNC%s:MULT %s,%s" %(number,oper1,oper2)))
            elif func == 'SUBT':        #A function that algebraically subtracts the second operand from the first operand
                VISARW.write(self.add,(":FUNC%s:SUBT %s,%s" %(number,oper1,oper2)))
            elif func == 'MAX':        #A function that shows the maximum points of the source
                VISARW.write(self.add,(":FUNC%s:MAX %s" %(number,oper1)))
            elif func == 'MIN':        #A function that shows the minimum points of the source
                VISARW.write(self.add,(":FUNC%s:MIN %s" %(number,oper1)))
            else:
                print ("Function argument not supported.")
        else:
            print ("No function defined for this model")

    def F_VRANGE(self,function,value):         
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":FUNC%s:RANG %s" %(function,value))) #function No and vertical range in Volts
        else:
            print ("No function defined for this model")    
    
    def F_VOFFSET(self,function,value):         
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":FUNC%s:OFFS %s" %(function,value))) #function No and offset value in Volts
        else:
            print ("No function defined for this model") 
    
    def DEF_THRESHOLDS(self,val1,val2,val3):      #Define the percentage thresholds used for eye measurements, jitter, etc. 
        if self.model in ("86100C", "86100D"):    # <upper_pct>,<middle_pct>,<lower_pct> e.g. 80,50,20
            VISARW.write(self.add,(":MEAS:DEF THR,PERC, %s,%s,%s" %(str(val1),str(val2),str(val3))))
        else:
            print ("No function defined for this model")

    def GET_JITTER(self):      # has to be in JITTER mode
        if self.model in ("86100C", "86100D"):
            dj = VISARW.read(self.add,(":MEAS:JITT:DJ?"))    # deterministic jitter
            ddj = VISARW.read(self.add,(":MEAS:JITT:DDJ?"))  # data-dependent jitter
            rj = VISARW.read(self.add,(":MEAS:JITT:RJ?"))    # random jitter
            dcd = VISARW.read(self.add,(":MEAS:JITT:DCD?"))  # jitter duty cicle distortion
            isi = VISARW.read(self.add,(":MEAS:JITT:ISI?"))  # intersymbol interference
        else:
            print ("No function defined for this model")
        return dj,ddj,rj,dcd,isi

    #----------- Marker commands (usually used in OSC mode) ------------

    def MARKER_STATE(self,marker_No,X_marker_state,Y_marker_state):
        if self.model in ("86100C", "86100D"):    # <marker_No>,<X_marker_state>,<Y_marker_state> e.g. [1|2],[OFF|TRACk|MANual],[OFF|TRACk|MANual]
            VISARW.write(self.add,(":MARK:STAT X%sY%s,%s,%s" %(str(marker_No),str(marker_No),str(X_marker_state),str(Y_marker_state))))
        else:
            print ("No function defined for this model")

    def MARKER_SOURCE(self,marker_No,marker_source):
        if self.model in ("86100C", "86100D"):    # <pair of markers Number>,<marker_source> e.g. [1|2],[CHAN1/2/3/4|WMEMORY1/2/3/4|FUNCTION1/2/3/4]
            VISARW.write(self.add,(":MARK:X%sY%s %s" %(str(marker_No),str(marker_No),str(marker_source))))
        else:
            print ("No function defined for this model")

    def MARKER_X_POS(self,marker_No,position): # Sets X marker position (in secs by default) and also returns the associated Y marker value 
        if self.model in ("86100C", "86100D"):    # <marker_No>,<position> e.g. <[1|2],[position in secs]>
            VISARW.write(self.add,(":MARK:X%sP %s" %(str(marker_No),str(position))))
            time.sleep(0.1)
            y_pos = float(VISARW.read(self.add,(":MARK:Y%sP?" %(str(marker_No)))))
        else:
            print ("No function defined for this model")
        return y_pos

    def MARKER_Y_POS(self,marker_No,position): # Sets Y marker position (in Volts by default) and also returns the associated X marker position 
        if self.model in ("86100C", "86100D"):    # <marker_No>,<position> e.g. <[1|2],[position in Volts]>
            VISARW.write(self.add,(":MARK:Y%sP %s" %(str(marker_No),str(position))))
            time.sleep(0.1)
            x_pos = float(VISARW.read(self.add,(":MARK:X%sP?" %(str(marker_No)))))
        else:
            print ("No function defined for this model")
        return x_pos

    def XDELTA(self):   # returns the X delta (between X1 and X2)
        if self.model in ("86100C", "86100D"):
            xdelta = float(VISARW.read(self.add,(":MARK:XDEL?")))
        return xdelta
    

    #----------- Precision timebase module commands ------------

    def PRECISION(self,state): #switches 'ON' or 'OFF' the precision timebase
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":TIM:PREC %s" %(state)))
        else:
            print ("No function defined for this model")

    def PRECISION_RF_FREQ(self,freq): #sets the RF of the reference clock
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":TIM:PREC:RFR %s" %(freq)))
        else:
            print ("No function defined for this model")

    def PRECISION_RF_FREQ_AUT(self,state): #sets the RF autodetect 'ON' or 'OFF'
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":TIM:PREC:RFR:AUT %s" %(state)))
        else:
            print ("No function defined for this model")

    def PRECISION_TIME_REF(self,value): #sets the time reference
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":TIM:PREC:TREF %s" %(value)))
        else:
            print ("No function defined for this model")
    #--------------------------------------------------------------------

    #-------------- EYE mode commands -----------------------------------

    def EYE_JITTER(self,source='CHAN1',mode='PP',query=1):
        ''' query=1 (default) -> returns the jitter value , query=0 -> sets up the jitter measurement in DCA
            source=[CHAN<N>|FUNC<N>|CGM], mode=['PP','RMS']  '''
        if self.model in ("86100C", "86100D"):  
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                if query == 1:
                    JITT = VISARW.read(self.add,(":MEAS:CGR:JITT? %s,%s" %(mode,source)))
                else:
                    VISARW.write(self.add,(":MEAS:CGR:JITT %s,%s" %(mode,source)))
                    JITT = 0
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
                JITT = 9.99999e37
        else:
            print ("No function defined for this model")
        return JITT
    
    def GET_CROSSING(self,source='CHAN1',query=1):  # query=1 (default) -> returns the crossing point percentage 
        if self.model in ("86100C", "86100D"):      # query=0 -> sets up the crossing point measurement in DCA 
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) # [CHAN<N>|FUNC<N>|CGM]
            time.sleep(0.1)
            if sysmode == 'EYE':
                if query == 1:
                    CROSS = VISARW.read(self.add,(":MEAS:CGR:CROS? %s" %(source)))
                else:
                    VISARW.write(self.add,(":MEAS:CGR:CROS %s" %(source)))
                    CROSS = 0
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
                CROSS = 9.99999e37
        else:
            print ("No function defined for this model")
        return CROSS

    def GET_ER(self,source='CHAN1',query=1): #Extinction Ratio # query=1 (default) -> returns the ER 
        if self.model in ("86100C", "86100D"):              # query=0 -> sets up the extinction ratio measurement in DCA 
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) # [CHAN<N>|FUNC<N>|CGM]
            time.sleep(0.1)
            if sysmode == 'EYE':
                if query == 1:
                    ER = VISARW.read(self.add,(":MEAS:CGR:ERAT? DEC,%s" %(source))) #decibel is selected by default
                    while float(ER) > 50.0 :
                        time.sleep(1)
                        ER = VISARW.read(self.add,(":MEAS:CGR:ERAT? DEC,%s" %(source))) #decibel is selected by default
                else:
                    VISARW.write(self.add,(":MEAS:CGR:ERAT DEC,%s" %(source)))
                    ER = 0
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
                ER = 9.99999e37
        else:
            print ("No function defined for this model")
        return ER

    def GET_EYEHEIGHT(self,source='CHAN1',query=1): # query=1 (default) -> returns the Eye height (EYE mode ONLY)
        if self.model in ("86100C", "86100D"):              # query=0 -> only sets up the Eye amplitude measurement in DCA 
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) # [CHAN<N>|FUNC<N>|CGM]
            time.sleep(0.1)
            if sysmode == 'EYE':
                if query == 1:
                    EYEHEI = VISARW.read(self.add,(":MEAS:CGR:EHE? DEC,%s" %(source)))
                else:
                    VISARW.write(self.add,(":MEAS:CGR:EHE DEC,%s" %(source)))
                    EYEHEI = 0
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
                EYEHEI = 9.99999e37
        else:
            print ("No function defined for this model")
        return EYEAMP
    
    def GET_EYEAMP(self,source='CHAN1',query=1):            # query=1 (default) -> returns the Eye amplitude (EYE mode ONLY)
        if self.model in ("86100C", "86100D"):              # query=0 -> only sets up the Eye amplitude measurement in DCA 
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) # [CHAN<N>|FUNC<N>|CGM]
            time.sleep(0.1)
            if sysmode == 'EYE':
                if query == 1:
                    EYEAMP = VISARW.read(self.add,(":MEAS:CGR:AMPL? %s" %(source)))
                else:
                    VISARW.write(self.add,(":MEAS:CGR:AMPL %s" %(source)))
                    EYEAMP = 0
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
                EYEAMP = 9.99999e37
        else:
            print ("No function defined for this model")
        return EYEAMP
    
    #-------------- MASK test commands -----------------

    def LOAD_MASK(self,filename):
        '''This command loads the specified mask file. This command operates only on files and directories on
            “A:\”, “D:\User Files”, “C:\scope\masks” and any mapped network drive. <file_name> is the filename,
            with the extension .msk or .pcm'''
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                VISARW.write(self.add,(":MTES:LOAD \"%s\"" %filename))
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
        else:
            print ("No function defined for this model")

    def RUNTIL(self,mode='WAV',number=500):
        '''Selects the acquisition run until mode. The acquisition may be set to run until n waveforms,
            n patterns, or n samples have been acquired, or to run forever (OFF).'''
        if self.model in ("86100C", "86100D"):
            if mode == 'OFF':
                VISARW.write(self.add,(":ACQ:RUNT OFF"))
            else:
                VISARW.write(self.add,(":ACQ:RUNT %s,%s" %(mode,str(number))))
        else:
            print ("No function defined for this model")    
    
    def MTEST_START(self):
        '''Aligns the currently loaded mask to the current waveform and starts testing. If no mask is currently
            loaded, a warning message will be displayed, but no error will be generated.'''
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                VISARW.write(self.add,(":MTES:STAR"))
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
        else:
            print ("No function defined for this model")
    
    def ALIGN_MASK(self): # Automatically aligns and scales the mask to the current waveform.
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                VISARW.write(self.add,(":MTES:ALIG"))
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
        else:
            print ("No function defined for this model")

    def MASK_OPTIM(self,state='ON'):
        '''Enables or disables optimization of the placement of the center mask region during mask alignment
            state= 'ON' or 'OFF'                    '''
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                VISARW.write(self.add,(":MTES:AOPT %s" %state))
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
        else:
            print ("No function defined for this model")
    
    def SET_MASK_MARGINS(self,mode='ON',Hit_ratio='1E-12'):
        '''Turns ON/OFF mask margins and automatically determines a mask-margin percent and displays the mask margin
            that has the expected number of errors (hit ratio) for the bit-error-ratio (BER) level entered.
            '''
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                if mode == 'OFF':
                    VISARW.write(self.add,(":MTES:MMAR:STAT OFF"))
                    MM = 9E99
                elif mode == 'ON':
                    VISARW.write(self.add,(":MTES:MMAR:STAT ON"))
                    VISARW.write(self.add,(":MTES:AMAR:BER %s" %str(Hit_ratio))) #set desired hit ration (BER) first
                    time.sleep(0.1)
                    VISARW.write(self.add,(":MTES:AMAR:CALC"))
                    time.sleep(2)
                else:
                    print ("Error: Invalid argument for mode")
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
        else:
            print ("No function defined for this model")

    def GET_MASK_MARGINS(self):
        '''If automatical MMs are switched ON, it returns the calculated Mask Margin percentage'''
        MM = 9E99
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                MM = VISARW.read(self.add,(":MTES:MMAR:PERC?"))
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
        else:
            print ("No function defined for this model")
        return MM

    def MTEST_EXIT(self):
        '''Terminates mask testing'''
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                VISARW.write(self.add,(":MTES:EXIT"))
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
        else:
            print ("No function defined for this model")
    
    def COUNT_WAVEFORMS(self): #  Returns the total number of waveforms gathered in the current mask test run
        if self.model in ("86100C", "86100D"):
            WVF = VISARW.read(self.add,(":MTES:COUN:WAV?"))
        else:
            print ("No function defined for this model")
        return WVF

    def COUNT_SAMPLES(self): #  Returns the total number of samples captured in the current mask test run.
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                SAMPLES = VISARW.read(self.add,(":MTES:COUN:SAMP?"))
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
                SAMPLES = 9.99999e37
        else:
            print ("No function defined for this model")
        return SAMPLES
                            
    def COUNT_FAILS(self): #  Returns the number of failures that occurred within a particular region.
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                TFAILS = VISARW.read(self.add,(":MTES:COUN:FAIL? TOT"))
                GFAILS = VISARW.read(self.add,(":MTES:COUN:FAIL? MARG"))
                MFAILS = VISARW.read(self.add,(":MTES:COUN:FAIL? MASK"))
                FAILS = TFAILS +','+ GFAILS +','+ MFAILS
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
                FAILS = 9.99999e37
        else:
            print ("No function defined for this model")
        return FAILS

    def COUNT_HITS(self): #  Returns the number of failed data points (or hits) that occurred while margin mask testing
        if self.model in ("86100C", "86100D"):
            sysmode = VISARW.read(self.add,(":SYST:MODE?")) 
            time.sleep(0.1)
            if sysmode == 'EYE':
                TFAILS = VISARW.read(self.add,(":MTES:COUN:HITS? TOT"))
                GFAILS = VISARW.read(self.add,(":MTES:COUN:HITS? MARG"))
                MFAILS = VISARW.read(self.add,(":MTES:COUN:HITS? MASK"))
                FAILS = TFAILS +','+ GFAILS +','+ MFAILS
            else:
                print ("Error: Command valid only in EYE/MASK system mode!")
                FAILS = 9.99999e37
        else:
            print ("No function defined for this model")
        return FAILS
        
    
    #--------------------------------------------------------------------

    #----------- CALIBRATION FUNCTIONS ------------
    def DSKEW_CAL(self,value="AUTO",chan='1'):
        #Set DIFFERENTIAL SKEW CAL - DCA must be in EYE mode with 2 channels enabled
        #value : STR value for skew in seconds, setting AUTO will run auto skew cal.  chan : STR valuae for channel
        response = "NOT SET"
        if self.model in ("86100C", "86100D"):
            response = VISARW.read_timeout(self.add,(":CHAN{}:DSK:AUTO;*OPC?".format(chan)),20000)
        else:
            print ("No function defined for this model")
        return(response)

    def SKEW_CAL(self,value="AUTO",chan='1'):
        #Set HORIZONTAL SKEW CAL - DCA must be in EYE mode with 2 channels enabled
        #value : STR value for skew in seconds.  chan : STR valuae for channel
        response = "NOT SET"
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":CAL:SKEW CHAN{},{}s".format(chan,value)))
        else:
            print ("No function defined for this model")
        return(response)

    def ER_CAL(self,channel=1):
        #Starts an extinction ratio calibration.
        #channel : value for channel
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":CAL:ERAT:STAR CHAN%s" %str(channel)))
            time.sleep(2)
            VISARW.write(self.add,(":CAL:CONT"))
            time.sleep(2)
            VISARW.write(self.add,(":CAL:CONT"))
            time.sleep(2)
            response = VISARW.read_timeout(self.add,(":CAL:ERAT:STAT? CHAN%s" %str(channel)))            
        else:
            print ("No function defined for this model")
        return(response)

    def OPTICAL_CORR(self,mode='ON'): #not working properly
        '''Applies dark calibration data to Average Power measurements. This removes an optical channel's
        dark current from the measurement results. Perform an extinction ratio calibration on a module's
        optical channel to create the dark current factor. Remove any input from the optical channel before
        performing the extinction ratio calibration.'''
        #channel : value for channel
        if self.model in ("86100C", "86100D"):
            VISARW.write(self.add,(":MEAS:APOW:CORR %s" %str(mode)))
            time.sleep(0.1)            
        else:
            print ("No function defined for this model")
    #------------------------------------------------------------------
