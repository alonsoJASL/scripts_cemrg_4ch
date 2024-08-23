import argparse
import os
import SimpleITK as sitk
import numpy as np
import json

import cut_labels as cuts

import seg_scripts.Labels as L
from seg_scripts.common import parse_txt_to_json, get_json_data
from seg_scripts.common import configure_logging
logger = configure_logging(log_name=__name__)

from process_handler import cut_vessels

def main(args):
    path2points = args.path_to_points
    
    C = L.Labels(filename=args.labels_file)
    if args.labels_file is None:
        logger.info("Creating labels file")
        labels_file = os.path.join(path2points, "custom_labels.json")
        C.save(filename=labels_file)
    
    cut_percent = args.cut_percentage

    cut_vessels(path2points, args.vc_joint_json, args.seg_name, labels_file, cut_percent)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To run: python3 cut_vessels.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--seg-name", "-seg-name", type=str, default="seg_s2a.nrrd") 
    files_group = parser.add_argument_group('files_group', 'File names')
    files_group.add_argument("--vc-joint-json", "-vc-joint", type=str, default="vc_joint.json")
    files_group.add_argument("--labels-file", "-labels-file", type=str, required=False, default=None, help="Name of the json file containing custom labels")
    optional_group = parser.add_argument_group('optional_group', 'Optional arguments')
    optional_group.add_argument("--cut-percentage", "-cut-percentage", type=float, default=0.75, help="Percentage of the vessel to be cut")

    args = parser.parse_args()
    main(args)
