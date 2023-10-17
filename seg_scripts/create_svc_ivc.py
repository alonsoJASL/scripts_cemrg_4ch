import img 
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import argparse
import os

# constants
DEFAULT_CONSTANTS = {
    'LV_BP_label' : 1,
    'LV_myo_label' : 2,
    'RV_BP_label' : 3,
    'LA_BP_label' : 4,
    'RA_BP_label' : 5,
    'Ao_BP_label' : 6,
    'PArt_BP_label' : 7,
    'LPV1_label' : 8,
    'LPV2_label' : 9,
    'RPV1_label' : 10,
    'RPV2_label' : 11,
    'LAA_label' : 12,
    'SVC_label' : 13,
    'IVC_label' : 14
}

def create_and_save_svc_ivc(
        seg_file: str, 
        svc_file: str, 
        ivc_file: str, 
        aorta_slicer_file: str, 
        PArt_slicer_file: str, 
        output_file: str,
        origin_spacing_data: json,
        labels: dict = DEFAULT_CONSTANTS ):
    seg_s2_array, _ = nrrd.read(seg_file)
    svc_array, _ = nrrd.read(svc_file)
    ivc_array, _ = nrrd.read(ivc_file)
    aorta_slicer_array, _ = nrrd.read(aorta_slicer_file)
    PArt_slicer_array, _ = nrrd.read(PArt_slicer_file)

    origin = origin_spacing_data['origin']
    spacings = origin_spacing_data['spacing']
    RPV1_label = labels['RPV1_label']
    SVC_label = labels['SVC_label']
    IVC_label = labels['IVC_label']
    
    # ----------------------------------------------------------------------------------------------
    # Add the SVC and IVC 
    # ----------------------------------------------------------------------------------------------
    print('\n ## Adding the SVC, IVC and slicers ## \n')
    seg_s2a_array = img.add_masks_replace_only(seg_s2_array, svc_array, SVC_label,RPV1_label)
    seg_s2a_array = img.add_masks(seg_s2a_array, ivc_array, IVC_label)
    
    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Formatting and saving the segmentation ##')
    seg_s2a_array = np.swapaxes(seg_s2a_array,0,2)
    img.save_itk(seg_s2a_array, origin, spacings, output_file)
    print(" ## Saved segmentation with SVC/IVC added ##")


def main(args) : 
    path2points = args.path_to_points
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    output_path = os.path.join(path2points, 'seg_s2a.nrrd') if args.output_path == "" else args.output_path

    if path2ptsjson == "" :
        points_file_name=f'{path2points}/points.json'
    else :
        points_file_name=os.path.join(path2points, path2ptsjson)
	
    if path2originjson == "" :
        origin_spacing_file_name=f'{path2points}/origin_spacing.json'
    else : 
        origin_spacing_file_name=os.path.join(path2points, path2originjson) 
		
    with open(points_file_name) as points_file :
        points_data = json.load(points_file)

    # ----------------------------------------------------------------------------------------------
    # Find the origin and spacing
    # ----------------------------------------------------------------------------------------------
    # NOTE - We save the origin and spacings because the "save_itk" function used in
    # the next step makes the format of the header difficult to work with.
    # ----------------------------------------------------------------------------------------------
    with open(origin_spacing_file_name) as origin_spacing_file :
        origin_spacing_data = json.load(origin_spacing_file)    
    
    # ----------------------------------------------------------------------------------------------
    # Give the path to the segmentation (with pulmonary veins separated)
    # ----------------------------------------------------------------------------------------------
    seg_corrected_nrrd = os.path.join(path2points, 'seg_corrected.nrrd')
    
    # ----------------------------------------------------------------------------------------------
    # Give the paths to the SVC/IVC cylinders and the aorta/pulmonary artery slicers
    # Give the associated labels
    # ----------------------------------------------------------------------------------------------
    svc_nrrd = os.path.join(path2points, 'SVC.nrrd')
    ivc_nrrd = os.path.join(path2points, 'IVC.nrrd')
    
    aorta_slicer_nrrd = os.path.join(path2points, 'aorta_slicer.nrrd')
    aorta_slicer_label = 0
    
    PArt_slicer_nrrd = os.path.join(path2points, 'PArt_slicer.nrrd')
    PArt_slicer_label = 0
    
    my_labels = {'RPV1_label' : args.RPV1_label, 'SVC_label' : args.SVC_label, 'IVC_label' : args.IVC_label}
    
    create_and_save_svc_ivc(seg_corrected_nrrd, svc_nrrd, ivc_nrrd, aorta_slicer_nrrd, PArt_slicer_nrrd, 
                            output_path, origin_spacing_data, my_labels)

    # # ----------------------------------------------------------------------------------------------
    # # Convert all of the segmentations to arrays
    # # ----------------------------------------------------------------------------------------------
    # seg_s2_array, header1 = nrrd.read(seg_corrected_nrrd)
    # svc_array, header2 = nrrd.read(svc_nrrd)
    # ivc_array, header3 = nrrd.read(ivc_nrrd)
    # aorta_slicer_array, header4 = nrrd.read(aorta_slicer_nrrd)
    # PArt_slicer_array, header5 = nrrd.read(PArt_slicer_nrrd)
    
    # # ----------------------------------------------------------------------------------------------
    # # Add the SVC and IVC 
    # # ----------------------------------------------------------------------------------------------
    # print('\n ## Adding the SVC, IVC and slicers ## \n')
    # seg_s2a_array = img.add_masks_replace_only(seg_s2_array, svc_array, SVC_label,RPV1_label)
    # seg_s2a_array = img.add_masks(seg_s2a_array, ivc_array, IVC_label)
    
    # # ----------------------------------------------------------------------------------------------
    # # Format and save the segmentation
    # # ----------------------------------------------------------------------------------------------
    # print(' ## Formatting and saving the segmentation ##')
    # seg_s2a_array = np.swapaxes(seg_s2a_array,0,2)
    # img.save_itk(seg_s2a_array, origin, spacings, path2points+'/seg_s2a.nrrd')
    # print(" ## Saved segmentation with SVC/IVC added ##")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To run: python3 create_svc_ivc.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")	#
    parser.add_argument("--output-path", "-output", type=str, required=False, default="", help="Output name")
    parser.add_argument("--RPV1_label", type=int, required=False, default=10, help="Label of the right pulmonary vein 1")
    parser.add_argument("--SVC_label", type=int, required=False, default=13, help="Label of the Superior Vena Cava")
    parser.add_argument("--IVC_label", type=int, required=False, default=14, help="Label of the Inferior Vena Cava")
    args = parser.parse_args()
    main(args)

    