# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 15:57:22 2018

@author: zongjun
"""


import skimage.io
import skimage.color
import skimage.segmentation
import skimage.filters
import skimage.morphology
from sklearn.ensemble import IsolationForest
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
        self.bk_image = np.copy( self.raw_image )
        
    
    def read_from_array(self, my_image = None):
        # set raw_image from a 2d array
        """ Question: when array is passed by value as a function argument, 
            why doesn't the change of input effects the assignment operator = ?
        """
        if (my_image is not None):
            self.raw_image = np.copy( my_image)
            self.bk_image =np.copy( my_image)
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
        result = Embryo(np.array([0]))
        result.gene_name = self.gene_name
        result.raw_image = np.copy( self.raw_image)
        result.gray_image = np.copy( self.gray_image)
        result.bk_image = np.copy( self.bk_image)
        return result
    
    
    def rgb2gray(self):
        # create a gray scale image, also change raw image to gray scale
        if (self.raw_image is not None):
            self.raw_image = skimage.color.rgb2gray(self.raw_image)
            self.gray_image = np.copy( self.raw_image )
        
    def set_gene_name(self, name = ''):
        # set gene name
        if (name != ''):
            self.gene_name = name
            
    def set_gene_position(self, position = None):
        if (position is not None):
            self.gene_position = position
            
            
    def denoise(self, mode='otsu'):
        if mode == 'otsu':
            threshold = skimage.filters.threshold_otsu(self.raw_image)
        elif mode == 'isodata':
            threshold = skimage.filters.threshold_isodata(self.raw_image)
        elif mode == 'mean':
            threshold = np.mean(self.raw_image)
        
        self.raw_image = self.raw_image * (self.raw_image > threshold)

        
    def clear_border(self, mode = 'otsu'):
        # remove imcomplete cells shown in the background        
        if mode == 'otsu':
            threshold = skimage.filters.threshold_otsu(self.raw_image)
        elif mode == 'isodata':
            threshold = skimage.filters.threshold_isodata(self.raw_image)
        elif mode == 'mean':
            threshold = np.mean(self.raw_image)

            
        self.raw_image = self.raw_image * skimage.segmentation.clear_border(self.raw_image > threshold)    
        
        
    def smoothing(self, radius = 10):
        # opening operation
        skimage.morphology.opening(self.raw_image,
                                   skimage.morphology.disk(radius))        
        # closing operation
        skimage.morphology.closing(self.raw_image,
                                   skimage.morphology.disk(radius))
        
    
    def clear_outlier(self):
        # using random forest method
              
        pos_data = []
        for (row,col),value in np.ndenumerate(self.raw_image):
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
        
        for i in range(len(pos_data)):
            row, col = pos_data[i,:]
            if label_predict[i] == -1:
                self.raw_image[row,col] = 0
       
        
        
# visualization methods        
    def view(self, figsize = (10,10) ):
        if self.raw_image is not None:
            fig,ax =plt.subplots(figsize = figsize)
            ax.imshow(self.raw_image, 'gray')
            plt.show()
        else:
            print('data is missing')
            
    def view_backup(self, figsize = (10,10) ):
        if self.raw_image is not None:
            fig,ax =plt.subplots(figsize = figsize)
            ax.imshow(self.bk_image, 'gray')
            plt.show()
        else:
            print('data is missing')


        
    
    
