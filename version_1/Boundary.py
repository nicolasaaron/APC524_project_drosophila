# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 14:45:12 2018

@author: iris
"""

import skimage.measure
import skimage.filter
import numpy as np
from Embryo import *

class Boundary(object):
    
    def __init__(self, data = None):
        
        self.head = None
        self.tail = None
        
        # boundary curve is a array of tuples
        self.boundary_curve = None
        
        # set referenced image
        self.ref_image = None
        self.set_ref_image(data)
        
        # private variables
        self.__polyfit_degree = 4
        self.__polyfit_width = 20
        self.__curvature = None
        
   
    
    def set_ref_image(self, data):
        if (data is None):
            assert("referenced image is not provided")
            #self.ref_image = None
        elif (type(data) is np.ndarray):
            # if data is an array
            self.ref_image = data
        elif (type(data) is Embryo):
            # if data is an Embryo object
            self.ref_image = data.raw_image.copy()
        else:
            assert('unknown reference image data type')
            pass
            
    
    def detect_boundary(self):
        # clear background images that are connected to the boarder
        #self.ref_image = skimage.segmentation.clear_border(self.ref_image > threshold)
        
        # find the external contour of the ref_image
        threshold = skimage.filters.threshold_otsu(self.ref_image)       
        contours = skimage.measure.find_contours(self.ref_image, level= threshold)
        
        if len(contours) ==1:
            self.boundary_curve = contours[0]
        elif (len(contours) > 1):
            # if more than one closed contours, find the maximual one
            # the maximal one is determined by the maximum lenght of contour curve
            size = 0
            for curve in contours:
                if (len(curve) > size):
                    self.boundary_curve = np.round(curve)
                    size = len(curve)
        else:
            assert('No boundaries are detected in the reference image')
        
    def detect_convex_hull(self):
        threshold = skimage.filters.threshold_otsu(self.ref_image)  
        convex_hull = skimage.morphology.convex_hull(self.ref_image > threshold)
        contours = skimage.measure.find_contours(convex_hull, level = 0)
        self.convex_contour = contours[0]
        
    
    # a polynomail is represented as an np array with coefficient from high to low    
    def poly_dev(poly, dev_n):
        if dev_n ==0:
            return poly[:]
        elif dev_n > len(poly):
            return np.array([])
        elif dev_n < 0:
            raise ValueError("negative derivative")
        else:
            degree= len(poly) -1
            result = np.zeros(degree+1 - dev_n)
            result[:] = poly[:-dev_n]
            for i in range(len(result)):
                for exponent in range(degree - i, degree - dev_n - i, -1):
                    result[i] *= exponent
            return result
        
    def poly_eval(polynomial, x):
         return sum(coef * x**exp for exp, coef in enumerate(reversed(polynomial)))
            
    
    def compute_curvature(self):
    # compute the curvature for a given boundary curve
    # we use a polynonmial to fit the local boundary curve
        bd_x = self.boundary_curve[:,0]
        bd_y = self.boundary_curve[:,1]
        half_width = np.floor( self.__polyfit_width / 2)
        self.__curvature = np.zeros(len(self.boundary_curve))
        
        bd_length= len(self.boundary_curve)
        

    def detect_head(self):
        pass
    
    def detect_tail(self):
        pass
        