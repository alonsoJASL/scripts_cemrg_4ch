import img
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import os
import argparse

from common import configure_logging
logger = configure_logging(log_name=__name__)

from common import Labels
from process_handler import create_myocardium


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


    # create_myocardium(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    path2points = args.path_to_points
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    labels_file = args.labels_file
    C = Labels(filename=labels_file)
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
        C.scale_factor = args.scale_factor
        C.LV_neck_WT_multiplier = args.LV_neck_WT_multiplier
        C.RV_WT_multiplier = args.RV_WT_multiplier
        C.LA_WT_multiplier = args.LA_WT_multiplier
        C.RA_WT_multiplier = args.RA_WT_multiplier
        C.Ao_WT_multiplier = args.Ao_WT_multiplier
        C.PArt_WT_multiplier = args.PArt_WT_multiplier
        C.set_wt_params()

        C.save(filename=labels_file)

    create_myocardium(path2points, path2ptsjson, path2originjson, labels_file)
    

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")

    labels_group = parser.add_argument_group("labels")
    labels_group.add_argument("--labels-file", '-labels-file', type=str, required=False, default=None, help="Name of the json file containing custom labels")
    labels_group.add_argument("--LV_BP_label", "-LV_BP_label", description="LV_BP_label", type=int, default=1)
    labels_group.add_argument("--LV_myo_label", "-LV_myo_label", description="LV_myo_label", type=int, default=2)
    labels_group.add_argument("--LV_neck_label", "-LV_neck_label", description="LV_neck_label", type=int, default=101)
    labels_group.add_argument("--RV_BP_label", "-RV_BP_label", description="RV_BP_label", type=int, default=3)
    labels_group.add_argument("--RV_myo_label", "-RV_myo_label", description="RV_myo_label", type=int, default=103)
    labels_group.add_argument("--Ao_BP_label", "-Ao_BP_label", description="Ao_BP_label", type=int, default=6)
    labels_group.add_argument("--Ao_wall_label", "-Ao_wall_label", description="Ao_wall_label", type=int, default=106)
    labels_group.add_argument("--PArt_BP_label", "-PArt_BP_label", description="PArt_BP_label", type=int, default=7)
    labels_group.add_argument("--PArt_wall_label", "-PArt_wall_label", description="PArt_wall_label", type=int, default=107)
    labels_group.add_argument("--LA_BP_label", "-LA_BP_label", description="LA_BP_label", type=int, default=4)
    labels_group.add_argument("--LA_myo_label", "-LA_myo_label", description="LA_myo_label", type=int, default=104)
    labels_group.add_argument("--RPV1_label", "-RPV1_label", description="RPV1_label", type=int, default=10)
    labels_group.add_argument("--RA_BP_label", "-RA_BP_label", description="RA_BP_label", type=int, default=5)
    labels_group.add_argument("--RA_myo_label", "-RA_myo_label", description="RA_myo_label", type=int, default=105)
    labels_group.add_argument("--SVC_label", "-SVC_label", description="SVC_label", type=int, default=13)

    wt_group = parser.add_argument_group("wall thickness")
    wt_group.add_argument("--scale_factor", "-scale_factor", description="scale_factor", type=float, default=1/0.39844)
    wt_group.add_argument("--LV_neck_WT_multiplier", "-LV_neck_WT_multiplier", description="LV_neck_WT_multiplier", type=float, default=2.00)
    wt_group.add_argument("--RV_WT_multiplier", "-RV_WT_multiplier", description="RV_WT_multiplier", type=float, default=3.50)
    wt_group.add_argument("--PArt_WT_multiplier", "-PArt_WT_multiplier", description="PArt_WT_multiplier", type=float, default=2.0)
    wt_group.add_argument("--LA_WT_multiplier", "-LA_WT_multiplier", description="LA_WT_multiplier", type=float, default=2.0)
    wt_group.add_argument("--RA_WT_multiplier", "-RA_WT_multiplier", description="RA_WT_multiplier", type=float, default=2.0)
    args = parser.parse_args()
    main(args)
