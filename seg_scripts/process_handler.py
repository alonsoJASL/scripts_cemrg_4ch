import os
import sys
import glob
import numpy as np

from common import configure_logging, add_file_handler
from common import parse_txt_to_json, get_json_data, make_tmp

import img
from img import MaskOperationMode as mom
import advanced_img as advimg
import Labels as L
import FourChamberProcess 

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

    fcp = FourChamberProcess(path2points, origin_data, CONSTANTS=L.Labels()) 
    if not fcp.check_nrrd(segmentation_name) :
        msg = f"Could not find {segmentation_name} file and conversion to .nii failed."
        logger.error(msg)
        raise FileNotFoundError(msg)
    
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
        fcp.create_cylinder(segmentation_name, points, fcp.DIR(out_name), radius, height)

def create_svc_ivc(path2points:str, path2originjson:str, segmentation_name="seg_corrected.nrrd", output_segname="seg_s2a.nrrd", labels_file=None) :
    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    C = L(filename=labels_file)
    fcp = FourChamberProcess(path2points, origin_data, CONSTANTS=C)

    if not fcp.check_nrrd(segmentation_name) : 
        msg = f"Could not find {segmentation_name} file and conversion to .nii failed."
        logger.error(msg)
        raise FileNotFoundError(msg)

    fcp.create_and_save_svc_ivc(segmentation_name, "SVC.nrrd", "IVC.nrrd", output_segname)

def create_slicers(path2points:str, path2ptsjson="", path2originjson="", segmentation_name="seg_s2a.nrrd") : 
    points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
    points_data = get_json_data(points_output_file)

    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    fcp = FourChamberProcess(path2points, origin_data, CONSTANTS=L.Labels())
    if not fcp.check_nrrd(segmentation_name) :
        msg = f"Could not find {segmentation_name} file and conversion to .nii failed."
        logger.error(msg)
        raise FileNotFoundError(msg)
        
    slicers = [
        ("SVC_slicer", 30, 2, ["SVC_slicer_1", "SVC_slicer_2", "SVC_slicer_3"], "SVC_slicer.nrrd"),
        ("IVC_slicer", 30, 2, ["IVC_slicer_1", "IVC_slicer_2", "IVC_slicer_3"], "IVC_slicer.nrrd")
    ]

    for name, radius, height, idx, out_name in slicers : 
        logger.info(f"Generating cylinder: {name}")
        # points = np.row_stack([points_data[pt] for pt in idx])
        points = np.row_stack((points_data[idx[0]], points_data[idx[1]], points_data[idx[2]]))
        fcp.cylinder(segmentation_name, points, out_name, radius, height)

