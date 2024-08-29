import os
import argparse

from seg_scripts.common import configure_logging
from seg_scripts.common import get_json_data

import seg_scripts.Labels as L
import seg_scripts.FourChamberProcess as FOURCH

logger = configure_logging(log_name=__name__)
ZERO_LABEL = 0
USE_NEW_IMPLEMENTATION = False

def main(args) : 
    path2points = args.path_to_points
    path2originjson = args.origin_spacing_json

    origin_data = get_json_data(path2originjson)

    C = L.Labels() 
    fcp = FOURCH.FourChamberProcess(path2points, origin_data, C)
    fcp.save_seg_steps = True
    fcp.swap_axes = True
    fcp._is_mri = args.is_mri
    fcp.debug = True
    fcp.ref_image_mri = fcp.load_image_array('seg_s2a.nrrd') if fcp.is_mri else None

    seg_array = fcp.load_image_array(args.seg_name)
    la_bp_thresh = fcp.load_image_array(f'TMP/{args.la_bp_thres_file}')
    ra_bp_distmap = fcp.load_image_array(f'TMP/{args.ra_bp_distm_file}')

    seg_new_array = fcp.valves_planes(seg_array, la_bp_thresh, ra_bp_distmap) 

    fcp.save_image_array(seg_new_array, fcp.DIR(args.outname))
    

if __name__ == '__main__' :

    parser = argparse.ArgumentParser(description='To run: python3 valve_plane_step_8.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--seg-name", "-seg-name", type=str, default="seg_s4j.nrrd")
    parser.add_argument("--la-bp-thres-file", "-la-bp-file", type=str, default="LA_BP_thresh.nrrd")
    parser.add_argument("--ra-bp-distm-file", "-ra-bp-file", type=str, default="RA_BP_DistMap.nrrd")
    parser.add_argument("--outname", "-outname", type=str, default="seg_s4k.nrrd")
    parser.add_argument("--is-mri", "-is-mri", action="store_true", help="Flag to indicate if the image is MRI")
    args = parser.parse_args()
    main(args)
