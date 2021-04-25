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
# Date          : 17.04.2021
# Literature    : none

import sys
import pip
import random
import numpy as np

import matplotlib
from matplotlib.figure import Figure
from matplotlib import patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
matplotlib.use('Qt5Agg')

from combfilter import *
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
    a = 0
    b = 0

    def __init__(self, y, x, color, f_s, b=None, a=None, length=None):
        self.x = x
        self.y = y
        self.color = color
        self.f_s = f_s
        self.length = length
        self.a = a
        self.b = b



# Class that plots our functions
class MplCanvas(FigureCanvasQTAgg):


    # Layout - 3 Rows, 2 Colums

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # Plot and its title
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.suptitle('Filters - Original Filter | Converted to comb filter')

        # Format spaces between plots
        fig.subplots_adjust(left=0.125,
                  bottom=0.1, 
                  right=0.9, 
                  top=0.9, 
                  wspace=0.2, 
                  hspace=1)

        # The Plots and their formatting
        # PLOT 1
        self.ax1 = fig.add_subplot(421, title='IIR Filter - Frequency Response')
        self.ax1.set_xlabel('Frequency [Hz]')
        self.ax1.set_ylabel('Amplitude [dB]')
        #self.ax1.set_ylim(-2.0,2.0)
        
        # PLOT 2
        self.ax2 = fig.add_subplot(423, title='IIR Comb Filter - Frequency Response')
        self.ax2.set_xlabel('Frequency [Hz]')
        self.ax2.set_ylabel('Amplitude [dB]')
        #self.ax2.set_ylim(-2.0,2.0)
        
        # PLOT 3
        self.ax3 = fig.add_subplot(425, title='IIR Comb Filter - Phase Response')
        self.ax3.set_xlabel('Frequency [Hz]')
        self.ax3.set_ylabel('Phase [°]')
        #self.ax3.set_ylim(-200.0,200.0)
        
        # PLOT 4
        self.ax4 = fig.add_subplot(427, title='IIR Comb Filter - PZ Map')
        self.ax4.set_xlabel('Imaginary')
        self.ax4.set_ylabel('Real')
        #self.ax4.set_ylim(-2.0,2.0)
        
        # PLOT 5
        self.ax5 = fig.add_subplot(422, title='FIR Filter - Frequency Response')
        self.ax5.set_xlabel('Frequency [Hz]')
        self.ax5.set_ylabel('Amplitude [dB]')
        #self.ax5.set_ylim(-2.0,2.0)
        
        # PLOT 6
        self.ax6 = fig.add_subplot(424, title='FIR Comb Filter - Frequency Response')
        self.ax6.set_xlabel('Frequency [Hz]')
        self.ax6.set_ylabel('Amplitude [dB]')
        #self.ax6.set_ylim(-2.0,2.0)
        
        # PLOT 7
        self.ax7 = fig.add_subplot(426, title='FIR Comb Filter - Phase Response')
        self.ax7.set_xlabel('Frequency [Hz]')
        self.ax7.set_ylabel('Phase [°]')
        #self.ax7.set_ylim(-200.0,200.0)
        
        # PLOT 8
        self.ax8 = fig.add_subplot(428, title='FIR Comb Filter - PZ Map')
        self.ax8.set_xlabel('Imaginary')
        self.ax8.set_ylabel('Real')
        #self.ax8.set_ylim(-2.0,2.0)
        

        super(MplCanvas, self).__init__(fig)


