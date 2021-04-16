#  ______     ______     __    __     ______           ______   __     __         ______   ______     ______    
# /\  ___\   /\  __ \   /\ "-./  \   /\  == \         /\  ___\ /\ \   /\ \       /\__  _\ /\  ___\   /\  == \   
# \ \ \____  \ \ \/\ \  \ \ \-./\ \  \ \  __<         \ \  __\ \ \ \  \ \ \____  \/_/\ \/ \ \  __\   \ \  __<   
#  \ \_____\  \ \_____\  \ \_\ \ \_\  \ \_____\        \ \_\    \ \_\  \ \_____\    \ \_\  \ \_____\  \ \_\ \_\ 
#   \/_____/   \/_____/   \/_/  \/_/   \/_____/         \/_/     \/_/   \/_____/     \/_/   \/_____/   \/_/ /_/ 
#                                                                                                               
# Project       : Comb Filter - turn an arbitrary single section filter into a comb filter and visualization with a GUI
# File Purpose  : Handles front end, filter creation and user interaction  
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

from combfilter import *
import numpy as np
from scipy import signal
from scipy.ndimage.interpolation import shift

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QGridLayout,QPushButton, QApplication, QSlider, QCheckBox)
from PyQt5.QtCore import Qt

# TODOs
# user can design a FIR filter with sliders  / knobs
# user can design a IIR Filter (must be stable)
# interpolate both filter design with the combfilter function
# visualize filter responses of the designed filters and the interpolated filters
# Plots should be labeled and must have axis labeling.

# ---------------------------------------------------------------------------------------------    
# Classes
# --------------------------------------------------------------------------------------------- 


# Saves a Signal and its parameters
class MySignal(object):
    x = None
    y = None
    color = ''
    f_s = 0
    length = 0

    def __init__(self, y, x, color, f_s, length=1):
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
        self.iir_filter_plot = fig.add_subplot(321, title='Original Square Signal')
        self.iir_filter_plot.set_xlabel('t [s]')
        self.iir_filter_plot.set_ylabel('f(t)')
        self.iir_filter_plot.set_ylim(-2.0,2.0)
        
        # PLOT 2
        self.original_fft_plot = fig.add_subplot(322, title='Original Linear Spectrum')
        
        # PLOT 3
        self.fir_filter_plot = fig.add_subplot(323, title='Upsampled Square Signal')
        self.fir_filter_plot.set_xlabel('t [s]')
        self.fir_filter_plot.set_ylabel('f(t)')
        self.fir_filter_plot.set_ylim(-2.0,2.0)
        
        # PLOT 4
        self.fir_comb_filter_plot = fig.add_subplot(324, title='Upsampled Linear Spectrum')
        
        # PLOT 5
        self.iir_filter_plot = fig.add_subplot(325, title='Downsampled Square Signal')
        self.iir_filter_plot.set_xlabel('t [s]')
        self.iir_filter_plot.set_ylabel('f(t)')
        self.iir_filter_plot.set_ylim(-2.0,2.0)
        
        # PLOT 6
        self.iir_comb_filter_plot = fig.add_subplot(326, title='Downsampled Linear Spectrum')


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
        self.plot_refs[name] = self.canvas.iir_filter_plot.plot(newSignal.y,
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


    # Add a filter to our plots
    def addFilter(self, f_0, f_s, d_t, color, type=None, Q=1):
        
        if type == 'fir_notch':
            f1 = 3000
            numtaps = 3
    
            # filter coeffs
            a = 1
            b = signal.firwin(numtaps, f1, pass_zero=False, fs=f_s)
        elif type == 'iir_notch':
            # filter coeffs
            b,a = signal.iirnotch(f_0, Q, f_s)

        else: 
            return 0
    
        # Transfer function - used fore dimpulse, dstep, scipy,...
        #filter = signal.TransferFunction(b, a, dt=d_t)
       
        # Calculate frequency and amplitude
        freq, h = signal.freqz(b, a, fs=f_s)
       
        # Create filter object
        newFilter = MySignal(freq, h, color, f_s)
       
        # SIGNAL - Add plot reference to our List of plot refs
        if type == 'fir_notch':
            self.plot_refs[type] = self.canvas.fir_filter_plot.plot(newFilter.y,
                                                newFilter.x,
                                                newFilter.color)
        elif type == 'iir_notch':
            self.plot_refs[type] = self.canvas.iir_filter_plot.plot(newFilter.y,
                                                newFilter.x,
                                                newFilter.color) 
       
        # And add the functions to our extra list
        self.signals[type] = newFilter
    
        # SPECTRUM
        #X = np.fft.fft(x)
        #
        ## Add plot reference to our List of plot refs
        #self.plot_refs[name + 'fft'] = self.canvas.original_fft_plot.plot(abs(X), newSignal.color) 
        #
        ## update Plots
        #self.upsamplePlot(1)
        #self.downsamplePlot(1)


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
            self.plot_refs['upsampled square signal'] = self.canvas.fir_filter_plot.plot(upsampledSignal.y,
                                                    upsampledSignal.x,
                                                    upsampledSignal.color) 

            # Add SPECTRUM plot reference to our List of plot_refs
            self.plot_refs['upsampled fft'] = self.canvas.fir_comb_filter_plot.plot(
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
                self.canvas.fir_comb_filter_plot.set_xlim(0,  X.shape[0] + f_s * l_upsampling)
            else:   
                self.canvas.fir_comb_filter_plot.set_xlim(0,  X.shape[0])

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
                self.plot_refs['downsampled square signal'] = self.canvas.iir_filter_plot.plot(downsampledSignal.y,
                                                        downsampledSignal.x,
                                                        downsampledSignal.color) 

                # Add SPECTRUM plot reference to our List of plot_refs
                self.plot_refs['downsampled fft'] = self.canvas.iir_comb_filter_plot.plot(
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
                self.canvas.iir_comb_filter_plot.set_xlim(0,  X_downsampled.shape[0])

            
            # Trigger the canvas to downdate and redraw.
            self.canvas.draw()

# ---------------------------------------------------------------------------------------------    
# MAIN
# ---------------------------------------------------------------------------------------------    
def main():
    # create square wave signal
    length = 1           # seconds
    f_s = 10000          # Hz - Sampling Frequency
    f_0 = 1000           # Frequency where the notch lies
    d_t = 1 / f_s        # discrete time steps    
    Q = 20               # Quality Factor

    # Create vector from 0 to 1 - stepsize = 1/fs
    # Calculate evenly spaced numbers over a specified interval.
    t = np.linspace(0, length, f_s, endpoint=False)

    # Fourier series of a square signal
    #x = myFourierSeries(fs, amplitude, t.shape[0], k_max_signal, f)

    # Our Application
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()

    # Add a function to our Application - y, x, color, name, sample frequency, duration in seconds
    #mainWindow.addFunction(t, x, 'r', 'square signal', fs, length)
    mainWindow.addFilter(f_0, f_s, d_t, 'r', 'fir_notch', Q)
    mainWindow.addFilter(f_0, f_s, d_t,'b', 'iir_notch', Q)

    app.exec_()

if __name__ == "__main__":
    main()