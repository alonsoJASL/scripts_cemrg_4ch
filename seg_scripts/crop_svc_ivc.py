
import os
import argparse

from common import parse_txt_to_json, get_json_data, make_tmp
from common import configure_logging
logger = configure_logging(log_name=__name__)

from common import Labels
from process_handler import crop_svc_ivc

def main(args):
    """
    Crop SVC and IVC from points
    USAGE:

    python3 crop_svc_ivc.py [path_to_points] [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]

    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --SVC-label [SVC_label]
        --IVC-label [IVC_label]
        --RA-BP-label [RA-BP-label]
    """
    path2points = args.path_to_points
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    labels_file = args.labels_file
    C = Labels(filename=labels_file)
    if labels_file is None :
        logger.info("Creating Labels file")
        labels_file = os.path.join(path2points, "custom_labels.json")
        
        C.RPV1_label = args.RPV1_label
        C.SVC_label = args.SVC_label
        C.IVC_label = args.IVC_label
    
        C.save(filename=labels_file)

    crop_svc_ivc(path2points, path2ptsjson, path2originjson, labels_file)

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='To run: python3 crop_svc_ivc.py [path_to_points]')
    parser.add_argument("path_to_points")
    files_group = parser.add_argument_group("files")
    files_group.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    files_group.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    labels_group = parser.add_argument_group("labels")
    labels_group.add_argument("--labels-file", '-labels-file', type=str, required=False, default=None, help="Name of the json file containing custom labels")
    labels_group.add_argument("--SVC-label", "-SVC-label", type=int, required=False, default=13, help="Label for SVC")
    labels_group.add_argument("--IVC-label", "-IVC-label", type=int, required=False, default=14, help="Label for IVC")
    labels_group.add_argument("--RA-BP-label", "-RA-BP-label", type=int, required=False, default=5, help="Label for RA blood pool")
    args = parser.parse_args()

    main(args)