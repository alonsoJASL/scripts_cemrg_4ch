import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser(description='To run: python3 relabel_mesh.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
heart_folder = args.heart_folder

mesh=heart_folder+"/meshing/myocardium_OUT/myocardium"
os.system("cp -n "+mesh+".elem "+mesh+"_old_labels.elem")

print('Reading mesh...')
mesh_elem = pd.read_csv(mesh+'.elem', sep=" ", header=0, names=['colA','colB','colC','colD','colE','colF'])
label_col = mesh_elem['colF']
other_cols = mesh_elem[['colA','colB','colC','colD','colE']]
print('Done')

print('Relabelling mesh...')
label_col.replace(to_replace=2,value=1,inplace=True) # LV
label_col.replace(to_replace=103,value=2,inplace=True) # RV
label_col.replace(to_replace=104,value=3,inplace=True) # LA
label_col.replace(to_replace=105,value=4,inplace=True) # RA
label_col.replace(to_replace=106,value=5,inplace=True) # Ao
label_col.replace(to_replace=107,value=6,inplace=True) # PArt
label_col.replace(to_replace=201,value=7,inplace=True) # MV
label_col.replace(to_replace=202,value=8,inplace=True) # TV
label_col.replace(to_replace=203,value=9,inplace=True) # AV
label_col.replace(to_replace=204,value=10,inplace=True) # PV
label_col.replace(to_replace=205,value=11,inplace=True) # LPV1
label_col.replace(to_replace=206,value=12,inplace=True) # LPV2
label_col.replace(to_replace=207,value=13,inplace=True) # RPV1
label_col.replace(to_replace=208,value=14,inplace=True) # RPV2
label_col.replace(to_replace=209,value=15,inplace=True) # LAA
label_col.replace(to_replace=210,value=16,inplace=True) # SVC
label_col.replace(to_replace=211,value=17,inplace=True) # IVC
label_col.replace(to_replace=225,value=18,inplace=True) # LAA_ring
label_col.replace(to_replace=226,value=19,inplace=True) # SVC_ring
label_col.replace(to_replace=227,value=20,inplace=True) # IVC_ring
label_col.replace(to_replace=221,value=21,inplace=True) # LPV1_ring
label_col.replace(to_replace=222,value=22,inplace=True) # LPV2_ring
label_col.replace(to_replace=223,value=23,inplace=True) # RPV1_ring
label_col.replace(to_replace=224,value=24,inplace=True) # RPV2_ring

mesh_elem_no_header = pd.concat([other_cols,label_col],axis=1)
print('Done')

print('Saving relabelled mesh...')
mesh_elem_no_header.to_csv(mesh+'_no_header.elem',sep='\t',header=False, index=False)
print('Done')

num_elems = str(mesh_elem_no_header.shape[0])

with open(mesh+'_no_header.elem','r') as contents:
      save = contents.read()
with open(mesh+'_new.elem','w') as contents:
      contents.write(num_elems+' \n')
with open(mesh+'_new.elem','a') as contents:
      contents.write(save)

os.system("rm "+mesh+"_no_header.elem")
os.system("mv "+mesh+"_new.elem "+mesh+".elem")
os.system("rm "+mesh+".vtk")
os.system("meshtool convert -imsh="+mesh+" -omsh="+mesh+".vtk")

