import argparse

from seg_scripts.parameters import Parameters
from seg_scripts.common import configure_logging, initialize_parameters
logger = configure_logging(log_name=__name__)

from process_handler import cut_vessels

def main(args):
    path2points, _, _, files_dict = initialize_parameters(args) 
    labels_file = files_dict["labels_file"]
    thickness_file = files_dict["thickness_file"]
    vein_cutoff_file = files_dict["vein_cutoff_file"]

    cut_vessels(path2points, args.seg_name, labels_file, thickness_file, vein_cutoff_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To run: python3 cut_vessels.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--seg-name", "-seg-name", type=str, default="seg_s2a.nrrd") 
    
    files_group = parser.add_argument_group('files_group', 'File names')
    files_group.add_argument("--labels-file", "-labels-file", type=str, required=False, default=None, help="Name of the json file containing custom labels")
    files_group.add_argument("--thickness-file", "-thickness-file", type=str, required=False, default=None, help="Name of the json file containing custom thickness")
    files_group.add_argument("--vein-cutoff-file", "-vein-cutoff-file", type=str, default=None, help="Name of the json file containing vein cutoff")

    optional_group = parser.add_argument_group('optional_group', 'Optional arguments')
    optional_group.add_argument("--modify-label", "-modify-label", nargs='*', help="Modify label in the format key=value, e.g., --modify-label SVC_label=5 IVC_label=6 RA_BP_label=10")

    args = parser.parse_args()
    main(args)
