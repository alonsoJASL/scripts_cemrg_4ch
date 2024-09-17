import numpy as np
import pandas as pd
import os
import argparse

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


def relabel_mesh(args) : 
      heart_folder = args.directory
      mesh=os.path.join(heart_folder, args.file)
      labels_to_replace = TO_REPLACE[args.labels_from]

      os.system(f"cp -n {mesh}.elem {mesh}_old_labels.elem")
      
      print('Reading mesh...')
      mesh_elem = pd.read_csv(f'{mesh}.elem', sep=" ", header=0, names=['colA','colB','colC','colD','colE','colF'])
      label_col = mesh_elem['colF']
      other_cols = mesh_elem[['colA','colB','colC','colD','colE']]
      print('Done')
      
      print('Relabelling mesh...')
      for label in CORRECT_ORDER:
            if label in labels_to_replace:
                  label_col.replace(to_replace=labels_to_replace[label], value=TARGET_LABELS[label], inplace=True)
      # label_col.replace(to_replace=2,value=1,inplace=True) # LV
      # label_col.replace(to_replace=103,value=2,inplace=True) # RV
      # label_col.replace(to_replace=104,value=3,inplace=True) # LA
      # label_col.replace(to_replace=105,value=4,inplace=True) # RA
      # label_col.replace(to_replace=106,value=5,inplace=True) # Ao
      # label_col.replace(to_replace=107,value=6,inplace=True) # PArt
      # label_col.replace(to_replace=201,value=7,inplace=True) # MV
      # label_col.replace(to_replace=202,value=8,inplace=True) # TV
      # label_col.replace(to_replace=203,value=9,inplace=True) # AV
      # label_col.replace(to_replace=204,value=10,inplace=True) # PV
      # label_col.replace(to_replace=205,value=11,inplace=True) # LPV1
      # label_col.replace(to_replace=206,value=12,inplace=True) # LPV2
      # label_col.replace(to_replace=207,value=13,inplace=True) # RPV1
      # label_col.replace(to_replace=208,value=14,inplace=True) # RPV2
      # label_col.replace(to_replace=209,value=15,inplace=True) # LAA
      # label_col.replace(to_replace=210,value=16,inplace=True) # SVC
      # label_col.replace(to_replace=211,value=17,inplace=True) # IVC
      # label_col.replace(to_replace=225,value=18,inplace=True) # LAA_ring
      # label_col.replace(to_replace=226,value=19,inplace=True) # SVC_ring
      # label_col.replace(to_replace=227,value=20,inplace=True) # IVC_ring
      # label_col.replace(to_replace=221,value=21,inplace=True) # LPV1_ring
      # label_col.replace(to_replace=222,value=22,inplace=True) # LPV2_ring
      # label_col.replace(to_replace=223,value=23,inplace=True) # RPV1_ring
      # label_col.replace(to_replace=224,value=24,inplace=True) # RPV2_ring
      
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
      parser.add_argument('-f', '--file', type=str, help='Name of the mesh file (No extension)', default='myocardium')
      parser.add_argument('-labels', '--labels-from', type=str, choices=['original', 'mri'], default='original', help='Labels to replace')
      parser.add_argument('-print', '--print', action='store_true', help='Print the tags to get from the mesh')
      
      args = parser.parse_args()

      main(args)

