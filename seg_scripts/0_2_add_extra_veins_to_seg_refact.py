import os
import argparse

from seg_scripts.common import configure_logging
logger = configure_logging(log_name=__name__)

import seg_scripts.Labels as L
from process_handler import add_extra_veins_to_seg

CONSTANTS = L.Labels()
def main(args) :
    
    path2points = args.path_to_points
    origin_spacing_json = args.origin_spacing_json

    seg_name = args.seg_name

    C = L.Labels()
    labels_file = os.path.join(path2points, 'labels.json')

    C.save(filename=labels_file)
    add_extra_veins_to_seg(path2points, origin_spacing_json, seg_name, args.which_vein, labels_file, args.is_mri)
    
if __name__ == "__main__" : 
    parser = argparse.ArgumentParser(description='To run: python3 create_extra_veins.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--which-vein", "-which-vein", choices=['LSPV', 'LIPV', 'RSPV', 'RIPV', 'LAA'], default='LIPV', help="Which vein to create")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    
    optional_group = parser.add_argument_group('Optional arguments')
    optional_group.add_argument("--seg-name", "-seg-name", type=str, default="seg_corrected.nrrd")
    optional_group.add_argument("--is-mri", "-mri", action=argparse.BooleanOptionalAction, default=True, help="If the image is an MRI image")

    args = parser.parse_args()
    main(args)