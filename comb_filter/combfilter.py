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


# calculate a Fourier Series for a Square Signal
def combfilter(b, a, factor):
    """
    Parameters
    ----------
    b,a:          array[double], filter coefficients of an single section filter
    factor:       int, repetition factor of the comb filter

    Returns
    ---------
    b,a:          array[double], filter coefficients transformed to a comb filter
    """

    # # Generate evenly spaced timestamps
    # #x = np.linspace(0, len_signal, fs_signal, endpoint=False) 
    # time = np.arange(0, len_signal, 1/fs_signal)   # Create vector from 0 to 1 - stepsize = 1/fs
    # 
    # # This will be our resulting signal
    # f = np.zeros([len_signal])
    # 
    # # Go over all samples for our signal and calculate its value via fourier series
    # for x in range(0, len_signal):
    # 
    #   # The inner sum - see RHS of formula
    #   sum = 0
    #   for k in range(1, k_max_signal+1, 2):
    #     sum += k**(-1) * np.sin(2 * np.pi * k * time[x] * frequency)
    #         
    #   # The scalar in front of the sum - see RHS of formula
    #   f[x] =  sum * 4 * h_signal * np.pi**(-1)
    
    return b,a


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
