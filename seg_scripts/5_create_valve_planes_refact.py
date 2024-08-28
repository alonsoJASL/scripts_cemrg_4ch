import img
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import copy
import json
import os
import argparse

from seg_scripts.common import configure_logging
logger = configure_logging(log_name=__name__)

import seg_scripts.Labels as L
from process_handler import create_valve_planes_refact
# ----------------------------------------------------------------------------------------------
# Define the wall thickness
# ----------------------------------------------------------------------------------------------
CONSTANTS = L.Labels()

def main(args) : 
    """
    Create Valve Planes
    USAGE:

    python3 create_valve_planes.py [path_to_points] [--points-json [points_json]] [--origin-spacing-json [origin_spacing_json]] [OPTIONS]

    OPTIONAL ARGUMENTS:
        --LV_BP_label [VALUE]
        --RV_BP_label [VALUE]
        --LA_BP_label [VALUE]
        --RA_BP_label [VALUE]
        --Ao_BP_label [VALUE]
        --PArt_BP_label [VALUE]
        --LV_myo_label [VALUE]
        --LA_myo_label [VALUE]
        --RA_myo_label [VALUE]
        --LA_WT [VALUE]
        --RA_WT [VALUE]
        --Ao_WT [VALUE]
        --PArt_WT [VALUE]
        --Ao_wall_label [VALUE]
        --PArt_wall_label [VALUE]
        --MV_label [VALUE]
        --TV_label [VALUE]
        --AV_label [VALUE]
        --PV_label [VALUE]
        --valve_WT [VALUE]
        --valve_WT_svc_ivc [VALUE]
        --LPV1_label [VALUE]
        --LPV2_label [VALUE]
        --RPV1_label [VALUE]
        --RPV2_label [VALUE]
        --LAA_label [VALUE]
        --SVC_label [VALUE]
        --IVC_label [VALUE]
        --ring_thickness [VALUE]
        --LPV1_ring_label [VALUE]
        --LPV2_ring_label [VALUE]
        --RPV1_ring_label [VALUE]
        --RPV2_ring_label [VALUE]
        --LAA_ring_label [VALUE]
        --SVC_ring_label [VALUE]
        --IVC_ring_label [VALUE]
        --plane_LPV1_label [VALUE]
        --plane_LPV2_label [VALUE]
        --plane_RPV1_label [VALUE]
        --plane_RPV2_label [VALUE]
        --plane_LAA_label [VALUE]
        --plane_SVC_label [VALUE]
        --plane_IVC_label [VALUE]
    """
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
        C.RV_BP_label = args.RV_BP_label
        C.LA_BP_label = args.LA_BP_label
        C.RA_BP_label = args.RA_BP_label
        C.Ao_BP_label = args.Ao_BP_label
        C.PArt_BP_label = args.PArt_BP_label
        C.LV_myo_label = args.LV_myo_label
        C.LA_myo_label = args.LA_myo_label
        C.RA_myo_label = args.RA_myo_label
        C.LA_WT = args.LA_WT
        C.RA_WT = args.RA_WT
        C.Ao_WT = args.Ao_WT
        C.PArt_WT = args.PArt_WT
        C.Ao_wall_label = args.Ao_wall_label
        C.PArt_wall_label = args.PArt_wall_label
        C.MV_label = args.MV_label
        C.TV_label = args.TV_label
        C.AV_label = args.AV_label
        C.PV_label = args.PV_label
        C.valve_WT = args.valve_WT
        C.valve_WT_svc_ivc = args.valve_WT_svc_ivc
        C.LPV1_label = args.LPV1_label
        C.LPV2_label = args.LPV2_label
        C.RPV1_label = args.RPV1_label
        C.RPV2_label = args.RPV2_label
        C.LAA_label = args.LAA_label
        C.SVC_label = args.SVC_label
        C.IVC_label = args.IVC_label
        C.ring_thickness = args.ring_thickness
        C.LPV1_ring_label = args.LPV1_ring_label
        C.LPV2_ring_label = args.LPV2_ring_label
        C.RPV1_ring_label = args.RPV1_ring_label
        C.RPV2_ring_label = args.RPV2_ring_label
        C.LAA_ring_label = args.LAA_ring_label
        C.SVC_ring_label = args.SVC_ring_label
        C.IVC_ring_label = args.IVC_ring_label
        C.plane_LPV1_label = args.plane_LPV1_label
        C.plane_LPV2_label = args.plane_LPV2_label
        C.plane_RPV1_label = args.plane_RPV1_label
        C.plane_RPV2_label = args.plane_RPV2_label
        C.plane_LAA_label = args.plane_LAA_label
        C.plane_SVC_label = args.plane_SVC_label
        C.plane_IVC_label = args.plane_IVC_label

        C.save(filename=labels_file)
    
    create_valve_planes_refact(path2points, path2ptsjson, path2originjson, labels_file, is_mri=args.is_mri)

