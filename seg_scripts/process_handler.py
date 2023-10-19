import os
import sys
import glob
import numpy as np

from common import configure_logging, add_file_handler
from common import parse_txt_to_json, get_json_data, make_tmp

import img
import advanced_img as advimg
import Labels

logger = configure_logging(log_name=__name__)

def get_origin_and_spacing(path2points:str, segmentation_name = "seg_corrected.nrrd", dicom_dir = 'ct', output_file = "") :
    """
    Find origin and spacing of the file.
    Needs a segmentation for spacing and dicom for origin.
    
    path2points: path to the folder with points
    segmentation_name: name of the segmentation file (inside path2points)
    dicom_dir: name of the dicom folder (inside path2points)

    output_file: name of the output file (optional, saved inside path2points)
    """
    logger.info("Finding origin and spacing")
    dir_name = os.path.join(path2points, dicom_dir)

    list_of_files = sorted(filter(os.path.isfile, glob.glob(dir_name + '*') ) )
    image_origin = img.get_origin_from_dicom(list_of_files)

    print(image_origin)

    seg_nrrd = os.path.join(path2points, segmentation_name)
    image_spacing = img.get_image_spacing(seg_nrrd)

    print(image_spacing)

    if output_file != "" :    
        with open(output_file, 'w') as f:
            f.write(f'{image_origin[0]} {image_origin[1]} {image_origin[2]}\n')
            f.write(f'{image_spacing[0]} {image_spacing[1]} {image_spacing[2]}\n')
        
def create_cylinders(path2points:str, path2ptsjson="", path2originjson="", segmentation_name="seg_corrected.nrrd") : 
    points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
    points_data = get_json_data(points_output_file)

    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    origin = origin_data["origin"]
    spacing = origin_data["spacing"]

    DIR = lambda x: os.path.join(path2points, x)
    seg_name  = DIR(segmentation_name)
    if not os.path.exists(seg_name) : 
        print(f"{segmentation_name} file does not exist. Attempting using .nii.")
        seg_nii = segmentation_name.replace(".nrrd", ".nii")
        seg_name = DIR(seg_nii)
        
        if os.path.exists(seg_name) : 
            print(f"Found {seg_nii} file. Converting to .nrrd.")
            seg_name = img.convert_to_nrrd(path2points, seg_nii)
        
    cylinders = [
        ("SVC", 10, 30, ["SVC_1", "SVC_2", "SVC_3"], "SVC.nrrd"),
        ("IVC", 10, 30, ["IVC_1", "IVC_2", "IVC_3"], "IVC.nrrd"),
        ("Ao", 30, 2, ["Ao_1", "Ao_2", "Ao_3"], "aorta_slicer.nrrd"),
        ("PArt", 30, 2, ["PArt_1", "PArt_2", "PArt_3"], "PArt_slicer.nrrd")
    ]

    for name, radius, height, idx, out_name in cylinders : 
        logger.info(f"Generating cylinder: {name}")
        # points = np.row_stack([points_data[pt] for pt in idx])
        points = np.row_stack((points_data[idx[0]], points_data[idx[1]], points_data[idx[2]]))
        advimg.cylinder(seg_name, points, DIR(out_name), radius, height, origin, spacing)

def create_svc_ivc(path2points:str, path2originjson:str, segmentation_name="seg_corrected.nrrd", output_segname="seg_s2a.nrrd", labels_file=None) :
    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    DIR = lambda x: os.path.join(path2points, x)
    seg_name  = DIR(segmentation_name)

    svc_nrrd = os.path.join(path2points, "SVC.nrrd")
    ivc_nrrd = os.path.join(path2points, "IVC.nrrd")
    # aorta_slicer_nrrd = os.path.join(path2points, "aorta_slicer.nrrd")
    # PArt_slicer_nrrd = os.path.join(path2points, "PArt_slicer.nrrd")

    # constants
    C = Labels(filename=labels_file)
    advimg.create_and_save_svc_ivc(seg_name, svc_nrrd, ivc_nrrd, 
                                #    aorta_slicer_nrrd, PArt_slicer_nrrd, 
                                   DIR(output_segname), origin_data, C.get_dictionary())


def create_slicers(path2points:str, path2ptsjson="", path2originjson="", segmentation_name="seg_s2a.nrrd") : 
    points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
    points_data = get_json_data(points_output_file)

    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    origin = origin_data["origin"]
    spacing = origin_data["spacing"]

    DIR = lambda x: os.path.join(path2points, x)
    seg_name  = DIR(segmentation_name)
    if not os.path.exists(seg_name) : 
        print(f"{segmentation_name} file does not exist. Attempting using .nii.")
        seg_nii = segmentation_name.replace(".nrrd", ".nii")
        seg_name = DIR(seg_nii)
        
        if os.path.exists(seg_name) : 
            print(f"Found {seg_nii} file. Converting to .nrrd.")
            seg_name = img.convert_to_nrrd(path2points, seg_nii)
        
    slicers = [
        ("SVC_slicer", 30, 2, ["SVC_slicer_1", "SVC_slicer_2", "SVC_slicer_3"], "SVC_slicer.nrrd"),
        ("IVC_slicer", 30, 2, ["IVC_slicer_1", "IVC_slicer_2", "IVC_slicer_3"], "IVC_slicer.nrrd")
    ]

    for name, radius, height, idx, out_name in slicers : 
        logger.info(f"Generating cylinder: {name}")
        # points = np.row_stack([points_data[pt] for pt in idx])
        points = np.row_stack((points_data[idx[0]], points_data[idx[1]], points_data[idx[2]]))
        advimg.cylinder(seg_name, points, DIR(out_name), radius, height, origin, spacing)

def crop_svc_ivc(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Cropping SVC and IVC") 
    points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
    points_data = get_json_data(points_output_file)

    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    make_tmp(path2points)
    DIR = lambda x: os.path.join(path2points, x)
    # TMP = lambda x: os.path.join(path2points, "tmp", x)

    C = Labels(filename=labels_file)

    SVC_seed = points_data['SVC_tip']
    IVC_seed = points_data['IVC_tip']

    advimg.remove_protruding_vessel(path2points, SVC_seed, C.SVC_label, 'seg_s2a.nrrd', 'seg_s2b.nrrd', origin_data) 
    advimg.remove_protruding_vessel(path2points, IVC_seed, C.IVC_label, 'seg_s2b.nrrd', 'seg_s2c.nrrd', origin_data)

    aorta_pair = (DIR("aorta_slicer.nrrd"), 0) # second is the slicer_label
    PArt_pair = (DIR("PArt_slicer.nrrd"), 0) # second is the slicer_label
    SVC_slicer_nrrd = DIR("SVC_slicer.nrrd")
    IVC_slicer_nrrd = DIR("IVC_slicer.nrrd")

    advimg.add_vessel_masks(DIR('seg_s2c.nrrd'), DIR('seg_s2d.nrrd'), aorta_pair, PArt_pair, SVC_slicer_nrrd, IVC_slicer_nrrd, origin_data, C)

    advimg.flatten_vessel_base('seg_s2d.nrrd', 'seg_s2e.nrrd', SVC_seed, C.SVC_label, path2points, 'tmp', origin_data, C)
    advimg.flatten_vessel_base('seg_s2e.nrrd', 'seg_s2f.nrrd', IVC_seed, C.IVC_label, path2points, 'tmp', origin_data, C)


    

