from __future__ import print_function
import time
import minimalmodbus
# import VISARW
import visa

AirJet = {'setpoint': 300, 'DUT_temp': 108, 'Air_temp': 104,'Nosel_temp':100}

class TEMP:

    TEMPcount = 0

    def __init__(self, model, add, baud=9600):
        self.model = model.upper()
        self.add = add
        if self.model == "RS232":
            self.instrument = minimalmodbus.Instrument(self.add, 1)
            self.instrument.serial.baudrate=baud
        else:
            try:
                self.rm = visa.ResourceManager()
            except: # for when on a raspberry pi
                self.rm = visa.ResourceManager('@py')
            # set write_termintation character to '\n' because one of the thermostreams doesn't like the default \n\r
            self.instrument = self.rm.open_resource(self.add, write_termination='\n')
        TEMP.TEMPcount += 1

    def displayCount(self):
        print("TEMP count %d" % TEMP.TEMPcount)

    def IDN(self):
        # IDN = VISARW.read(self.add,"*IDN?")
        IDN = self.instrument.query('*IDN?')
        return(IDN)

    def SPREAD(self):
        # temp = VISARW.read(self.add,"?SP")
        temp = self.instrument.query('?SP')
        return(temp)

    def SP(self,temp):
        if self.model == 'RS232':
            try:
                self.instrument.write_register(AirJet['setpoint'], temp,
                                               numberOfDecimals=1, signed=True)
            except IOError : # try again
                self.instrument.write_register(AirJet['setpoint'], temp,
                                               numberOfDecimals=1, signed=True)
        else:
            #VISARW.write(self.add, "SP%s" %temp)
            self.instrument.write("SP%s" %temp)

    def GET_DUT_TEMP(self):
        if self.model == 'RS232':
            temp = self.instrument.read_register(AirJet['DUT_temp'],
                                                 numberOfDecimals=1, signed=True)
        else:
            #temp = VISARW.read(self.add, "?PV")
            temp = self.instrument.query("?TD")
        return(temp)

    def GET_NOSEL_TEMP(self):
        if self.model == 'RS232':
            temp = self.instrument.read_register(AirJet['Nosel_temp'],
                                                 numberOfDecimals=1, signed=True)
        else:
            # temp = VISARW.read(self.add, "?TA")
            temp = self.instrument.query("?TA")
        return(temp)

    def get_dut_temp_safe(self, tcurrent=0.0):
        """ Returns a temperature even if the call to GET_DUT_TEMP returns an error"""
        tcurrentemp = tcurrent
        tz = "no temp"
        try:
            time.sleep(0.05)
            tz = float(self.GET_DUT_TEMP())
        except tz == "9E99":
            tcurrent = tcurrentemp
        except tz == "Err 1":
            tcurrent = tcurrentemp
        except IOError:
            tcurrent = tcurrentemp
        except visa.VisaIOError as e:
            print("\nvisa error caught", e)
            tcurrent = tcurrentemp
        except ValueError:
            tcurrent = tcurrentemp
        else:
            tcurrent = tz
        return tcurrent


    def SETTEMP(self,temp,acc,settle):
        #settle in mins
        def wait_until_target_reached(temp, tcurrent):
            tacc = 100
            while tacc > acc:
                tcurrent = self.get_dut_temp_safe(tcurrent)
                time.sleep(0.5)
                # print(tcurrent)
                tacc = abs(temp - float(tcurrent))
                print('{:5}'.format(tcurrent), end='\r')
                time.sleep(2)
        temp = float(temp)
        self.SP(temp)
        # VISARW.write(self.add,"SP%s" %temp)
        print("target temperture: ", temp)
        tcurrent = self.get_dut_temp_safe()
        wait_until_target_reached(temp, tcurrent) # wait for target within accuracy range
        time.sleep(2)
        tcurrent = self.get_dut_temp_safe(temp)
        error_temp = abs(temp - tcurrent)
        if error_temp > acc: # it may have overshot
            wait_until_target_reached(temp, tcurrent) # if so, try again
        print("\nREACHED TEMP, SETTLING")
        wait = settle * 60
        # y = wait
        settle_temp = temp
        for x in reversed(range(0,wait)):
            time.sleep(1)
            settle_temp = self.get_dut_temp_safe(settle_temp)
            print('{:5}'.format(x), '{:5}'.format(settle_temp), end='\r')
            #y = y - 1
        print("\nDONE")
