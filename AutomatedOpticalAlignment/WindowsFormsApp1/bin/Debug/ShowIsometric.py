import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import os
from numpy import genfromtxt
import pandas as pd
import numpy as np


f = open(r'\\.\pipe\NPtest', 'r+b', 0)

file_name_length = int.from_bytes((f.read(1)), 'big');

file_name = f.read(file_name_length).decode("ascii")

base_path = os.getcwd()

file_path = base_path + "/Results/CSV_Data/" + file_name + ".csv"

results = genfromtxt(file_path, delimiter=',')



shape = list(results.shape)
file_name = file_name.split('_')

XStart = float(file_name[0])-((shape[0]-1)/2 * float(file_name[2]))
XEnd = float(file_name[0])+((shape[0]-1)/2 * float(file_name[2]))
YStart = float(file_name[1])-((shape[1]-1)/2 * float(file_name[2]))
YEnd = float(file_name[1])+((shape[1]-1)/2 * float(file_name[2]))

rows = range(len(results))
columns = range(len(results[0]))

hf = plt.figure()
ha = hf.add_subplot(111, projection='3d')

X, Y = numpy.meshgrid(rows, columns)  # `plot_surface` expects `x` and `y` data to be 2D

X = ((XEnd-XStart)/shape[0])*X + XStart
Y = ((YEnd-YStart)/shape[1])*Y + YStart

ha.plot_surface(X.T, Y.T, results, rstride=1, cstride=1,
                cmap='plasma', edgecolor='none')

ha.set_title('Current Readings')

hf.suptitle('Stepper Scan', fontsize=20)

Xlabel = ha.set_xlabel('X-Axis', fontsize=8)
Ylabel = ha.set_ylabel('Y-Axis', fontsize=8)
Zlabel = ha.set_zlabel('current readings (e-11)', fontsize=8)

plt.show()

quit()