import argparse
import os

from seg_scripts.parameters import Parameters

from seg_scripts.common import configure_logging, initialize_parameters
logger = configure_logging(log_name=__name__)

from process_handler import create_svc_ivc

CONSTANTS = Parameters()

def main(args) : 
    """
    Create SVC and IVC from points
    USAGE: 
    python3 create_svc_ivc.py [path_to_points] [--origin-spacing-json [origin_spacing_json]] [--seg-name [seg_name]] [--output-name [output_name]] [OPTIONS]
    
    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --modify-label [key=value]
    """
    path2points, _, path2originjson, labels_file, _ = initialize_parameters(args) 
    
    seg_name = args.seg_name
    output_name = "seg_s2a.nrrd"

    create_svc_ivc(path2points, path2originjson, seg_name, output_name, labels_file)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To run: python3 create_svc_ivc.py [path_to_points]', usage=main.__doc__)
    parser.add_argument("path_to_points")
    file_group = parser.add_argument_group('file_group', 'File names')
    file_group.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")	#
    file_group.add_argument("--seg-name", "-seg-name", type=str, default="seg_corrected.nrrd")
    
    labels_group = parser.add_argument_group('labels_group', 'Labels that can be modified')
    labels_group.add_argument("--labels-file", "-labels-file", type=str, required=False, default=None, help="Name of the json file containing custom labels")
    labels_group.add_argument("--modify-label", "-modify-label", nargs='*', help="Modify label in the format key=value, e.g., --modify-label RPV1_label=5 SVC_label=6")
    args = parser.parse_args()
    main(args)

    