if __name__ == '__main__' : 
    parser = argparse.ArgumentParser(description='To run: python3 create_valve_planes.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--labels-file", '-labels-file', type=str, required=False, default=None, help="Name of the json file containing custom labels")
    parser.add_argument("--thickness-file", '-thickness-file', type=str, required=False, default=None, help="Name of the json file containing custom thickness")
    parser.add_argument("--is-mri", '-is-mri', action='store_true', help="Flag to indicate if the input is MRI data")

    bp_group = parser.add_argument_group('Bloodpool labels')
    bp_group.add_argument('--LV_BP_label', help='LV_BP_label', default=CONSTANTS.LV_BP_label, metavar='VALUE')
    bp_group.add_argument('--RV_BP_label', help='RV_BP_label', default=CONSTANTS.RV_BP_label, metavar='VALUE')
    bp_group.add_argument('--LA_BP_label', help='LA_BP_label', default=CONSTANTS.LA_BP_label, metavar='VALUE')
    bp_group.add_argument('--RA_BP_label', help='RA_BP_label', default=CONSTANTS.RA_BP_label, metavar='VALUE')
    bp_group.add_argument('--Ao_BP_label', help='Ao_BP_label', default=CONSTANTS.Ao_BP_label, metavar='VALUE')
    bp_group.add_argument('--PArt_BP_label', help='PArt_BP_label', default=CONSTANTS.PArt_BP_label, metavar='VALUE')
    
    myo_group = parser.add_argument_group('Myocardium labels')
    myo_group.add_argument('--LV_myo_label', help='LV_myo_label', default=CONSTANTS.LV_myo_label, metavar='VALUE')
    myo_group.add_argument('--LA_myo_label', help='LA_myo_label', default=CONSTANTS.LA_myo_label, metavar='VALUE')
    myo_group.add_argument('--RA_myo_label', help='RA_myo_label', default=CONSTANTS.RA_myo_label, metavar='VALUE')

    wall_group = parser.add_argument_group('Wall thickness')
    wall_group.add_argument('--LA_WT', help='LA_WT', default=CONSTANTS.LA_WT, metavar='VALUE')
    wall_group.add_argument('--RA_WT', help='RA_WT', default=CONSTANTS.RA_WT, metavar='VALUE')
    wall_group.add_argument('--Ao_WT', help='Ao_WT', default=CONSTANTS.Ao_WT, metavar='VALUE')
    wall_group.add_argument('--PArt_WT', help='PArt_WT', default=CONSTANTS.PArt_WT, metavar='VALUE')
    wall_group.add_argument('--Ao_wall_label', help='Ao_wall_label', default=CONSTANTS.Ao_wall_label, metavar='VALUE')
    wall_group.add_argument('--PArt_wall_label', help='PArt_wall_label', default=CONSTANTS.PArt_wall_label, metavar='VALUE')

    valve_group = parser.add_argument_group('Valve labels')
    valve_group.add_argument('--MV_label', help='MV_label', default=CONSTANTS.MV_label, metavar='VALUE')
    valve_group.add_argument('--TV_label', help='TV_label', default=CONSTANTS.TV_label, metavar='VALUE')
    valve_group.add_argument('--AV_label', help='AV_label', default=CONSTANTS.AV_label, metavar='VALUE')
    valve_group.add_argument('--PV_label', help='PV_label', default=CONSTANTS.PV_label, metavar='VALUE')
    valve_group.add_argument('--valve_WT', help='valve_WT', default=CONSTANTS.valve_WT, metavar='VALUE')
    valve_group.add_argument('--valve_WT_svc_ivc', help='valve_WT_svc_ivc', default=CONSTANTS.valve_WT_svc_ivc, metavar='VALUE')

    veins_group = parser.add_argument_group('Vein labels')
    veins_group.add_argument('--LPV1_label', help='LPV1_label', default=CONSTANTS.LPV1_label, metavar='VALUE')
    veins_group.add_argument('--LPV2_label', help='LPV2_label', default=CONSTANTS.LPV2_label, metavar='VALUE')
    veins_group.add_argument('--RPV1_label', help='RPV1_label', default=CONSTANTS.RPV1_label, metavar='VALUE')
    veins_group.add_argument('--RPV2_label', help='RPV2_label', default=CONSTANTS.RPV2_label, metavar='VALUE')
    veins_group.add_argument('--LAA_label', help='LAA_label', default=CONSTANTS.LAA_label, metavar='VALUE')
    veins_group.add_argument('--SVC_label', help='SVC_label', default=CONSTANTS.SVC_label, metavar='VALUE')
    veins_group.add_argument('--IVC_label', help='IVC_label', default=CONSTANTS.IVC_label, metavar='VALUE')

    ring_group = parser.add_argument_group('Vein ring labels')
    ring_group.add_argument('--ring_thickness', help='ring_thickness', default=CONSTANTS.ring_thickness, metavar='VALUE')
    ring_group.add_argument('--LPV1_ring_label', help='LPV1_ring_label', default=CONSTANTS.LPV1_ring_label, metavar='VALUE')
    ring_group.add_argument('--LPV2_ring_label', help='LPV2_ring_label', default=CONSTANTS.LPV2_ring_label, metavar='VALUE')
    ring_group.add_argument('--RPV1_ring_label', help='RPV1_ring_label', default=CONSTANTS.RPV1_ring_label, metavar='VALUE')
    ring_group.add_argument('--RPV2_ring_label', help='RPV2_ring_label', default=CONSTANTS.RPV2_ring_label, metavar='VALUE')
    ring_group.add_argument('--LAA_ring_label', help='LAA_ring_label', default=CONSTANTS.LAA_ring_label, metavar='VALUE')
    ring_group.add_argument('--SVC_ring_label', help='SVC_ring_label', default=CONSTANTS.SVC_ring_label, metavar='VALUE')
    ring_group.add_argument('--IVC_ring_label', help='IVC_ring_label', default=CONSTANTS.IVC_ring_label, metavar='VALUE')

    plane_group = parser.add_argument_group('Valve plane labels')
    plane_group.add_argument('--plane_LPV1_label', help='plane_LPV1_label', default=CONSTANTS.plane_LPV1_label, metavar='VALUE')
    plane_group.add_argument('--plane_LPV2_label', help='plane_LPV2_label', default=CONSTANTS.plane_LPV2_label, metavar='VALUE')
    plane_group.add_argument('--plane_RPV1_label', help='plane_RPV1_label', default=CONSTANTS.plane_RPV1_label, metavar='VALUE')
    plane_group.add_argument('--plane_RPV2_label', help='plane_RPV2_label', default=CONSTANTS.plane_RPV2_label, metavar='VALUE')
    plane_group.add_argument('--plane_LAA_label', help='plane_LAA_label', default=CONSTANTS.plane_LAA_label, metavar='VALUE')
    plane_group.add_argument('--plane_SVC_label', help='plane_SVC_label', default=CONSTANTS.plane_SVC_label, metavar='VALUE')
    plane_group.add_argument('--plane_IVC_label', help='plane_IVC_label', default=CONSTANTS.plane_IVC_label, metavar='VALUE')

    args = parser.parse_args()
    main(args)