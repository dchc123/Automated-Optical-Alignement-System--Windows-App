import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import os
from numpy import genfromtxt
import numpy as np
import scipy

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

# Set option(s)
plt.rcParams['font.size'] = 15

# Create a figure with two axes:
# Top axes   :  Used to draw text containing the coordinates of the mouse
# Bottom axes:  Used to plot the data
fig, ax = plt.subplots(nrows=2,
                       ncols=1,
                       # Note: default figsize is [6.4, 4.8] in inches
                       figsize=(6.4, 5.6),
                       # Using height_ratios, we make the top axes small
                       # and the bottom axes as big as usual
                       gridspec_kw={'height_ratios': [0.8 / 5.6, 4.8 / 5.6]}
                       )

# ax[0] is where the coordinates will be shown, so remove the x- and y-axis
ax[0].axis('off')

# Set default text on the top axes
default_text = "Cursor location will be shown here"
ax[0].text(0.5, 0.5, default_text, va='center', ha='center', color='black')

# Plot the data on the bottom axes (ax[1])
ax[1].imshow(results,cmap='plasma', extent=[XStart,XEnd,YEnd,YStart])

numrows, numcols = results.shape

# Define a function which is called when the location of the mouse changes
def update_mouse_coordinates(ax, text,event):
    # Don't print coordinates if not on bottom axes
    if event.inaxes == ax or event.xdata == None or event.ydata == None:
        ax.texts[0].set_text(text)
        plt.draw()
        return


    gradientX=(shape[0])/(XEnd-XStart)
    gradientY=(shape[1])/(YEnd-YStart)

    col = round(gradientX*event.xdata - gradientX*XStart)
    row = round(gradientY*event.ydata - gradientY*YStart)

    if col >= 0 and col < numcols and row >= 0 and row < numrows:
        z = results[row, col]

    # Show mouse coordinates to user
    ax.texts[0].set_text(f"X={event.xdata:.4f} mm     Y={event.ydata:.4f} mm     I={z:.4f}e-11 A")
    plt.draw()


plt.connect('motion_notify_event',
            # Using a lambda expression, we supply the top axes and the default
            # text to this function (our resulting function may only have one
            # argument!)
            lambda event: update_mouse_coordinates(ax[0], default_text,event)
            )


plt.show()


quit()