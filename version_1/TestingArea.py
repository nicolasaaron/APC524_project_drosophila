# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 20:19:14 2018

@author: iris
"""

import sys

if 'ABC' not in sys.modules:
    from abc import ABC
    
from Mask import *
import numpy as np
    
    
class TestingArea(ABC):
    
    def __init__(self, data = None):
        self.area_type =''        
        self.area = None
        
        # initialize reference image
        self.ref_image = None
        
        # initialize reference image dimension
        self.ref_image_dim = None
        
        # boundary
        self.boundary = None
        
        # mask
        self.area_mask = None
        
    
    def set_ref_image(self, data = None):
        pass
    
    def set_boundary(self, boundary = None):
        pass
    
    def detect_area(self):
        pass
     
# optional method
    def load_ref_image(self, data = None, filename=''):
        if (data is not None):
            self.ref_image.read_from_array(data)
        if (filename != ''):
            self.ref_image.read_from_filename(filename)            
   
    
    def set_mask(self, mask_type, pattern =[]):
        self.area_mask.set_mask_type(mask_type)
        self.area_mask.set_mask_type(pattern)
    
      
    
      

        