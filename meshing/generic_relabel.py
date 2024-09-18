import numpy as np
import pandas as pd
import os
import argparse
import json

SOURCE_LABELS = { "LV" : 2 , "RV" : 103 , "LA" : 104 , "RA" : 105 , "Ao" : 106 , 
                 "PArt" : 107 , "MV" : 201 , "TV" : 202 , "AV" : 203 , "PV" : 204 ,
                 "LPV1" : 205 , "LPV2" : 206 , "RPV1" : 207 , "RPV2" : 208 , "LAA" : 209 ,
                 "SVC" : 210 , "IVC" : 211 , "LAA_ring" : 225 , "SVC_ring" : 226 , "IVC_ring" : 227 ,
                 "LPV1_ring" : 221 , "LPV2_ring" : 222 , "RPV1_ring" : 223 , "RPV2_ring" : 224
                 }

SOURCE_LABELS_SLICER = { "LV" : 2 , "RV" : 15 , "LA" : 16 , "RA" : 17 , "Ao" : 18 , 
                        "PArt" : 19 , "MV" : 20 , "TV" : 21 , "AV" : 22 , "PV" : 23 ,
                        "LPV1" : 24 , "LPV2" : 25 , "RPV1" : 26 , "RPV2" : 27 , "LAA" : 28 ,
                        "SVC" : 29 , "IVC" : 30 , "LAA_ring" : 31 , "SVC_ring" : 32 , "IVC_ring" : 33 ,
                        "LPV1_ring" : 34 ,"LPV2_ring" : 35 ,"RPV1_ring" : 36 ,"RPV2_ring" : 37 
                        }

TARGET_LABELS = { "LV" : 1 , "RV" : 2 , "LA" : 3 , "RA" : 4 , "Ao" : 5 , 
                 "PArt" : 6 , "MV" : 7 , "TV" : 8 , "AV" : 9 , "PV" : 10 , 
                 "LPV1" : 11 , "LPV2" : 12 , "RPV1" : 13 , "RPV2" : 14 , "LAA" : 15 ,
                 "SVC" : 16 , "IVC" : 17 , "LAA_ring" : 18 , "SVC_ring" : 19 , "IVC_ring" : 20 ,
                 "LPV1_ring" : 21 , "LPV2_ring" : 22 , "RPV1_ring" : 23 , "RPV2_ring" : 24
                 }

TO_REPLACE = {
      "original" : SOURCE_LABELS ,
      "mri" : SOURCE_LABELS_SLICER
}

CORRECT_ORDER = [
        "LV", "RV", "LA", "RA", "Ao", "PArt", "MV", "TV", "AV", "PV", 
        "LPV1", "LPV2", "RPV1", "RPV2", "LAA", "SVC", "IVC", 
        "LAA_ring", "SVC_ring", "IVC_ring", "LPV1_ring", "LPV2_ring", 
        "RPV1_ring", "RPV2_ring"
    ]


def simple_read_elem(meshname) : 
      mesh_elem = pd.read_csv(f'{meshname}.elem', sep=" ", header=0, names=['colA','colB','colC','colD','colE','colF'])
      label_col = mesh_elem['colF']
      other_cols = mesh_elem[['colA','colB','colC','colD','colE']]
      return label_col, other_cols

def relabel_mesh(args) : 
      heart_folder = args.directory
      mesh=os.path.join(heart_folder, args.input_mesh)
      if args.replace_labels != '':
         with open(args.replace_labels) as f:
            labels_to_replace = json.load(f)
      else :
            labels_to_replace = TO_REPLACE[args.labels_from]

      os.system(f"cp -n {mesh}.elem {mesh}_old_labels.elem")
      
      print('Reading mesh...')
      label_col, other_cols = simple_read_elem(mesh)
      print('Done')
      
      print('Relabelling mesh...')
      for label in CORRECT_ORDER:
            if label in labels_to_replace:
                  print(f'[{label}] Replacing {labels_to_replace[label]} with {TARGET_LABELS[label]}')
                  label_col.replace(to_replace=labels_to_replace[label], value=TARGET_LABELS[label], inplace=True)
      
      mesh_elem_no_header = pd.concat([other_cols,label_col],axis=1)
      print('Done')
      
      print('Saving relabelled mesh...')
      mesh_elem_no_header.to_csv(mesh+'_no_header.elem',sep='\t',header=False, index=False)
      print('Done')
      
      num_elems = str(mesh_elem_no_header.shape[0])

      with open(f'{mesh}_no_header.elem','r') as contents:
            save = contents.read()
      with open(f'{mesh}_new.elem','w') as contents:
            contents.write(num_elems+' \n')
      with open(f'{mesh}_new.elem','a') as contents:
            contents.write(save)

      os.system(f"rm {mesh}_no_header.elem")
      os.system(f"mv {mesh}_new.elem {mesh}.elem")
      os.system(f"rm {mesh}.vtk")
      os.system(f"meshtool convert -imsh={mesh} -omsh={mesh} -ofmt=vtk")

def get_tags(labels_to_replace_dict) :
      msg='-tags='
      for label in CORRECT_ORDER:
            if label in labels_to_replace_dict:
                  msg+=f'{str(labels_to_replace_dict[label])}'
                  msg+=',' if label != CORRECT_ORDER[-1] else ''

      return msg


def main(args) : 
      if args.print : 
            labels_to_replace = TO_REPLACE[args.labels_from]
            print(get_tags(labels_to_replace))
            return
      
      relabel_mesh(args)


if __name__ == '__main__':
      parser = argparse.ArgumentParser(description='To run: python3 relabel_mesh.py [heart_folder]')
      parser.add_argument('-dir', '--directory', type=str, required=True, help='Path to the folder with mesh files') 
      parser.add_argument('-msh', '--input-mesh', type=str, help='Name of the mesh file (No extension)', default='myocardium')
      parser.add_argument('-labels', '--labels-from', type=str, choices=['original', 'mri'], default='original', help='Labels to replace')
      parser.add_argument('-replace-labels', '--replace-labels', type=str, help='File with labels to replace, default empty, uses common segmentation labels', default='')
      parser.add_argument('-print', '--print', action='store_true', help='Print the tags to get from the mesh')
      
      args = parser.parse_args()

      main(args)

