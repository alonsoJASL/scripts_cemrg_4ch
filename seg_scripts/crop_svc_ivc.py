
import os
import argparse

from seg_scripts.common import configure_logging, initialize_parameters
logger = configure_logging(log_name=__name__)

from seg_scripts.parameters import Parameters
from process_handler import crop_svc_ivc

CONSTANTS = Parameters()

def main(args):
    """
    Crop SVC and IVC from points
    USAGE:

    python3 crop_svc_ivc.py [path_to_points] [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]

    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --modify-label [key=value]
    """
    path2points, path2ptsjson, path2originjson, labels_file, _ = initialize_parameters(args) 

    crop_svc_ivc(path2points, path2ptsjson, path2originjson, labels_file)

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='To run: python3 crop_svc_ivc.py [path_to_points]', usage=main.__doc__)
    parser.add_argument("path_to_points")
    files_group = parser.add_argument_group("files")
    files_group.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    files_group.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    labels_group = parser.add_argument_group("labels")
    labels_group.add_argument("--labels-file", '-labels-file', type=str, required=False, default=None, help="Name of the json file containing custom labels")
    labels_group.add_argument("--modify-label", "-modify-label", nargs='*', help="Modify label in the format key=value, e.g., --modify-label SVC_label=5 IVC_label=6 RA_BP_label=10")
    args = parser.parse_args()

    main(args)