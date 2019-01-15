#!/bin/bash

project_folder='/mnt/d/Princeton_3rd/course/APC524/APC524_project_drosophila'
version='version_1'
working_folder=$project_folder/$version

echo $working_folder
cd $working_folder

# testing classes
echo '-------------------testing embryo class---------------------'
python3 test/test_embryo.py
echo '-------------------testing boundary class------------------'
python3 test/test_boundary.py
echo '------------------testing rotation class-------------------'
python3 test/test_rotation.py
echo '------------------testing polygon class---------------------'
python3 test/test_polygon.py
echo '------------------testing intensity class------------------'
python3 test/test_intensity.py
