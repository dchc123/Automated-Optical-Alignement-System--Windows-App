import numpy as np
from COMMON.Equipment.SourceMeter.Keithley24XX.keithley_2400 import Keithley2400
import matplotlib.pyplot as plt
import os.path
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

#TODO Work out if float to byte array is needed and implement - remember only the automatic scan needs to take average readings bc it is used for progressing to next scan.
#     decimal is only needed for running local, corner and edge scans

#TODO motors should initialise themselves if user hasn't already

#TODO double check that Piezo Voltages are calculated correctly

#TODO 3D plotting software needs replaced

#TODO Automatic scan outputs average reading in real time on 2d plot -Python

#TODO Fiddle with motor speeds

#TODO Oscilloscope

#TODO average of 9 point square should have tiny step sizes I think

f = open("GPIBAddress.txt", "r")
address = f.read()

address = "TCPIP0::" + address + "::gpib0,9::INSTR"

keithley = Keithley2400(address)

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

    base_path = "Results/CSV_Data/"

    file_name_length = int.from_bytes((f.read(1)), 'big');

    file_name = f.read(file_name_length).decode("ascii")
    file_path = base_path + file_name + ".csv"

    shape = list(results.shape)
    file_name_split = file_name.split('_')

    XStart = float(file_name_split[0]) - ((shape[0] - 1) / 2 * float(file_name_split[2]))
    XEnd = float(file_name_split[0]) + ((shape[0] - 1) / 2 * float(file_name_split[2]))
    YStart = float(file_name_split[1]) - ((shape[1] - 1) / 2 * float(file_name_split[2]))
    YEnd = float(file_name_split[1]) + ((shape[1] - 1) / 2 * float(file_name_split[2]))

    if os.path.isfile(file_path) == False:
        i = 0
        i = i.to_bytes(4, 'big')
        f.write(i)
    else:

        i = 0

        while os.path.exists(file_path):
            i += 1

            file_path = base_path + file_name + "_" + str(i) + ".csv"

        file_name = file_name + "_" + str(i)

        folder_number = i.to_bytes(4, 'big')

        f.write(folder_number)

    np.savetxt(file_path, results, delimiter=",")

    fig2 = plt.figure()

    ax = fig2.add_subplot(111)
    ax.set_title('Current Readings')
    fig2.suptitle('Stepper Scan', fontsize=20)
    plt.imshow(results, cmap='plasma', extent=[XStart,XEnd,YStart,YEnd])
    ax.set_aspect('equal')
    #plt.show()

    cax = fig2.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(False)
    cax.get_yaxis().set_visible(False)
    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation='vertical')
    #plt.show()

    root = "Results/JPG_Data/"
    file_path = root + file_name + "_ViewB"

    fig2.savefig(file_path + '.jpg')

    rows = range(len(results))
    columns = range(len(results[0]))

    hf = plt.figure()
    ha = hf.add_subplot(111, projection='3d')

    X, Y = numpy.meshgrid(rows, columns)  # `plot_surface` expects `x` and `y` data to be 2D

    X = ((XEnd - XStart) / shape[0]) * X + XStart
    Y = ((YEnd - YStart) / shape[1]) * Y + YStart

    ha.plot_surface(X.T, Y.T, results, rstride=1, cstride=1,
                cmap='plasma', edgecolor='none')

    ha.set_title('Current Readings')

    hf.suptitle('Stepper Scan', fontsize=20)
    #ha.set_xlim(XStart, XEnd)
    #ha.set_ylim(YStart, YEnd)

    Xlabel = ha.set_xlabel('X-Axis', fontsize=8)
    Ylabel = ha.set_ylabel('Y-Axis', fontsize=8)
    Zlabel = ha.set_zlabel('current readings (e-11)', fontsize=8)

    file_path = root+file_name

    hf.savefig(file_path+'.jpg')

    #plt.show()

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

                break
            else:
                x = int(B_array[0]);
                y = int(B_array[1]);

        except:
            x = int(B_array[0]);
            y = int(B_array[1]);

        current = 1e11*keithley.channel[1].measure.current.value
        print(i)
        results[x][y] = current
        current_reading = int(results[x][y])
        current_reading_bytes = current_reading.to_bytes(4, 'big')

        f.write(current_reading_bytes)

    base_path = "Results/CSV_Data/"

    file_name_length = int.from_bytes((f.read(1)), 'big');

    file_name = f.read(file_name_length).decode("ascii")
    file_path = base_path + file_name + ".csv"

    shape = list(results.shape)
    file_name_split = file_name.split('_')

    XStart = float(file_name_split[0]) - ((shape[0] - 1) / 2 * float(file_name_split[2]))
    XEnd = float(file_name_split[0]) + ((shape[0] - 1) / 2 * float(file_name_split[2]))
    YStart = float(file_name_split[1]) - ((shape[1] - 1) / 2 * float(file_name_split[2]))
    YEnd = float(file_name_split[1]) + ((shape[1] - 1) / 2 * float(file_name_split[2]))

    if os.path.isfile(file_path) == False:
        i = 0
        i = i.to_bytes(4, 'big')
        f.write(i)
    else:

        i = 0

        while os.path.exists(file_path):
            i += 1
            file_path = base_path + file_name + "_" + str(i) + ".csv"

        file_name = file_name + "_" + str(i)

        folder_number = i.to_bytes(4, 'big')

        f.write(folder_number)

    np.savetxt(file_path, results, delimiter=",")
    fig2 = plt.figure()

    ax = fig2.add_subplot(111)
    ax.set_title('colorMap')
    plt.imshow(results, cmap='plasma', extent=[XStart,XEnd,YStart,YEnd])
    ax.set_aspect('equal')

    cax = fig2.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(False)
    cax.get_yaxis().set_visible(False)
    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation='vertical')
    # plt.show()

    root = "Results/JPG_Data/"
    file_path = root + file_name + "_ViewB"

    fig2.savefig(file_path + '.jpg')

    rows = range(len(results))
    columns = range(len(results[0]))

    hf = plt.figure()
    ha = hf.add_subplot(111, projection='3d')

    X, Y = numpy.meshgrid(rows, columns)  # `plot_surface` expects `x` and `y` data to be 2D

    X = ((XEnd - XStart) / shape[0]) * X + XStart
    Y = ((YEnd - YStart) / shape[1]) * Y + YStart

    ha.plot_surface(X.T, Y.T, results, rstride=1, cstride=1,
                    cmap='plasma', edgecolor='none')

    ha.set_title('Current Readings')

    hf.suptitle('Stepper Scan', fontsize=20)

    Xlabel = ha.set_xlabel('X-Axis', fontsize=8)
    Ylabel = ha.set_ylabel('Y-Axis', fontsize=8)
    Zlabel = ha.set_zlabel('current readings (e-11)', fontsize=8)

    file_path = root + file_name

    hf.savefig(file_path + '.jpg')

    keithley.disconnect()

    quit()

