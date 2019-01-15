import os
cwd = os.getcwd()

import sys
sys.path.append(cwd)


import matplotlib.pyplot as plt
import math

import Intensity
from Embryo import *
from TestingArea import *
from Polygon import *
from Rotation import *
from Boundary import *

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
    #egg.view()
    egg.rgb2gray()
	
egg1 = embryo_list[0]


############################################
# test polygon class

testing_img = Polygon(egg1)
#testing_img.view()

print(testing_img.ref_image_dim)

# detect area from the image, using Fourier transformation and convex_hull curve
testing_img.detect_area()
#testing_img.view_area()

for (x,y) in testing_img.vertices:
    print('vertice: [', x,',', y,']')
	
	
#detect area with the help of a boundary curve

testing_img = Polygon(egg1)
#testing_img.view()

mode = 'curvature'
#mode = 'pca'
bd = Boundary(egg1)
bd.detect_head_tail(mode)

testing_img.detect_area(boundary = bd)
#testing_img.view_area()

for (x,y) in testing_img.vertices:
    print('vertice: [', x,',', y,']')
	

print('PASS: polygon class')