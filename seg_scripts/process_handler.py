import os
import sys
import glob
import numpy as np

from seg_scripts.common import configure_logging, add_file_handler
from seg_scripts.common import parse_txt_to_json, get_json_data, make_tmp, mycp

import seg_scripts.img as img
from seg_scripts.img import MaskOperationMode as mom
import seg_scripts.Labels as L
import seg_scripts.FourChamberProcess as FOURCH

logger = configure_logging(log_name=__name__)

def parse_input_parameters(path2points:str, path2originjson:str, path2ptsjson:str = "", labels_file=None) :

    if path2ptsjson is not None: 
        points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
        points_data = get_json_data(points_output_file)
    else :
        points_data = None
    
    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    C = L.Labels(filename=labels_file)
    fcp = FOURCH.FourChamberProcess(path2points, origin_data, CONSTANTS=C)

    return fcp, C, points_data

def get_origin_and_spacing(path2points:str, segmentation_name = "seg_corrected.nrrd", dicom_dir = 'ct', output_file = "") :
    """
    Find origin and spacing of the file.
    Needs a segmentation for spacing and dicom for origin.
    
    path2points: path to the folder with points
    segmentation_name: name of the segmentation file (inside path2points)
    dicom_dir: name of the dicom folder (inside path2points)

    output_file: name of the output file (optional, saved inside path2points)
    """
    def get_vec_string(vec) :
        return f'{vec[0]} {vec[1]} {vec[2]}'
    
    logger.info("Finding origin and spacing")
    dir_name = os.path.join(path2points, dicom_dir)
    print(dir_name)

    list_of_files = sorted(filter(os.path.isfile, glob.glob(os.path.join(dir_name, '*')) ) )
    image_origin = img.get_origin_from_dicom(list_of_files)

    origin_string = get_vec_string(image_origin)
    logger.info(f"Origin: {origin_string}")
    
    seg_nrrd = os.path.join(path2points, segmentation_name)
    image_spacing = img.get_image_spacing(seg_nrrd)

    spacing_string = get_vec_string(image_spacing)    
    logger.info(f"Spacing: {spacing_string}")

    if output_file != "" :    
        logger.info(f"Saving origin and spacing to {path2points}/{output_file}")

        # adding _labels to the name of the file
        output_file_labels = output_file.split('.')[0] + '_labels.txt'
        output_path = os.path.join(path2points, output_file)
        with open(output_path, 'w') as f:
            f.write(f'{origin_string}\n')
            f.write(f'{spacing_string}\n')
        
        output_path_labels = os.path.join(path2points, output_file_labels)
        with open(output_path_labels, 'w') as f:
            f.write(f'origin\n')
            f.write(f'spacing\n')
        
def create_cylinders(path2points:str, path2ptsjson="", path2originjson="", segmentation_name="seg_corrected.nrrd") : 
    fcp, _, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=None)

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
        fcp.cylinder(segmentation_name, points, fcp.DIR(out_name), radius, height)

def create_svc_ivc(path2points:str, path2originjson:str, segmentation_name="seg_corrected.nrrd", output_segname="seg_s2a.nrrd", labels_file=None) :
    fcp, _, _ = parse_input_parameters(path2points, path2originjson, path2ptsjson=None, labels_file=labels_file)
   
    if not fcp.check_nrrd(segmentation_name) : 
        msg = f"Could not find {segmentation_name} file and conversion to .nii failed."
        logger.error(msg)
        raise FileNotFoundError(msg)

    fcp.create_and_save_svc_ivc(segmentation_name, "SVC.nrrd", "IVC.nrrd", output_segname)

def create_slicers(path2points:str, path2ptsjson="", path2originjson="", segmentation_name="seg_s2a.nrrd") : 
    fcp, _, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=None)

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
        fcp.cylinder(segmentation_name, points, fcp.DIR(out_name), radius, height)

