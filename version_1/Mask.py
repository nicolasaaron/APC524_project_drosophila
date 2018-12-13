# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 21:33:58 2018

@author: iris
"""

class Mask(object):
    
    def __init__(self):
        self.mask_type = "BY_COLUMN"
        self.pattern = []
    
    def set_mask_type(self, the_type="BY_COLUMN"):
        self.mask_type = the_type

        
    def set_mask_pattern(self, the_pattern=[]):
        self.pattern = the_pattern
        
        if (not the_pattern and self.mask_type=="BY_COLUMN"):
            self.build_new_pattern()
        
        
    def build_new_pattern(self):
        pass