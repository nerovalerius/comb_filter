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

import numpy as np

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