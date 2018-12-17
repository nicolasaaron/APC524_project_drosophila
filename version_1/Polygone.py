# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 22:05:51 2018

@author: iris
"""
from TestingArea import *
from Embryo import *
#from Mask import *
import numpy as np
#from PIL import Image, ImageDraw
import skimage.morphology
import skimage.measure


class Polygon(TestingArea):
    
    def __init__(self, data = None, num_vertices=4, vertices = None):
        super()
        
        self.area_type="POLYGON" 
        
        #init reference image
        self.set_ref_image(data)        
      
        # set default number of vertices of a polygone, 
        # the default shap is a rectangle
        self.num_vertices = num_vertices  
        
        # vertices of a polygone : nx2 array
        self.vertices = None
        #init vertices list
        self.set_vertices(vertices)
        
        
        self.head_dropoff_threshold = 0.1
        self.tail_dropoff_threshold = 0.1
     
        # private variable
        #self.__area_pil = None
        self.__boundary = None
        self.__contour = None
        self.__regions = None

        
#method for initialization
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
                assert('vertices type is not known')
                pass
        else:
            assert('vertice type is not known')
            pass  
    
    
    def check_vertices(self):
        """ check validity of vertices"""
        pass;
    
    def set_ref_image(self, data):
        if (type(data) is np.ndarray and len(data.shape) == 2):
            self.ref_image = data
        elif (type(data) is Embryo):
            self.ref_image = data.raw_image.copy
        else:
            assert('data must have type numpy.ndarry or Embryo')
            pass
        
        
    def set_ref_image_dim(self):
        if (self.ref_image is not None):
            self.ref_image_dim = self.ref_image.shape
        else:
            assert('reference image is not known')
            pass
            
    def init_area(self):
    # initialize "area" as a 2d array with the same size of "ref_image"
    # "area" is set to a black image 
        if (self.ref_image is not None):
            if (self.ref_image_dim is None):
                self.set_ref_image_dim(self)            
            self.area = np.zeros(self.ref_image_dim, dtype = bool)
        else:
            assert('reference image is not known')
            pass
        
# methodes for computation
    def vertex2poly(self):
    # find the area (polygone) in the referece image
    # the vertices are sorted counter clock-wise, using PIL library
    
        #self.__area_pil = Image(mode='L', self.ref_image_dim, color = 0)
        #ImageDraw.Draw(self.__area_pil).polygon(self.vertices, outline = 1, fill = 1)
        #self.area = np.array(self.__area_pil)
    
    # use skimage.morphology package
        for (x,y) in self.vertices:
            self.area[x,y] = 1
        self.area = skimage.morphology.convex_hull_image(self.area)
    
    
    def detect_area(self, boundary = None):
    # if boundary = None, find the largest polygon (in area) within the convex hull of referenced image
    # return a list of vertices of polygon whose number of vertices equals to n = num_vertices 

    # use find_contour to detect external contour boundary
    # the threshold is set by the otsu method
        threshold = skimage.filters.threshold_otsu(self.ref_image)
        
    # remove background noise in reference image using threshold
        denoised_image = self.ref_image >= threshold
        
    # find the convex hull image of the denoised image
        convex_hull = skimage.morphology.convex_hull(denoised_image)
        
    # find the regions using built-in label and regionprops functions
        label_img = skimage.measure.label(convex_hull)
        self.__regions = skimage.measure.regionprops(label_img)
        
    #find out the largest area
        if len(self.__regions) ==1 :
            self.__main_region = self.__regions
        elif len(self.__regions) > 1:
            temp_area = 0
            for rg in self.__regions:
                if rg.area > temp_area:
                    temp_area = rg.area
                    self.__main_region = rg
        else:
            assert('no region detected in the image')
            pass
    
    #crop __cell_region with head and tail dropoff threshold
    
    # step1: find the bounding box of __cell_region
    # bbox vertices order: WN - WS - ES - EN (counterclockwise)
        minr, minc, maxr, maxc = self.__main_region.bbox
    # step2: find the intersection points with boundary using dropoff threashold
        self.__embryo_bbox = np.array([(minc, minr), (minc, maxr),(maxc, maxr),(maxc, minr)])
        self.__head_dropoff_pos = minc + self.head_dropoff_threashold * (maxc - minc)
        self.__tail_dropoff_pos = maxc - self.head_dropoff_threashold * (maxc - minc)
        
        # using denoised_image
        min_head_r = min(denoised_image[:,self.__head_dropoff_pos] > 0)
        max_head_r = max(denoised_image[:,self.__head_dropoff_pos] > 0)
        min_tail_r = min(denoised_image[:,self.__tail_dropoff_pos] > 0)
        max_tail_r = max(denoised_image[:,self.__tail_dropoff_pos] > 0)
        
        self.vertices = np.array([(min_head_r, self.__head_dropoff_pos),
                                  (max_head_r, self.__head_dropoff_pos),
                                  (max_tail_r, self.__tail_dropoff_pos),
                                  (min_tail_r, self.__tail_dropoff_pos)],
                                    dtype = 'int, int')
        self.vertices.dtype.names=['x','y']
        
        
        
    
        