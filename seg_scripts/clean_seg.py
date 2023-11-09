
from img import save_itk, push_inside
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import argparse
import os

from common import configure_logging
logger = configure_logging(log_name=__name__)

import Labels as L
from process_handler import clean_segmentation
# ----------------------------------------------------------------------------------------------
# Define the wall thickness
# ----------------------------------------------------------------------------------------------
CONSTANTS = L.Labels()

def main(args):
    """
    Clean the segmentation
    USAGE:

    python clean_seg.py [path_to_points] [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]
    
    OPTIONAL ARGUMENTS:
        --LA_BP_label [VALUE]
        --Ao_BP_label [VALUE]
        --LPV2_label [VALUE]
        --RPV2_label [VALUE]
        --LAA_label [VALUE]
        --ring_thickness [VALUE]
        --LPV1_ring_label [VALUE]
        --LPV2_ring_label [VALUE]
        --RPV1_ring_label [VALUE]
        --RPV2_ring_label [VALUE]
        --LAA_ring_label [VALUE]
        --SVC_ring_label [VALUE]
        --RV_myo_label [VALUE]
        --LA_myo_label [VALUE]
        --LA_WT [VALUE]
        --Ao_WT [VALUE]
        --Ao_wall_label [VALUE]

    """
    path2points = args.path_to_points
    path2originjson = args.origin_spacing_json

    labels_file = args.labels_file
    C = L.Labels(filename=labels_file)
    if labels_file is None:
        logger.info("Creating labels file")
        labels_file = os.path.join(path2points, "custom_labels.json")

        C.LA_BP_label = args.LA_BP_label
        C.Ao_BP_label = args.Ao_BP_label
        C.LPV2_label = args.LPV2_label
        C.RPV2_label = args.RPV2_label
        C.LAA_label = args.LAA_label
        C.ring_thickness = args.ring_thickness
        C.LPV1_ring_label = args.LPV1_ring_label
        C.LPV2_ring_label = args.LPV2_ring_label
        C.RPV1_ring_label = args.RPV1_ring_label
        C.RPV2_ring_label = args.RPV2_ring_label
        C.LAA_ring_label = args.LAA_ring_label
        C.SVC_ring_label = args.SVC_ring_label
        C.RV_myo_label = args.RV_myo_label
        C.LA_myo_label = args.LA_myo_label
        C.LA_WT = args.LA_WT
        C.Ao_WT = args.Ao_WT
        C.Ao_wall_label = args.Ao_wall_label

        C.save(filename=labels_file)
    
    clean_segmentation(path2points, path2originjson, path2ptsjson="", labels_file=labels_file)

    

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='To run: python3 clean_seg.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--labels-file", "-labels-file", type=str, required=False, default=None, help="Name of the json file containing the labels")
    
    bp_group = parser.add_argument_group('Bloodpool labels')
    bp_group.add_argument('--LA_BP_label', help="LA_BP_label", metavar="VALUE", default=CONSTANTS.LA_BP_label)
    bp_group.add_argument('--Ao_BP_label', help="Ao_BP_label", metavar="VALUE", default=CONSTANTS.Ao_BP_label)

    myo_group = parser.add_argument_group('Myocardium labels')
    myo_group.add_argument('--RV_myo_label', help="RV_myo_label", metavar="VALUE", default=CONSTANTS.RV_myo_label)
    myo_group.add_argument('--LA_myo_label', help="LA_myo_label", metavar="VALUE", default=CONSTANTS.LA_myo_label)

    veins_group = parser.add_argument_group('Veins labels')
    veins_group.add_argument('--LPV2_label', help="LPV2_label", metavar="VALUE", default=CONSTANTS.LPV2_label)
    veins_group.add_argument('--RPV2_label', help="RPV2_label", metavar="VALUE", default=CONSTANTS.RPV2_label)
    veins_group.add_argument('--LAA_label', help="LAA_label", metavar="VALUE", default=CONSTANTS.LAA_label)

    ring_group = parser.add_argument_group('Vein ring labels')
    veins_group.add_argument('--ring_thickness', help="ring_thickness", metavar="VALUE", default=CONSTANTS.ring_thickness)
    veins_group.add_argument('--LPV1_ring_label', help="LPV1_ring_label", metavar="VALUE", default=CONSTANTS.LPV1_ring_label)
    veins_group.add_argument('--LPV2_ring_label', help="LPV2_ring_label", metavar="VALUE", default=CONSTANTS.LPV2_ring_label)
    veins_group.add_argument('--RPV1_ring_label', help="RPV1_ring_label", metavar="VALUE", default=CONSTANTS.RPV1_ring_label)
    veins_group.add_argument('--RPV2_ring_label', help="RPV2_ring_label", metavar="VALUE", default=CONSTANTS.RPV2_ring_label)
    veins_group.add_argument('--LAA_ring_label', help="LAA_ring_label", metavar="VALUE", default=CONSTANTS.LAA_ring_label)
    veins_group.add_argument('--SVC_ring_label', help="SVC_ring_label", metavar="VALUE", default=CONSTANTS.SVC_ring_label)

    wall_group = parser.add_argument_group('Wall thickness labels')
    wall_group.add_argument('--LA_WT', help="LA_WT", metavar="VALUE", default=CONSTANTS.LA_WT)
    wall_group.add_argument('--Ao_WT', help="Ao_WT", metavar="VALUE", default=CONSTANTS.Ao_WT)
    wall_group.add_argument('--Ao_wall_label', help="Ao_wall_label", metavar="VALUE", default=CONSTANTS.Ao_wall_label)
    
    args = parser.parse_args()
    main(args)