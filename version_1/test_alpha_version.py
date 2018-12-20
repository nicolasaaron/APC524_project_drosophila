# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 16:18:09 2018

@author: iris
"""

%matplotlib inline
import matplotlib.pyplot as plt
import math

import Intensity
from Embryo import *
from TestingArea import *
from Polygon import *
from Rotation import *
from Boundary import *


#%% read in an embryo from a files

embryo_list =[]

gene_names = np.array( ['C1-WT','C2-WT','C3-WT','C4-WT'] )
gene_position = 9

for name in gene_names:
    filename ="%s-%i.png"%(name, gene_position)
    egg = Embryo(filename)
    egg.gene_name = name
    egg.gene_position = gene_position
    embryo_list.append( egg )

for egg in embryo_list:
    egg.view()
    egg.rgb2gray()

egg1 = embryo_list[0]
print(egg1.gene_name)
print(egg1.gene_position)

plt.imshow(egg1.gray_image)
plt.show()

plt.imshow(egg1.bk_image)
plt.show()

#%%
"""
 Test Embryo class
"""


# test read from array
egg = Embryo(egg1.raw_image)

plt.imshow(egg.raw_image)
plt.show()

"""
Todo:  test existence of a filename: 
    
egg = Embryo('aaa')

"""


#%%
"""
 Test boundary class:
"""

# initialization from an Embryo object
bd = Boundary(egg1)
bd.view()

# initialization from an array
egg2 = embryo_list[1]
bd.set_ref_image(egg2)
bd.view()

#detect boundary
bd = Boundary(egg1.raw_image)
bd.detect_boundary()
bd.view_boundary_curve()

#%%
#debug: detect head and tail
mode ='curvature'
bd.detect_head_tail(mode)

print('head:', bd.get_head(mode))
print('tail:', bd.get_tail(mode))
print('center:', bd.get_center(mode))
print('orientation', bd.get_orientation(mode))

bd.view_head_tail_curvature()
 
curvature, angles, distances = bd.get_curvature_info()
peaks = bd.get_peaks()

plt.polar(angles, curvature)
plt.show()

plt.polar(angles, distances)
plt.show()

plt.plot(angles, curvature)
plt.plot(angles[peaks], curvature[peaks], 'x', color='r')
plt.show()

head_idx = peaks[0]
tail_idx = peaks[2]       

head_angle = angles[head_idx]
head_distance = distances[head_idx]
tail_angle = angles[tail_idx]
tail_distance = distances[tail_idx]

head = bd.transform_polar_to_cartesian(head_angle, head_distance, bd.get_center(mode))
tail = bd.transform_polar_to_cartesian(tail_angle, tail_distance, bd.get_center(mode))

orientation = bd.compute_angle(head, bd.get_center(mode))

print(head)
print(tail)
print(orientation)

        

#%%
#debug: pca method
mode = 'pca'
bd.detect_head_tail(mode)

print('head:', bd.get_head(mode))
print('tail:', bd.get_tail(mode))
print('center:', bd.get_center(mode))
print('orientation', bd.get_orientation(mode))

bd.view_head_tail_pca()


#%% Test Rotation Class: rotate randomly the inpur images

# init a rotation operation for egg1
r = Rotation(egg1)

angle = math.pi/6
r.set_angle(angle)

r.rotate_embryo(egg1, angle=angle)