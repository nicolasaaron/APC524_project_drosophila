import numpy as np
from Embryo import * 
from Boundary import *

class Rotate(object):

    def __init__(self, raw_image):
        self.angle = 0
        
        self.raw_image =  Embryo()
        self.raw_image.read_from_array(raw_image)
        
        self.rotated_image = Embryo()
        self.boundary = Boundary()
    
    
    def set_boundary(self):
        pass
    
    def detect_angle(self, boundary):
        self.angle = 0

    def rotate_embryo(self, boundary):
        self.rotated_image = None

    def get_rotated(self):
        return self.rotated_image



#        r = Rotate(Embryo())
#        abc = r.rotated_image
#        abc = r.get_rotated
