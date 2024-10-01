

import argparse
import os
import json

from seg_scripts.common import configure_logging, add_file_handler, initialize_parameters
logger = configure_logging(log_name=__name__)

from seg_scripts.FourChamberProcess import FourChamberProcess
from seg_scripts.parameters import Parameters
import seg_scripts.process_handler as process 
# ----------------------------------------------------------------------------------------------
# Define the wall thickness
# ----------------------------------------------------------------------------------------------

def manage_labels_file(args) : 
    labels_file = args.labels_file
    C = L.Labels(filename=labels_file)
    if labels_file is None:
        labels_file = os.path.join(args.base_dir, "custom_labels.json")
        C.save(filename=labels_file)
    
    return C, labels_file

def docker_origin_and_spacing(args, help=False) : 
    """
    Find origin and spacing of the file. You can call this through 'origin' and 'spacing' modes.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch origin [--seg-name [seg_name]] --dicom-dir [dicom_dir] [--output-file [output_file]]
    
    ARGUMENTS:
        path2points: path to the main directory
        seg_name: name of the segmentation file
        dicom_dir: name of the dicom directory
        output_file: name of the output file
    """

    from seg_scripts.process_handler import get_origin_and_spacing
    if(help) : 
        print(docker_origin_and_spacing.__doc__)
        return
    path2points = args.base_dir
    seg_name = args.seg_name if args.seg_name != "" else "seg_corrected.nrrd"
    dicom_dir = args.dicom_dir
    output_file = args.output_file

    get_origin_and_spacing(path2points, seg_name, dicom_dir, output_file)

def docker_pad_image(args, help=False) :
    """
    Pad image. You can call this through 'pad' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch pad --origin-spacing-json [origin_spacing_json] --seg-name [seg_name] --output-name [output_name] --pad-size [pad_size] --is-mri
    
    ARGUMENTS:
        path2points:           path to the main directory
        origin_spacing_json:   name of the json file containing the origin and spacing
        seg_name:              name of the segmentation file
        output_name:           name of the output file
        pad_size:              size of the padding
        is_mri:                if the input is MRI
    """

    from seg_scripts.process_handler import pad_image
    if(help) : 
        print(docker_pad_image.__doc__)
        return
    
    with open(args.origin_spacing_json, 'r') as f:
        loaded_origin_spacing = json.load(f)

    params = Parameters()
    fourch = FourChamberProcess(path2points=args.path_to_points, origin_spacing=loaded_origin_spacing, CONSTANTS=params)
    fourch.is_mri = args.is_mri
    outname = args.seg_name if args.output_name == '' else args.output_name

    pad_image(fourch, args.origin_spacing_json, args.seg_name, outname, pad_size=args.pad_size)

def docker_create_cylinders(args, help=False) :
    """
    Create cylinders. You can call this through 'cylinders' mode.

    USAGE:
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch cylinders [--seg-name [seg_name]] --points-json [points_json] --origin-spacing-json [origin_spacing_json] [--create-cylinder SVC IVC Ao PArt] [--physical-points] [--mm]

    ARGUMENTS:
        path2points:            path to the main directory
        seg_name:               name of the segmentation file (default: seg_corrected.nrrd)
        points_json:            name of the json file containing the points
        origin_spacing_json:    name of the json file containing the origin and spacing
        create_cylinder:        list of cylinders to create: SVC, IVC, Ao, or PArt. Default: [SVC, IVC]
        physical_points:        points file is in physical coordinates 
        mm:                     calculate cylinder with mm units 
    """

    if(help) :
        print(docker_create_cylinders.__doc__)
        return

    which_cylinders = []
    for entry in args.create_cylinder:
        lower_entry = entry.lower()
        if lower_entry in ['svc', 'ivc', 'ao', 'part']:
            which_cylinders.append(lower_entry)
        else:
            logger.error(f"Invalid cylinder name: {entry}. Skipping...")
    
    if which_cylinders == []:
        logger.error("No valid cylinders selected. Exiting...") 
        return
    
    path2points = args.base_dir
    path2pointsjson = args.points_json
    path2originjson = args.origin_spacing_json

    seg_name = args.seg_name if args.seg_name != "" else "seg_corrected.nrrd"
    seg_name += ".nrrd" if not seg_name.endswith(".nrrd") else ""
    physical_points = args.physical_points

    process.create_cylinders_general(path2points, path2pointsjson, path2originjson, which_cylinders, 
                            segmentation_name=seg_name, is_mm=args.mm, world_coords=physical_points)


