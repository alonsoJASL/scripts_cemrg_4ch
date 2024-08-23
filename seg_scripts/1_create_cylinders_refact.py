#!/usr/bin/env python3
import argparse
import numpy as np

from seg_scripts.common import parse_txt_to_json, get_json_data
from seg_scripts.common import configure_logging
logger = configure_logging(log_name=__name__)

from process_handler import create_cylinders_general

def main(args) : 
    """
    Create cylinders for SVC, IVC, Ao, PArt

    """
    path2points = args.path_to_points
    path2pointsjson = args.points_json
    path2originjson = args.origin_spacing_json

    which_cylinders = []
    if args.SVC:
        which_cylinders.append("SVC")
    if args.IVC:
        which_cylinders.append("IVC")
    if args.Ao:
        which_cylinders.append("Ao")
    if args.PArt:
        which_cylinders.append("PArt")
    
    if which_cylinders == []:
        logger.error("No cylinders selected. Exiting...") 
        return
    
    seg_name = args.seg_name
    physical_points = args.physical_points
    mm = args.mm
    
    create_cylinders_general(path2points, path2pointsjson, path2originjson, which_cylinders, 
                             segmentation_name=seg_name, is_mm=mm, world_coords=physical_points) 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To run: python3 create_cylinders.py [path_to_points]', usage=main.__doc__)
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")	

    processing_group = parser.add_argument_group('Processing arguments')
    processing_group.add_argument("--SVC", "-svc", action=argparse.BooleanOptionalAction, default=True, help="Create SVC cylinder")
    processing_group.add_argument("--IVC", "-ivc", action=argparse.BooleanOptionalAction, default=True, help="Create IVC cylinder")
    processing_group.add_argument("--Ao", "-ao", action='store_true', help="Create AO cylinder")
    processing_group.add_argument("--PArt", "-part", action='store_true', help="Create PA cylinder")
    
    optional_group = parser.add_argument_group('Optional arguments')
    optional_group.add_argument("--seg-name", "-seg-name", type=str, default="seg_corrected.nrrd")
    optional_group.add_argument("--physical-points", action='store_true', help="Points file is in physical coordinates")
    optional_group.add_argument("--mm", "-mm", action='store_true', help="Calculate cylinder with mm units") 

    args = parser.parse_args()
    main(args)