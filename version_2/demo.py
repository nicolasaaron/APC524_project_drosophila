# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 03:04:07 2019

@author: iris
"""
#%matplotlib inline
#%reload_ext autoreload
#%autoreload 2

import matplotlib.pyplot as plt
#import math

import Intensity
from Embryo import *
from TestingArea import *
from Polygon import *
from Rotation import *
from Boundary import *

import numpy as np
from sklearn.ensemble import IsolationForest



#%%
#@profile
def load_data():
    embryo_list =[]
    
    data_path = 'data'
    
    #gene_names = np.array( ['C1-ubcd full blue','C2-ubcd full blue','C3-ubcd full blue','C4-ubcd full blue'] )
    gene_names = np.array( ['C1-ubcd dark','C2-ubcd dark','C3-ubcd dark','C4-ubcd dark'] )
    gene_positions = [2]
    
    for position in gene_positions:
        temp_list = []
        for name in gene_names:       
            filename ="%s/%s-%i.png"%(data_path, name, position)
            egg = Embryo(filename)
            
            egg.gene_name = name
            egg.gene_position = position
            
            temp_list.append( egg )
        
        embryo_list.append(temp_list)
        
    return np.array(embryo_list)


def convert_to_grayscale(embryo_list):
    for embryos in embryo_list:
        for egg in embryos:
            egg.rgb2gray()
            
        




#%%

def superpose_images(embryo_list):
    img_shape = embryo_list[0].raw_image.shape
    img = np.zeros(img_shape)
    for i in range(0,len(embryo_list)):
        img += embryo_list[i].raw_image
    
    return img

#@profile
def extract_position(egg):
    pos_data = []
    n_row, n_col = egg.raw_image.shape
    for row in range(0,n_row):
        for col in range(0,n_col):
            if egg.raw_image[(row,col)] > 0:
                pos_data.append([row, col])
    pos_data = np.array(pos_data)
    
    return pos_data


def extract_position_fast(img):
    indices = np.where(img > 0)
    coordinates = np.array( list(zip(indices[0], indices[1])) )
    return coordinates



#@profile
def remove_outliers(img, perc_outlier = 0.01):
    
    egg = Embryo(img)        
    egg.denoise()    
    egg.clear_border()
    
    #pos_data = extract_position(egg)
    pos_data = extract_position_fast(egg.raw_image)
    
    rng = np.random.RandomState(42)
    clf = IsolationForest(behaviour="new",
                          max_samples=np.floor(len(pos_data) / 100).astype(int), 
                          bootstrap=False,
                          contamination=perc_outlier,
                          random_state = rng)
    
    clf.fit(pos_data)
    label_predict = clf.predict(pos_data)    
    
    for i in range(len(pos_data)):
        row, col = pos_data[i,:]
        if label_predict[i] == -1:
            egg.raw_image[(row,col)] = 0
    
        
    return egg


def pre_processing_single_embryo(embryo_list, mode='0'): 
    
    if mode=='superposed':
        filtered_img = superpose_images(embryo_list)   
    else:
        filtered_img = embryo_list[0].raw_image
    filtered_embryo = remove_outliers(filtered_img)
    
    
    filtered_img = filtered_embryo.raw_image
    active_position = filtered_img > 0
    
    for egg in embryo_list:
        egg.raw_image *= active_position
        
        
def pre_processing(embryo_list, mode='0'):
    for embryos in embryo_list:
        pre_processing_single_embryo(embryos, mode=mode)


#%%
def rotation_process_angles(embryo_list, mode='pca', epsilon = 0.005, max_operations= 5):
    r_list = []
    rotated_list = []
    cum_angles = []
       
    for egg in embryo_list:        
        r = Rotation(egg)
        count_operation = 0
        angle = 0
        
        while (count_operation < max_operations and abs(r.view_inclination(bd_mode = mode)) > epsilon):
            count_operation +=1
            #print(r.view_inclination(bd_mode=mode))
            rotated_egg = r.rotate_embryo(bd_mode = mode, inplace=True)
            angle += r.angle
        
        #print(r.view_inclination(bd_mode=mode))
        r_list.append(r)
        rotated_list.append(rotated_egg)
        cum_angles.append(angle)
    
    return [r_list, rotated_list, cum_angles]
    


def rotation_process(embryo_list, angle_list, mode='pca'):    
    n_samples = embryo_list.shape[0]
    r = Rotation(np.array([[0,0],[0,0]]) )
    rotated_embryo_list = []
    
    
    for i in range(n_samples):
        embryos = embryo_list[i,:]
        angle = angle_list[i]        
        temp_list = []
        for egg in embryos:
            temp_list.append( r.rotate_embryo(egg, angle=angle, bd_mode=mode) )
            
        rotated_embryo_list.append(temp_list)
        
    return np.array(rotated_embryo_list)
#%%
def active_area_process(embryo_list, mode='pca'):
    active_area_list=[]
    
    for egg in embryo_list:
        poly = Polygon(egg)
        bd = Boundary(egg)
        bd.detect_head_tail(mode)
        poly.detect_area(boundary=bd)
        #poly.view_area()
        
        active_area_list.append(poly)
        
    return np.array(active_area_list)

#%%

def intensity_process(embryo_list, active_area_list, mode='pca'):
    
    n_samples = embryo_list.shape[0]
    if n_samples != len(active_area_list):
        print("Error: length mismatch")
        return
    
    intensity_curves =[]
    
    for i in range(n_samples):
        embryos = embryo_list[i,:]
        active_area = active_area_list[i]
        
        print(i)
        curves = []
        for egg in embryos:
            print(egg.gene_name, egg.gene_position)
            bd = Boundary(egg)
            bd.detect_head_tail(mode)
            
            curves.append( Intensity.detect_intensity(egg, 
                                                       boundary=bd,
                                                       testing_area = active_area,
                                                       horizontal_flag = True,
                                                       bd_mode='pca')
                                    )
        
        intensity_curves.append(curves)
    
    return np.array(intensity_curves)
        
#%%
def view_embryos(embryo_list):
    for embryos in embryo_list:
        for egg in embryos:
            egg.view()

def view_embryos_backup(embryo_list):
    for embryos in embryo_list:
        for egg in embryos:
            egg.view_backup()       

def view_rotation_angles(r_list):
    for r in r_list:
        print(r.angle)

def view_inclination(r_list, mode='pca'):
    for r in r_list:
        print(r.view_inclination(bd_mode = mode))

def view_intensity_curves(intensity_curves, col_idx=0):
    Intensity.view(intensity_curves[col_idx, :])
        

#%%
      

if __name__ == '__main__':
    embryo_list = load_data()  
    convert_to_grayscale(embryo_list)
    pre_processing(embryo_list)
    #view_embryos(embryo_list)
    
    
    acceptance_threshold = 0.001
    max_operations = 2
    reference_embryo = embryo_list[:,0]
    
    _, _, cum_angles =rotation_process_angles(reference_embryo,
                                              mode='pca', 
                                              epsilon=acceptance_threshold,
                                              max_operations = max_operations)
                
    rotated_embryo_list = rotation_process(embryo_list, cum_angles, mode='pca')
    
    #view_embryos(rotated_list)
    
    reference_embryo = rotated_embryo_list[:,0]
    active_area_list = active_area_process(reference_embryo, mode='pca')
    
    intensity_curves = intensity_process(embryo_list, active_area_list, mode='pca')


    #view_intensity_curves(intensity_curves, col_idx=0)

    
    
    
   
    
    
    
    
    