def docker_create_svc_ivc(args, help=False) : 
    """
    Create SVC and IVC. You can call this through 'svc_ivc' mode.

    USAGE:
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch svc_ivc [--seg-name [seg_name]] --origin-spacing-json JSON_FILE [--labels-file JSON_FILE] [--modify-label [key=value]]

    ARGUMENTS:
        path2points:            path to the main directory
        seg_name:               name of the segmentation file
        origin_spacing_json:    name of the json file containing the origin and spacing
        labels_file:            name of the json file containing the labels
        modify_label:           modify label in the format key=value, e.g., --modify-label RPV1_label=5 SVC_label=6
        
    """

    if help:
        print(docker_create_svc_ivc.__doc__)
        return

    path2points, _, path2originjson, const = initialize_parameters(args)

    seg_name = args.seg_name if args.seg_name != "" else "seg_corrected.nrrd"
    output_name = "seg_s2a.nrrd"

    process.create_svc_ivc(path2points, path2originjson, seg_name, output_name, const["labels"])

def docker_cut_vessels(args, help=False) :
    """
    Cut vessels. You can call this through 'cut' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch cut [--seg-name [seg_name]] [OPTIONS]

    ARGUMENTS:
        path_to_points: Path to the folder containing the points
        seg_name: Name of the segmentation file (default: seg_s2a.nrrd)

        --modify-label [key1=value1 key2=value2 ...] Modify label in the format key=value


    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --thickness-file [thickness_file]
        --vein-cutoff-file [vein_cutoff_file]
    """

    if(help) : 
        print(docker_cut_vessels.__doc__)
        return

    path2points, _, _, const = initialize_parameters(args)
    seg_name = args.seg_name if args.seg_name != "" else "seg_s2a.nrrd"

    process.cut_vessels(path2points, seg_name, const["labels"], const["thickness"], const["vein_cutoff"])


def docker_create_myo(args, help=False) :
    """
    Create myocardium. You can call this through 'myo' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch myo [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]

    ARGUMENTS;
        path2points: path to the main directory
        --points-json [points_json]: name of the json file containing the seed points
        --origin-spacing-json [origin_spacing_json]: name of the json file containing the origin and spacing

    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --modify-label [key_label=value] [key_thickness=value]
    """

    if(help) : 
        print(docker_create_myo.__doc__)
        return
    
    path2points, path2ptsjson, path2originjson, const = initialize_parameters(args)
    process.create_myocardium_refact(path2points, path2ptsjson, path2originjson, const["labels"], const["thickness"], const["vein_cutoff"], is_mri=args.is_mri)


def docker_create_valve_planes(args, help=False) :
    """
    Create valve planes. You can call this through 'valve_planes' mode.

    USAGE:
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch valve_planes [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]

    ARGUMENTS:
        path2points: path to the main directory
        --points-json: name of the json file containing the points
        --origin-spacing-json: name of the json file containing the origin and spacing

    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --thickness-file [thickness_file]
        --modify-label [key_label=value] [key_thickness=value]
    """
    
    if(help) : 
        print(docker_create_valve_planes.__doc__)
        return
    
    path2points, path2ptsjson, path2originjson, const = initialize_parameters(args)
    process.create_valve_planes_refact(path2points, path2ptsjson, path2originjson, const["labels"], const["thickness"], is_mri=args.is_mri)

def docker_clean_seg(args, help=False) :
    """
    Clean segmentation from points. You can call this through 'clean_seg' mode.

    USAGE:
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch clean_seg [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]

    ARGUMENTS:
        path2points: path to the main directory
        --points-json [points_json]: name of the json file containing the points
        --origin-spacing-json [origin_spacing_json]: name of the json file containing the origin and spacing

    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        --thickness-file [thickness_file]
        --modify-label [key1=value1] [key2=value2] ... [keyN=valueN]
    """

    if(help) : 
        print(docker_clean_seg.__doc__)
        return
    
    path2points, path2ptsjson, path2originjson, const = initialize_parameters(args)
    process.clean_segmentation_refact(path2points, path2ptsjson, path2originjson, const["labels"], const["thickness"], is_mri=args.is_mri)

