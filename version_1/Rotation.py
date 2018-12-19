import numpy as np
import skimage.transform
from Embryo import * 
from Boundary import *

class Rotate(object):

    def __init__(self, data=None, boundary=None):
        # initialize angle
        self.angle = 0
        
        # ref_image is a 2d array
        self.ref_image = None
        self.set_ref_image(data)
        
        # rotated image is of 2d array
        self.rotated_image = None
        
        # boundary is of Boundary type
        self.boundary = None
        
    
    def set_ref_image(self, data):
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
        
    def set_boundary(self, boundary):
        if (boundary is None):
            self.boundary = Boundary(self.ref_image)
            self.boundary.detect_boundary()
            self.boundary.detect_head_tail()
            self.boundary.PCA_orientation()
        else:
            self.boundary = boundary
    
    def set_angle(self, boundary):
        self.angle = boundary.orientation

    def rotate_embryo(self, boundary= None, mode='curvature'):
        if self.boundary is not None:
            self.set_boundary(boundary)
            self.set_angle(boundary)
            
        self.rotated_image = skimage.transform.rotate(self.ref_image, 
                                                      self.angle,
                                                      resize = False,
                                                      center = self.boundary.get_center(mode))
        return Embryo(self.rotated_image)

    def get_rotated_image(self):
        return self.rotated_image

