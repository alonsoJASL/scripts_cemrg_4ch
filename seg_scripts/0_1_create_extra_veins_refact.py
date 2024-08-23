#!/usr/bin/env python3
import nrrd
import copy
import numpy as np
import os
import SimpleITK as sitk
import string
from img import *
import subprocess
import time
import multiprocessing as mp
import json
import argparse

from seg_scripts.txt_2_json import txt2json
from seg_scripts.common import configure_logging
logger = configure_logging(log_name=__name__)

from process_handler import create_extra_veins

def main(args) : 

    path2points = args.path_to_points
    origin_spacing_json = args.origin_spacing_json
    veins_json = os.path.join(path2points, args.veins_file)

    seg_name = args.seg_name
    slicer_radius = args.slicer_radius
    slicer_height = args.slicer_height


    if '.txt' in veins_json : 
        veins_txt = veins_json
        veins_labels = veins_json.replace('.txt', '_labels.txt')
        txt2json(veins_txt, veins_labels, veins_json)
    
    create_extra_veins(path2points, origin_spacing_json, seg_name, veins_json, slicer_radius, slicer_height)
        


if __name__ == "__main__" : 
    parser = argparse.ArgumentParser(description='To run: python3 create_extra_veins.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--which-vein", "-which-vein", choices=['LSPV', 'LIPV', 'RSPV', 'RIPV', 'LAA'], default='LIPV', help="Which vein to create")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    parser.add_argument("--veins-file", "-veins", default="vein_points.json", required=False)
    
    optional_group = parser.add_argument_group('Optional arguments')
    optional_group.add_argument("--seg-name", "-seg-name", type=str, default="seg_corrected.nrrd")
    optional_group.add_argument("--slicer-radius", "-sradius", type=float, default=5)
    optional_group.add_argument("--slicer-height", "-sheight", type=float, default=15)

    args = parser.parse_args()
    main(args)

