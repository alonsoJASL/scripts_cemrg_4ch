import img 
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import argparse
import os

import Labels as L
from common import parse_txt_to_json, get_json_data
from common import configure_logging
logger = configure_logging(log_name=__name__)

from process_handler import create_svc_ivc

CONSTANTS = L.Labels()

def main(args) : 
    """
    Create SVC and IVC from points
    USAGE: 

    python3 create_svc_ivc.py [path_to_points] [--origin-spacing-json [origin_spacing_json]] [--seg-name [seg_name]] [--output-name [output_name]] [OPTIONS] 
    
    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --RPV1_label [RPV1_label] 
        --SVC_label [SVC_label] 
        --IVC_label [IVC_label]
    """
    path2points = args.path_to_points
    path2originjson = args.origin_spacing_json
    seg_name = args.seg_name
    output_name = "seg_s2a.nrrd"

    labels_file = args.labels_file
    C = L.Labels(filename=labels_file)
    if labels_file is None :
        logger.info("Creating labels file")
        labels_file = os.path.join(path2points, "custom_labels.json")

        C.RPV1_label = args.RPV1_label
        C.SVC_label = args.SVC_label
        C.IVC_label = args.IVC_label

        C.save(filename=labels_file)

    create_svc_ivc(path2points, path2originjson, seg_name, output_name, labels_file)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To run: python3 create_svc_ivc.py [path_to_points]', usage=main.__doc__)
    parser.add_argument("path_to_points")
    file_group = parser.add_argument_group('file_group', 'File names')
    file_group.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")	#
    file_group.add_argument("--seg-name", "-seg-name", type=str, default="seg_corrected.nrrd")
    labels_group = parser.add_argument_group('labels_group', 'Labels that can be modified')
    labels_group.add_argument("--labels-file", "-labels-file", type=str, required=False, default=None, help="Name of the json file containing custom labels")
    labels_group.add_argument("--RPV1_label", type=int, required=False, default=CONSTANTS.RPV1_label, help="Label of the right pulmonary vein 1")
    labels_group.add_argument("--SVC_label", type=int, required=False, default=CONSTANTS.SVC_label, help="Label of the Superior Vena Cava")
    labels_group.add_argument("--IVC_label", type=int, required=False, default=CONSTANTS.IVC_label, help="Label of the Inferior Vena Cava")
    args = parser.parse_args()
    main(args)

    