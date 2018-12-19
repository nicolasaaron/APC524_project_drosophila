# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 16:16:14 2018

@author: iris
"""

import numpy, scipy, scipy.interpolate, numpy.fft, math
import matplotlib.pyplot as plt


#%%
# Using Fourier transfor to approx contours
# cf https://stackoverflow.com/questions/13604611/how-to-fit-a-closed-contour

# create simple square
img = numpy.zeros( (10, 10) )
img[1:9, 1:9] = 1
img[2:8, 2:8] = 0

plt.imshow(img)
plt.show()

# find contour
x, y = numpy.nonzero(img)

# find center point and conver to polar coords
x0, y0 = numpy.mean(x), numpy.mean(y)
C = (x - x0) + 1j * (y - y0)
angles = numpy.angle(C)
distances = numpy.absolute(C)
sortidx = numpy.argsort( angles )
angles = angles[ sortidx ]
distances = distances[ sortidx ]

# copy first and last elements with angles wrapped around. needed so can interpolate over full range -pi to pi
angles = numpy.hstack(([ angles[-1] - 2*math.pi ], angles, [ angles[0] + 2*math.pi ]))
distances = numpy.hstack(([distances[-1]], distances, [distances[0]]))

plt.polar(angles, distances, color='r')
plt.show()

# Irregular sampling problem:
# interpolate to evenly spaced angles
f = scipy.interpolate.interp1d(angles, distances)
angles_uniform = scipy.linspace(-math.pi, math.pi, num=100, endpoint=False) 
distances_uniform = f(angles_uniform)

# fft and inverse fft
fft_coeffs = numpy.fft.rfft(distances_uniform)
# zero out all but lowest 10 coefficients
fft_coeffs[11:] = 0
distances_fit = numpy.fft.irfft(fft_coeffs)

# plot results

plt.polar(angles, distances, color='r')
plt.polar(angles_uniform, distances_uniform, color='g')
plt.polar(angles_uniform, distances_fit, color='b')
plt.show()

#%%
# find boundary curve

from Embryo import *
from Boundary import *
import numpy as np
import skimage.filter

filename = "C1-WT-9.png"

gene1 = Embryo(filename)
gene1.rgb2gray()
plt.imshow(gene1.raw_image, 'gray')
plt.show()


threshold = skimage.filter.threshold_otsu(gene1.raw_image)
contours = skimage.measure.find_contours(gene1.raw_image, level= threshold)

bw_image = gene1.raw_image > threshold
plt.imshow(bw_image)
plt.show()

label_image = skimage.measure.label(bw_image)
regions = skimage.measure.regionprops(label_image)
print(len(regions))

temp_area = 0
for rg in regions:
    if rg.area> temp_area:
        boundary_curve = rg.coords
        temp_area = rg.area        
    
temp_img = np.zeros(gene1.raw_image.shape)
temp_img[boundary_curve[:,0], boundary_curve[:,1]] = 1
plt.imshow(temp_img)
plt.show()


#%%
contours = skimage.measure.find_contours(gene1.raw_image, level= threshold)
print('number of contours', len(contours))

temp_img = np.zeros(gene1.raw_image.shape, dtype = int)
for curve in contours:
    coords = np.round(curve).astype(int)
    temp_img[coords[:,0], coords[:,1]] = 1

plt.imshow(temp_img)
plt.show()

label_img = skimage.measure.label(temp_img)
regions = skimage.measure.regionprops(label_img)
print('number of regions',len(regions))


temp_area = 0
for rg in regions:
    if rg.area> temp_area:
        boundary_curve = rg.coords
        temp_area = rg.area        
    
temp_img = np.zeros(gene1.raw_image.shape)
temp_img[boundary_curve[:,0], boundary_curve[:,1]] = 1
plt.imshow(temp_img)
plt.show()


#%%

# Using the above FTT for embryo data

from Embryo import *
from Boundary import *
import numpy as np
import skimage.filter

filename = "C1-WT-9.png"

gene1 = Embryo(filename)
gene1.rgb2gray()
plt.imshow(gene1.raw_image, 'gray')
plt.show()

boundary_gene1 = Boundary(gene1)
boundary_gene1.detect_boundary()

threshold = skimage.filters.threshold_otsu(gene1.raw_image)   
bw_image = gene1.raw_image > threshold

plt.imshow(boundary_gene1.ref_image)
plt.plot(boundary_gene1.boundary_curve[:,1], boundary_gene1.boundary_curve[:,0], color='r')
plt.show()


x = boundary_gene1.boundary_curve[:,1]
y = boundary_gene1.boundary_curve[:,0]

# the central of gravity is determined from the convex_hull
cgx = np.sum ( np.arange(0, gene1.raw_image.shape[1]) * np.sum(bw_image, axis = 0) ) / np.sum(bw_image)
cgy = np.sum ( np.arange(0, gene1.raw_image.shape[0]) * np.sum(bw_image, axis = 1) ) / np.sum(bw_image)
center_x, center_y = np.round(cgx), np.round(cgy)

#center_x, center_y = np.mean(x), np.mean(y)

C = (x - center_x) + 1j * (center_y- y)
angles = np.angle(C)
distances = np.absolute(C)
sortidx = np.argsort( angles )
angles = angles[ sortidx ]
distances = distances[ sortidx ]

plt.polar(angles[: 2000], distances[:2000])
plt.show()

# copy first and last elements with angles wrapped around. needed so can interpolate over full range -pi to pi
angles = numpy.hstack(([ angles[-1] - 2*math.pi ], angles, [ angles[0] + 2*math.pi ]))
distances = numpy.hstack(([distances[-1]], distances, [distances[0]]))

#plt.imshow(boundary_gene1.ref_image)
plt.polar(angles, distances, color='r')
plt.show()
       
# interpolate to evenly spaced angles
f = scipy.interpolate.interp1d(angles, distances, 'linear')
angles_uniform = scipy.linspace(-math.pi, math.pi, num=3000, endpoint=False) 
distances_uniform = f(angles_uniform)

# fft and inverse fft
fft_coeffs = numpy.fft.rfft(distances_uniform)
# zero out all but lowest 10 coefficients
fft_coeffs[20 :] = 0
distances_fit = numpy.fft.irfft(fft_coeffs)

# plot results

fig,ax = plt.subplots(figsize=(10,10))
plt.polar(angles, distances, color='r')
plt.polar(angles_uniform, distances_uniform, color='g')
plt.polar(angles_uniform, distances_fit, color='b')
plt.show()

# plot with original image
x_fit = center_x + distances_fit * np.cos(angles_uniform)
y_fit = center_y - distances_fit * np.sin(angles_uniform)

fig, ax = plt.subplots(figsize=(10,10))
plt.imshow(gene1.raw_image)
plt.plot(x_fit, y_fit, color='b')
plt.show()

#%% find convex contour and fit it with linear interpolation in polar coordinate

import skimage.morphology
threshold = skimage.filter.threshold_otsu(gene1.raw_image)
bw_image = gene1.raw_image > threshold

convex_hull = skimage.morphology.convex_hull_image(bw_image)
contours = skimage.measure.find_contours(convex_hull, level = 0)
boundary_curve = contours[0]


plt.subplots(figsize=(10,10))
plt.imshow(gene1.raw_image)
plt.plot(boundary_curve[:,1], boundary_curve[:,0], color='r')
plt.show()

x = boundary_curve[:,1]
y = boundary_curve[:,0]

# the central of gravity is determined from the convex_hull
cgx = np.sum ( np.arange(0, gene1.raw_image.shape[1]) * np.sum(convex_hull, axis = 0) ) / np.sum(convex_hull)
cgy = np.sum ( np.arange(0, gene1.raw_image.shape[0]) * np.sum(convex_hull, axis = 1) ) / np.sum(convex_hull)
center_x, center_y = np.round(cgx), np.round(cgy)




C = (x - center_x) + 1j * (center_y- y)
angles = np.angle(C)
distances = np.absolute(C)
sortidx = np.argsort( angles )
angles = angles[ sortidx ]
distances = distances[ sortidx ]

# copy first and last elements with angles wrapped around. needed so can interpolate over full range -pi to pi
angles = numpy.hstack(([ angles[-1] - 2*math.pi ], angles, [ angles[0] + 2*math.pi ]))
distances = numpy.hstack(([distances[-1]], distances, [distances[0]]))

     
# interpolate to evenly spaced angles
f = scipy.interpolate.interp1d(angles, distances, 'linear')
angles_uniform = scipy.linspace(-math.pi, math.pi, num=6000, endpoint=False) 
distances_uniform = f(angles_uniform)


# fft and inverse fft
fft_coeffs = numpy.fft.rfft(distances_uniform)
# zero out all but lowest 10 coefficients
fft_coeffs[20 :] = 0
distances_fit = numpy.fft.irfft(fft_coeffs)



plt.subplots(figsize=(10,10))
plt.polar(angles, distances, color='r')
plt.polar(angles_uniform, distances_uniform, color='b')
plt.polar(angles_uniform, distances_fit, color = 'g')
plt.show()



#%% using FFT fitted curve for computing the curvature

r = distances_fit
r_prime = np.gradient(r, angles_uniform)
r_prime2 = np.gradient(r_prime, angles_uniform)
curvature = np.divide ( (np.abs(r**2 + 2 * r_prime**2- r * r_prime2) ) **2 , np.power( (r**2 + r_prime**2), 1.5) )

plt.plot(angles_uniform, curvature)
plt.show()

# drop bizzar curvature
print( len(curvature)) 

plt.subplots(figsize=(10,10))
plt.polar(angles_uniform, curvature, color = 'b')
plt.show()

#%% find the peaks in the curvature plot
import scipy.signal

peaks, _ = scipy.signal.find_peaks(curvature, height = np.mean(curvature) )

plt.plot(angles_uniform, curvature)
plt.plot(angles_uniform[peaks], curvature[peaks], 'x', color='r')
plt.show()

peaks_idx = np.argsort(curvature[peaks])
peaks_idx = np.flip(peaks_idx)
peaks = peaks[peaks_idx]

head_idx = peaks[0]
tail_idx = peaks[2]

head_angle = angles_uniform[head_idx]
head_distance = distances_fit[head_idx]
tail_angle = angles_uniform[tail_idx]
tail_distance = distances_fit[tail_idx]

head_x = center_x + head_distance * math.cos(head_angle)
head_y = center_y - head_distance * math.sin(head_angle)
tail_x = center_x + tail_distance * math.cos(tail_angle)
tail_y = center_y - head_distance * math.sin(tail_angle)

# plot with original image
x_fit = center_x + distances_fit * np.cos(angles_uniform)
y_fit = center_y - distances_fit * np.sin(angles_uniform)

# head tail angle
head_tail_angle = np.angle( (head_x - tail_x) - 1j * (head_y - tail_y))
center_head_angle = np.angle( (head_x - center_x) - 1j * (head_y - center_y))
print(head_tail_angle)
print(center_head_angle)

plt.subplots(figsize=(10,10))
plt.imshow(gene1.raw_image)
plt.plot(x_fit, y_fit, color='b')
plt.plot(head_x, head_y, marker='x', color = 'orange')
plt.plot(tail_x, tail_y, marker='x', color = 'orange')
plt.plot(center_x, center_y, marker='x', color = 'orange')
plt.plot((center_x, head_x),(center_y, head_y), color='green', linewidth = 2)
plt.plot((center_x, tail_x),(center_y, tail_y), color='green', linewidth = 2)
plt.plot((head_x, tail_x),(head_y, tail_y), color='red', linewidth = 2)
plt.show()


#%% comparison between the elliptic fitted method and the maximum curvature method
label_img = skimage.measure.label(convex_hull)
regions = skimage.measure.regionprops(label_img)

main_region = regions[0]
orientation = main_region.orientation

cy,cx = main_region.centroid
x1 = cx + math.cos(orientation) * 0.5 * main_region.major_axis_length
y1 = cy - math.sin(orientation) * 0.5 * main_region.major_axis_length
x2 = cx - math.sin(orientation) * 0.5 * main_region.minor_axis_length
y2 = cy - math.cos(orientation) * 0.5 * main_region.minor_axis_length


plt.subplots(figsize=(10,10))
plt.imshow(gene1.raw_image)
plt.plot(x_fit, y_fit, color='b')
plt.plot(head_x, head_y, marker='x', color = 'orange')
plt.plot(tail_x, tail_y, marker='x', color = 'orange')
plt.plot(center_x, center_y, marker='x', color = 'red', markersize = 15)
plt.plot((center_x, head_x),(center_y, head_y), color='green', linewidth = 2)
plt.plot((center_x, tail_x),(center_y, tail_y), color='green', linewidth = 2)
plt.plot((head_x, tail_x),(head_y, tail_y), color='orange', linewidth = 2)

plt.plot((cx, x1), (cy, y1), '--r', linewidth=2.5)
plt.plot((cx, x2), (cy, y2), '--r', linewidth=2.5)
plt.plot(cx, cy, '.', color='yellow' , markersize=15)

plt.show()

print('region orientation:', orientation)
print('fitted center head angle:', center_head_angle)
print('fitted head tial angle:', head_tail_angle)
print('cx,cy', cx,cy)
print('central gravity:', center_x, center_y)


#%% robust linear regression


threshold = skimage.filter.threshold_otsu(gene1.raw_image)
bw_image = gene1.raw_image > threshold

x = []
y = []

for i in range(bw_image.shape[0]):
    for j in range(bw_image.shape[1]):
        if bw_image[i,j] :
            x.append(j)
            y.append(i)

data = np.column_stack( (x,y))
  
#%%      
model_robust, inliers = skimage.measure.ransac(data, 
                                               skimage.measure.LineModelND, 
                                               min_samples=5,
                                               residual_threshold=5, 
                                               max_trials=1000)

outliers = inliers == False

#using all data
model = skimage.measure.LineModelND()
model.estimate(data)

#%%
# generate coordiante
line_x = np.arange(0,bw_image.shape[1])
line_y = model.predict_y(line_x)
line_y_robust = model_robust.predict_y(line_x)


#figures
fig, ax = plt.subplots(figsize=(10,10))
ax.imshow(gene1.raw_image)
ax.scatter(data[inliers, 0], data[inliers, 1], s = 0.5, c= 'b', alpha=0.2, label='Inlier data')
#ax.plot(data[outliers, 0], data[outliers, 1], '.r', alpha=0.6,
#        label='Outlier data')
ax.plot(line_x, line_y, '-r', label='Line model from all data')
ax.plot(line_x, line_y_robust, '-b', label='Robust line model')
#ax.legend(loc='lower left')
plt.show()

linear_all_angle = np.angle( (line_x[-1]-  line_x[0]) - 1j * (line_y[-1] - line_y[0]) )
linear_ransac_angle =  np.angle( (line_x[-1]- line_x[0]) - 1j * (line_y_robust[-1] - line_y_robust[0]) )

print('linear all angle:', linear_all_angle)
print('linear ransac angle:', linear_ransac_angle)

#%%
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
pca.fit(data)

def draw_vector(v0, v1, ax=None):
    ax = ax or plt.gca()
    arrowprops=dict(arrowstyle='->',
                    linewidth=2,
                    shrinkA=0, shrinkB=0)
    ax.annotate('', v1, v0, arrowprops=arrowprops)

print(pca.explained_variance_)
print(pca.components_)

# plot data
fig, ax = plt.subplots(figsize=(10,10))
ax.imshow(gene1.raw_image)
#plt.scatter(data[:, 0], data[:, 1],  alpha=0.2)
arrowprops=dict(arrowstyle='->',linewidth=2,shrinkA=0, shrinkB=0)

for length, vector in zip(pca.explained_variance_, pca.components_):
    v = vector*2 * np.sqrt(length)
    #draw_vector(pca.mean_, pca.mean_ + v)
    ax.annotate('', pca.mean_ + v, pca.mean_, arrowprops= arrowprops)    
plt.show()


#pca angle
v1 = pca.components_[0]
pca_angle_1= np.angle(v1[0] - 1j * v1[1])
v2 = pca.components_[1]
pca_angle_2= np.angle(v2[0] - 1j * v2[1])

print('pca angles: ', pca_angle_1, pca_angle_2)


#%%
  
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
        
