# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 15:57:22 2018

@author: iris
"""


import skimage.io
import skimage.color as color

class Embryo(object):
    
    def __init__(self):
        self.raw_image = None
        self.gray_image= None
        self.gene_name = ''
    
    def read_from_filename(self, filename):
        self.raw_image = skimage.io.imread(filename)
    
    def read_from_array(self, my_image):
        self.raw_image = my_image
        
    def rgb2gray(self):
        self.gray_image = color.rgb2gray(self.raw_image.copy())
        
    def set_gene_name(self, name=''):
        self.gene_name = name
        
   
    
#%%    
"""
#testing class Embryo

import numpy as np
import matplotlib.pyplot as plt

#%%

        
filename = "C1-WT-9.png"

gene1 = Embryo()

gene1.read_from_filename(filename)       

plt.imshow(gene1.raw_image)
        
#%%

my_image = np.ones((10,10))
gene1.read_from_array(my_image)

plt.imshow(gene1.raw_image)

#%%
Embryo.rgb2gray(gene1)
gene1.rgb2gray()

plt.imshow(gene1.gray_image, 'gray')
"""