def crop_svc_ivc(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Cropping SVC and IVC") 
    points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
    points_data = get_json_data(points_output_file)

    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    SVC_seed = points_data['SVC_tip']
    IVC_seed = points_data['IVC_tip']

    C = L(filename=labels_file)
    fcp = FourChamberProcess(path2points, origin_data, CONSTANTS=C)

    fcp.remove_protruding_vessel(SVC_seed, C.SVC_label, 'seg_s2a.nrrd', 'seg_s2b.nrrd')
    fcp.remove_protruding_vessel(IVC_seed, C.IVC_label, 'seg_s2b.nrrd', 'seg_s2c.nrrd')

    aorta_pair = ("aorta_slicer.nrrd", 0) # second is the slicer_label
    PArt_pair = ("PArt_slicer.nrrd", 0) # second is the slicer_label
    fcp.add_vessel_masks('seg_s2c.nrrd', 'seg_s2d.nrrd', aorta_pair, PArt_pair, "SVC_slicer.nrrd", "IVC_slicer.nrrd")

    fcp.flatten_vessel_base('seg_s2d.nrrd', 'seg_s2e.nrrd', SVC_seed, C.SVC_label)
    fcp.flatten_vessel_base('seg_s2e.nrrd', 'seg_s2f.nrrd', IVC_seed, C.IVC_label)

def create_myocardium(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Creating myocardium")
    points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
    points_data = get_json_data(points_output_file)

    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    C = L(filename=labels_file)
    fcp = FourChamberProcess(path2points, origin_data, CONSTANTS=C)
    
    labelsd, thresd = fcp.get_distance_map_dictionaries('LV_BP_label', 'LV_DistMap.nrrd', 'LV_neck_WT', 'LV_neck.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE, C.LV_neck_label, [],  mom.NO_OVERRIDE, 2, [])
    
    logger.info("<Step 1/10> Creating myocardium for the LV outflow tract")
    
    fcp.create_mask_from_distance_map('seg_s2f.nrrd', 'seg_s3a.nrrd', labelsd, thresd, maskt)
    fcp.push_in_and_save('seg_s3a.nrrd', C.RV_BP_label, C.LV_myo_label, C.LV_BP_label, C.LV_neck_WT)

    labelsd, thresd = fcp.get_distance_map_dictionaries('Ao_BP_label', 'Ao_DistMap.nrrd', 'Ao_WT', 'Ao_wall.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE, C.Ao_wall_label, [], mom.REPLACE_EXCEPT, C.Ao_wall_label, [C.LV_BP_label, C.LV_myo_label])
    
    logger.info("<Step 2/10> Creating the aortic wall")
    
    fcp.create_mask_from_distance_map('seg_s3a.nrrd', 'seg_s3b.nrrd', labelsd, thresd, maskt)

    labelsd, thresd= fcp.get_distance_map_dictionaries('PArt_BP_label', 'PArt_DistMap.nrrd','PArt_WT', 'PArt_wall.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE, C.PArt_wall_label, [], mom.REPLACE_EXCEPT, C.PArt_wall_label, [3,C.Ao_wall_label])
    
    logger.info("<Step 3/10> Creating the pulmonary artery wall")
    
    fcp.create_mask_from_distance_map('seg_s3b.nrrd', 'seg_s3c.nrrd', labelsd, thresd, maskt)
    fcp.push_in_and_save('seg_s3c.nrrd', C.Ao_wall_label,C.PArt_wall_label,C.PArt_BP_label,C.PArt_WT, outname='seg_s3d.nrrd')

    logger.info("<Step 4/10> Cropping veins")
    slicer_tuple_list = [ ("aorta_slicer.nrrd", mom.REPLACE_ONLY, 0, [C.Ao_wall_label]), 
                         ("PArt_slicer.nrrd",  mom.REPLACE_ONLY, 0, [C.PArt_wall_label])]
    fcp.cropping_veins('seg_s3d.nrrd', slicer_tuple_list, 'seg_s3e.nrrd') 

    inputs_tuple_list = [ ('seg_s3d.nrrd', points_data['Ao_tip'], C.Ao_BP_label, 'seg_s3f.nrrd'), 
                           ('seg_s3f.nrrd', points_data['PArt_tip'], C.PArt_BP_label, 'seg_s3f.nrrd')]
    for inputname, seed, label, outname in inputs_tuple_list :
        fcp.get_connected_component_and_save(inputname, outname, seed, label)

    logger.info("<Step 5/10> Creating the right ventricular myocardium") 
    labelsd, thresd = fcp.get_distance_map_dictionaries('RV_BP_label', 'RV_DistMap.nrrd', 'RV_WT', 'RV_myo.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE, C.RV_myo_label, [], mom.REPLACE_ONLY, C.RV_myo_label, [C.Ao_wall_label])

    fcp.create_mask_from_distance_map('seg_s3e.nrrd', 'seg_s3g.nrrd', labelsd, thresd, maskt)

    logger.info("<Step 6/10> Creating the left atrial myocardium")
    labelsd, thresd = fcp.get_distance_map_dictionaries('LA_BP_label', 'LA_BP_DistMap.nrrd', 'LA_WT', 'LA_myo.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE_ONLY, C.LA_myo_label, [C.RA_BP_label], mom.REPLACE_ONLY, C.LA_myo_label, [C.SVC_label])

    fcp.create_mask_from_distance_map('seg_s3g.nrrd', 'seg_s3h.nrrd', labelsd, thresd, maskt)

    logger.info("<Step 7/10> Creating the right atrial myocardium")
    labelsd, thresd = fcp.get_distance_map_dictionaries('RA_BP_label', 'RA_BP_DistMap.nrrd', 'RA_WT', 'RA_myo.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE, C.RA_myo_label, [], mom.REPLACE_ONLY, C.RA_myo_label, [C.RPV1_label])

    fcp.create_mask_from_distance_map('seg_s3h.nrrd', 'seg_s3i.nrrd', labelsd, thresd, maskt)

    fcp.push_in_and_save('seg_s3i.nrrd', C.LA_myo_label, C.RA_myo_label, C.RA_BP_label, C.RA_WT, outname='seg_s3j.nrrd')
    fcp.push_in_and_save('seg_s3j.nrrd', C.Ao_wall_label,C.RA_myo_label,C.RA_BP_label,C.RA_WT, outname='seg_s3k.nrrd')
    fcp.push_in_and_save('seg_s3k.nrrd', C.LV_myo_label,C.RA_myo_label,C.RA_BP_label,C.RA_WT, outname='seg_s3l.nrrd')

    logger.info("<Step 8/10> LA myo: Pushing the left atrium with the aorta") 
    fcp.push_in_and_save('seg_s3l.nrrd', C.Ao_wall_label, C.LA_myo_label, C.LA_BP_label, C.LA_WT, outname='seg_s3m.nrrd')

    logger.info("<Step 9/10> PArt wall: Pushing the pulmonary artery with the aorta")
    fcp.push_in_and_save('seg_s3m.nrrd', C.Ao_wall_label, C.PArt_wall_label, C.PArt_BP_label, C.PArt_WT, outname='seg_s3n.nrrd')
    fcp.push_in_and_save('seg_s3n.nrrd', C.LV_myo_label,C.PArt_wall_label,C.PArt_BP_label,C.PArt_WT, outname='seg_s3o.nrrd')

    logger.info("<Step 10/10> RV myo: Pushing the right ventricle with the aorta") 
    fcp.push_in_and_save('seg_s3o.nrrd', C.Ao_wall_label,C.RV_myo_label,C.RV_BP_label,C.RV_WT, outname='seg_s3p.nrrd')

