# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 07:48:50 2018

@author: iris

testing class Embryo
"""
%matplotlib inline

import skimage.morphology
import skimage.segmentation
import skimage.measure
import skimage.filters
import skimage.draw


from Embryo import *

import numpy as np
import matplotlib.pyplot as plt


#%% create Embryo object
        
filename = "C1-WT-9.png"

gene1 = Embryo(filename)

#gene1.read_from_filename(filename)       

plt.imshow(gene1.raw_image)
        
#%%

my_image = np.ones((10,10))
gene2= Embryo(my_image)
#gene2.read_from_array(my_image)

plt.imshow(gene2.raw_image)

#%%

gene1.rgb2gray()
plt.imshow(gene1.raw_image, 'gray')

#%%

binary_im= gene1.raw_image
print('image gray scale', binary_im.max(), binary_im.min())



#%% test convex hull

threshold = 0.03
binary_im[binary_im <= threshold] = 0.0
binary_im[binary_im > threshold]  = 1.0


fig, (ax1,ax2) = plt.subplots(nrows=2, ncols=1,figsize=(10,10), sharex=True, sharey=True)
ax1.imshow(binary_im,'gray')
ax1.set_title('binary image, threshold = 0.03 ', fontsize = 10)
ax2.imshow(hull_1, 'gray')
ax2.set_title('convex hull from binary image, threshold =0.03', fontsize = 10)

#%%  otsu threshold in filters 

threshold = skimage.filters.threshold_otsu(binary_im)
mask = binary_im >= threshold
print('otsu threshold:', threshold)

hull_1= skimage.morphology.convex_hull_image(binary_im)
print("dim hull from binary detection:", np.shape(hull_1))
hull_2= skimage.morphology.convex_hull_image(mask)


fig, (ax1,ax2) = plt.subplots(nrows=2, ncols=1,figsize=(10,10), sharex=True, sharey=True)
ax1.imshow(mask, 'gray')
ax1.set_title('mask, threshold={:f}'.format(threshold), fontsize=10)
ax2.imshow(hull_2, 'gray')
ax2.set_title('convex hull from mask, threshold={:f}'.format(threshold), fontsize=10)

#%%  polygon in draw

vertices = np.array([(100, 200), (100, 750), (350, 180), (350,800)], dtype = 'int,int')
vertices.dtype.names=['x','y']
ref_image_dim = gene1.raw_image.shape


vertices_array = np.array( tuple(map(tuple, vertices)) )

vertices_array = np.array([(100, 200), (100, 750), (350, 180), (350,800)])

rr, cc = skimage.draw.polygon(vertices_array[:,0], vertices_array[:,1], ref_image_dim)

area = np.zeros( ref_image_dim, dtype = bool)
area[rr,cc] = 1

plt.imshow(area)
plt.show()

#find the convex hull
poly_hull = skimage.morphology.convex_hull_image(area)

plt.imshow(poly_hull)
plt.show()



#%% plot points and generate convex hull


vertices = np.array([(100, 200), (100, 750), (350, 180), (350,800)], dtype = 'int,int')
vertices.dtype.names=['x','y']
ref_image_dim = gene1.raw_image.shape
area = np.zeros( ref_image_dim, dtype = bool)

for (x,y) in vertices:
    area[x,y] = 1
    
plt.imshow(area)
plt.show()

#find the convex hull
poly_hull2 = skimage.morphology.convex_hull_image(area)
plt.imshow(poly_hull2)
plt.show()

#%%

from skimage.draw import ellipse
from skimage.measure import find_contours, approximate_polygon, \
    subdivide_polygon


hand = np.array([[1.64516129, 1.16145833],
                 [1.64516129, 1.59375],
                 [1.35080645, 1.921875],
                 [1.375, 2.18229167],
                 [1.68548387, 1.9375],
                 [1.60887097, 2.55208333],
                 [1.68548387, 2.69791667],
                 [1.76209677, 2.56770833],
                 [1.83064516, 1.97395833],
                 [1.89516129, 2.75],
                 [1.9516129, 2.84895833],
                 [2.01209677, 2.76041667],
                 [1.99193548, 1.99479167],
                 [2.11290323, 2.63020833],
                 [2.2016129, 2.734375],
                 [2.25403226, 2.60416667],
                 [2.14919355, 1.953125],
                 [2.30645161, 2.36979167],
                 [2.39112903, 2.36979167],
                 [2.41532258, 2.1875],
                 [2.1733871, 1.703125],
                 [2.07782258, 1.16666667]])

# subdivide polygon using 2nd degree B-Splines
new_hand = hand.copy()
for _ in range(5):
    new_hand = subdivide_polygon(new_hand, degree=2, preserve_ends=True)

# approximate subdivided polygon with Douglas-Peucker algorithm
appr_hand = approximate_polygon(new_hand, tolerance=0.02)

print("Number of coordinates:", len(hand), len(new_hand), len(appr_hand))

fig, ax = plt.subplots(figsize=(10, 10))

ax.plot(hand[:, 0], hand[:, 1])

ax.plot(new_hand[:, 0], new_hand[:, 1])
ax.plot(appr_hand[:, 0], appr_hand[:, 1])

plt.show()


#%% create two ellipses in image
img = np.zeros((800, 800), 'int32')
rr, cc = ellipse(250, 250, 180, 230, img.shape)
img[rr, cc] = 1
rr, cc = ellipse(600, 600, 150, 90, img.shape)
img[rr, cc] = 1

img[:, :100] = 0
img[700:, :] = 0

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(img)

# approximate / simplify coordinates of the two ellipses
for contour in find_contours(img, 0):
    
    coords = approximate_polygon(contour, tolerance=2.5)
    ax.plot(coords[:, 1], coords[:, 0], '-r', linewidth=2)
    
    coords2 = approximate_polygon(contour, tolerance=39.5)
    ax.plot(coords2[:, 1], coords2[:, 0], '-g', linewidth=2)
    
    print("Number of coordinates:", len(contour), len(coords), len(coords2))
    
#ax.axis((0, 800, 0, 800))

plt.show()


#%%
import math
import matplotlib.pyplot as plt
import numpy as np

from skimage.draw import ellipse
from skimage.measure import label, regionprops
from skimage.transform import rotate


image = np.zeros((1000, 1000))

rr, cc = ellipse(300, 350, 100, 220)
image[rr, cc] = 1

image = rotate(image, angle=15, order=0)

rr,cc = ellipse(600, 600, 200, 400)
image[rr,cc] = 1

image = rotate(image, angle = -30, order =0)

image[:, 600:] = 0


label_img = label(image)
regions = regionprops(label_img)



fig, ax = plt.subplots(figsize = (10,10))
ax.imshow(image, cmap=plt.cm.gray)

for props in regions:
    
    print('label of region', props.label)
    print('area', props.area)
    print('convex_area', props.convex_area)
    print('area/bbox ratio', props.extent)
    
    
    y0, x0 = props.centroid
    orientation = props.orientation
    
    x1 = x0 + math.cos(orientation) * 0.5 * props.major_axis_length
    y1 = y0 - math.sin(orientation) * 0.5 * props.major_axis_length
    x2 = x0 - math.sin(orientation) * 0.5 * props.minor_axis_length
    y2 = y0 - math.cos(orientation) * 0.5 * props.minor_axis_length

    ax.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
    ax.plot((x0, x2), (y0, y2), '-r', linewidth=2.5)
    ax.plot(x0, y0, '.g', markersize=15)

    minr, minc, maxr, maxc = props.bbox
    bx = (minc, maxc, maxc, minc, minc)
    by = (minr, minr, maxr, maxr, minr)
    ax.plot(bx, by, '-b', linewidth=2.5)

ax.axis((0, 1000, 1000, 0))
plt.show()



#%% region property of raw_image

threshold = skimage.filters.threshold_otsu(gene1.raw_image)
convex_hull = skimage.morphology.convex_hull_image(gene1.raw_image >= threshold)

label_img = label(convex_hull)
regions = regionprops(label_img)

cell = regions[0]
print(cell.area)

y0, x0 = cell.centroid
print('x0,y0', x0,y0)
orientation = cell.orientation
print(orientation)

x1 = x0 + math.cos(orientation) * 0.5 * cell.major_axis_length
y1 = y0 - math.sin(orientation) * 0.5 * cell.major_axis_length
x2 = x0 - math.sin(orientation) * 0.5 * cell.minor_axis_length
y2 = y0 - math.cos(orientation) * 0.5 * cell.minor_axis_length


fig, ax = plt.subplots(figsize=(10,10))
ax.imshow(gene1.raw_image, cmap = plt.cm.gray)
#ax.imshow(convex_hull, 'gray')
ax.plot( (x0, x1), (y0,y1), '-r', linewidth = 2)
ax.plot( (x0, x2), (y0,y2), '-r', linewidth = 2)   
ax.plot( x0,y0,'.g', markersize =10)

minr, minc, maxr, maxc = cell.bbox
bx = (minc, maxc, maxc, minc, minc)
by = (minr, minr, maxr, maxr, minr)
ax.plot(bx, by, '-y', linewidth=2.5)

#%%
import skimage.segmentation

ref_img = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 5, 5, 5, 0, 0],
                    [0, 1, 1, 1, 0, 5, 5, 5, 0, 0],
                    [0, 1, 1, 1, 0, 5, 5, 5, 0, 0],
                    [0, 1, 1, 1, 0, 5, 5, 5, 0, 0],
                    [0, 0, 0, 0, 0, 5, 5, 5, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.uint8)

plt.imshow(ref_img)
plt.show()


bd1 = skimage.segmentation.find_boundaries(ref_img, mode='thick').astype(np.uint8)

plt.imshow(bd1)
plt.show()


inner = skimage.segmentation.find_boundaries(ref_img, mode='inner').astype(np.uint8)

plt.imshow(inner)
plt.show()

outer = skimage.segmentation.find_boundaries(ref_img, mode='outer').astype(np.uint8)

plt.imshow(outer)
plt.show()


label_img = skimage.measure.label(inner)
regions = skimage.measure.regionprops(label_img)

for props in regions:
    print('label of region', props.label)
    print('area', props.area)
    print('convex_area', props.convex_area)
    print('area/bbox ratio', props.extent)
    
    temp_img = np.zeros(ref_img.shape)
    temp_img[props.coords[:,0], props.coords[:,1]] = 1
    plt.imshow(temp_img)
    plt.show()
    
#%% test clean boarder


ref_img = np.array([[0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                    [0, 0, 0, 0, 0, 5, 5, 0, 0, 1],
                    [0, 1, 1, 1, 0, 5, 5, 5, 0, 1],
                    [0, 1, 1, 1, 0, 5, 5, 5, 0, 0],
                    [0, 1, 1, 1, 0, 5, 5, 5, 0, 0],
                    [0, 0, 0, 0, 0, 5, 5, 5, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.uint8)

plt.imshow(ref_img)
plt.show()

new_img = skimage.segmentation.clear_border(ref_img)

plt.imshow(new_img)
plt.show()

#%%
print(np.max(gene1.raw_image) )
plt.imshow(gene1.raw_image)
plt.show()

threshold = skimage.filter.threshold_otsu(gene1.raw_image)
bw_image = gene1.raw_image > threshold
plt.imshow(bw_image)
plt.show()


new_image = skimage.segmentation.clear_border(bw_image)
plt.imshow(new_image)
plt.show()


    
