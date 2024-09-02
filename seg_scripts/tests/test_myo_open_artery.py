import os
import argparse

from seg_scripts.common import configure_logging, initialize_parameters
logger = configure_logging(log_name=__name__)

from seg_scripts.parameters import Parameters
from seg_scripts.FourChamberProcess import FourChamberProcess 

CONSTANTS = Parameters()
def main(args) :
    """
    
    """    
    path2points, path2ptsjson, path2originjson, files_dict = initialize_parameters(args) 
    labels_file = files_dict["labels_file"]
    thickness_file = files_dict["thickness_file"]
    vein_cutoff_file = files_dict["vein_cutoff_file"]

    fcp = FourChamberProcess(path2points, path2ptsjson, path2originjson, labels_file, thickness_file, vein_cutoff_file, is_mri=args.is_mri)
    C = fcp.CONSTANTS
    seg_name = 'seg_s3b.nrrd' if args.type == 'aorta' else 'seg_s3c.nrrd'
    seg_name_no_ext = os.path.splitext(seg_name)[0]

    input_seg_array = fcp.load_image_array(seg_name) 
    _ = fcp.myo_helper_open_artery(input_seg_array, cut_ratio=C.Aorta_open_cutoff, basename=seg_name_no_ext, suffix=args.type)


    

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]', usage=main.__doc__)
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--is-mri", "-mri", action="store_true", help="If the input is MRI")

    inputs_group = parser.add_argument_group('inputs', 'Input files')
    inputs_group.add_argument("--type", choices=['aorta', 'PA'], help="Identifier of segmentation file 9aorta or PArt")

    parameters_group = parser.add_argument_group("labels")
    parameters_group.add_argument("--labels-file", '-labels-file', type=str, required=False, default=None, help="Name of the json file containing custom labels")
    parameters_group.add_argument("--thickness-file", '-thickness-file', type=str, required=False, default=None, help="Name of the json file containing custom thickness")
    parameters_group.add_argument("--modify-label", "-modify-label", nargs='*', help="Modify label in the format key=value, e.g., --modify-label SVC_label=5 IVC_label=6 RA_BP_label=10")
    
    args = parser.parse_args()
    main(args)