if Mode==2:  #Automatic Scan NO hardware

    ResultsList = [None] * Length ** 3
    move_on_command = 'kill'
    move_on_command = bytes(move_on_command, 'ascii')

    z=0;
    results = np.zeros((Length, Length,Length))
    MatrixElementsX = np.zeros(11)
    MatrixElementsY = np.zeros(11)

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

            if i<13:
                MatrixElementsX[i-2] = int(B_array[0])
                MatrixElementsY[i-2] = int(B_array[1])

            if i>9:
                for j in range(1,8,1):
                    Average=(Average+ResultsList[i-j])/2

            if i>12:
                MatrixElementsX=np.roll(MatrixElementsX, -1)
                MatrixElementsY=np.roll(MatrixElementsY, -1)

                MatrixElementsX[10]=int(B_array[0])
                MatrixElementsY[10]=int(B_array[1])

            if Average>Greatest_Average:
                Greatest_Average=Average
                Greatest_Average_Position = i

            XSpread = max(MatrixElementsX)-min(MatrixElementsX)
            YSpread = max(MatrixElementsY)-min(MatrixElementsY)

            # if i>4995:
            #    print("test")

            #Conditions for next scan
            if MatrixElementsX[0]==MatrixElementsX[10] and MatrixElementsY[0]==MatrixElementsY[10] and MatrixElementsX[0]!=max(MatrixElementsX) and MatrixElementsY[0]!=max(MatrixElementsY):
               if Average>5000:
                    f.write(move_on_command)
                    i = 0
                    z+=1
                    Greatest_Average = 0
                    Greatest_Average_Position=0
               else:
                    f.write(current_reading_bytes)
            else:
                f.write(current_reading_bytes)

    Results_Arrays2d = [None] * (z)

    for k in range(0,z-1,1):
        Results_Arrays2d[k]=results[:,:,k]

    base_path = "Results/CSV_Data/Multi-Layer-Scan"

    if not os.path.exists(base_path):
        os.makedirs(base_path)
        i=0
        i=i.to_bytes(4,'big')
        f.write(i)
    else:
        i=0
        New_base_path=base_path

        while os.path.exists(New_base_path):
            i += 1
            New_base_path = base_path + "_" + str(i)

        os.makedirs(New_base_path)
        base_path = New_base_path

        folder_number = i.to_bytes(4, 'big')

        f.write(folder_number)


    file_name_length = int.from_bytes((f.read(1)), 'big');

    file_name = f.read(file_name_length).decode("ascii")

    layers = z.to_bytes(4, 'big')

    f.write(layers)

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

