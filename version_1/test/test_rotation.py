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

#########################################
# test rotation class
r = Rotation(egg1)

angle = math.pi / 6
print('manual rotation angle:', angle)

r.set_angle(angle)
rotated_embryo = r.rotate_embryo(egg1, angle=angle)
#egg1.view()
#rotated_embryo.view()



# test get_rotated_image
rotated_egg = Embryo(r.get_rotated_image())
print('pass: get rotation from image')

#rotated_egg.view()

# rotate back

#mode = 'curvature'
mode = 'pca'
bd = Boundary(rotated_egg)
bd.detect_head_tail(mode)
print('rotation angle:', -bd.get_orientation(mode))

#with the presence of the boundary
rotated_egg2 = r.rotate_embryo(rotated_embryo, boundary=bd)
#rotated_egg2.view()

# without boundary, using pca method to generate a boundary on the fly
rotated_egg3 = r.rotate_embryo(rotated_egg2, bd_mode = 'curvature')
print('rotation angle:', r.angle)
#rotated_egg3.view()

#without boundary, use pca method on the fly
rotated_egg4 = r.rotate_embryo(rotated_egg3, bd_mode = 'pca')
print('rotation angle:', r.angle)
#rotated_egg4.view()


print('PASS: rotation class')