# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 22:05:51 2018

@author: iris
"""
from TestingArea import *

class Polygone(TestingArea):
    
    def __init__(self):
        super()
        self.area_type="POLYGONE"
        
        self.vertice = None
        self.head_dropoff_threshold = 0.2
        self.tail_dropoff_threshold = 0.2
     
    def set_mask(self):
        super().set_mask()
    
    def set_vertice(self, vertice):
        self.vertice = vertice
    
    def vertex2area(self):
        pass
    
    def detect_area(self):
        pass
   
    
        