# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 14:45:12 2018

@author: iris
"""

import skimage.measure
import skimage.filter
import numpy as np
import math
import scipy, scipy.interpolate
import numpy.fft
import scipy.signal
from sklearn.decomposition import PCA

from Embryo import *

class Boundary(object):
    
    def __init__(self, data = None):
        
        self.mode = 'curvature'
        self.head = None
        self.tail = None
        self.orientation = 0
        
        # boundary curve is a array of tuples
        self.boundary_curve = None
        
        # set referenced image
        self.set_ref_image(data)
        
        # convex contour
        self.convex_contour = None
        
        # private variables
        self.__curvature = None
        self.__fft_approx_order = 20
        self.__cgx = 0
        self.__cgy = 0
        self.__central_gravity = None
        
        # Principle component analysis
        self.__pca = None
        self.__pca_major_axis = 0
        self.__pca_minor_axis = 0
        self.__pca_center = None
        self.__pca_head = None
        self.__pca_tail = None
        self.__pca_angles = np.array([0, math.pi])
        self.__pca_orientation = 0
        
   
    
    def set_ref_image(self, data):
        if (data is None):
            assert("referenced image is not provided")
            self.ref_image = None
        elif (type(data) is np.ndarray):
            # if data is an array
            self.ref_image = data
        elif (type(data) is Embryo):
            # if data is an Embryo object
            self.ref_image = data.raw_image.copy()
        else:
            assert('unknown reference image data type')
            #pass
            
    
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
        
           
    
    def compute_angle(self, point, origin=(0,0)):
        return np.angle( (point[0] - origin[0] ) + 1j * (point[1] - origin[1]) )
    
    def transform_polar_to_cartesian(self, angle, distance, origin=(0,0)):
        x = origin[0] + distance * math.cos(angle)
        y = origin[1] + distance * math.sin(angle)
        return np.array([x,y])
  
    def detect_gravity_central(self):
        threshold = skimage.filters.threshold_otsu(self.ref_image)   
        bw_image = self.ref_image > threshold
        
        self.detect_convex_hull(threshold)
        
        # the central of gravity is determined from the convex_hull
        cgx = np.sum ( np.arange(0, self.ref_image.shape[1]) * np.sum(bw_image, axis = 0) ) / np.sum(bw_image)
        cgy = np.sum ( np.arange(0, self.ref_image.shape[0]) * np.sum(bw_image, axis = 1) ) / np.sum(bw_image)
        self.__cgx, self.__cgy = np.round(cgx), np.round(cgy)
        self.central_gravity = np.array([self.__cgx, self.__cgy])
    
    def detect_convex_hull(self, threshold=None):
        if threshold is None:
            threshold = skimage.filters.threshold_otsu(self.ref_image)
            
        self.convex_hull = skimage.morphology.convex_hull(self.ref_image > threshold)
        contours = skimage.measure.find_contours(self.convex_hull, level = threshold)
        self.convex_contour = contours[0]    
   
    
    
    def detect_head_tail(self, mode= 'curvature'):
        self.mode = mode
        if mode == 'curvature':
            self.curvature_method()
        if mode == 'pca':
            self.PCA_method()
        
        
    
    def curvature_method(self):
    # compute the curvature for the convex contour of referenced image
    # we transform boundary_curve into polar coordinates and use FFT to fit the curve
        self.detect_gravity_central()
        self.detect_convex_hull()
        
        x = self.convex_contour[:,1]
        y = self.convex_contour[:,0]
        
        complex_bd_points = (x - self.__cgx) + 1j * (y - self.__cgy)
        angles = np.angle(complex_bd_points)
        distances = np.absolute(complex_bd_points)
        sortidx = np.argsort( angles )
        angles = angles[ sortidx ]
        distances = distances[ sortidx ]
        
        # copy first and last elements with angles wrapped around. needed so can interpolate over full range -pi to pi
        angles = np.hstack(([ angles[-1] - 2*math.pi ], angles, [ angles[0] + 2*math.pi ]))
        distances = np.hstack(([distances[-1]], distances, [distances[0]]))
        
        # interpolate to evenly spaced angles
        f = scipy.interpolate.interp1d(angles, distances, 'linear')
        angles_uniform = scipy.linspace(-math.pi, math.pi, num=1000, endpoint=False) 
        distances_uniform = f(angles_uniform)


        # fft and inverse fft
        fft_coeffs = numpy.fft.rfft(distances_uniform)
        # zero out all but lowest 20 coefficients
        fft_coeffs[self.__fft_approx_order :] = 0
        distances_fit = numpy.fft.irfft(fft_coeffs)
        
        r = distances_fit
        r_prime = np.gradient(r, angles_uniform)
        r_prime2 = np.gradient(r_prime, angles_uniform)
        
        self.__curvature = np.divide ( (np.abs(r**2 + 2 * r_prime**2- r * r_prime2) ) **2,
                                        np.power( (r**2 + r_prime**2), 1.5) )
        
        

        # find the peaks in curvature 
        peaks, _ = scipy.signal.find_peaks(self.__curvature, height = np.mean(self.__curvature) )
        peaks_idx = np.argsort(self.__curvature[peaks])
        peaks_idx = np.flip(peaks_idx)
        self.__peaks = peaks[peaks_idx]
        
        head_idx = peaks[0]
        tail_idx = peaks[2]
        
        head_angle = angles_uniform[head_idx]
        head_distance = distances_fit[head_idx]
        tail_angle = angles_uniform[tail_idx]
        tail_distance = distances_fit[tail_idx]
        
        self.head = self.transform_polar_to_cartesian(head_angle, head_distance, self.__central_gravity)
        self.tail = self.transform_polar_to_cartesian(tail_angle, tail_distance, self.__central_gravity)
        
        self.orientation = self.compute_angle(self.head, self.__central_gravity)
     
        
        
        
    
    def PCA_method(self):
        
        self.detect_boundary()
        
        threshold = skimage.filter.threshold_otsu(self.ref_image)
        bw_image = self.ref_image > threshold
        
        x = []
        y = []
        
        for i in range(bw_image.shape[0]):
            for j in range(bw_image.shape[1]):
                if bw_image[i,j] :
                    x.append(j)
                    y.append(i)
        
        data = np.column_stack( (x,y))
  
        # fit a PCA model 
        self.__pca = PCA(n_components=2)
        self.__pca.fit(data)
        
        # pca gravity center
        self.__pca_center = self.__pca.mean_
        
        # pca vectors
        if self.__pca.explained_variance_[0] > self.__pca.explained_variance_[1]:
            self.__pca_major_axis = self.__pca.components_[0]
            self.__pca_minor_axis = self.__pca.components_[1]
        else:
            self.__pca_major_axis = self.__pca.components_[1]
            self.__pca_minor_axis = self.__pca.components_[0]
        
        #pca angle
        self.__pca_angles = np.array([ self.compute_angle(self.__pca_major_axis), 
                                      self.compute_angle(self.__pca_minor_axis)])
        self.__pca_orientation = self.__pca_angles[0]
        
        self.__pca_head, self.__pca_tail = self.PCA_head_tail(self.boundary_curve)
    
        return self.__pca_orientation
    
    
    def PCA_head_tail(self, curve):
        # find head position in the curve with PCA parameters
        diff_angle = math.inf 
        result1 = []
        
        for point in curve:
            angle = self.compute_angle(point, self.__pca_center)
            if np.abs(angle - self.__pca_orientation) < diff_angle:
                diff_angle = np.abs(angle - self.__pca_orientation)
                result1 = point
                
        # find tail position in the curve with PCA parameters
        diff_angle = math.inf
        if self.__pca_orientation > 0:
            angle_tail = self.__pca_orientation - math.pi
        else:
            angle_tail = self.__pca_orientation + math.pi
        
        result2 = []
        for point in curve:
            angle = self.compute_angle(point, self.__pca_center)
            if np.abs(angle - angle_tail) < diff_angle:
                diff_angle = np.abs(angle - angle_tail)
                result2 = point
        
        return [result1, result2]
    
    
                
    def get_center(self, method='curvature'):
        if (method == 'curvature') and (self.__central_gravity is not None):
            return self.__central_gravity
        elif (method =='pca') and (self.__pca_center is not None):
            return self.__pca_center
        else:
            return np.round(self.ref_image.shape / 2)
        
    def get_orientation(self, method ='curvature'):
        if (method == 'curvature'):
            return self.orientation
        elif (method == 'pca'):
            return self.__pca_orientation
        else:
            return 0
        
   
     def get_head(self, method = 'curvature'):
        if (method == 'curvature'):
            return self.head
        elif (method == 'pca'):
            return self.__pca_head
        else:
            assert('method is not recognized')
            
     def get_tail(self, method = 'curvature'):
        if (method == 'curvature'):
            return self.tail
        elif (method == 'pca'):
            return self.__pca_tail
        else:
            assert('method is not recognized')
            
    
                
        
        
    
        
                    