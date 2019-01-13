# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 14:45:12 2018

@author: zongjun
"""

import skimage.measure
import skimage.filters
import skimage.draw
import numpy as np
import math
import scipy, scipy.interpolate
import numpy.fft
import scipy.signal
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


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
        self.ref_image = None
        
        # convex contour
        self.convex_hull = None
        self.convex_contour = None
        
        # private variables
        self.__curvature = None
        self.__angles_cur = None
        self.__distances_cur = None
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
        
        # initialization
        self.set_ref_image(data)

        
   
    
    def set_ref_image(self, data=None):
        if (data is None):
            print("referenced image is not provided")
            #self.ref_image = None
        elif (isinstance(data, np.ndarray) ):
            # if data is an array
            self.ref_image = data
        elif (isinstance(data, Embryo)):
            # if data is an Embryo object
            self.ref_image = np.copy(data.raw_image)
        else:
            print('unknown reference image data type')
            #pass
            
    
    def detect_boundary(self, threshold =None):
        # clear background images that are connected to the boarder
        #self.ref_image = skimage.segmentation.clear_border(self.ref_image > threshold)
        
        # find the external contour of the ref_image
        if threshold is None:
            threshold = skimage.filters.threshold_otsu(self.ref_image)       
        contours = skimage.measure.find_contours(self.ref_image, level= threshold)
        
        if len(contours) ==1:
            self.boundary_curve = np.round(contours[0]).astype(int)
        elif (len(contours) > 1):
            # if more than one closed contours, find the maximual one
            # the maximal one is determined by the maximum lenght of contour curve
            size = 0
            for curve in contours:
                if (len(curve) > size):
                    self.boundary_curve = np.round(curve).astype(int)
                    size = len(curve)
        else:
            print('No boundaries are detected in the reference image')
            
            
    def detect_convex_hull(self, threshold=None):
        if threshold is None:
            threshold = skimage.filters.threshold_otsu(self.ref_image)
        
        self.convex_hull = skimage.morphology.convex_hull_image(self.ref_image > threshold)
        contours = skimage.measure.find_contours(self.convex_hull, level = threshold)
        self.convex_contour = np.round(contours[0]).astype(int)    
   
    
    def detect_convex_hull_from_boundary(self, threshold=None):
        if threshold is None:
            threshold = skimage.filters.threshold_otsu(self.ref_image)
        self.detect_boundary(threshold)
        
        bw_image = np.zeros(self.ref_image.shape)
        bw_image[self.boundary_curve[:,0], self.boundary_curve[:,1]] = 1
        
        self.convex_hull = skimage.morphology.convex_hull_image(bw_image)
        contours = skimage.measure.find_contours(self.convex_hull, level = threshold)
        self.convex_contour = np.round(contours[0]).astype(int)
        
        
           
    
    def compute_angle(self, point, origin=(0,0)):
        return np.angle( (point[0] - origin[0] ) - 1j * (point[1] - origin[1]) )
    
    def transform_polar_to_cartesian(self, angle, distance, origin=(0,0)):
        x = origin[0] + distance * math.cos(angle)
        y = origin[1] - distance * math.sin(angle)
        return np.array([x,y])
  
    def detect_gravity_central(self):
        threshold = skimage.filters.threshold_otsu(self.ref_image)   
        bw_image = self.ref_image > threshold  
        cgx = np.sum ( np.arange(0, self.ref_image.shape[1]) * np.sum(bw_image, axis = 0) ) / np.sum(bw_image)
        cgy = np.sum ( np.arange(0, self.ref_image.shape[0]) * np.sum(bw_image, axis = 1) ) / np.sum(bw_image)
        self.__cgx, self.__cgy = np.round(cgx), np.round(cgy)
        self.__central_gravity = np.array([self.__cgx, self.__cgy])
    
    
    
    
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
        
        #self.detect_convex_hull()
        self.detect_convex_hull_from_boundary()
        
        x = self.convex_contour[:,1]
        y = self.convex_contour[:,0]
        
        complex_bd_points = (x - self.__cgx) - 1j * (y - self.__cgy)
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
        angles_uniform = scipy.linspace(-math.pi, math.pi, num=3000, endpoint=False) 
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
        self.__angles_cur = angles_uniform
        self.__distances_cur = distances_fit
        
        
        """
        #  two different method for detecting head and tail:
        """
        """
        # method 1: selecting the maximum curvature as head point
        """        
        #self.curvature_head_tail_from_peak(angles_uniform, distances_fit)
        
        """
        # method 2:
        # selecting the stomach first and then determine the head and tail
        # the point of stomach correspond to the least variation of curvature.
        """
        self.curvature_head_tail_from_stomach(angles_uniform, f, zone=20)
        
        
        # method 3:
        # mixture of peak and pick from stomach
        #self.curvature_head_tail_peak_stomach(angles_uniform, distances_fit, f, zone=20)
        
        
    def curvature_head_tail_from_peak(self, angles_uniform, distances_fit):
        # find the peaks in curvature 
        peaks, _ = scipy.signal.find_peaks(self.__curvature, height = np.mean(self.__curvature) )
        peaks_idx = np.argsort(self.__curvature[peaks])
        peaks_idx = np.flip(peaks_idx)
        self.__peaks = peaks[peaks_idx]
        
        
        head_idx = self.__peaks[0]
        tail_idx = self.__peaks[2]       
        
        head_angle = angles_uniform[head_idx]
        head_distance = distances_fit[head_idx]
        tail_angle = angles_uniform[tail_idx]
        tail_distance = distances_fit[tail_idx]
        
        self.head = self.transform_polar_to_cartesian(head_angle, head_distance, self.__central_gravity)
        self.tail = self.transform_polar_to_cartesian(tail_angle, tail_distance, self.__central_gravity)
        
        self.orientation = self.compute_angle(self.head, self.__central_gravity)
        
        
    def local_curvature_variation(self, f, angle):
        """
            detect the local curvature variation for a given angle
        """
        
        if (angle- math.pi/18 >  -math.pi and angle + math.pi/18 < math.pi) :
            test_angles= scipy.linspace(angle- math.pi/18, angle+ math.pi/18, num=30, endpoint=False) 
        elif (angle- math.pi/18 <= -math.pi):
            test_angles_1 = scipy.linspace(-math.pi, angle+ math.pi/18, num=20, endpoint=False) 
            test_angles_2 = scipy.linspace(angle - math.pi/18 + 2 * math.pi, math.pi, num=10, endpoint=False)
            test_angles = np.concatenate([test_angles_1, test_angles_2])
        else:
            test_angles_2 = scipy.linspace(angle- math.pi/18, math.pi, num=20, endpoint=False) 
            test_angles_1 = scipy.linspace(-math.pi, angle + math.pi/18 - 2 * math.pi, num=10, endpoint=False)
            test_angles = np.concatenate([test_angles_1, test_angles_2])
            
        
                
        test_distance = f(test_angles)
        
        # fft and inverse fft
        fft_coeffs = numpy.fft.rfft(test_distance)
        # zero out all but lowest 20 coefficients
        fft_coeffs[self.__fft_approx_order :] = 0
        r = numpy.fft.irfft(fft_coeffs)         
        r_prime = np.gradient(r, test_angles)
        r_prime2 = np.gradient(r_prime, test_angles)
        
        local_curvature = np.divide ( (np.abs(r**2 + 2 * r_prime**2- r * r_prime2) ) **2,
                                        np.power( (r**2 + r_prime**2), 1.5) )
        
        return np.var(local_curvature)

      
    def curvature_head_tail_from_stomach(self, angles_uniform, f, zone = 20):
        """
            find the position where the variation of curvatures is the least significant
        """
        min_variance = math.inf
        idx_stomach = 0
        N = len(self.__curvature)
        if zone < N / 90:
            zone = round(N/90)
            
        for i in range(N):
            if i + zone < N:
                idx = np.arange(i-zone, i+zone+1)
            else:
                idx = np.array( list(range(i-zone, N)) + list(range(0, i+zone-N)))
            data = self.__curvature[idx]
            temp = np.var(data)
            if temp < min_variance:
                idx_stomach = i
                min_variance = temp
        
        stomach_angle = angles_uniform[idx_stomach]
        #print(stomach_angle)
        
        head_angle = stomach_angle+ math.pi/2
        if head_angle > math.pi:
            head_angle -= 2* math.pi
        tail_angle = stomach_angle- math.pi/2
        if tail_angle < -math.pi:
            tail_angle += 2*math.pi
        
        #print(head_angle)
        #print(head_angle, tail_angle)
        head_curvature_variance = self.local_curvature_variation(f,head_angle)
        
        #print(tail_angle)
        tail_curvature_variance = self.local_curvature_variation(f,tail_angle)
        if head_curvature_variance < tail_curvature_variance:
            head_angle, tail_angle = tail_angle, head_angle
        
        head_distance = f(head_angle)
        tail_distance = f(tail_angle)
        
        self.head = self.transform_polar_to_cartesian(head_angle, head_distance, self.__central_gravity)
        self.tail = self.transform_polar_to_cartesian(tail_angle, tail_distance, self.__central_gravity)
        
        self.orientation = self.compute_angle(self.head, self.__central_gravity)
      
    
    
        
        
                
        
            
        
        
        
        
    def extract_position(self, img):
        x = []
        y = []
        
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i,j] :
                    x.append(j)
                    y.append(i)
        
        data = np.column_stack( (x,y))
        return data
    
    def extract_position_fast(self, img):
        indices = np.where(img > [0])
        coordinates = np.array( list( zip(indices[0], indices[1]) ) )
        return coordinates
    
    
    def distinguish_major_minor_axis(self, img, axis_0, axis_1, central):
        theta_0 = self.compute_angle(axis_0)
        theta_1 = self.compute_angle(axis_1)
        
        img_row, img_col = img.shape
        c_row, c_col = np.round(central).astype(int)
        
        if ( theta_0 > -math.pi / 4 and theta_0 < math.pi/4) or \
           (theta_0 > math.pi* 3/4 or theta_0 < - math.pi * 3 / 4):
            temp_row = np.round(math.tan( theta_0) * (img_col - c_col)).astype(int) + c_row
            if temp_row >= img_row:
                temp_row = img_row-1
            if temp_row < 0:
                temp_row =0
            pt_0_a = [temp_row , img_col-1]
            
            temp_row = - np.round(math.tan( theta_0 ) * c_col).astype(int) + c_row
            if temp_row <0:
                temp_row = 0
            if temp_row >= img_row:
                temp_row = img_row -1
                
            pt_0_b = [temp_row , 0]
        else:
            temp_col = np.round( c_row/math.tan(theta_0) ).astype(int) + c_col
            if temp_col >= img_col:
                temp_col = img_col-1
            if temp_col < 0:
                tmep_col = 0
            pt_0_a = [0, temp_col]
            
            temp_col = - np.round( (img_row - c_row) / math.tan(theta_0) ).astype(int) +c_col
            if temp_col >= img_col:
                temp_col = img_col-1
            if temp_col < 0:
                tmep_col = 0
            pt_0_b = [img_row-1, temp_col ]
        
        
        if ( theta_1 > -math.pi / 4 and theta_1 < math.pi/4) or \
           (theta_1 > math.pi* 3/4 or theta_1 < - math.pi * 3 / 4):
            temp_row = np.round(math.tan( theta_1) * (img_col - c_col)).astype(int) + c_row
            if temp_row >= img_row:
                temp_row = img_row-1
            if temp_row < 0:
                temp_row =0
            pt_1_a = [temp_row , img_col-1]
            
            temp_row = - np.round(math.tan( theta_1 ) * c_col).astype(int) + c_row
            if temp_row >= img_row:
                temp_row = img_row-1
            if temp_row < 0:
                temp_row =0
            pt_1_b = [temp_row, 0]
        else:
            temp_col = np.round( c_row/math.tan(theta_1) ).astype(int) + c_col
            if temp_col >= img_col:
                temp_col = img_col-1
            if temp_col < 0:
                tmep_col = 0
            pt_1_a = [0, temp_col]
            
            temp_col = - np.round( (img_row - c_row) / math.tan(theta_1) ).astype(int) +c_col
            if temp_col >= img_col:
                temp_col = img_col-1
            if temp_col < 0:
                tmep_col = 0
            pt_1_b = [img_row-1, temp_col]
        
        #print(pt_0_a, pt_0_b, pt_1_a, pt_1_b)
        
        rr_0,cc_0 = skimage.draw.line(pt_0_a[0], pt_0_a[1], pt_0_b[0], pt_0_b[1])
        rr_1,cc_1 = skimage.draw.line(pt_1_a[0], pt_1_a[1], pt_1_b[0], pt_1_b[1])
        
        
        
        sum_0 = np.sum(img[rr_0,cc_0])
        sum_1 = np.sum(img[rr_1,cc_1])
        
        if sum_1 > sum_0:
            major_axis = axis_1
            minor_axis = axis_0
        else:
            major_axis = axis_0
            minor_axis = axis_1
            
        return [major_axis, minor_axis]
        
        
            
        
    
    def PCA_method(self):
        
        self.detect_boundary()
        
        threshold = skimage.filters.threshold_otsu(self.ref_image)
        bw_image = self.ref_image > threshold
        
        #data = extract_position(self, bw_image)
        data = self.extract_position_fast(bw_image)
  
        # fit a PCA model 
        self.__pca = PCA(n_components=2)
        self.__pca.fit(data)
        
        # pca gravity center
        self.__pca_center = self.__pca.mean_
        
        # pca vectors
        #if self.__pca.explained_variance_[0] > self.__pca.explained_variance_[1]:
        #    self.__pca_major_axis = self.__pca.components_[0]
        #    self.__pca_minor_axis = self.__pca.components_[1]
        #else:
        #    self.__pca_major_axis = self.__pca.components_[1]
        #    self.__pca_minor_axis = self.__pca.components_[0]
        self.__pca_major_axis, self.__pca_minor_axis = self.distinguish_major_minor_axis(bw_image,
                                                                                         self.__pca.components_[0],
                                                                                         self.__pca.components_[1],
                                                                                         self.__pca_center)
        
        #pca angle
        self.__pca_angles = np.array([ self.compute_angle(self.__pca_major_axis), 
                                      self.compute_angle(self.__pca_minor_axis)])
        self.__pca_orientation = self.__pca_angles[0]
        
        # detect head and tail
        #self.__pca_head, self.__pca_tail = self.PCA_head_tail(self.boundary_curve)
        self.detect_convex_hull_from_boundary()
        self.__pca_head, self.__pca_tail = self.PCA_head_tail(self.convex_contour)
    
        return self.__pca_orientation
    
    
    def PCA_head_tail(self, curve):
        # find head position in the curve with PCA parameters
        diff_angle = math.inf 
        head = []
        tail = []
        
        for point in curve:
            angle = self.compute_angle([point[1],point[0]], self.__pca_center)
            if np.abs(angle - self.__pca_orientation) < diff_angle:
                diff_angle = np.abs(angle - self.__pca_orientation)
                head = [point[1], point[0]]
                
        # find tail position in the curve with PCA parameters
        diff_angle = math.inf
        if self.__pca_orientation > 0:
            angle_tail = self.__pca_orientation - math.pi
        else:
            angle_tail = self.__pca_orientation + math.pi
        
        for point in curve:
            angle = self.compute_angle([point[1],point[0]], self.__pca_center)
            if np.abs(angle - angle_tail) < diff_angle:
                diff_angle = np.abs(angle - angle_tail)
                tail = [point[1], point[0]]
        
        return np.array([head, tail]).astype(int)
    
    
    

# method for getting attributes
    def get_center(self, method='curvature'):
        if (method == 'curvature') and (self.__central_gravity is not None):
            return self.__central_gravity
        elif (method =='pca') and (self.__pca_center is not None):
            return self.__pca_center
        else:
            return np.round(np.array( self.ref_image.shape) / 2)
        
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
            print('method is not recognized')
            
    def get_tail(self, method = 'curvature'):
        if (method == 'curvature'):
            return self.tail
        elif (method == 'pca'):
            return self.__pca_tail
        else:
            print('method is not recognized')
            
    def get_curvature_info(self):
        if self.__curvature is not None:
            return [self.__curvature, self.__angles_cur, self.__distances_cur]
        else:
            print('curvature is None')
            
    def get_peaks(self):
        if self.__peaks is not None:
            return self.__peaks
        else:
            print('peak array is None')
        
    def get_approx_curve(self, mode = 'curvature'):
        if mode == 'curvature':
            if self.convex_contour is None:
                self.detect_convex_hull()
            return self.convex_contour
        elif mode == 'pca':        
            if self.boundary_curve is None:
                self.detect_boundary()
            return self.boundary_curve
        else:
            print('method is not recognized')
            return None
     
        
        
        
# methods for visulization
    def view_boundary_curve(self, figsize=(10,10)):
        if self.boundary_curve is not None:
            fig,ax =plt.subplots(figsize = figsize)            
            ax.imshow(self.ref_image,'gray')
            ax.plot(self.boundary_curve[:,1], self.boundary_curve[:,0], color = 'r')
            plt.show()
        else:
            print('data is missing')
            
    def view(self, figsize = (10,10) ):
        if self.ref_image is not None:
            fig,ax =plt.subplots(figsize = figsize)
            ax.imshow(self.ref_image, 'gray')
            plt.show()
        else:
            print('data is missing')
            
    def view_head_tail_curvature(self, figsize = (10,10)):
        fig,ax =plt.subplots(figsize = figsize)
        
        x_fit = self.__central_gravity[0] + self.__distances_cur * np.cos(self.__angles_cur)
        y_fit = self.__central_gravity[1] - self.__distances_cur * np.sin(self.__angles_cur)

        plt.imshow(self.ref_image, 'gray')
        plt.plot(x_fit, y_fit, color='b')
        plt.plot(self.head[0], self.head[1], marker='x', color = 'orange')
        plt.plot(self.tail[0], self.tail[1], marker='x', color = 'orange')
        plt.plot(self.__central_gravity[0], self.__central_gravity[1], marker='x', color = 'orange')
        
        plt.plot((self.__central_gravity[0], self.head[0]),(self.__central_gravity[1], self.head[1]), color='green', linewidth = 2)
        plt.plot((self.__central_gravity[0], self.tail[0]),(self.__central_gravity[1], self.tail[1]), color='green', linewidth = 2)
        plt.plot((self.head[0], self.tail[0]),(self.head[1], self.tail[1]), color='red', linewidth = 2)
        plt.show()
        
    def view_head_tail_pca(self, figsize = (10,10)):
        arrowprops=dict(arrowstyle='->',linewidth=2,shrinkA=0, shrinkB=0)

        fig,ax =plt.subplots(figsize = figsize)
        ax.imshow(self.ref_image, 'gray')        
        for length, vector in zip(self.__pca.explained_variance_, self.__pca.components_):
            v = vector*2 * np.sqrt(length)
            ax.annotate('', self.__pca.mean_ + v, self.__pca.mean_, arrowprops= arrowprops)    
        plt.show()

        
            
    
                
        
        
    
        
                    