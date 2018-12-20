import numpy as np
import skimage.transform
from Embryo import * 
from Boundary import *

class Rotation(object):

    def __init__(self, data=None, boundary=None):
        # initialize angle
        self.angle = 0
        
        # ref_image is a 2d array
        self.ref_image = None
        #self.set_ref_image(data)
        
        # boundary is of Boundary type
        self.boundary = None
        
        
        #private variables
        # rotated image is of 2d array
        self.__rotated_image = None
        
        
        
    
    def set_ref_image(self, data = None):
        if data is None:
            assert('reference image has not yet been provided')
            #self.ref_image = None
        elif ( (type(data) is np.ndarray) and (len(data.shape) == 2) ):
            # data is an image
            self.ref_image = data
        elif (type(data) is Embryo):
            # data is an Embryo object
            self.ref_image = data.raw_image.copy
        else:        
            assert('data must have type of numpy.ndarry or Embryo')
            pass
        
    def set_boundary(self, boundary = None):
        if (boundary is None):
            self.boundary = Boundary(self.ref_image)
            self.boundary.detect_boundary()
            self.boundary.detect_head_tail()
            self.boundary.PCA_orientation()
        else:
            self.boundary = boundary
    
    def set_angle(self, boundary):
        self.angle = boundary.orientation

    def get_rotated_image(self):
        return self.__rotated_image
    
    
    def rotate_embryo(self, embryo= None, boundary= None, mode='curvature'):
    #return an Embryo object with an image after rotation
        if embryo is not None:
            self.set_ref_image(embryo)
            
        if boundary is not None:
            self.set_boundary(boundary)
            self.set_angle(boundary)
            
        self.__rotated_image = skimage.transform.rotate(self.ref_image, 
                                                      self.angle,
                                                      resize = False,
                                                      center = self.boundary.get_center(mode))
        return Embryo(self.rotated_image)

