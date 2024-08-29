import argparse
import os
import SimpleITK as sitk
import numpy as np
import json

import cut_labels as cuts

from seg_scripts.parameters import Parameters
from seg_scripts.common import configure_logging, initialize_parameters
logger = configure_logging(log_name=__name__)

from process_handler import cut_vessels

def main(args):
    path2points, _, _, labels_file, thickness_file = initialize_parameters(args) 
    
    cut_percent = args.cut_percentage

    vc_json_path = os.path.join(path2points, args.vc_joint_json)
    if not os.path.exists(vc_json_path):
        logger.info("Creating vc joint json file")
        vc_dict = {'SVC': 0.2, 'IVC': 0.2} 
        with open(vc_json_path, 'w') as f:
            json.dump(vc_dict, f)

    cut_vessels(path2points, args.vc_joint_json, args.seg_name, labels_file, thickness_file, cut_percent)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To run: python3 cut_vessels.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--seg-name", "-seg-name", type=str, default="seg_s2a.nrrd") 
    
    files_group = parser.add_argument_group('files_group', 'File names')
    files_group.add_argument("--vc-joint-json", "-vc-joint", type=str, default="vc_joint.json")
    files_group.add_argument("--labels-file", "-labels-file", type=str, required=False, default=None, help="Name of the json file containing custom labels")
    files_group.add_argument("--thickness-file", "-thickness-file", type=str, required=False, default=None, help="Name of the json file containing custom thickness")

    optional_group = parser.add_argument_group('optional_group', 'Optional arguments')
    optional_group.add_argument("--modify-label", "-modify-label", nargs='*', help="Modify label in the format key=value, e.g., --modify-label SVC_label=5 IVC_label=6 RA_BP_label=10")
    optional_group.add_argument("--cut-percentage", "-cut-percentage", type=float, default=0.75, help="Percentage of the vessel to be cut")

    args = parser.parse_args()
    main(args)
