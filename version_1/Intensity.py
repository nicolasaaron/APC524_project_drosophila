# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 10:18:13 2018

@author: iris
"""

import scipy.signal
import numpy as np
import pandas as pd
from Embryo import *
from TestingArea import *
from Polygone import *
import skimage.measure
import matplotlib.pyplot as plt



def detect_intensity(embryo, boundary = None, testing_area = None, horizontal_flag = True,
                     boundary_flag = False, bd_mode= ''):
    
    """ need to check the 'raw_image' size and the 'area' image size are the same """
    """ need some initialation in the case when testing_area = None and boundary= None """
    
    # initialize boundary
    if boundary is None:        
        boundary = Boundary(embryo.raw_image)
        boundary.detect_boundary()
        if bd_mode != '':
            boundary.mode = bd_mode
        boundary.detect_head_tail(bd_mode)        
    else:
        boundary_flag = True
        # if we specify the boundary mode as "curvature" or "pca"
        if (bd_mode != '') and (bd_mode != boundary.mode):            
            boundary.mode = bd_mode
            boundary.detect_head_tail(bd_mode)
            
     
    # initialize end_pt as head
    end_pt = boundary.get_head(boundary.mode)
    # initialize start_pt
    if horizontal_flag: 
        # predict the starting point for profile line based on center and end_pt
        if boundary.mode == 'curvature':
            start_pt = None
            for point in boundary.convex_contour:
                if (np.round(point[1]) == np.round(end_pt[1]) ) and (np.round(point[0]) < np.round(end_pt[0])):
                    start_pt = point
            #diff_angle = math.inf
            #start_pt = None
            #for point in boundary.convex_contour:
            #    # compute angle for the line from point to end_pt
            #    angle = boundary.compute_angle(point, end_pt)
            #    if np.abs(angle) < diff_angle:
            #        diff_angle = np.abs(angle)
            #       start_pt = point
        elif boundary.mode == 'pca':
            start_pt = boundary.get_tail('pca')
    else:
        start_pt = boundary.get_tail(boundary.mode)

    
    #initialize testing area     
    if testing_area is None:
        testing_area= Polygon(embryo.raw_image)
        if boundary_flag:        
            testing_area.detect_area(boundary)
        else:
            testing_area.detect_area()
  
    
    # find testing area in 'raw_image'
    testing_zone = embryo.raw_image *  testing_area.area
    
    # compute intensity along the line connecting start and end points in testing_zone
    value = skimage.measure.profile_line(testing_zone, start_pt, end_pt)

    if horizontal_flag:
        # in case the embryo is level
        x = np.arange(start_pt[0], end_pt[0])
        intensity_curve = np.column_stack((x,value))
    else:
        rr,cc = skimage.draw.line(start_pt[0], start_pt[1], end_pt[0], end_pt[1])
        intensity_curve = np.column_stack((rr,cc,value))
        
    return intensity_curve



def collect_curves_from_files(gene_name ='', positions = []):
    curves = []
    for p in positions:
        intensity_curve =pd.read_csv('%s-%s.csv'%(gene_name,p), sep=',',header=0,encoding="utf8")
        curves.append([intensity_curve.values[:,0], intensity_curve.values[:,1]] )
        
    return np.array(curves)
        


def normalization(curves, y_flag = True, filter_size = 101):
# assume that the size of intensity curve is a N x 2 array
# assume that we use savgol_filter by default
    normalized_curves = np.array([])
    
    for intensity_curve in curves:    
        x = intensity_curve[:,0] # suppose x is increasing
        y = intensity_curve[:,1]
        
        x_norm = (x / x[-1]) * 100 # normalize to Egg Length     
        y_filtered=scipy.signal.savgol_filter(y, filter_size, 3) # filter out signal noise by Savitzky–Golay filter
        
        if y_flag:
            y_norm = (y_filtered-min(y_filtered))/(max(y_filtered)-min(y_filtered)) #normalize by min max values
        
        normalized_curves.append( np.column_stack((x_norm, y_norm)), axis = 0 )
    
    return normalized_curves 




def view(curves, gene_name='', figsize = (10,10)):
    fig,ax = plt.subplots(figsize=figsize)
    ax.set_xlabel("Egg lenght ")
    ax.set_ylabel("Intensity")
    ax.set_title("%s Intensity of uBcd posteriorly illuminated" %gene_name)
    
    for curve in curves:
        ax.plot(curve[:,0], curve[:,1])
    
    plt.show()
    """ possible to save the image afterward """

    
    
    
        
    
    
   
    
    
    
    
   