# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 18:55:51 2019

@author: iris
"""

#%matplotlib inline
#%reload_ext autoreload
#%autoreload 2

#%%

import matplotlib.pyplot as plt
import math

import Intensity
from Embryo import *
from TestingArea import *
from Polygon import *
from Rotation import *
from Boundary import *
import numpy as np
import skimage

#%%
embryo_list =[]

data_path = 'data'

#gene_names = np.array( ['C1-ubcd full blue','C2-ubcd full blue','C3-ubcd full blue','C4-ubcd full blue'] )
gene_names = np.array( ['C1-ubcd dark','C2-ubcd dark','C3-ubcd dark','C4-ubcd dark'] )
gene_position = 8


for name in gene_names:
    filename ="%s/%s-%i.png"%(data_path, name, gene_position)
    egg = Embryo(filename)
    egg.gene_name = name
    egg.gene_position = gene_position
    embryo_list.append( egg )
   

for egg in embryo_list:
    #egg.view()
    egg.rgb2gray()
    
composition_img = embryo_list[0].raw_image.copy()
for i in range(1,4):
    composition_img += embryo_list[i].raw_image
#plt.imshow(composition_img)
#plt.show()    



#%% see the distribution of data
egg1 = embryo_list[0].copy()
egg1_luminosity = egg1.raw_image.ravel()
plt.hist( egg1_luminosity, bins = 100)

#%% remove outlier by distance (fail)
"""
center = np.round( np.array(egg1.raw_image.shape)/2).astype(int)
threshold = skimage.filters.threshold_otsu(egg1.raw_image)

dist_img = np.zeros(egg1.raw_image.shape)
for (row,col), value in np.ndenumerate(egg1.raw_image):
    if value >= threshold:
        dist_img[row,col] = np.sqrt((row - center[0])**2 + (col -center[1])**2 )

plt.imshow(dist_img)
plt.show()

#plt.plot(dist_img.ravel())
plt.show()

thres_dist = skimage.filters.threshold_otsu(dist_img)
plt.imshow( dist_img >= thres_dist )
plt.show()
"""
#%% remove outlier by closing and opening

egg1 = Embryo(composition_img)
#egg1 = embryo_list[0].copy()
egg1.view()

egg1.denoise()
egg1.view()

egg1.clear_border()
egg1.view()

#egg1.smoothing()

threshold = skimage.filters.threshold_otsu(egg1.raw_image)
plt.imshow(egg1.raw_image > threshold)
plt.show()

# remove outlier
from sklearn.ensemble import IsolationForest

pos_data = []
for (row,col),value in np.ndenumerate(egg1.raw_image):
    if value > 0:
        pos_data.append([row, col])
pos_data = np.array(pos_data)

rng = np.random.RandomState(42)
clf = IsolationForest(max_samples=np.floor(len(pos_data) / 100).astype(int), 
                      bootstrap=False,
                      contamination=0.01,
                      random_state = rng,
                      behaviour='new')

clf.fit(pos_data)
label_predict = clf.predict(pos_data)


outlier_img = egg1.raw_image.copy()

for i in range(len(pos_data)):
    row, col = pos_data[i,:]
    if label_predict[i] == -1:
        outlier_img[row,col] = 1
    else:
        outlier_img[row,col] = 0.3

plt.imshow(outlier_img)
plt.show()

for i in range(len(pos_data)):
    row, col = pos_data[i,:]
    if label_predict[i] == -1:
        egg1.raw_image[row,col] = 0
plt.imshow(egg1.raw_image)
plt.show()


# find convex hull
threshold = skimage.filters.threshold_otsu(egg1.raw_image)
convex_hull = skimage.morphology.convex_hull_image(egg1.raw_image > threshold)
plt.imshow(convex_hull)
plt.show()

#%%
egg2 = embryo_list[0].copy()
egg2.view()

egg2.denoise()
egg2.view()

egg2.clear_border()
egg2.view()

egg2.raw_image = egg2.raw_image * (egg1.raw_image > 0)
egg2.view()

# find convex hull
convex_hull = skimage.morphology.convex_hull_image(egg2.raw_image > 0)
plt.imshow(convex_hull)
plt.show()


bd = Boundary(egg2)
bd.detect_boundary()
bd.view_boundary_curve()

bd.detect_convex_hull()
plt.imshow(bd.convex_hull)
plt.show()

#%%





""""
The following are debug code for demo.py    
#%%  debug

 
embryo_list = load_data() 
convert_to_grayscale(embryo_list)
    
