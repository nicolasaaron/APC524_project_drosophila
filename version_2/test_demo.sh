#!/bin/bash

project_folder='/mnt/d/Princeton_3rd/course/APC524/APC524_project_drosophila'
version='version_2'
profile_dir='profile'

# the py file
filename='demo.py'

# define output filenames


# change to project repository
#echo $(pwd)
working_folder=$project_folder/$version
#echo $working_folder
cd $working_folder

# run cProfile
python3 -m cProfile -o profile/demo.pstats demo.py

# change to profile folder
cd $profile_dir

# run pyprof2calltree
pyprof2calltree -i demo.pstats -o demo.callgrind

# convert to dot file for graphviz
gprof2dot -f callgrind demo.callgrind -o demo.dot

# save as png file
dot -Tpng demo.dot -o demo.png

# run qcachegrind
qcachegrind.exe demo.callgrind
