import numpy as np
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
        
        
        
    
    def set_ref_image(self, data = None):
        if data is None:
            #assert('reference image has not yet been provided')
            #self.ref_image = None
            pass
        elif ( isinstance(data, np.ndarray)  and (len(data.shape) == 2) ):
            # data is an image
            self.ref_image = data
        elif (isinstance(data, Embryo) ):
            # data is an Embryo object
            self.ref_image = data.raw_image.copy()
        else:        
            assert('data must have type of numpy.ndarry or Embryo')
              
        
    def set_boundary(self, boundary = None):
        if (boundary is None):
            if self.boundary is None:
                self.boundary = Boundary(self.ref_image)
                self.boundary.detect_boundary()
                self.boundary.detect_head_tail()
            else:
                # do nothing
                assert('no argument provided, and the attribute "boundary" is not None')
                pass 
        else:
            self.boundary = boundary
    
    def set_angle(self, angle):
        self.angle = angle

    def set_angle_from_boundary(self, boundary):
        self.angle = boundary.get_orientation(boundary.mode)
    
   
    def get_rotated_image(self):
        return self.__rotated_image
    
    
    def rotate_embryo(self, embryo= None, angle= None, boundary= None, center_mode='simple'):
    #return an Embryo object with an image after rotation
        if embryo is not None:
            self.set_ref_image(embryo)
        else:
            if self.ref_image is None:
                raise ValueError("no reference image provided")
        
        # if self.boundary is None, then initialize self.boundary
        self.set_boundary(boundary)
            
        if angle is not None:
            self.set_angle(angle)
        else:
            self.set_angle_from_boundary(boundary)
        
        if center_mode == 'simple':
            center = np.round(self.ref_image.shape / 2)       
        elif center_mode =='boundary':
            center = self.boundary.get_center(self.boundary.mode)
        
        self.__rotated_image = skimage.transform.rotate(self.ref_image, 
                                                      self.angle,
                                                      resize = False,
                                                      center = center)
        if embryo is not None:
            embryo.raw_image = self.__rotated_image.copy
        else:
            embryo = Embryo(self.__rotated_image)
            
        return embryo
