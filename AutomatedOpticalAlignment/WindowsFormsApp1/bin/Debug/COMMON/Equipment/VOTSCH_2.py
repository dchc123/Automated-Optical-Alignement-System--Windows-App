"""Votsch 7004 Driver"""

import time
import serial
import analysis

class VOTSCH_2:

    # port = 'COM1'
    # baudrate = 9600
    # timeout = 10

    def __init__(self, add, port, baudrate, timeout):
        self.add = add
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def PARSE(self, temp):
        temp = str(temp)
        if '.' not in temp:
            temp = temp + '.0'
        n = 6 - len(temp)
        if temp[0] == '-':
            print '-' + '0'*(n - 1) + temp[1:]
            temp = '-' + '0'*(n - 1) + temp[1:]
        else:
            temp = '0'*n + temp
        return temp

    def TEMPREAD(self, add):
        ser = self.ser
        ser.isOpen()
        # ser.open()
        time.sleep(0.1)
        _payload_ = '$%sI' %self.add
        _payload = _payload_.encode('utf-8')
        ser.write(_payload + '\r\n')
        out = ''
        time.sleep(0.5)
        while ser.inWaiting() > 0:
            out += ser.read(1)
        if out != '':
            out = out.split()
            if len(out) > 15:
                del out[0]
            format = []
            if len(out) > 1:
                for x in out:
                    i = 0
                    if x[0] == '-':
                        m = '-'
                        n = 1
                    else:
                        m = ''
                        n = 0
                    while x[i + n] == '0':
                        i += 1
                    x = m + x[i + n:]
                    format.append(x)
                time.sleep(0.1)
                tempSet  = format[0]
                tempRead = format[1]
            # print "Set Temperature: " + tempSet + "C "
            # print "Actual Temperature: " + tempRead + "C"
            return tempRead
            ser.close()

    def SETTEMP(self, temp, temp1, temp2, clock2, acc, settle):
        temp = float(temp)
        self.SP(temp)
        print "RUN"
        tacc = 100
        tcurrent = 0
        tcurrentemp = 0
        while tacc > acc:
            tcurrentemp = tcurrent
            start = time.time()
            tz = float(self.TEMPREAD(self.add))
            end = time.time()
            clock2 += end - start
            # print 'Clock: ', clock2, 's'
            dataX = int(clock2)
            dataY = tz
            analysis.PLOT(analysis.xdata, analysis.ydata, dataX, dataY, False)
            tcurrent = tz
            time.sleep(0.5)
            tacc = abs(temp - float(tcurrent))
            time.sleep(2)
        print("REACHED TEMP, SETTLING")
        analysis.PLOT(analysis.xdata, analysis.ydata, dataX, dataY, True)
        wait = settle * 30
        y = wait
        for x in range(0,wait):
            # print str(y)+'\r',
            start = time.time()
            tz = float(self.TEMPREAD(self.add))
            end = time.time()
            clock2 += end - start
            dataX = int(clock2)
            dataY = tz
            analysis.PLOT(analysis.xdata, analysis.ydata, dataX, dataY, False)
            time.sleep(1)
            y = y - 1
        print("DONE")
        # analysis.PLOT(DATA)
        # result_file.close()
        return clock2


    def SP(self, temp):
        ser = self.ser
        ser.open
        ser.isOpen()
        temp = str(temp)
        temp = self.PARSE(temp)
        _payload_ = '$%sE %s 0000.0 0000.0 0000.0 0000.0 0000.0 0000.0 01000000000000000000000000000000' %(self.add, temp)
        _payload = _payload_.encode('utf-8')
        ser.write(_payload + '\r\n')
        out = ''
        time.sleep(1)





