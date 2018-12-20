"""
author:zongjun
"""


import numpy as np
import math
import skimage.transform
from Embryo import * 
from Boundary import *

class Rotation(object):

    def __init__(self, data=None):
        # initialize angle
        self.angle = None
        
        # ref_image is a 2d array
        self.ref_image = None
        #self.set_ref_image(data)
        
        # boundary is of Boundary type
        self.boundary = None        
        
        #private variables
        # rotated image is of 2d array
        self.__rotated_image = None
        
        self.set_ref_image(data)
        
        
        
    
    def set_ref_image(self, data):
        if ( isinstance(data, np.ndarray) and (len(data.shape) == 2) ):
            # data is an image
            self.ref_image = np.copy( data )
        elif (isinstance(data, Embryo) ):
            # data is an Embryo object
            self.ref_image = np.copy( data.raw_image)
        elif (data is None):
            print('referenc image is not provided')
        else:        
            print('data must have type of numpy.ndarry or Embryo')
              
    def get_rotated_image(self):
        return self.__rotated_image
    
       
    
    def set_boundary(self, boundary):
        self.boundary = boundary
    
    def set_angle(self, angle):
        self.angle = angle

    def set_angle_from_boundary(self, boundary):
        self.angle = - boundary.get_orientation(boundary.mode)
    
    def generate_boundary_for_rotation(self, boundary = None, mode ='curvature'):
        if (boundary is None):
            self.boundary = Boundary(self.ref_image)
            self.boundary.detect_head_tail(mode)           
        else:
            self.boundary = boundary
            
   
   
    def rotate_embryo(self, embryo= None, angle= None, boundary= None, 
                      inplace = False, resize= True, center_mode='simple', bd_mode ='curvature'):
    #return an Embryo object with an image after rotation
        if embryo is not None:
            self.set_ref_image(embryo)
        else:
            if self.ref_image is None:
                raise ValueError("no reference image provided")
        
        if angle is not None:
            self.set_angle(angle)
        else:
            self.generate_boundary_for_rotation(boundary,bd_mode)        
            self.set_angle_from_boundary(self.boundary)
            
        
        if center_mode == 'simple':
            center = np.round(np.array(self.ref_image.shape) / 2).astype(int)       
        elif center_mode =='boundary':
            center = self.boundary.get_center(self.boundary.mode)
        
        self.__rotated_image = skimage.transform.rotate(self.ref_image.copy(), 
                                                        self.angle / math.pi * 180,
                                                        resize = resize,
                                                        center = center,
                                                        preserve_range = True)
        
        if (inplace) and (embryo is not None):
            embryo.raw_image = np.copy(self.__rotated_image)
            return embryo
        else:
            return Embryo(self.__rotated_image)

