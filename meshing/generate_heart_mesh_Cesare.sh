# shell script for generating heart mesh with meshtools3d
export TBB_NUM_THREADS=16
/home/rb21/Software/CemrgApp_v2.1.1/bin/M3DLib/meshtools3d -f heart_mesh_data_file 

mv ./myocardium_OUT/myocardium.elem ./myocardium_OUT/heart_mesh.elem
mv ./myocardium_OUT/myocardium.lon ./myocardium_OUT/heart_mesh.lon
mv ./myocardium_OUT/myocardium.pts ./myocardium_OUT/heart_mesh.pts
mv ./myocardium_OUT/myocardium.vtk ./myocardium_OUT/heart_mesh.vtk