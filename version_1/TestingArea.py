# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 20:19:14 2018

@author: iris
"""

import sys

if 'ABC' not in sys.modules:
    from abc import ABC
    
from Mask import *
    
    
class TestingArea(ABC):
    
    def __init__(self):
        self.area_type =''        
        self.area = None
        self.area_mask = Mask()
    
    def detect_area(self):
        pass
    
    def set_mask(self, mask_type, pattern =[]):
        self.area_mask.set_mask_type(mask_type)
        self.area_mask.set_mask_type(pattern)
       

        