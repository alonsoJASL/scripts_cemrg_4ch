import numpy as np
import pandas as pd
import os
import json 
import argparse

from generic_relabel import SOURCE_LABELS, SOURCE_LABELS_SLICER, TARGET_LABELS, TO_REPLACE, CORRECT_ORDER, get_tags

def main(args) :     
    heart_folder = args.directory   
    meshname = args.input_mesh
    if args.replace_labels != '':
         with open(args.replace_labels) as f:
            labels_to_replace = json.load(f)
    else :
        labels_to_replace = TO_REPLACE[args.labels_from]
    
    tags = get_tags(labels_to_replace)
    cmd = f'meshtool extract mesh -msh={heart_folder}/{meshname} {tags} -submsh={heart_folder}/myocardium -ifmt=carp_txt'  
    print(cmd)
    os.system(cmd)

    cmd = f'meshtool convert -imsh={heart_folder}/myocardium -omsh={heart_folder}/myocardium -ofmt=vtk'
    print(cmd)
    os.system(cmd)

    if args.simplify_topology:
        cmd = f'{args.meshtool_path}/simplify_tag_topology -msh={heart_folder}/myocardium -outmsh={heart_folder}/myocardium_clean  -neigh=50 -ifmt=carp_txt -ofmt=carp_txt'
        print(cmd)
        os.system(cmd)
    
    input_mesh = 'myocardium_clean' if args.simplify_topology else 'myocardium'
    cmd = f'meshtool smooth mesh -msh={heart_folder}/{input_mesh} {tags} -smth=0.15 -outmsh=${heart_folder}/myocardium_smooth -ifmt=carp_txt -ofmt=carp_txt'
    print(cmd)
    os.system(cmd)

    cmd = f'meshtool extract surface -msh=${heart_folder}/myocardium_smooth -surf=${heart_folder}/whole_surface -ofmt=vtk'
    print(cmd)
    os.system(cmd)

    cmd = f'meshtool extract unreachable -msh=${heart_folder}/whole_surface.surfmesh.vtk -submsh=${heart_folder}/whole_surface_CC -ofmt=vtk'
    print(cmd)
    os.system(cmd)
    
  
if __name__ == '__main__':
      parser = argparse.ArgumentParser(description='To run: python3 relabel_mesh.py [heart_folder]')
      parser.add_argument('-dir', '--directory', type=str, required=True, help='Path to the folder with mesh files') 
      parser.add_argument('-msh', '--input-mesh', type=str, help='Name of the mesh file (No extension)', default='heart_mesh')

      parser.add_argument('-labels', '--labels-from', type=str, choices=['original', 'mri'], default='original', help='Labels to replace')
      parser.add_argument('-replace-labels', '--replace-labels', type=str, help='Labels to replace', default='')
      parser.add_argument('-print', '--print', action='store_true', help='Print the tags to get from the mesh')

      meshtool_group = parser.add_argument_group('Meshtool options')
      meshtool_group.add_argument('-meshtool-path', '--meshtool-path', type=str, help='Path to meshtool', default='')
      meshtool_group.add_argument('-simplify-topology', '--simplify-topology', action='store_true', help='Simplify the topology of the mesh')

      
      args = parser.parse_args()

      main(args)

