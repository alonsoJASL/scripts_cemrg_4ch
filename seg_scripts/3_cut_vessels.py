import argparse
import SimpleITK as sitk
import numpy as np
import json

import cut_labels

parser = argparse.ArgumentParser(description='To run: python3 cut_vessels.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()


path2points = args.path_to_points

### Labels

LV_BP_label = 1
LV_myo_label = 2
RV_BP_label = 3
LA_BP_label = 4
RA_BP_label = 5
Ao_BP_label = 6
PArt_BP_label = 7
LPV1_label = 8
LPV2_label = 9
RPV1_label = 10
RPV2_label = 11
LAA_label = 12
SVC_label = 13
IVC_label = 14

vc_cutoff = json.load(open(f"{path2points}/vc_joint.json"))

# #### Aorta

cut_labels.cut_vessels(path2image      = f"{path2points}/seg_s2a.nrrd", 
            label_to_be_cut  = Ao_BP_label, 
            label_in_contact = LV_BP_label, 
            cut_percentage   = 0.75, 
            save_filename    = f"{path2points}/seg_s2a_aorta.nrrd")

#### PA 

cut_labels.cut_vessels(path2image      = f"{path2points}/seg_s2a_aorta.nrrd", 
            label_to_be_cut  = PArt_BP_label, 
            label_in_contact = RV_BP_label, 
            cut_percentage   = 0.75, 
            save_filename    = f"{path2points}/seg_s2a_PA.nrrd")


## For the venae cavae we can use the same method but setting the voxels below the threshold to the RA label 

## SVC 

cut_labels.reassign_vessels(path2image      = f"{path2points}/seg_s2a_PA.nrrd", 
            label_to_be_cut  = SVC_label, 
            label_in_contact = RA_BP_label, 
            cut_percentage   = vc_cutoff["SVC"], 
            save_filename    = f"{path2points}/seg_s2a_SVC.nrrd")

#### IVC 

cut_labels.reassign_vessels(path2image      = f"{path2points}/seg_s2a_SVC.nrrd", 
            label_to_be_cut  = IVC_label, 
            label_in_contact = RA_BP_label, 
            cut_percentage   = vc_cutoff["IVC"], 
            save_filename    = f"{path2points}/seg_s2f.nrrd")