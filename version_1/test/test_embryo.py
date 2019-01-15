import os
cwd = os.getcwd()

import sys
sys.path.append(cwd)

#%%
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
	
	
# test gray_image and backup_imgae
# test attribute
egg1 = embryo_list[0]

print(egg1.gene_name)
print(egg1.gene_position)

#plt.imshow(egg1.gray_image, 'gray')
#plt.show()
#plt.imshow(egg1.bk_image)
#plt.show()


print('PASS: embryo class')