def main(args):
    """
    Docker entrypoint: 

    USAGE:

        docker run --rm --volume=[path2points]:/data cermg/seg-4ch MODE [help] [options]

    path2points: path to the main directory

    Choose MODE from the following list:
        - origin or spacing (either do the same thing)
        - cylinders
        - svc_ivc
        - slicers
        - crop
        - myo
        - valve_planes
        - clean_seg
        - labels

    Use the option 'help' to get the help page specific to each mode.
    """

    myhelp = args.help
    
    if args.mode == 'origin' or args.mode == 'spacing':
        docker_origin_and_spacing(args, help=myhelp)
    if args.mode == 'pad':
        docker_pad_image(args, help=myhelp)
    elif args.mode == 'cylinders':
        docker_create_cylinders(args, help=myhelp)
    elif args.mode == 'svc_ivc':
        docker_create_svc_ivc(args, help=myhelp)
    elif args.mode == 'cut' or args.mode == 'cut_vessels':
        docker_cut_vessels(args, help=myhelp)
    elif args.mode == 'myo':
        docker_create_myo(args, help=myhelp)
    elif args.mode == 'valve_planes':
        docker_create_valve_planes(args, help=myhelp)
    elif args.mode == 'clean_seg':
        docker_clean_seg(args, help=myhelp)
    elif args.mode == 'params':
        CONSTANTS = Parameters()
        CONSTANTS.print_all()

if __name__ == '__main__' :
    my_choices = ['origin', 'pad', 'spacing', 'cylinders', 'svc_ivc', 'cut', 'cut_vessels', 'myo', 'valve_planes', 'clean_seg', 'params']

    parser = argparse.ArgumentParser(description='Docker entrypoint', usage=main.__doc__)
    parser.add_argument("mode", choices=my_choices, help="Mode of operation")
    parser.add_argument("help", nargs='?', type=bool, default=False, help="Help page specific to each mode")

    common_group = parser.add_argument_group('Common arguments two or more modes')
    common_group.add_argument("--seg-name", "-seg-name", type=str, required=False, default="", help="Name of the segmentation file")
    common_group.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    common_group.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")

    params_group = parser.add_argument_group('Parameters arguments')
    params_group.add_argument("--modify-label", "-modify-label", nargs='*', help="Modify label in the format key=value, e.g., --modify-label RPV1_label=5 SVC_label=6")
    params_group.add_argument("--labels-file", "-labels-file", type=str, required=False, default=None, help="Name of the json file containing the labels")
    params_group.add_argument("--thickness-file", "-thickness-file", type=str, required=False, default=None, help="Name of the json file containing the thickness")
    params_group.add_argument("--vein-cutoff-file", "-labels-vein-cutoff", type=str, required=False, default=None, help="Name of the json file containing the vein-cutoff")

    cylinders_group = parser.add_argument_group('Cylinders arguments')
    cylinders_group.add_argument('--create-cylinder', '-create', nargs='*', default=['SVC', 'IVC'])
    cylinders_group.add_argument("--physical-points", action='store_true', help="Points file is in physical coordinates")
    cylinders_group.add_argument("--mm", "-mm", action='store_true', help="Calculate cylinder with mm units")

    os_group = parser.add_argument_group('Origin and spacing arguments')
    os_group.add_argument("--dicom-dir", "-dicom-dir", type=str, required=False, default="ct", help="Name of the dicom directory")
    os_group.add_argument("--output-file", "-output-file", type=str, required=False, default="", help="Name of the output file")

    dev_group = parser.add_argument_group('Development arguments')
    dev_group.add_argument("-dir", "--base-dir", type=str, required=False, default="/data", help="Base directory") # this is path2points
    dev_group.add_argument("-debug", "--debug", action="store_true", help="Debug outputs")
    
    args = parser.parse_args()
    main(args)