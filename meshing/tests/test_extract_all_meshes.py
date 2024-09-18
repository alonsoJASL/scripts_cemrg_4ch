import numpy as np
import pandas as pd
import os
import json 
import argparse

from meshing.generic_relabel import  simple_read_elem

def main(args) :     
    heart_folder = args.directory   
    meshname = args.input_mesh
    
    label_col, _ = simple_read_elem(os.path.join(heart_folder, meshname))
    labels_in_mesh = np.unique(label_col)

    # make tmp directory
    tmp_folder = os.path.join(heart_folder, 'tmp')
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    for label in labels_in_mesh:
        print(f"Label {label} found in mesh")
        cmd = f'meshtool extract mesh -msh={heart_folder}/{meshname} -tags={label} -submsh={tmp_folder}/label_{label} -ifmt=carp_txt' 
        print(cmd)
        os.system(cmd)

        cmd = f'meshtool convert -imsh={tmp_folder}/label_{label} -omsh={tmp_folder}/label_{label} -ofmt=vtk'
        print(cmd)
        os.system(cmd)
  
if __name__ == '__main__':
      parser = argparse.ArgumentParser(description='To run: python3 relabel_mesh.py [heart_folder]')
      parser.add_argument('-dir', '--directory', type=str, required=True, help='Path to the folder with mesh files') 
      parser.add_argument('-msh', '--input-mesh', type=str, help='Name of the mesh file (No extension)', default='heart_mesh')
      
      args = parser.parse_args()

      main(args)

