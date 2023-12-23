import numpy as np
from COMMON.Equipment.SourceMeter.Keithley24XX.keithley_2400 import Keithley2400
import matplotlib.pyplot as plt
import os.path

#TODO Work out if float to byte array is needed and implement - remember only the automatic scan needs to take average readings bc it is used for progressing to next scan.
#     decimal is only needed for running local, corner and edge scans

#TODO motors should initialise themselves if user hasn't already

#TODO double check that Piezo Voltages are calculated correctly

#TODO 3D plotting software needs replaced

#TODO Automatic scan outputs average reading in real time on 2d plot -Python

#TODO Fiddle with motor speeds

#TODO Oscilloscope

keithley = Keithley2400(address="TCPIP0::10.160.72.212::gpib0,9::INSTR")

f = open(r'\\.\pipe\NPtest', 'r+b', 0)
i = 1

Mode = f.read(1)
Mode = int.from_bytes(Mode,"big")

Length = f.read(1)
Length = 2*(int.from_bytes(Length,"big", signed=True))+1
results = np.zeros((Length,Length))
Greatest_Average=0

if Mode==0:   #Not Connected to Hardware Single Scan

    while True:
        s = 'Message[{0}]'.format(i)
        i += 1
        B_array = f.read(4)
        f.seek(0)

        try:
            if B_array[0] == 107 and B_array[1] == 105 and B_array[2] == 108 and B_array[3] == 108:
                break

            else:
                x = int(B_array[0]);
                y = int(B_array[1]);

        except:
            x = int(B_array[0]);
            y = int(B_array[1]);

        print(i)
        results[x][y] = i
        current_reading = int(results[x][y])
        current_reading_bytes = current_reading.to_bytes(4, 'big')

        f.write(current_reading_bytes)

    base_path = "C:/Users/bscriven/Documents/Optical_Alignment_Project/C#_work/results/CSV_data/"

    file_name = f.read().decode("ascii")
    f.seek(0)
    file_path = base_path + file_name + ".csv"

    if os.path.isfile(file_path) == False:
        np.savetxt(file_path, results, delimiter=",")
    else:
        i = 0

        while os.path.exists(file_path):
            i += 1
            file_path = base_path + file_name + "_" + str(i) + ".csv"

        np.savetxt(file_path, results, delimiter=",")

    quit()

if Mode==1:     #Connected to hardware single scan

    keithley.connect()

    keithley.channel[1].terminal_select = "FRONT"
    keithley.channel[1].remote_sensing = "DISABLE"
    keithley.channel[1].output = 'disable'
    keithley.channel[1].source.current.compliance_current = 100e-6
    keithley.channel[1].source.voltage.setpoint = 3
    keithley.channel[1].output = 'enable'

    while True:
        s = 'Message[{0}]'.format(i)
        i += 1
        B_array = f.read(4)

        try:
            if B_array[0] == 107 and B_array[1] == 105 and B_array[2] == 108 and B_array[3] == 108:

                # results.tobytes()
                # f.write(results)

                break
            else:
                x = int(B_array[0]);
                y = int(B_array[1]);

        except:
            x = int(B_array[0]);
            y = int(B_array[1]);

        current = keithley.channel[1].measure.current.value
        print(i)
        results[x][y] = current
        current_reading = int(results[x][y])
        current_reading_bytes = current.to_bytes(4, 'big')

        f.write(current_reading_bytes)

    base_path = "C:/Users/bscriven/Documents/Optical_Alignment_Project/C#_work/results/CSV_data/"
    file_name = f.read().decode("ascii")
    file_path = base_path + file_name + ".csv"

    if os.path.isfile(file_path) == False:
        np.savetxt(file_path, results, delimiter=",")
    else:

        i = 0

        while os.path.exists(file_path):
            i += 1
            file_path = base_path + file_name + "_" + str(i) + ".csv"

        np.savetxt(file_path, results, delimiter=",")

    keithley.disconnect()

    quit()

if Mode==2:  #Automatic Scan

    ResultsList = [None] * Length ** 3
    move_on_command = 'kill'
    move_on_command = bytes(move_on_command, 'ascii')


    z=0;
    results = np.zeros((Length, Length,Length))

    while True:
        s = 'Message[{0}]'.format(i)
        i += 1
        B_array = f.read(4)
        f.seek(0)

        try:
            if B_array[0] == 107 and B_array[1] == 105 and B_array[2] == 108 and B_array[3] == 108:

                break

            elif B_array[0] == 100 and B_array[1] == 111 and B_array[2] == 110 and B_array[3] == 101:

                Greatest_Average_Position_Bytes= Greatest_Average_Position.to_bytes(2,'big')
                f.write(Greatest_Average_Position_Bytes)

                i = 0
                z += 1
                Greatest_Average = 0
                Greatest_Average_Position = 0

            else:

                x = int(B_array[0]);
                y = int(B_array[1]);

        except:
            x = int(B_array[0]);
            y = int(B_array[1]);

        if len(B_array)==2:

            print(i)
            results[x][y][z] = i
            current_reading = int(results[x][y][z])
            current_reading_bytes = current_reading.to_bytes(4, 'big')

            if results[x][y][z]==0:
                results[x][y][z] = i
            else:
                results[x][y][z] = (results[x][y][z] + i) / 2

            ResultsList[i]=int(results[x][y][z])
            Average = ResultsList[i]


            if i>9:
                for j in range(1,8,1):
                    Average=(Average+ResultsList[i-j])/2

            if Average>Greatest_Average:
                Greatest_Average=Average
                Greatest_Average_Position = i


            if Average>5000:
                f.write(move_on_command)
                i = 0
                z+=1
                Greatest_Average = 0
                Greatest_Average_Position=0
            else:
                f.write(current_reading_bytes)

    Results_Arrays2d = [None] * (z)

    for k in range(0,z-1,1):
        Results_Arrays2d[k]=results[:,:,k]

    base_path = "Results/CSV_Data/Multi-Layer-Scan"

    if not os.path.exists(base_path):
        os.makedirs(base_path)
    else:
        i=0
        New_base_path=base_path

        while os.path.exists(New_base_path):
            i += 1
            New_base_path = base_path + "_" + str(i)

        os.makedirs(New_base_path)
        base_path = New_base_path

    file_name_length = int.from_bytes((f.read(1)), 'big');

    file_name = f.read(file_name_length).decode("ascii")

    Layer_Data_Filenames = [None]*z

    for l in range(0,z-1,1):
        Layer_Data_Filenames[l] = base_path + "/" + file_name + "_Layer" + str(l) + ".csv"

        if os.path.isfile(Layer_Data_Filenames[l]) == False:
            np.savetxt(Layer_Data_Filenames[l], Results_Arrays2d[l], delimiter=",")
        else:

            i = 0

            while os.path.exists(base_path):
                i += 1
                Layer_Data_Filenames[l] = base_path + file_name + "_Layer" + str(l) + "_" + i + ".csv"

            np.savetxt(Layer_Data_Filenames[l], Results_Arrays2d[l], delimiter=",")

    quit()
