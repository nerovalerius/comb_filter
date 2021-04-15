#  ______     ______     __    __     ______           ______   __     __         ______   ______     ______    
# /\  ___\   /\  __ \   /\ "-./  \   /\  == \         /\  ___\ /\ \   /\ \       /\__  _\ /\  ___\   /\  == \   
# \ \ \____  \ \ \/\ \  \ \ \-./\ \  \ \  __<         \ \  __\ \ \ \  \ \ \____  \/_/\ \/ \ \  __\   \ \  __<   
#  \ \_____\  \ \_____\  \ \_\ \ \_\  \ \_____\        \ \_\    \ \_\  \ \_____\    \ \_\  \ \_____\  \ \_\ \_\ 
#   \/_____/   \/_____/   \/_/  \/_/   \/_____/         \/_/     \/_/   \/_____/     \/_/   \/_____/   \/_/ /_/ 
#                                                                                                               
# Project       : Comb Filter - turn an arbitrary single section filter into a comb filter and visualization with a GUI
# File Purpose  : Holds the function which turns an arbitrary single section filter into a comb filter
# Course        : Digital Signal Processing 2 - Salzburg University Of Applied Sciences
# Author        : Armin Niedermueller
# Date          : 15.04.2021
# Literature    : none

import sys
import pip
import random

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
matplotlib.use('Qt5Agg')

import numpy as np
from scipy import signal
from scipy.ndimage.interpolation import shift

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QGridLayout,QPushButton, QApplication, QSlider, QCheckBox)
from PyQt5.QtCore import Qt


# Saves a Signal and its parameters
class MySignal(object):
    x = None
    y = None
    color = ''
    f_s = 0
    length = 0

    def __init__(self, y, x, color, f_s, length):
        self.x = x
        self.y = y
        self.color = color
        self.f_s = f_s
        self.length = length



# Class that plots our functions
class MplCanvas(FigureCanvasQTAgg):


    # Layout - 3 Rows, 2 Colums

    #   | Original Time Domain    | Original FFT Linear Spectrum    |
    #   | Upsampled Time Domain   | Upsampled FFT Linear Spectrum   |  
    #   | Downsampled Time Domain | Downsampled FFT Linear Spectrum |
    #   
    #   | Upsampling Slider       | Downsampling Slider             |


    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # Plot and its title
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.suptitle('Functions: Time Domain | Fourier Domain')

        # Format spaces between plots
        fig.subplots_adjust(left=0.125,
                  bottom=0.1, 
                  right=0.9, 
                  top=0.9, 
                  wspace=0.2, 
                  hspace=1)

        # The Plots and their formatting
        # PLOT 1
        self.original_signal_plot = fig.add_subplot(321, title='Original Square Signal')
        self.original_signal_plot.set_xlabel('t [s]')
        self.original_signal_plot.set_ylabel('f(t)')
        self.original_signal_plot.set_ylim(-2.0,2.0)
        
        # PLOT 2
        self.original_fft_plot = fig.add_subplot(322, title='Original Linear Spectrum')
        
        # PLOT 3
        self.upsampled_signal_plot = fig.add_subplot(323, title='Upsampled Square Signal')
        self.upsampled_signal_plot.set_xlabel('t [s]')
        self.upsampled_signal_plot.set_ylabel('f(t)')
        self.upsampled_signal_plot.set_ylim(-2.0,2.0)
        
        # PLOT 4
        self.upsampled_fft_plot = fig.add_subplot(324, title='Upsampled Linear Spectrum')
        
        # PLOT 5
        self.downsampled_signal_plot = fig.add_subplot(325, title='Downsampled Square Signal')
        self.downsampled_signal_plot.set_xlabel('t [s]')
        self.downsampled_signal_plot.set_ylabel('f(t)')
        self.downsampled_signal_plot.set_ylim(-2.0,2.0)
        
        # PLOT 6
        self.downsampled_fft_plot = fig.add_subplot(326, title='Downsampled Linear Spectrum')


        super(MplCanvas, self).__init__(fig)


