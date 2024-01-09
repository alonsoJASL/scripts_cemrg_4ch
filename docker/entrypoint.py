

import argparse
import os

from seg_scripts.common import configure_logging, add_file_handler
logger = configure_logging(log_name=__name__)

import seg_scripts.Labels as L
# ----------------------------------------------------------------------------------------------
# Define the wall thickness
# ----------------------------------------------------------------------------------------------
CONSTANTS = L.Labels()

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

def docker_create_cylinders(args, help=False) :
    """
    Create cylinders. You can call this through 'cylinders' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch cylinders [--seg-name [seg_name]] --points-json [points_json] --origin-spacing-json [origin_spacing_json]

    ARGUMENTS:
        path2points: path to the main directory
        seg_name: name of the segmentation file
        points_json: name of the json file containing the points
        origin_spacing_json: name of the json file containing the origin and spacing
    """

    from seg_scripts.process_handler import create_cylinders
    if(help) : 
        print(docker_create_cylinders.__doc__)
        return

    path2points = args.base_dir
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json
    seg_name = args.seg_name if args.seg_name != "" else "seg_corrected.nrrd"

    create_cylinders(path2points, path2ptsjson, path2originjson, seg_name)

def docker_create_svc_ivc(args, help=False) :
    """
    Create SVC and IVC. You can call this through 'svc_ivc' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch svc_ivc [--seg-name [seg_name]] --points-json [points_json] --origin-spacing-json [origin_spacing_json]

    ARGUMENTS:
        path2points: path to the main directory
        seg_name: name of the segmentation file
        points_json: name of the json file containing the points
        origin_spacing_json: name of the json file containing the origin and spacing
    """
    from seg_scripts.process_handler import create_svc_ivc
    if(help) : 
        print(docker_create_svc_ivc.__doc__)
        return

    _, labels_file = manage_labels_file(args)

    path2points = args.base_dir
    path2originjson = args.origin_spacing_json
    seg_name = args.seg_name if args.seg_name != "" else "seg_corrected.nrrd"

    create_svc_ivc(path2points, path2originjson, seg_name, "seg_s2a.nrrd", labels_file)

def docker_create_slicers(args, help=False) :
    """
    Create slicers. You can call this through 'slicers' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch slicers [--seg-name [seg_name]] --points-json [points_json] --origin-spacing-json [origin_spacing_json]

    ARGUMENTS:
        path2points: path to the main directory
        seg_name: name of the segmentation file
        points_json: name of the json file containing the points
        origin_spacing_json: name of the json file containing the origin and spacing
    """

    from seg_scripts.process_handler import create_slicers
    if(help) : 
        print(docker_create_slicers.__doc__)
        return

    path2points = args.base_dir
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json
    seg_name = args.seg_name if args.seg_name != "" else "seg_corrected.nrrd"

    create_slicers(path2points, path2ptsjson, path2originjson, seg_name)

def docker_crop_svc_ivc(args, help=False) :
    """
    Crop SVC and IVC. You can call this through 'crop' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch crop --points-json [points_json] --origin-spacing-json [origin_spacing_json]
    
    ARGUMENTS:
        path2points: path to the main directory
        points_json: name of the json file containing the points
        origin_spacing_json: name of the json file containing the origin and spacing
    """
    from seg_scripts.process_handler import crop_svc_ivc
    if(help) : 
        print(docker_crop_svc_ivc.__doc__)
        return

    _, labels_file = manage_labels_file(args)

    path2points = args.base_dir
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    crop_svc_ivc(path2points, path2ptsjson, path2originjson, labels_file)

def docker_create_myo(args, help=False) :
    """
    Create myocardium. You can call this through 'myo' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch myo --points-json [points_json] --origin-spacing-json [origin_spacing_json]
    
    ARGUMENTS:
        path2points: path to the main directory
        points_json: name of the json file containing the points
        origin_spacing_json: name of the json file containing the origin and spacing
    """

    from seg_scripts.process_handler import create_myocardium
    if(help) : 
        print(docker_create_myo.__doc__)
        return

    _, labels_file = manage_labels_file(args)

    path2points = args.base_dir
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    create_myocardium(path2points, path2ptsjson, path2originjson, labels_file)


def docker_create_valve_planes(args, help=False) :
    """
    Create valve planes. You can call this through 'valve_planes' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch valve_planes --points-json [points_json] --origin-spacing-json [origin_spacing_json]
    
    ARGUMENTS:
        path2points: path to the main directory
        points_json: name of the json file containing the points
        origin_spacing_json: name of the json file containing the origin and spacing
    """
    
    from seg_scripts.process_handler import create_valve_planes
    if(help) : 
        print(docker_create_valve_planes.__doc__)
        return

    _, labels_file = manage_labels_file(args)

    path2points = args.base_dir
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    create_valve_planes(path2points, path2ptsjson, path2originjson, labels_file)

