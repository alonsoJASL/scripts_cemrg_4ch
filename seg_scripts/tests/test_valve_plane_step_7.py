import os
import argparse

from seg_scripts.common import configure_logging
from seg_scripts.common import get_json_data

from seg_scripts.parameters import Parameters
import seg_scripts.FourChamberProcess as FOURCH

logger = configure_logging(log_name=__name__)
ZERO_LABEL = 0
USE_NEW_IMPLEMENTATION = False

def main(args) : 
    path2points = args.path_to_points
    path2originjson = args.origin_spacing_json

    origin_data = get_json_data(path2originjson)

    C = Parameters()
    fcp = FOURCH.FourChamberProcess(path2points, origin_data, C)
    fcp.save_seg_steps = True
    fcp.swap_axes = True
    fcp._is_mri = args.is_mri
    fcp.debug = True
    fcp.ref_image_mri = fcp.load_image_array('seg_s2a.nrrd') if fcp.is_mri else None

    seg_array = fcp.load_image_array(args.seg_name)
    seg_h_array = fcp.load_image_array(args.seg_name)

    la_myo_thresh = fcp.load_image_array(f'tmp/{args.la_myo_thres_file}')
    ra_myo_thresh = fcp.load_image_array(f'tmp/{args.ra_myo_thres_file}')

    seg_new_array, seg_new_i_array = fcp.valves_vein_rings(seg_array, seg_h_array, la_myo_thresh, ra_myo_thresh)

    fcp.save_image_array(seg_new_array, fcp.DIR('output_seg_s4j.nrrd'))
    fcp.save_image_array(seg_new_i_array, fcp.DIR('output_seg_s4i.nrrd'))
    

if __name__ == '__main__' :

    parser = argparse.ArgumentParser(description='To run: python3 valve_plane_step_8.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--seg-name", "-seg-name", type=str, default="seg_s4h.nrrd")
    parser.add_argument("--la-myo-thres-file", "-la-myo-file", type=str, default="LA_myo_thresh.nrrd")
    parser.add_argument("--ra-myo-thres-file", "-ra-myo-file", type=str, default="RA_myo_thresh.nrrd")
    # parser.add_argument("--outname", "-outname", type=str, default="seg_s4k.nrrd")
    parser.add_argument("--is-mri", "-is-mri", action="store_true", help="Flag to indicate if the image is MRI")
    args = parser.parse_args()
    main(args)
