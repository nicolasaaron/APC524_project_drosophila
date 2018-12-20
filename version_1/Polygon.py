# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 22:05:51 2018

@author: iris
"""
from TestingArea import *
from Embryo import *
from Boundary import *
#from Mask import *

import numpy as np
import math
import matplotlib.pyplot as plt

import skimage.morphology
import skimage.measure


class Polygon(TestingArea):
    
    def __init__(self, data = None, boundary = None, num_vertices=4, vertices = None):
        super().__init__()
        
        self.area_type="POLYGON"
        self.head_dropoff_threshold = 0.1
        self.tail_dropoff_threshold = 0.1
     
        
        #init reference image
        self.set_ref_image(data)
        
        # set boundary
        self.set_boundary(boundary)        
        
        #(optional)
        # set default number of vertices of a polygone, the default shap is a rectangle
        self.num_vertices = num_vertices          
        # vertices of a polygone : nx2 array
        self.vertices = None
        
        # private variable
        self.__regions = None
        self.__main_region = None
        self.__embryo_bbox = None
        
        #area detection with boundary
        self.__tail_poly_vertice_upper = None
        self.__tail_poly_vertice_lower = None
        self.__head_poly_vertice_upper = None
        self.__head_poly_vertice_lower = None

        
#method for initialization    
    def set_ref_image(self, data):
        if data is None:
            print('reference image information has not yet been provided')
            self.ref_image = None
            self.ref_image_dim = None
        elif ( isinstance(data, np.ndarray) and (len(data.shape) == 1) ):
            # data indicate the dimension of referenced image
            self.ref_image_dim = np.copy(data)
            self.ref_image = np.zeros(self.ref_image_dim, dtype=np.double)
        elif ( isinstance(data, np.ndarray) and (len(data.shape) == 2) ):
            # data is an image
            self.ref_image = np.copy(data)
            self.set_ref_image_dim()
        elif isinstance(data, Embryo):
            # data is an Embryo object
            self.ref_image = np.copy( data.raw_image)
            self.set_ref_image_dim()
        else:        
            print('data must have type numpy.ndarry or Embryo')
            #pass
        
        
    def set_ref_image_dim(self):
        if (self.ref_image is not None):
            self.ref_image_dim = np.array( self.ref_image.shape )
        else:
            print('reference image size is not known')
            
            
    def init_area(self):
    # initialize "area" as a 2d array with the same size of "ref_image"
    # "area" is set to a black image 
        if (self.ref_image_dim is not None):
            self.area = np.zeros(self.ref_image_dim, dtype = bool)
        else:
            print('reference image is not known')
        
        
    def set_boundary(self, boundary = None):
        if boundary is not None:
            self.boundary = boundary
        else:
            self.boundary = None
           
    def detect_area(self, boundary = None):
        if boundary is None:
            if (self.boundary is None):
                """ need to check whether raw_image is avaliable """
                assert self.ref_image is not None, "reference image is empty"
                self.detect_area_from_image()
            else:
                self.detect_area_with_boundary(self.boundary)
        else:
            """ Todo: need to check whether boundary is valid """
            self.detect_area_with_boundary(boundary)
            
    def vertex2poly(self):
    # find the area (polygone) in the referece image
        if self.area is None:
            self.init_area()
            
        for (x,y) in self.vertices:
            self.area[x,y] = 1
        self.area = skimage.morphology.convex_hull_image(self.area)
    
                   
        
# optional methods
    def set_mask(self):
        super().set_mask()
    
    def set_vertices(self, vertices):
        # set "vertices" from a list of positions of type (int, int)
        if (vertices is not None):
            if ( len(vertices.shape) == 1):
                #input is a list of tuple (x,y)
                self.vertices = np.array( tuple(map(tuple, vertices)) )
                self.num_vertices = vertices.shape[0]
            elif ( len(vertices.shape) == 2 and vertices.shape[1] == 2):
                self.vertices = vertices
                self.num_vertices = vertices.shape[0]
            else:
                print('vertices type is not known')
        else:
            print('vertices has not been provided')
        #    pass  
    
    def check_vertices(self):
        """ Todo: check validity of vertices"""
        pass
        
        
    def load_ref_image(self, data = None, filename=''):
        if (data is not None):
            self.ref_image.read_from_array(data)
        elif (filename != ''):
            self.ref_image.read_from_filename(filename)            
        else:
            print('error for loading images dircetly')
    
        
# methodes for computation    
    
    # auxilary function to detect_area: in the case without providing boundary
    def detect_area_from_image(self):
        # if boundary = None, find the largest rectangle (in area) within the convex hull of referenced image
        # return a list of vertices of a rectangle
        
        # use find_contour to detect external contour boundary
        # the threshold is set by the otsu method
        threshold = skimage.filters.threshold_otsu(self.ref_image)
        
        # remove background noise in reference image using threshold
        denoised_image = self.ref_image >= threshold
        
        # find the convex hull image of the denoised image
        convex_hull = skimage.morphology.convex_hull_image(denoised_image)
        
        # find the regions using built-in label and regionprops functions
        label_img = skimage.measure.label(convex_hull)
        self.__regions = skimage.measure.regionprops(label_img)
        
        #find out the largest region
        if len(self.__regions) ==1 :
            self.__main_region = self.__regions[0]
        elif len(self.__regions) > 1:
            temp_area = 0
            for rg in self.__regions:
                if rg.area > temp_area:
                    temp_area = rg.area
                    self.__main_region = rg
        else:
            print('no region detected in the image')
            #pass
    
        #crop __main_region with head and tail dropoff threshold
        """ suppose that the ref_image is horizontal after rotation
            suppose tail on the left, head on the right 
            Todo: justify assumptions
        """
    
        # step1: find the bounding box of __cell_region
        # bbox vertices order: WN - WS - ES - EN (counterclockwise)
        minr, minc, maxr, maxc = self.__main_region.bbox
        # step2: find the intersection points with boundary using dropoff threshold
        self.__embryo_bbox = np.array([(minc, minr), (minc, maxr),(maxc, maxr),(maxc, minr)])
        
        tail_dropoff_pos_col = np.round( minc + self.tail_dropoff_threshold * (maxc - minc) ).astype(int)
        head_dropoff_pos_col = np.round( maxc - self.head_dropoff_threshold * (maxc - minc) ).astype(int)
        
        # using denoised_image
        head_minr = 0
        while denoised_image[head_minr,head_dropoff_pos_col] == 0:
            head_minr +=1
        head_maxr = self.ref_image_dim[0]-1
        while denoised_image[head_maxr, head_dropoff_pos_col] == 0:
            head_maxr -=1
        
        tail_minr = 0
        while denoised_image[tail_minr, tail_dropoff_pos_col] == 0:
            tail_minr +=1
        tail_maxr = self.ref_image_dim[0]-1
        while denoised_image[tail_maxr, tail_dropoff_pos_col] == 0:
            tail_maxr -=1
        
        
        self.vertices = np.array([(tail_minr, tail_dropoff_pos_col), \
                                  (tail_maxr, tail_dropoff_pos_col), \
                                  (head_maxr, head_dropoff_pos_col), \
                                  (head_minr, head_dropoff_pos_col)] )        
        #draw the polygone
        self.vertex2poly()
        
        
    
    def coordinate_shift(self, start, length, angle):
        new_row = start[0] + length * math.cos(angle)
        new_col = start[1] - length * math.sin(angle)        
        return np.array([new_row, new_col])
    
    def compute_angle(self, point, origin=(0,0)):
        return np.angle( (point[0] - origin[0] ) - 1j * (point[1] - origin[1]) )
        
    
    def detect_area_with_boundary(self, boundary):      
        # create a polynome approximation with the boundary curve
        """
            the major axis that link head and tail may not be level
            assume that the tail is on the left hand side of the head
            Todo: justify assumptions
        """
        #update boundary
        self.set_boundary(boundary)
        
        # step 1: find the line connected head and tail
        head = boundary.get_head(boundary.mode)
        tail = boundary.get_tail(boundary.mode)
        
        major_axis_angle = self.compute_angle(head, tail) 
        major_axis_length = math.sqrt( (head[1]- tail[1])**2 +(head[0]- tail[0])**2)
        # step 2: find cropping positions
        tail_dropoff_pos = self.coordinate_shift(tail, \
                                                 major_axis_length * self.tail_dropoff_threshold, \
                                                 major_axis_angle) 
        
        head_dropoff_pos = self.coordinate_shift(head, \
                                                 - major_axis_length * self.head_dropoff_threshold,\
                                                 major_axis_angle)
        
        # find the intersection points with boundary_curve
        # minor_axis_angle is range from (-pi/2 , pi/2)
        if major_axis_angle < 0:
            minor_axis_angle = major_axis_angle + math.pi / 2
        else:
            minor_axis_angle = major_axis_angle - math.pi / 2
        
        if minor_axis_angle > 0:
            minor_axis_angle_prime = minor_axis_angle - math.pi
        else:
            minor_axis_angle_prime = minor_axis_angle + math.pi
        
           
        # find the two vetices of polygone which are close to tail    
        min_diff_angle_0 = math.inf
        min_diff_angle_pi = math.inf
        
        curve = boundary.get_approx_curve(boundary.mode)
        
        for (r,c) in curve:
            # compute the angle for the line connecting (bd_x, bd_y) and tail_dropoff_pos
            bd_angle = self.compute_angle( (c,r), tail_dropoff_pos )
            
            diff_angle = np.abs( bd_angle - minor_axis_angle)  
            if (diff_angle < min_diff_angle_0):
                min_diff_angle_0 = diff_angle
                pos_1 = (r,c)
                
            diff_angle = np.abs(bd_angle - minor_axis_angle_prime )  
            if (diff_angle < min_diff_angle_pi):
                min_diff_angle_pi = diff_angle
                pos_2 = (r,c)
                
        if pos_1[0] < pos_2[0]:
            self.__tail_poly_vertice_upper = pos_1
            self.__tail_poly_vertice_lower = pos_2
        else:
            self.__tail_poly_vertice_upper = pos_2
            self.__tail_poly_vertice_lower = pos_1
        
        # find the two vertices of polygone which are close to head
        min_diff_angle_0 = math.inf
        min_diff_angle_pi = math.inf
        for (r,c) in curve:
            # compute the angle for the line connecting (bd_x, bd_y) and head_dropoff_pos
            bd_angle = self.compute_angle( (c,r), head_dropoff_pos )
            # diff_angle is range from (0, pi)
            diff_angle = np.abs( bd_angle - minor_axis_angle)  
            if (diff_angle < min_diff_angle_0):
                min_diff_angle_0 = diff_angle
                pos_1 = (r,c)
            diff_angle = np.abs(bd_angle - minor_axis_angle_prime )  
            if (diff_angle < min_diff_angle_pi):
                min_diff_angle_pi = diff_angle
                pos_2 = (r,c)
        
        if pos_1[0] < pos_2[0]:
            self.__head_poly_vertice_upper = pos_1
            self.__head_poly_vertice_lower = pos_2
        else:
            self.__head_poly_vertice_upper = pos_2
            self.__head_poly_vertice_lower = pos_1
      
        # construct the vertices of polygone
        self.vertices = np.array([self.__tail_poly_vertice_upper, \
                                  self.__tail_poly_vertice_lower, \
                                  self.__head_poly_vertice_lower, \
                                  self.__head_poly_vertice_upper])
    
        self.vertices = np.round(self.vertices).astype(int)
        
        # creat area form vertices
        self.vertex2poly()
        
        
     
        
        
# methods for visualization
    def view(self, figsize = (10,10) ):
        if self.ref_image is not None:
            fig,ax =plt.subplots(figsize = figsize)
            ax.imshow(self.ref_image, 'gray')
            plt.show()
        else:
            print('data is missing')
    
    def view_area(self, figsize = (10,10) ):
        if self.area is not None:
            fig,ax =plt.subplots(figsize = figsize)
            ax.imshow(self.ref_image, 'gray')
            ax.imshow(self.area * self.ref_image, cmap = 'jet', alpha = 0.1)
            for vertex in self.vertices:
                ax.plot(vertex[1], vertex[0], marker='x', markersize =15, color='orange')
            
            plt.show()
        else:
            print('data is missing')
            
            
            
                        
            
            
        
        
    
        