# The Main window of our program
class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
  
    def initUI(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Set Window Size and Title
        self.setGeometry(200, 200, 1200, 900)
        self.setWindowTitle('Up- and Downsampling Demonstration - Armin Niedermüller')

        # Define a grid layout
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        # Define the Plot with its subplots
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Create checkboxes
        self.upsampleCheckBox = QCheckBox("Upsampling")
        self.downsampleCheckBox = QCheckBox("Downsampling")
        self.upsampleCheckBox.setChecked(False)
        self.downsampleCheckBox.setChecked(False)
        self.upsampleCheckBox.stateChanged.connect(self.upsamplingCheckboxAction)
        self.downsampleCheckBox.stateChanged.connect(self.downsamplingCheckboxAction)


        # Create a slider
        self.upsample_slider = QSlider(Qt.Horizontal)
        self.upsample_slider.setRange(0,10)
        self.upsample_slider.setSingleStep(1)
        self.upsample_slider.setValue(1)
        self.upsample_slider.setTickInterval(1)
        self.upsample_slider.setTickPosition(QSlider.TicksBothSides)

        # Create a slider
        self.downsample_slider = QSlider(Qt.Horizontal)
        self.downsample_slider.setRange(0,10)
        self.downsample_slider.setSingleStep(1)
        self.downsample_slider.setValue(1)
        self.downsample_slider.setTickInterval(1)
        self.downsample_slider.setTickPosition(QSlider.TicksBothSides)

        # Create Labels
        self.downsampleLabel = QtWidgets.QLabel()
        self.downsampleLabel.setText('Status: INACTIVE')
        self.upsampleLabel = QtWidgets.QLabel()
        self.upsampleLabel.setText('Status: INACTIVE')

        # Connect the sliders to our plots - if the slider value changes, the plot is updated
        self.upsample_slider.valueChanged[int].connect(self.upsamplePlot)
        self.downsample_slider.valueChanged[int].connect(self.downsamplePlot)

        # Layout - 3 Rows, 2 Colums

        #   | Original Time Domain      | Original FFT Linear Spectrum    |
        #   | Upsampled Time Domain     | Upsampled FFT Linear Spectrum   |  
        #   | Downsampled Time Domain   | Downsampled FFT Linear Spectrum |
        #   
        #   | Upsampling Checkbox       | Upsampling Slider               |
        #   | Upsampling Status         | Upsampling Slider               |
        #   | Downsampling Checkbox     | Downsampling Slider             |
        #   | Downsampling Status       | Downsampling Slider             |


        # Create a Grid Layout and put the single widgets into it
        #   | Original Time Domain    | Original FFT Linear Spectrum      |   
        #   | Upsampled Time Domain   | Upsampled FFT Linear Spectrum     | 
        #   | Downsampled Time Domain | Downsampled FFT Linear Spectrum   | 
        grid_layout.addWidget(self.canvas, 1,1,12,10) # span over 12 rows and 10 columns
        
        #   | Upsampling Checkbox       | Upsampling Slider               |
        #   | Upsampling Status         | Upsampling Slider               |
        grid_layout.addWidget(self.upsampleCheckBox, 13,1,1,1)
        grid_layout.addWidget(self.upsampleLabel, 14,1,1,1)
        grid_layout.addWidget(self.upsample_slider, 13,2,2,9)     
        
        #   | Downsampling Checkbox     | Downsampling Slider             |
        #   | Downsampling Status       | Downsampling Slider             |
        grid_layout.addWidget(self.downsampleLabel, 15,1,1,1)
        grid_layout.addWidget(self.downsampleCheckBox, 16,1,1,1)
        grid_layout.addWidget(self.downsample_slider, 15,2,2,9)

       
        # A dictionary where our functions are stored
        self.plot_refs = dict()
        self.signals = dict()

        # Initial Values for checkboxes
        self.activateUpsampling = False
        self.activateDownsampling = False

        self.show()


    # Upsampling Checkbox Function
    def upsamplingCheckboxAction(self, state):
        if (Qt.Checked == state):
            # activate upsampling
            self.activateUpsampling = True
            self.upsampleLabel.setText('Status: ACTIVE')
        else: 
            # deactivate upsampling
            self.activateUpsampling = False
            self.upsampleLabel.setText('Status: INACTIVE')
            self.upsamplePlot(1)


    # Downsampling Checkbox Function
    def downsamplingCheckboxAction(self, state):
        if (Qt.Checked == state):
            # activate downsampling
            self.activateDownsampling = True
            self.downsampleLabel.setText('Status: ACTIVE')
        else: 
            # deactivate downsampling
            self.activateDownsampling = False
            self.downsampleLabel.setText('Status: INACTIVE')
            self.downsamplePlot(1)


    # Add a function to our plots
    def addFunction(self, y, x, color, name, f_s, length):
        
        newSignal = MySignal(y, x, color, f_s, length)

        # SIGNAL - Add plot reference to our List of plot refs
        self.plot_refs[name] = self.canvas.original_signal_plot.plot(newSignal.y,
                                                newSignal.x,
                                                newSignal.color) 
        # And add the functions to our extra list
        self.signals[name] = newSignal

        # SPECTRUM
        X = np.fft.fft(x)

        # Add plot reference to our List of plot refs
        self.plot_refs[name + 'fft'] = self.canvas.original_fft_plot.plot(abs(X), newSignal.color) 

        # update Plots
        self.upsamplePlot(1)
        self.downsamplePlot(1)


    # Function to be called after using the slider
    def upsamplePlot(self, value):
        
        if self.signals['square signal'] is None:
            return False 

        f_s = self.signals['square signal'].f_s
        length = self.signals['square signal'].length

        # Upsampling
        # 0 er Array erstellen
        l_upsampling = value
        np.zeros(f_s * l_upsampling)

        # our function
        x = self.signals['square signal'].x
        

        # Calculate FFT
        X = np.fft.fft(x)
        freq = np.fft.fftfreq(len(x), 1/f_s)

        # Add zeros
        X_upsampled = np.insert(X, int(X.shape[0]/2), np.zeros(f_s * l_upsampling))
        Y_upsampled = np.arange(0, X.shape[0] + f_s * l_upsampling)

        # Inverse FFT
        x_upsampled = np.fft.ifft(X_upsampled)
       
        # Keep energy the same after transformations / up-downsampling
        if l_upsampling != 0:
            x_upsampled *= X_upsampled.shape[0] / X.shape[0]
            
        # Create vector from 0 to 1 - stepsize = 1/fs
        t_upsampled = np.linspace(0, length,
                                 f_s
                                 + f_s * l_upsampling)

        # Only upsample if Checkbox is active
        if self.activateUpsampling is True:
            upsampledSignal = MySignal(t_upsampled, x_upsampled, 'g', f_s, length)
        else:
            upsampledSignal = self.signals['square signal']
            upsampledSignal.color = 'g'
            X_upsampled = X
            Y_upsampled = np.arange(0, X.shape[0])


        # Add the upsampled signal to our plots
        if self.plot_refs.get('upsampled square signal') is None:

            # Add SIGNAL plot reference to our List of plot_refs
            self.plot_refs['upsampled square signal'] = self.canvas.upsampled_signal_plot.plot(upsampledSignal.y,
                                                    upsampledSignal.x,
                                                    upsampledSignal.color) 

            # Add SPECTRUM plot reference to our List of plot_refs
            self.plot_refs['upsampled fft'] = self.canvas.upsampled_fft_plot.plot(
                                                    abs(X_upsampled),
                                                    upsampledSignal.color) 

        # change values over reference
        else:
            # SIGNAL
            self.plot_refs['upsampled square signal'][0].set_ydata(upsampledSignal.x)
            self.plot_refs['upsampled square signal'][0].set_xdata(upsampledSignal.y)
            self.plot_refs['upsampled square signal'][0].set_color(upsampledSignal.color)
            
            # SPECTRUM
            self.plot_refs['upsampled fft'][0].set_ydata(np.abs(X_upsampled))
            self.plot_refs['upsampled fft'][0].set_xdata(Y_upsampled)

            # SPECTRUM - change the x value range of the plot accordingly
            if self.activateUpsampling is True:
                self.canvas.upsampled_fft_plot.set_xlim(0,  X.shape[0] + f_s * l_upsampling)
            else:   
                self.canvas.upsampled_fft_plot.set_xlim(0,  X.shape[0])

        # Trigger the canvas to update and redraw.
        self.canvas.draw()



    # Function to be called after using the slider
    def downsamplePlot(self, value):
     
            if self.signals['square signal'] is None or value == 0:
                return False 

            # our function and sampling frequency
            x = self.signals['square signal'].x
            y = self.signals['square signal'].x
            f_s = self.signals['square signal'].f_s
            length = self.signals['square signal'].length

            # Our downsampling factor
            downsampling_factor = value

            # Create an FIR Anti-Aliasing Filter
            # Cutoff Frequency is f_s/2 
            # by - 0.01 we give a headroom for the filter of 1 %  
            b = signal.firwin(30, (1.0/downsampling_factor) - 0.01) 

            # Apply the Anti-Aliasgin Filter
            # Since a FIR filter only has b coefficients, set a = 1
            a=1
            lowpass = signal.lfilter(b, a, x) 

            # Create vector from 0 to 1 - stepsize = 1/fs
            t_downsampled = np.linspace(0, length,
                                 int(np.ceil(f_s / downsampling_factor)))

            # Perform the downsampling
            x_downsampled = lowpass[::downsampling_factor]
            
            # Calculate FFT
            X_downsampled = np.fft.fft(x_downsampled)
            Y_downsampled = np.arange(0, X_downsampled.shape[0])

            X = np.fft.fft(x)
            Y = np.arange(0, X.shape[0])

            # cancel time_shift
            x_shift = int(13/downsampling_factor)
                        
            # Keep energy the same after transformations / up-downsampling
            x_downsampled *= X_downsampled.shape[0] / X.shape[0]
            x_downsampled = np.concatenate((x_downsampled[x_shift:],x_downsampled[:x_shift]))

            # Only upsample if Checkbox is active
            if self.activateDownsampling is True:
                downsampledSignal = MySignal(t_downsampled, x_downsampled, 'b', f_s, length)
            else:
                downsampledSignal = self.signals['square signal']
                downsampledSignal.color = 'b'
                X_downsampled = X
                Y_downsampled = Y

            # Add the downsampled signal to our plots
            if self.plot_refs.get('downsampled square signal') is None:

                # Add SIGNAL plot reference to our List of plot_refs
                self.plot_refs['downsampled square signal'] = self.canvas.downsampled_signal_plot.plot(downsampledSignal.y,
                                                        downsampledSignal.x,
                                                        downsampledSignal.color) 

                # Add SPECTRUM plot reference to our List of plot_refs
                self.plot_refs['downsampled fft'] = self.canvas.downsampled_fft_plot.plot(
                                                        abs(X_downsampled),
                                                        downsampledSignal.color) 
            else:
                # SIGNAL
                self.plot_refs['downsampled square signal'][0].set_ydata(downsampledSignal.x)
                self.plot_refs['downsampled square signal'][0].set_xdata(downsampledSignal.y)
                self.plot_refs['downsampled square signal'][0].set_color(downsampledSignal.color)
            
                # SPECTRUM
                self.plot_refs['downsampled fft'][0].set_ydata(np.abs(X_downsampled))
                self.plot_refs['downsampled fft'][0].set_xdata(Y_downsampled)

                # SPECTRUM - change the x value range of the plot accordingly
                self.canvas.downsampled_fft_plot.set_xlim(0,  X_downsampled.shape[0])

            
            # Trigger the canvas to downdate and redraw.
            self.canvas.draw()






# calculate a Fourier Series for a Square Signal
def myFourierSeries(fs_signal, h_signal, len_signal, k_max_signal, frequency):
    """
    Parameters
    ----------
    fs_signal:    int,    Sampling frequency of the signal
    h_signal:     double, Amplitude
    len_signal:   int,    Signal length in seconds
    k_max_signal: int,    variable Fourier Series length

    Returns
    ---------
    f:            array[double], Fourier Series of a square signal
    """

    # Generate evenly spaced timestamps
    #x = np.linspace(0, len_signal, fs_signal, endpoint=False) 
    time = np.arange(0, len_signal, 1/fs_signal)   # Create vector from 0 to 1 - stepsize = 1/fs
    
    # This will be our resulting signal
    f = np.zeros([len_signal])

    # Go over all samples for our signal and calculate its value via fourier series
    for x in range(0, len_signal):

      # The inner sum - see RHS of formula
      sum = 0
      for k in range(1, k_max_signal+1, 2):
        sum += k**(-1) * np.sin(2 * np.pi * k * time[x] * frequency)
            
      # The scalar in front of the sum - see RHS of formula
      f[x] =  sum * 4 * h_signal * np.pi**(-1)
    
    return f 
