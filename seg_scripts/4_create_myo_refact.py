import img
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import os
import argparse

from seg_scripts.common import configure_logging, initialize_parameters
logger = configure_logging(log_name=__name__)

from seg_scripts.parameters import Parameters
from process_handler import create_myocardium_refact

CONSTANTS = Parameters()
def main(args) :
    """
    Create myocardium from points 
    USAGE:

    python3 create_myo.py [path_to_points] [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]

    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --modify-label [key_label=value] [key_thickness=value]
    """    
    path2points, path2ptsjson, path2originjson, labels_file, thickness_file = initialize_parameters(args) 

    create_myocardium_refact(path2points, path2ptsjson, path2originjson, labels_file, thickness_file, is_mri=args.is_mri)
    

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]', usage=main.__doc__)
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--is-mri", "-mri", action="store_true", help="If the input is MRI")

    parameters_group = parser.add_argument_group("labels")
    parameters_group.add_argument("--labels-file", '-labels-file', type=str, required=False, default=None, help="Name of the json file containing custom labels")
    parameters_group.add_argument("--thickness-file", '-thickness-file', type=str, required=False, default=None, help="Name of the json file containing custom thickness")
    parameters_group.add_argument("--modify-label", "-modify-label", nargs='*', help="Modify label in the format key=value, e.g., --modify-label SVC_label=5 IVC_label=6 RA_BP_label=10")
    
    args = parser.parse_args()
    main(args)