def crop_svc_ivc(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Cropping SVC and IVC") 
    fcp, C, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=labels_file)

    SVC_seed = points_data['SVC_tip']
    IVC_seed = points_data['IVC_tip']

    fcp.make_tmp()

    fcp.remove_protruding_vessel(SVC_seed, C.SVC_label, 'seg_s2a.nrrd', 'seg_s2b.nrrd')
    fcp.remove_protruding_vessel(IVC_seed, C.IVC_label, 'seg_s2b.nrrd', 'seg_s2c.nrrd')

    aorta_pair = ("aorta_slicer.nrrd", 0) # second is the slicer_label
    PArt_pair = ("PArt_slicer.nrrd", 0) # second is the slicer_label
    fcp.add_vessel_masks('seg_s2c.nrrd', 'seg_s2d.nrrd', aorta_pair, PArt_pair, "SVC_slicer.nrrd", "IVC_slicer.nrrd")

    fcp.flatten_vessel_base('seg_s2d.nrrd', 'seg_s2e.nrrd', SVC_seed, C.SVC_label)
    fcp.flatten_vessel_base('seg_s2e.nrrd', 'seg_s2f.nrrd', IVC_seed, C.IVC_label)

def create_myocardium(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Creating myocardium")
    fcp, C, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=labels_file)

    logger.info("<Step 1/10> Creating myocardium for the LV outflow tract")
    labelsd, thresd = fcp.get_distance_map_dictionaries('LV_BP_label', 'LV_DistMap.nrrd', 'LV_neck_WT', 'LV_neck.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE, C.LV_neck_label, [],  mom.NO_OVERRIDE, 2, [])
    fcp.create_mask_from_distance_map('seg_s2f.nrrd', 'seg_s3a.nrrd', labelsd, thresd, maskt)

    fcp.push_in_and_save('seg_s3a.nrrd', C.RV_BP_label, C.LV_myo_label, C.LV_BP_label, C.LV_neck_WT)

    logger.info("<Step 2/10> Creating the aortic wall")
    labelsd, thresd = fcp.get_distance_map_dictionaries('Ao_BP_label', 'Ao_DistMap.nrrd', 'Ao_WT', 'Ao_wall.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE, C.Ao_wall_label, [], mom.REPLACE_EXCEPT, C.Ao_wall_label, [C.LV_BP_label, C.LV_myo_label])
    fcp.create_mask_from_distance_map('seg_s3a.nrrd', 'seg_s3b.nrrd', labelsd, thresd, maskt)
    
    logger.info("<Step 3/10> Creating the pulmonary artery wall")
    labelsd, thresd= fcp.get_distance_map_dictionaries('PArt_BP_label', 'PArt_DistMap.nrrd','PArt_WT', 'PArt_wall.nrrd')
    maskt = fcp.get_distance_map_tuples(mom.REPLACE, C.PArt_wall_label, [], mom.REPLACE_EXCEPT, C.PArt_wall_label, [3,C.Ao_wall_label])
    fcp.create_mask_from_distance_map('seg_s3b.nrrd', 'seg_s3c.nrrd', labelsd, thresd, maskt)
    
    fcp.push_in_and_save('seg_s3c.nrrd', C.Ao_wall_label,C.PArt_wall_label,C.PArt_BP_label,C.PArt_WT, outname='seg_s3d.nrrd')

    logger.info("<Step 4/10> Cropping veins")
    slicer_tuple_list = [ ("aorta_slicer.nrrd", mom.REPLACE_ONLY, 0, [C.Ao_wall_label]), 
                         ("PArt_slicer.nrrd",  mom.REPLACE_ONLY, 0, [C.PArt_wall_label])]
    fcp.cropping_veins('seg_s3d.nrrd', slicer_tuple_list, 'seg_s3e.nrrd') 

    inputs_tuple_list = [ ('seg_s3d.nrrd', points_data['Ao_tip'], C.Ao_BP_label, 'seg_s3f.nrrd'), 
                           ('seg_s3f.nrrd', points_data['PArt_tip'], C.PArt_BP_label, 'seg_s3f.nrrd')]
    for inputname, seed, label, outname in inputs_tuple_list :
        fcp.get_connected_component_and_save(inputname, seed, label, output_name=outname)

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

def create_valve_planes(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Creating valve planes")
    fcp, C, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=labels_file) 

    logger.info("<Step 1/8> Cropping major vessels")
    fcp.get_connected_component_and_save('seg_s3p.nrrd', points_data['Ao_WT_tip'], C.Ao_wall_label, 'seg_s3r.nrrd')
    fcp.get_connected_component_and_save('seg_s3r.nrrd', points_data['PArt_WT_tip'], C.PArt_wall_label, 'seg_s3s.nrrd')

    list_to_extract = [
        ('seg_s3s.nrrd', 'seg_s4a.nrrd', C.LV_BP_label, C.MV_label, 'LA_BP_label', 'LA_BP_DistMap.nrrd', 'valve_WT', 'LA_BP_thresh.nrrd', False, 1),
        ('seg_s4a.nrrd', 'seg_s4b.nrrd', C.LA_BP_label, C.LA_myo_label, 'LV_myo_label', 'LV_myo_DistMap.nrrd', 'LA_WT', 'LV_myo_extra.nrrd', False, 1),
        ('seg_s4b.nrrd', 'seg_s4c.nrrd', C.RV_BP_label, C.TV_label, 'RA_BP_label', 'RA_BP_DistMap.nrrd', 'valve_WT', 'RA_BP_thresh.nrrd', False, 1),
        ('seg_s4c.nrrd', 'seg_s4d.nrrd', C.RA_BP_label, C.RA_myo_label, 'RV_myo_label', 'RV_myo_DistMap.nrrd', 'RA_WT', 'RV_myo_extra.nrrd', False, 1),
        ('seg_s4d.nrrd', 'seg_s4e.nrrd', C.LV_BP_label, C.AV_label, 'Ao_BP_label', 'Ao_BP_DistMap.nrrd', 'valve_WT', 'AV.nrrd', False, 1),
        ('seg_s4e.nrrd', 'seg_s4f.nrrd', C.Ao_BP_label, C.Ao_wall_label, 'LV_myo_label', 'LV_myo_DistMap.nrrd', 'Ao_WT', 'Ao_wall_extra.nrrd', True, 1),
        ('seg_s4f.nrrd', 'seg_s4f.nrrd', C.MV_label, C.LV_myo_label, 'AV_label', 'AV_DistMap.nrrd', 'valve_WT', 'AV_sep.nrrd', False, 2),
        ('seg_s4f.nrrd', 'seg_s4g.nrrd', C.RV_BP_label, C.PV_label, 'PArt_BP_label', 'PArt_BP_DistMap.nrrd', 'valve_WT', 'PV.nrrd', False, 1),
        ('seg_s4g.nrrd', 'seg_s4h.nrrd', C.PArt_BP_label, C.PArt_wall_label, 'RV_myo_label', 'RV_myo_DistMap.nrrd', 'PArt_WT', 'PArt_wall_extra.nrrd', True, 1)
    ]

    msg_list = ['mitral valve', '', 'tricuspid valve', '', 'aortic valve', '', '', '', 'pulmonary valve']

    count = 2
    for msg, extractables in zip(msg_list, list_to_extract) :
        iname, oname, label, new_label, dmap_l, dmap_n, thresh, thresh_name, skip_dmap, mult = extractables
        if (msg != '') :
            logger.info(f'<Step {count}/8> Creating {msg}')
            count += 1
        labelsd, thresd = fcp.get_distance_map_dictionaries(dmap_l, dmap_n, thresh, thresh_name)
        thresd['threshold'] *= mult
        fcp.extract_structure_w_distance_map(iname, oname, labelsd, thresd, label, new_label, skip_dmap=skip_dmap)


    logger.info('<Step 6/8> Create the distance maps needed to cut the vein rings')
    list_of_rings = []
    list_of_inputs = [('LA_myo_label', 'LA_myo_DistMap.nrrd', 'ring_thickness', 'LA_myo_thresh.nrrd'),
                      ('RA_myo_label', 'RA_myo_DistMap.nrrd', 'ring_thickness', 'RA_myo_thresh.nrrd'),
                      ('LPV1_label', 'LPV1_BP_DistMap.nrrd', 'ring_thickness', 'LPV1_ring.nrrd'),
                      ('LPV2_label', 'LPV2_BP_DistMap.nrrd', 'ring_thickness', 'LPV2_ring.nrrd'),
                      ('RPV1_label', 'RPV1_BP_DistMap.nrrd', 'ring_thickness', 'RPV1_ring.nrrd'),
                      ('RPV2_label', 'RPV2_BP_DistMap.nrrd', 'ring_thickness', 'RPV2_ring.nrrd'),
                      ('LAA_label', 'LAA_BP_DistMap.nrrd', 'ring_thickness', 'LAA_ring.nrrd'),
                      ('SVC_label', 'SVC_BP_DistMap.nrrd', 'ring_thickness', 'SVC_ring.nrrd'),
                      ('IVC_label', 'IVC_BP_DistMap.nrrd', 'ring_thickness', 'IVC_ring.nrrd')]
    
     
    for label, dmap, wt, outname in list_of_inputs :
        labelsd, thresd = fcp.get_distance_map_dictionaries(label, dmap, wt, outname)
        aux_dict = fcp.threshold_distance_map('seg_s4h.nrrd', labelsd, thresd)
        list_of_rings.append(aux_dict['threshold'])

    logger.info('<Step 7/8> Creating the vein rings')
    list_of_processes = [
        ('LPV1_ring_label', mom.NO_OVERRIDE, ''),
        ('LPV2_ring_label', mom.NO_OVERRIDE, ''),
        ('RPV1_ring_label', mom.REPLACE_ONLY, 'SVC_label'),
        ('RPV2_ring_label',  mom.NO_OVERRIDE, ''),
        ('LAA_ring_label', mom.NO_OVERRIDE, ''),
        ('SVC_ring_label', mom.REPLACE_ONLY, 'Ao_wall_label,LA_myo_label,RPV1_ring_label,RPV1_label'),
        ('IVC_ring_label', mom.NO_OVERRIDE, '')
    ]

    fcp.creating_vein_rings('seg_s4h.nrrd', 'seg_s4i.nrrd', 'seg_s4j.nrrd', list_of_rings, list_of_processes)

    logger.info('<Step 8/8> Creating the valve planes')
    fcp.threshold_and_save('RA_BP_DistMap.nrrd', 'RA_BP_thresh_2mm.nrrd', C.valve_WT_svc_ivc)
    LA_BP_thresh_path = 'LA_BP_thresh.nrrd'
    RA_BP_thresh_path = 'RA_BP_thresh_2mm.nrrd'

    list_of_la_labels = [
        (C.LPV1_label,C.plane_LPV1_label), 
        (C.LPV2_label,C.plane_LPV2_label),
        (C.RPV1_label,C.plane_RPV1_label),
        (C.RPV2_label,C.plane_RPV2_label),
        (C.LAA_label,C.plane_LAA_label)
    ]

    list_of_ra_labels = [
        (C.SVC_label,C.plane_SVC_label),
        (C.IVC_label,C.plane_IVC_label)
    ]

    fcp.creating_valve_planes('seg_s4j.nrrd', LA_BP_thresh_path, RA_BP_thresh_path, 'seg_s4k.nrrd', list_of_la_labels, list_of_ra_labels)

def clean_segmentation(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Cleaning segmentation")
    fcp, C, _ = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=labels_file)

    mycp(fcp.DIR('seg_s4k.nrrd'), fcp.DIR('seg_s5.nrrd'))

    list_of_corrections1 = [(C.RPV1_ring_label,C.RPV2_ring_label,C.RPV2_label,C.ring_thickness),
                            (C.LPV1_ring_label,C.LPV2_ring_label,C.LPV2_label,C.ring_thickness),
                            (C.LPV1_ring_label,C.LAA_ring_label,C.LAA_label,C.ring_thickness),
                            (C.RV_myo_label,C.Ao_wall_label,C.Ao_BP_label,C.Ao_WT),
                            (C.SVC_ring_label,C.LA_myo_label,C.LA_BP_label,C.LA_WT)]
    
    for pusher_wall_lab,pushed_wall_lab,pushed_BP_lab, pushed_WT in list_of_corrections1 : 
        fcp.push_in_and_save('seg_s5.nrrd', pusher_wall_lab, pushed_wall_lab, pushed_BP_lab, pushed_WT)    
    


