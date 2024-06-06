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
os.system(f"mkdir -p {folder}/meshing/myocardium_OUT")
os.system("cp ./heart_mesh_data_file "+folder+"/meshing/heart_mesh_data_file")
os.system("cp ./generate_heart_mesh_Cesare.sh "+folder+"/meshing/generate_heart_mesh_Cesare.sh")
os.system(f"cp {folder}/segmentations/seg_final_smooth_corrected.inr {folder}/meshing/seg_final_smooth_corrected.inr")
