# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 15:57:22 2018

@author: iris
"""


import skimage.io
import skimage.color
import skimage.segmentation
import numpy as np
import matplotlib.pyplot as plt


#%%
class Embryo(object):
    
    def __init__(self, data = None):
        # raw_image is of type 2d np.array 
        self.raw_image = None
        # gene_name is of type string
        self.gene_name = ''
        self.gene_position = None
        
        # backup if raw image after first initialization
        self.bk_image = None
        # backup after change raw image to its gray scale
        # gray_image is of type 2d np.array
        self.gray_image= None
        
        # initialize raw_image
        self.init_raw_image(data)
        

    def read_from_filename(self, filename=''):
        """ add checking exisitng filename """
        self.raw_image = skimage.io.imread(filename)
        self.bk_image = self.raw_image.copy()
        
    
    def read_from_array(self, my_image = None):
        # set raw_image from a 2d array
        """ Question: when array is passed by value as a function argument, 
            why doesn't the change of input effects the assignment operator = ?
        """
        if (my_image is not None):
            self.raw_image = my_image.copy()
            self.bk_image = my_image.copy()
        else:
            print('Image is not provided.')

        
    def init_raw_image(self, data):
        if (isinstance(data, str) and data != ''):
            self.read_from_filename(data)
        elif (isinstance( data, np.ndarray) and data is not None):
            self.read_from_array(data)
        else:
            print('input data is unkonwn, please input a filename or an array')
    
    def copy(self):
        result = Embryo()
        result.gene_name = self.gene_name
        result.raw_image = self.raw_image.copy()
        result.gray_image = self.gray_image.copy()
        result.bk_image = self.bk_image.copy()
        return result
    
    
    def rgb2gray(self):
        # create a gray scale image, also change raw image to gray scale
        if (self.raw_image is not None):
            self.raw_image = skimage.color.rgb2gray(self.raw_image)
            self.gray_image = self.raw_image.copy()
        
    def set_gene_name(self, name = ''):
        # set gene name
        if (name != ''):
            self.gene_name = name
            
    def set_gene_position(self, position = None):
        if (position is not None):
            self.gene_position = position
            
            
    def clear_border(self):
        threshold = skimage.filter.threshold_otsu(self.raw_image)
        bw_image = skimage.segmentation.clear_border(self.raw_image > threshold)
        self.raw_image = self.raw_image * bw_image
        
        
    def view(self, figsize = (10,10) ):
        if self.raw_image is not None:
            fig,ax =plt.subplots(figsize = figsize)
            ax.imshow(self.raw_image)
            plt.show()
        else:
            print('data is missing')

        
    
    
