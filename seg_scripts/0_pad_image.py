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
from seg_scripts.FourChamberProcess import FourChamberProcess
from process_handler import pad_image

CONSTANTS = Parameters()
def main(args) :
    with open(args.origin_spacing_json, 'r') as f:
        loaded_origin_spacing = json.load(f)
    params = Parameters()
    fourch = FourChamberProcess(path2points=args.path_to_points, origin_spacing=loaded_origin_spacing, CONSTANTS=params)
    fourch.is_mri = args.is_mri
    outname = args.seg_name if args.output_name == '' else args.output_name

    pad_image(fourch, args.origin_spacing_json, args.seg_name, outname, pad_size=args.pad_size)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]', usage=main.__doc__)
    parser.add_argument("path_to_points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--seg-name", "-seg-name", type=str, help="Name of the segmentation file")
    parser.add_argument("--output-name", "-output-name", type=str, default='', help="Name of the output file")
    parser.add_argument("--pad-size", "-pad-size", type=int, help="Size of the padding")
    parser.add_argument("--is-mri", "-mri", action="store_true", help="If the input is MRI")
    
    args = parser.parse_args()
    main(args)