# The Main window of our program
class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
  
    def initUI(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Set Window Size and Title
        self.setGeometry(200, 200, 1600, 1000)
        self.setWindowTitle('Up- and FIR Combing Demonstration - Armin Niedermüller')

        # Define a grid layout
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        # Define the Plot with its subplots
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Create checkboxes
        self.iir_comb_checkbox = QCheckBox("IIR to IIR-comb")
        self.fir_comb_checkbox = QCheckBox("FIR to FIR-comb")
        self.iir_comb_checkbox.setChecked(False)
        self.fir_comb_checkbox.setChecked(False)
        self.iir_comb_checkbox.stateChanged.connect(self.iirCheckBoxAction)
        self.fir_comb_checkbox.stateChanged.connect(self.firCheckBoxAction)


        # Create a slider
        self.iir_comb_slider = QSlider(Qt.Horizontal)
        self.iir_comb_slider.setRange(0,10)
        self.iir_comb_slider.setSingleStep(1)
        self.iir_comb_slider.setValue(1)
        self.iir_comb_slider.setTickInterval(1)
        self.iir_comb_slider.setTickPosition(QSlider.TicksBothSides)

        # Create a slider
        self.fir_comb_slider = QSlider(Qt.Horizontal)
        self.fir_comb_slider.setRange(0,10)
        self.fir_comb_slider.setSingleStep(1)
        self.fir_comb_slider.setValue(1)
        self.fir_comb_slider.setTickInterval(1)
        self.fir_comb_slider.setTickPosition(QSlider.TicksBothSides)

        # Create Labels
        self.fir_comb_label = QtWidgets.QLabel()
        self.fir_comb_label.setText('Status: INACTIVE')
        self.iir_comb_label = QtWidgets.QLabel()
        self.iir_comb_label.setText('Status: INACTIVE')

        # Connect the sliders to our plots - if the slider value changes, the plot is updated
        self.iir_comb_slider.valueChanged[int].connect(self.IIRplotsUpdate)
        self.fir_comb_slider.valueChanged[int].connect(self.FIRplotsUpdate)

        # Layout - 3 Rows, 2 Colums

        #   | Original Time Domain      | Original FFT Linear Spectrum    |
        #   | Upsampled Time Domain     | Upsampled FFT Linear Spectrum   |  
        #   | Downsampled Time Domain   | Downsampled FFT Linear Spectrum |
        #   
        #   | IIR Combing Checkbox       | IIR Combing Slider               |
        #   | IIR Combing Status         | IIR Combing Slider               |
        #   | FIR Combing Checkbox     | FIR Combing Slider             |
        #   | FIR Combing Status       | FIR Combing Slider             |


        # Create a Grid Layout and put the single widgets into it
        #   | Original Time Domain    | Original FFT Linear Spectrum      |   
        #   | Upsampled Time Domain   | Upsampled FFT Linear Spectrum     | 
        #   | Downsampled Time Domain | Downsampled FFT Linear Spectrum   | 
        grid_layout.addWidget(self.canvas, 1,1,12,10) # span over 12 rows and 10 columns
        
        #   | IIR Combing Checkbox       | IIR Combing Slider               |
        #   | IIR Combing Status         | IIR Combing Slider               |
        grid_layout.addWidget(self.iir_comb_checkbox, 13,1,1,1)
        grid_layout.addWidget(self.iir_comb_label, 14,1,1,1)
        grid_layout.addWidget(self.iir_comb_slider, 13,2,2,9)     
        
        #   | FIR Combing Checkbox     | FIR Combing Slider             |
        #   | FIR Combing Status       | FIR Combing Slider             |
        grid_layout.addWidget(self.fir_comb_label, 15,1,1,1)
        grid_layout.addWidget(self.fir_comb_checkbox, 16,1,1,1)
        grid_layout.addWidget(self.fir_comb_slider, 15,2,2,9)

       
        # A dictionary where our functions are stored
        self.plot_refs = dict()
        self.signals = dict()

        # Initial Values for checkboxes
        self.activateIIRCombFilter = False
        self.activateFIRCombFilter = False

        self.show()


    # IIR Combing Checkbox Function
    def iirCheckBoxAction(self, state):
        if (Qt.Checked == state):
            # activate upsampling
            self.activateIIRCombFilter = True
            self.iir_comb_label.setText('Status: ACTIVE')
        else: 
            # deactivate upsampling
            self.activateIIRCombFilter = False
            self.iir_comb_label.setText('Status: INACTIVE')
            self.IIRplotsUpdate(1)


    # FIR Combing Checkbox Function
    def firCheckBoxAction(self, state):
        if (Qt.Checked == state):
            # activate downsampling
            self.activateFIRCombFilter = True
            self.fir_comb_label.setText('Status: ACTIVE')
        else: 
            # deactivate downsampling
            self.activateFIRCombFilter = False
            self.fir_comb_label.setText('Status: INACTIVE')
            self.FIRplotsUpdate(1)


    # Add a filter to our plots
    def addFilter(self, f_0, f_1, f_s, d_t, color, type=None, Q=1):
        
        if type == 'fir':
            numtaps = 37
    
            # filter coeffs
            a = 1
            b = signal.firwin(numtaps, [f_0, f_1], fs=f_s, window=('kaiser', 8))
        elif type == 'iir':
            # filter coeffs
            b,a = signal.iirnotch(f_0, Q, f_s)

        else: 
            return 0
    
        # Calculate frequency and amplitude
        freq, h = signal.freqz(b, a, fs=f_s)
        
        # Create filter object
        combedFilter = MySignal(freq, 20 * np.log10(abs(h)), color, f_s, b, a)

        # Get poles and zeros
        z, p, k = signal.tf2zpk(b, a)
       
        # SIGNAL - Add plot reference to our List of plot refs
        if type == 'fir':
            self.plot_refs["fir_filter_freq"] = self.canvas.ax5.plot(combedFilter.y,
                                                combedFilter.x,
                                                combedFilter.color)
            self.plot_refs["fir_comb_filter_freq"] = self.canvas.ax6.plot(combedFilter.y,
                                                combedFilter.x,
                                                combedFilter.color)
            self.plot_refs["fir_comb_filter_phase"] = self.canvas.ax7.plot(freq,
                                                np.unwrap(np.angle(h)) * 180,
                                                combedFilter.color)
            self.plot_refs["fir_comb_filter_pz"] = self.canvas.ax8.plot(np.real(z),
                                                np.imag(z),
                                                combedFilter.color)
        elif type == 'iir':
            self.plot_refs["iir_filter_freq"] = self.canvas.ax1.plot(combedFilter.y,
                                                combedFilter.x,
                                                combedFilter.color) 
            self.plot_refs["iir_comb_filter_freq"] = self.canvas.ax2.plot(combedFilter.y,
                                                combedFilter.x,
                                                combedFilter.color) 
            self.plot_refs["iir_comb_filter_phase"] = self.canvas.ax3.plot(freq,
                                                np.unwrap(np.angle(h)) * 180,
                                                combedFilter.color)
            self.plot_refs["iir_comb_filter_pz"] = self.canvas.ax4.plot(np.real(z),
                                                np.imag(z),
                                                combedFilter.color)
       
        # And add the functions to our extra list
        self.signals[type+"_filter"] = combedFilter
        self.signals[type+"_comb_filter_freq"] = combedFilter
        self.signals[type+"_comb_filter_phase"] = combedFilter
        self.signals[type+"_comb_filter_pz"] = combedFilter
    
        ## update Plots
        if type == 'fir':
            self.FIRplotsUpdate(1)
        elif type == 'iir':
            self.IIRplotsUpdate(1)


    # Function to be called after using the slider
    def IIRplotsUpdate(self, value):

        # Does the original filter even exist?
        if self.signals['iir_filter'] is None:
            return False 
        
        # Get some data from our filter
        f_s = self.signals['iir_comb_filter_freq'].f_s
        a = self.signals['iir_comb_filter_freq'].a
        b = self.signals['iir_comb_filter_freq'].b
        
        # Convert Filter to Comb Filter
        b_comb, a_comb = combfilter(b,a, value)
        
        # Calculate frequency and amplitude
        freq, h = signal.freqz(b_comb, a_comb, fs=f_s)
        
        # Only create comb filter if checkbox is True
        if self.activateIIRCombFilter is True:
            combedFilter = MySignal(freq, 20 * np.log10(abs(h)), 'g', f_s, b_comb, a_comb)
        else: # else display the original uncombed filter
            combedFilter = self.signals["iir_filter"]
            combedFilter.color = 'r'
        
        # Get poles and zeros
        z, p, k = signal.tf2zpk(b_comb, a_comb)
        
        ############# Update IIR Comb Filter Plot - Frequency Response##########
        self.plot_refs['iir_comb_filter_freq'][0].set_ydata(combedFilter.x)
        self.plot_refs['iir_comb_filter_freq'][0].set_xdata(combedFilter.y)
        self.plot_refs['iir_comb_filter_freq'][0].set_color(combedFilter.color)

        ############# Update IIR Comb Filter Plot - Phase Response ##########
        self.plot_refs['iir_comb_filter_phase'][0].set_ydata(np.unwrap(np.angle(h)) * 180)
        self.plot_refs['iir_comb_filter_phase'][0].set_xdata(freq)
        self.plot_refs['iir_comb_filter_phase'][0].set_color(combedFilter.color)

        ############# Update IIR Comb Filter Plot- PZ Map ##########
        self.canvas.ax4.cla()
        self.canvas.ax4.add_patch(patches.Circle((0, 0), radius=1, fill=False, color='black', ls='dashed'))
        self.canvas.ax4.plot(np.real(z), np.imag(z), 'oy', label='Zeros')
        self.canvas.ax4.plot(np.real(p), np.imag(p), 'xb', label='Poles')
        self.canvas.ax4.legend(loc=2)
        self.canvas.ax4.set(title='IIR Comb Filter - PZ Map', xlabel='Real', ylabel='Imaginary')

        self.canvas.draw()



    # Function to be called after using the slider
    def FIRplotsUpdate(self, value):
     
        # Does the original filter even exist?
        if self.signals['fir_filter'] is None:
            return False 
        
        # Get some data from our filter
        f_s = self.signals['fir_comb_filter_freq'].f_s
        a = self.signals['fir_comb_filter_freq'].a
        b = self.signals['fir_comb_filter_freq'].b
        
        # Convert Filter to Comb Filter
        b_comb, a_comb = combfilter(b,a, value)
        
        # Calculate frequency and amplitude
        freq, h = signal.freqz(b_comb, a_comb, fs=f_s)
        
        # Only create comb filter if checkbox is True
        if self.activateFIRCombFilter is True:
            combedFilter = MySignal(freq, 20 * np.log10(abs(h)), 'g', f_s, b_comb, a_comb)
        else: # else display the original uncombed filter
            combedFilter = self.signals["fir_filter"]
            combedFilter.color = 'r'

         # Get poles and zeros
        z, p, k = signal.tf2zpk(b_comb, a_comb)
        
        ############# Update FIR Comb Filter Plot - Frequency Response##########
        self.plot_refs['fir_comb_filter_freq'][0].set_ydata(combedFilter.x)
        self.plot_refs['fir_comb_filter_freq'][0].set_xdata(combedFilter.y)
        self.plot_refs['fir_comb_filter_freq'][0].set_color(combedFilter.color)

        ############# Update FIR Comb Filter Plot - Phase Response ##########
        self.plot_refs['fir_comb_filter_phase'][0].set_ydata(np.unwrap(np.angle(h)) * 180)
        self.plot_refs['fir_comb_filter_phase'][0].set_xdata(freq)
        self.plot_refs['fir_comb_filter_phase'][0].set_color(combedFilter.color)

        ############# Update FIR Comb Filter Plot- PZ Map ##########
        self.canvas.ax8.cla()
        self.canvas.ax8.add_patch(patches.Circle((0, 0), radius=1, fill=False, color='black', ls='dashed'))
        self.canvas.ax8.plot(np.real(z), np.imag(z), 'oy', label='Zeros')
        self.canvas.ax8.plot(np.real(p), np.imag(p), 'xb', label='Poles')
        self.canvas.ax8.legend(loc=2)
        self.canvas.ax8.set(title='FIR Comb Filter - PZ Map', xlabel='Real', ylabel='Imaginary')


        
        self.canvas.draw()

# ---------------------------------------------------------------------------------------------    
# MAIN
# ---------------------------------------------------------------------------------------------    
def main():
    # create square wave signal
    length = 1           # seconds
    f_s = 10000          # Hz - Sampling Frequency
    f_notch = 2500       # Notch Frequency
    f_0 = 1000           # Frequency 1
    f_1 = 4000           # Frequency 2
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
    mainWindow.addFilter(f_0, f_1, f_s, d_t, 'r', 'fir', Q)
    mainWindow.addFilter(f_notch, f_1,f_s, d_t,'r', 'iir', Q)

    app.exec_()

if __name__ == "__main__":
    main()