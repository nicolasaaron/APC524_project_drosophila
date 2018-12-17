# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 17:11:38 2018

@author: iris
"""
%matplotlib inline

import numpy
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt


polygon = [(10,10), (10, 20), (40,50), (40, 10)]
width = 100
height = 60

img = Image.new('L', (width, height), 0)
mask = numpy.array(img)


#%%
ImageDraw.Draw(img).polygon(polygon, outline =1, fill = 1)
#%%
mask = numpy.array(img)
#%%
img2 = Image.fromarray(mask, mode = 'L')

#%%

plt.imshow(mask)

#%%
plt.imshow(img2)