acceptance_threshold = 0.001
max_operations = 10
reference_embryo = embryo_list[:,0]
    
_, _, cum_angles =rotation_process_angles(reference_embryo,
                                          mode='curvature', 
                                          epsilon=acceptance_threshold,
                                          max_operations = max_operations)
    
rotated_embryo_list = rotation_process(embryo_list, cum_angles, mode='curvature')


reference_embryo = rotated_embryo_list[:,0]
active_area_list = active_area_process(reference_embryo, mode='curvature')

#intensity_curves = intensity_process(embryo_list, active_area_list, mode='pca')


#%% Debug PCA

import skimage.filters
import skimage.draw
from sklearn.decomposition import PCA
import math

egg = embryo_list[0,0]
threshold = skimage.filters.threshold_otsu(egg.raw_image)
bw_image = egg.raw_image > threshold
data = extract_position_fast(bw_image)

pca = PCA(n_components=2)
pca.fit(data)

def compute_angle(point, origin=(0,0)):
        return np.angle( (point[0] - origin[0] ) - 1j * (point[1] - origin[1]) )
   

def distinguish_major_minor_axis(img, axis_0, axis_1, central):
    theta_0 = compute_angle(axis_0)
    theta_1 = compute_angle(axis_1)
    print(theta_0, theta_1)
    
    img_row, img_col = img.shape
    c_row, c_col = central
    
    if ( theta_0 > -math.pi / 4 and theta_0 < math.pi/4) or \
       (theta_0 > math.pi* 3/4 or theta_0 < - math.pi * 3 / 4):
        pt_0_a = [ np.round(math.tan( theta_0) * (img_col - c_col)).astype(int) + c_row , img_col-1]
        pt_0_b = [- np.round( math.tan( theta_0 ) * c_col).astype(int) + c_row, 0]
    else:
        pt_0_a = [0, np.round( c_row / math.tan(theta_0) ).astype(int) + c_col]
        pt_0_b = [img_row-1, - np.round( (img_row - c_row) / math.tan(theta_0) ).astype(int) + c_col ]
    
    if ( theta_1 > -math.pi / 4 and theta_1 < math.pi/4) or \
       (theta_1 > math.pi* 3/4 or theta_1 < - math.pi * 3 / 4):
        pt_1_a = [np.round(math.tan( theta_1) * (img_col - c_col)).astype(int) + c_row , img_col-1]
        pt_1_b = [- np.round(math.tan( theta_1 ) * c_col).astype(int) + c_row, 0]
    else:
        pt_1_a = [0, np.round( c_row/math.tan(theta_1) ).astype(int) + c_col]
        pt_1_b = [img_row-1, - np.round( (img_row - c_row) / math.tan(theta_1) ).astype(int) +c_col ]
        
    
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
    
pca_center = np.array(pca.mean_).astype(int)
pca_axis = pca.components_

distinguish_major_minor_axis(bw_image, pca_axis[0], pca_axis[1], pca_center)    
        
        


#%%
embryo_list = load_data() 
convert_to_grayscale(embryo_list)

egg = embryo_list[0,0]
mode = 'pca'

r=Rotation(egg)
r.rotate_embryo(egg, bd_mode = mode, inplace=True)

#active_area = active_area_list[0]
testing_img = Polygon(egg)
bd = Boundary(egg)
bd.detect_head_tail(mode)

testing_img.view()
testing_img.detect_area(boundary = bd)
testing_img.view_area()





#%%
Intensity.detect_intensity(egg, boundary=bd, testing_area = testing_img, horizontal_flag=False, bd_mode='pca')

"""