def docker_clean_seg(args, help=False) :
    """
    Clean segmentation. You can call this through 'clean_seg' mode.

    USAGE: 
        docker run --rm --volume=[path2points]:/data cermg/seg-4ch clean_seg --origin-spacing-json [origin_spacing_json] --points-json [points_json]
    
    ARGUMENTS:
        path2points: path to the main directory
        origin_spacing_json: name of the json file containing the origin and spacing
        points_json: name of the json file containing the points
    """

    from seg_scripts.process_handler import clean_segmentation
    if(help) : 
        print(docker_clean_seg.__doc__)
        return

    _, labels_file = manage_labels_file(args)

    path2points = args.base_dir
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    clean_segmentation(path2points, path2ptsjson, path2originjson, labels_file)

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
    elif args.mode == 'cylinders':
        docker_create_cylinders(args, help=myhelp)
    elif args.mode == 'svc_ivc':
        docker_create_svc_ivc(args, help=myhelp)
    elif args.mode == 'slicers':
        docker_create_slicers(args, help=myhelp)
    elif args.mode == 'crop':
        docker_crop_svc_ivc(args, help=myhelp)
    elif args.mode == 'myo':
        docker_create_myo(args, help=myhelp)
    elif args.mode == 'valve_planes':
        docker_create_valve_planes(args, help=myhelp)
    elif args.mode == 'clean_seg':
        docker_clean_seg(args, help=myhelp)
    elif args.mode == 'labels':
        CONSTANTS.print_label_explanation()

