# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 14:45:12 2018

@author: iris
"""

import skimage.measure
import numpy as np
from Embryo import *

class Boundary(object):
    
    def __init__(self, data = None):
        # if data is a 2d array
        self.head = -1
        self.tail = -1
        
        # if data is an array
        if (type(data) is np.ndarray):
            self.ref_image = data
            self.ref_embryo = Embryo(data)
        elif (type(data) is Embryo):
            # if data is an Embryo object
            self.ref_embryo = data.copy()
            self.ref_image = data.raw_image.copy()
        else:
            self.ref_image = None
            self.ref_embryo = Embryo()
      
    
                