if Mode==3:  #Automatic Scan with hardware

    keithley.connect()

    keithley.channel[1].terminal_select = "FRONT"
    keithley.channel[1].remote_sensing = "DISABLE"
    keithley.channel[1].output = 'disable'
    keithley.channel[1].source.current.compliance_current = 100e-6
    keithley.channel[1].source.voltage.setpoint = 3
    keithley.channel[1].output = 'enable'

    ResultsList = [None] * Length ** 3
    move_on_command = 'kill'
    move_on_command = bytes(move_on_command, 'ascii')

    z=0;
    results = np.zeros((Length, Length,Length))
    MatrixElementsX = np.zeros(11)
    MatrixElementsY = np.zeros(11)

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

            current = 1e11 * keithley.channel[1].measure.current.value
            print(i)
            results[x][y][z] = current
            current_reading = int(results[x][y][z])
            current_reading_bytes = current_reading.to_bytes(4, 'big')

            if results[x][y][z]==0:
                results[x][y][z] = current
            else:
                results[x][y][z] = (results[x][y][z] + current) / 2

            ResultsList[i]=int(results[x][y][z])
            Average = ResultsList[i]

            if i<13:
                MatrixElementsX[i-2] = int(B_array[0])
                MatrixElementsY[i-2] = int(B_array[1])

            if i>9:
                for j in range(1,8,1):
                    Average=(Average+ResultsList[i-j])/2

            if i>12:
                MatrixElementsX=np.roll(MatrixElementsX, -1)
                MatrixElementsY=np.roll(MatrixElementsY, -1)

                MatrixElementsX[10]=int(B_array[0])
                MatrixElementsY[10]=int(B_array[1])

            if Average>Greatest_Average:
                Greatest_Average=Average
                Greatest_Average_Position = i

            XSpread = max(MatrixElementsX)-min(MatrixElementsX)
            YSpread = max(MatrixElementsY)-min(MatrixElementsY)

        #   if i>4995:
          #      print("test")

        target = 150
        temp_target=((0.5+(z/10)))*target

            #Conditions for next scan
        if Average>temp_target:

            if MatrixElementsX[0]==MatrixElementsX[10] and MatrixElementsY[0]==MatrixElementsY[10] and MatrixElementsX[0]!=max(MatrixElementsX) and MatrixElementsY[0]!=max(MatrixElementsY):
                f.write(move_on_command)
                ResultsList[0:i] = [0] * i
                i = 0
                z+=1
                Greatest_Average = 0
                Greatest_Average_Position=0
            else:
                f.write(current_reading_bytes)
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

        folder_number = i.to_bytes(4, 'big')

        f.write(folder_number)


    file_name_length = int.from_bytes((f.read(1)), 'big');

    file_name = f.read(file_name_length).decode("ascii")

    layers = z.to_bytes(4, 'big')

    f.write(layers)

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

    keithley.disconnect()

    quit()