if __name__ == '__main__' :
    my_choices = ['origin', 'spacing', 'cylinders', 'svc_ivc', 'slicers', 'crop', 'myo', 'valve_planes', 'clean_seg', 'labels']

    parser = argparse.ArgumentParser(description='Docker entrypoint', usage=main.__doc__)
    parser.add_argument("mode", choices=my_choices, help="Mode of operation")
    parser.add_argument("help", nargs='?', type=bool, default=False, help="Help page specific to each mode")
    parser.add_argument("--labels-file", "-labels-file", type=str, required=False, default=None, help="Name of the json file containing the labels")

    common_group = parser.add_argument_group('Common arguments two or more modes')
    common_group.add_argument("--seg-name", "-seg-name", type=str, required=False, default="", help="Name of the segmentation file")
    common_group.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    common_group.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")

    os_group = parser.add_argument_group('Origin and spacing arguments')
    os_group.add_argument("--dicom-dir", "-dicom-dir", type=str, required=False, default="ct", help="Name of the dicom directory")
    os_group.add_argument("--output-file", "-output-file", type=str, required=False, default="", help="Name of the output file")

    dev_group = parser.add_argument_group('Development arguments')
    dev_group.add_argument("-dir", "--base-dir", type=str, required=False, default="/data", help="Base directory") # this is path2points
    # dev_group.add_argument("-local", "--local", action="store_true", help="Run locally")

    labels_group = parser.add_argument_group('Labels (not all used in all modes)')
    labels_group.add_argument("--LV_BP_label", metavar='INT', help="LV_BP_label", default=CONSTANTS.LV_BP_label) 
    labels_group.add_argument("--LV_myo_label", metavar='INT', help="LV_myo_label", default=CONSTANTS.LV_myo_label) 
    labels_group.add_argument("--RV_BP_label", metavar='INT', help="RV_BP_label", default=CONSTANTS.RV_BP_label) 
    labels_group.add_argument("--LA_BP_label", metavar='INT', help="LA_BP_label", default=CONSTANTS.LA_BP_label) 
    labels_group.add_argument("--RA_BP_label", metavar='INT', help="RA_BP_label", default=CONSTANTS.RA_BP_label) 
    labels_group.add_argument("--Ao_BP_label", metavar='INT', help="Ao_BP_label", default=CONSTANTS.Ao_BP_label) 
    labels_group.add_argument("--PArt_BP_label", metavar='INT', help="PArt_BP_label", default=CONSTANTS.PArt_BP_label) 
    labels_group.add_argument("--LPV1_label", metavar='INT', help="LPV1_label", default=CONSTANTS.LPV1_label) 
    labels_group.add_argument("--LPV2_label", metavar='INT', help="LPV2_label", default=CONSTANTS.LPV2_label) 
    labels_group.add_argument("--RPV1_label", metavar='INT', help="RPV1_label", default=CONSTANTS.RPV1_label) 
    labels_group.add_argument("--RPV2_label", metavar='INT', help="RPV2_label", default=CONSTANTS.RPV2_label) 
    labels_group.add_argument("--LAA_label", metavar='INT', help="LAA_label", default=CONSTANTS.LAA_label) 
    labels_group.add_argument("--SVC_label", metavar='INT', help="SVC_label", default=CONSTANTS.SVC_label) 
    labels_group.add_argument("--IVC_label", metavar='INT', help="IVC_label", default=CONSTANTS.IVC_label) 
    labels_group.add_argument("--LV_neck_label", metavar='INT', help="LV_neck_label", default=CONSTANTS.LV_neck_label) 
    labels_group.add_argument("--RV_myo_label", metavar='INT', help="RV_myo_label", default=CONSTANTS.RV_myo_label) 
    labels_group.add_argument("--LA_myo_label", metavar='INT', help="LA_myo_label", default=CONSTANTS.LA_myo_label) 
    labels_group.add_argument("--RA_myo_label", metavar='INT', help="RA_myo_label", default=CONSTANTS.RA_myo_label) 
    labels_group.add_argument("--Ao_wall_label", metavar='INT', help="Ao_wall_label", default=CONSTANTS.Ao_wall_label) 
    labels_group.add_argument("--PArt_wall_label", metavar='INT', help="PArt_wall_label", default=CONSTANTS.PArt_wall_label) 
    labels_group.add_argument("--MV_label", metavar='INT', help="MV_label", default=CONSTANTS.MV_label) 
    labels_group.add_argument("--TV_label", metavar='INT', help="TV_label", default=CONSTANTS.TV_label) 
    labels_group.add_argument("--AV_label", metavar='INT', help="AV_label", default=CONSTANTS.AV_label) 
    labels_group.add_argument("--PV_label", metavar='INT', help="PV_label", default=CONSTANTS.PV_label) 
    labels_group.add_argument("--plane_LPV1_label", metavar='INT', help="plane_LPV1_label", default=CONSTANTS.plane_LPV1_label) 
    labels_group.add_argument("--plane_LPV2_label", metavar='INT', help="plane_LPV2_label", default=CONSTANTS.plane_LPV2_label) 
    labels_group.add_argument("--plane_RPV1_label", metavar='INT', help="plane_RPV1_label", default=CONSTANTS.plane_RPV1_label) 
    labels_group.add_argument("--plane_RPV2_label", metavar='INT', help="plane_RPV2_label", default=CONSTANTS.plane_RPV2_label) 
    labels_group.add_argument("--plane_LAA_label", metavar='INT', help="plane_LAA_label", default=CONSTANTS.plane_LAA_label) 
    labels_group.add_argument("--plane_SVC_label", metavar='INT', help="plane_SVC_label", default=CONSTANTS.plane_SVC_label) 
    labels_group.add_argument("--plane_IVC_label", metavar='INT', help="plane_IVC_label", default=CONSTANTS.plane_IVC_label) 
    labels_group.add_argument("--LPV1_ring_label", metavar='INT', help="LPV1_ring_label", default=CONSTANTS.LPV1_ring_label) 
    labels_group.add_argument("--LPV2_ring_label", metavar='INT', help="LPV2_ring_label", default=CONSTANTS.LPV2_ring_label) 
    labels_group.add_argument("--RPV1_ring_label", metavar='INT', help="RPV1_ring_label", default=CONSTANTS.RPV1_ring_label) 
    labels_group.add_argument("--RPV2_ring_label", metavar='INT', help="RPV2_ring_label", default=CONSTANTS.RPV2_ring_label) 
    labels_group.add_argument("--LAA_ring_label", metavar='INT', help="LAA_ring_label", default=CONSTANTS.LAA_ring_label) 
    labels_group.add_argument("--SVC_ring_label", metavar='INT', help="SVC_ring_label", default=CONSTANTS.SVC_ring_label) 
    labels_group.add_argument("--IVC_ring_label", metavar='INT', help="IVC_ring_label", default=CONSTANTS.IVC_ring_label) 
    labels_group.add_argument("--scale_factor", metavar='FLOATs', help="scale_factor", default=CONSTANTS.scale_factor) 
    labels_group.add_argument("--valve_WT_multiplier", metavar='FLOAT', help="valve_WT_multiplier", default=CONSTANTS.valve_WT_multiplier) 
    labels_group.add_argument("--valve_WT_svc_ivc_multiplier", metavar='FLOAT', help="valve_WT_svc_ivc_multiplier", default=CONSTANTS.valve_WT_svc_ivc_multiplier) 
    labels_group.add_argument("--ring_thickness_multiplier", metavar='FLOAT', help="ring_thickness_multiplier", default=CONSTANTS.ring_thickness_multiplier) 
    labels_group.add_argument("--LV_neck_WT_multiplier", metavar='FLOAT', help="LV_neck_WT_multiplier", default=CONSTANTS.LV_neck_WT_multiplier) 
    labels_group.add_argument("--RV_WT_multiplier", metavar='FLOAT', help="RV_WT_multiplier", default=CONSTANTS.RV_WT_multiplier) 
    labels_group.add_argument("--LA_WT_multiplier", metavar='FLOAT', help="LA_WT_multiplier", default=CONSTANTS.LA_WT_multiplier) 
    labels_group.add_argument("--RA_WT_multiplier", metavar='FLOAT', help="RA_WT_multiplier", default=CONSTANTS.RA_WT_multiplier) 
    labels_group.add_argument("--Ao_WT_multiplier", metavar='FLOAT', help="Ao_WT_multiplier", default=CONSTANTS.Ao_WT_multiplier) 
    labels_group.add_argument("--PArt_WT_multiplier", metavar='FLOAT', help="PArt_WT_multiplier", default=CONSTANTS.PArt_WT_multiplier) 
    
    args = parser.parse_args()
    main(args)