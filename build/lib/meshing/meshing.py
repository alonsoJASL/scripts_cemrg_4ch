import os
import argparse

# ----------------------------------------------------------------------------------------------
# Point to segmentation folder
# ----------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='To run: python3 meshing.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
folder = args.heart_folder

# ----------------------------------------------------------------------------------------------
# Set up meshing folder structure
# ----------------------------------------------------------------------------------------------
print('\n ## Setting up meshing folder structure ## \n')
os.system("mkdir "+folder+"meshing")
os.system("cp /data/Dropbox/scripts_cemrgapp/meshing/heart_mesh_data_file "+folder+"/meshing/heart_mesh_data_file")
os.system("cp /data/Dropbox/scripts_cemrgapp/meshing/generate_heart_mesh_Cesare.sh "+folder+"/meshing/generate_heart_mesh_Cesare.sh")
# os.system("cp "+folder+"/segmentations/seg_final_smooth.inr "+folder+"/meshing/myocardium.inr")
os.system("cp "+folder+"/segmentations/seg_final_smooth.nrrd "+folder+"/meshing/myocardium.nrrd")
# os.system("segconvert "+folder+"/meshing/myocardium.nrrd "+folder+"/meshing/myocardium.inr")
os.system("/home/rb21/Software/segtools/bin/segconvert "+folder+"/meshing/myocardium.nrrd "+folder+"/meshing/myocardium.inr")