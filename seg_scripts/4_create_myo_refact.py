import img
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import os
import argparse

from seg_scripts.common import configure_logging
logger = configure_logging(log_name=__name__)

import seg_scripts.Labels as L
from process_handler import create_myocardium_refact

CONSTANTS = L.Labels()
def main(args) :
    """
    Create myocardium from points 
    USAGE:

    python3 create_myo.py [path_to_points] [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]

    OPTIONAL ARGUMENTS:
        --labels-file [labels_file]
        LABELS ARGUMENTS:
        --LV_BP_label [VALUE]
        --LV_myo_label [VALUE]
        --LV_neck_label [VALUE]
        --RV_BP_label [VALUE]
        --RV_myo_label [VALUE]
        --Ao_BP_label [VALUE]
        --Ao_wall_label [VALUE]
        --PArt_BP_label [VALUE]
        --PArt_wall_label [VALUE]
        --LA_BP_label [VALUE]
        --LA_myo_label [VALUE]
        --RPV1_label [VALUE]
        --RA_BP_label [VALUE]
        --RA_myo_label [VALUE]
        --SVC_label [VALUE]

        WALL THICKNESS ARGUMENTS: 
        ** ATTENTION: These are calculated as VALUE * scale_factor **
        --scale_factor [VALUE]
        --LV_neck_WT_multiplier [VALUE] 
        --RV_WT_multiplier [VALUE] 
        --LA_WT_multiplier [VALUE] 
        --RA_WT_multiplier [VALUE] 
        --Ao_WT_multiplier [VALUE] 
        --PArt_WT_multiplier [VALUE] 
    """

    # create_myocardium_refact(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    path2points = args.path_to_points
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    labels_file = args.labels_file
    thickness_file = args.thickness_file

    C = L.Labels(filename=labels_file, thickness_file=thickness_file)
    if labels_file is None :
        logger.info("Creating Labels file")
        labels_file = os.path.join(path2points, "custom_labels.json")

        C.LV_BP_label = args.LV_BP_label
        C.LV_myo_label = args.LV_myo_label
        C.LV_neck_label = args.LV_neck_label
        C.RV_BP_label = args.RV_BP_label
        C.RV_myo_label = args.RV_myo_label
        C.Ao_BP_label = args.Ao_BP_label
        C.Ao_wall_label = args.Ao_wall_label
        C.PArt_BP_label = args.PArt_BP_label
        C.PArt_wall_label = args.PArt_wall_label
        C.LA_BP_label = args.LA_BP_label
        C.LA_myo_label = args.LA_myo_label
        C.RPV1_label = args.RPV1_label
        C.RA_BP_label = args.RA_BP_label
        C.RA_myo_label = args.RA_myo_label
        C.SVC_label = args.SVC_label
        
        C.save(filename=labels_file)

    if thickness_file is None :
        logger.info("Creating Thickness file")
        thickness_file = os.path.join(path2points, "thickness.json")

        C.scale_factor = args.scale_factor
        C.LV_neck_WT_multiplier = args.LV_neck_WT_multiplier
        C.RV_WT_multiplier = args.RV_WT_multiplier
        C.LA_WT_multiplier = args.LA_WT_multiplier
        C.RA_WT_multiplier = args.RA_WT_multiplier
        C.Ao_WT_multiplier = args.Ao_WT_multiplier
        C.PArt_WT_multiplier = args.PArt_WT_multiplier
        C.set_wt_params()

        C.save_thickness(filename=thickness_file)

    create_myocardium_refact(path2points, path2ptsjson, path2originjson, labels_file, is_mri=args.is_mri)
    

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]', usage=main.__doc__)
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--is-mri", "-mri", action="store_true", help="If the input is MRI")

    labels_group = parser.add_argument_group("labels")
    labels_group.add_argument("--labels-file", '-labels-file', type=str, required=False, default=None, help="Name of the json file containing custom labels")
    labels_group.add_argument("--thickness-file", '-thickness-file', type=str, required=False, default="thickness.json", help="Name of the json file containing custom labels")
    labels_group.add_argument("--LV_BP_label", "-LV_BP_label", help="LV_BP_label", type=int, default=CONSTANTS.LV_BP_label)
    labels_group.add_argument("--LV_myo_label", "-LV_myo_label", help="LV_myo_label", type=int, default=CONSTANTS.LV_myo_label)
    labels_group.add_argument("--LV_neck_label", "-LV_neck_label", help="LV_neck_label", type=int, default=CONSTANTS.LV_neck_label)
    labels_group.add_argument("--RV_BP_label", "-RV_BP_label", help="RV_BP_label", type=int, default=CONSTANTS.RV_BP_label)
    labels_group.add_argument("--RV_myo_label", "-RV_myo_label", help="RV_myo_label", type=int, default=CONSTANTS.RV_myo_label)
    labels_group.add_argument("--Ao_BP_label", "-Ao_BP_label", help="Ao_BP_label", type=int, default=CONSTANTS.Ao_BP_label)
    labels_group.add_argument("--Ao_wall_label", "-Ao_wall_label", help="Ao_wall_label", type=int, default=CONSTANTS.Ao_wall_label)
    labels_group.add_argument("--PArt_BP_label", "-PArt_BP_label", help="PArt_BP_label", type=int, default=CONSTANTS.PArt_BP_label)
    labels_group.add_argument("--PArt_wall_label", "-PArt_wall_label", help="PArt_wall_label", type=int, default=CONSTANTS.PArt_wall_label)
    labels_group.add_argument("--LA_BP_label", "-LA_BP_label", help="LA_BP_label", type=int, default=CONSTANTS.LA_BP_label)
    labels_group.add_argument("--LA_myo_label", "-LA_myo_label", help="LA_myo_label", type=int, default=CONSTANTS.LA_myo_label)
    labels_group.add_argument("--RPV1_label", "-RPV1_label", help="RPV1_label", type=int, default=CONSTANTS.RPV1_label)
    labels_group.add_argument("--RA_BP_label", "-RA_BP_label", help="RA_BP_label", type=int, default=CONSTANTS.RA_BP_label)
    labels_group.add_argument("--RA_myo_label", "-RA_myo_label", help="RA_myo_label", type=int, default=CONSTANTS.RA_myo_label)
    labels_group.add_argument("--SVC_label", "-SVC_label", help="SVC_label", type=int, default=CONSTANTS.SVC_label)

    wt_group = parser.add_argument_group("wall thickness")
    wt_group.add_argument("--scale_factor", "-scale_factor", help="scale_factor", type=float, default=CONSTANTS.scale_factor)
    wt_group.add_argument("--LV_neck_WT_multiplier", "-LV_neck_WT_multiplier", help="LV_neck_WT_multiplier", type=float, default=CONSTANTS.LV_neck_WT_multiplier)
    wt_group.add_argument("--RV_WT_multiplier", "-RV_WT_multiplier", help="RV_WT_multiplier", type=float, default=CONSTANTS.RV_WT_multiplier)
    wt_group.add_argument("--Ao_WT_multiplier", "-Ao_WT_multiplier", help="Ao_WT_multiplier", type=float, default=CONSTANTS.Ao_WT_multiplier)
    wt_group.add_argument("--PArt_WT_multiplier", "-PArt_WT_multiplier", help="PArt_WT_multiplier", type=float, default=CONSTANTS.PArt_WT_multiplier)
    wt_group.add_argument("--LA_WT_multiplier", "-LA_WT_multiplier", help="LA_WT_multiplier", type=float, default=CONSTANTS.LA_WT_multiplier)
    wt_group.add_argument("--RA_WT_multiplier", "-RA_WT_multiplier", help="RA_WT_multiplier", type=float, default=CONSTANTS.RA_WT_multiplier)
    args = parser.parse_args()
    main(args)
