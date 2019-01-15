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



# rotate the embryo first to horizonal position
r = Rotation(egg1)
rotated_egg = r.rotate_embryo(egg1, bd_mode = 'pca')
#rotated_egg.view()

# compute the intensity curve
intensity_curve = Intensity.detect_intensity(rotated_egg)
print(intensity_curve.shape)

# without normalization
#Intensity.view([intensity_curve])

# after normalization
normalized_curves = Intensity.normalization([intensity_curve])
#Intensity.view(normalized_curves)


print('PASS: Intensity module')