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
  
    # get length of coefficients array
    n = b.shape[0]
        
    # Create array full of zeros, length = 
    v = n + (factor * (n - 1))

    a_comb = np.zeros(v)
    b_comb = np.zeros(v)
        
    # Insert at every factor+1 position a coefficient value, the rest are zeros
    a_comb[::factor+1] = a
    b_comb[::factor+1] = b

    # Is a even an array?
    if not isinstance(a, int):
        a = a_comb

    b = b_comb
    
    return b,a