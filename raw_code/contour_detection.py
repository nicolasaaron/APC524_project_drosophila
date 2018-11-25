%matplotlib inline

import skimage
import skimage.io
import skimage.exposure
import skimage.morphology
import skimage.segmentation
import skimage.viewer
import skimage.measure

import matplotlib
import matplotlib.pyplot as plt
import numpy
import scipy.ndimage
imflat = skimage.io.imread("C1-WT-9.png")
fig, ax = plt.subplots(figsize=(8, 8))
ax.axis('off')
tmp = ax.imshow(imflat,"gray")

#%%

import numpy as np
from skimage import color

print(np.shape(imflat))

imflatgray = color.rgb2gray(imflat)

print(np.shape(imflatgray))

fig, ax = plt.subplots(figsize=(8, 8))
ax.axis('off')
tmp = ax.imshow(imflatgray)

#%%
import cv2
#fig, (ax1,ax2) = plt.subplots(nrows=1, ncols=2, figsize=(8,8))

im = cv2.imread('C1-WT-9.png')
imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(imgray,1,255,cv2.THRESH_BINARY)

#ax1.imshow(thresh)

image_contours,contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

for contour in contours:
    area = cv2.contourArea(contour)
    print(area)    
    if area > 1000:
        print(np.shape(contour))
        plt.imshow( cv2.drawContours(thresh, [contour], -1, (0,255), 3) )
        
        
        