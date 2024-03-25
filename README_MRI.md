Instructions for using four-chamber mesh generation pipeline
=========================================================================================================

Segmentation
=========================================================================================================
1) Make folder (e.g. henry) in /data/Dropbox then make folder `segmentations' inside
<!-- 2) Copy `points.txt`, `labels.txt`, `origin_spacing.txt` and `origin_spacing_labels.txt` templates into `segmentations` folder (currently in `h_templates` folder) -->
5) Manually split and relabel pulmonary veins:
6) Export the segmentation as `seg_corrected.nrrd` with the new tags:
- LSPV = 8
- LIPV = 9
- RSPV = 10
- RIPV = 11
- LAA = 12
1) Make sure the image is in a suitable orientation (by opening it in ITKsnap, for instance). If not, you can use `c3d seg_corrected.nii -orient RAI -o seg_corrected_RAI.nii.gz` to convert it to RAI orientation.
5) Resample to 0.3 mm isotropic using the `img.py` script.

6) Run `create_origin_spacing_files` in `img.py`. Otherwise, select manually in itksnap the origin and spacing and add it to origin_spacing.txt

9) Select 3 points for SVC and IVC cylinders (pixel) and save in `points.txt`

11) Run `create_cylinders.py /heart_folder/segmentations`

12) Run `create_svc_ivc.py /heart_folder/segmentations`. At this point the segmentation should have the venae cavae incorporated.

1) Run `cut_vessels.py /heart_folder/segmentations`. Check that the venae cava have some base, otherwise adjust the threhsold values. 

17) Run `create_myo.py /heart_folder/segmentations`

19) Run `create_valve_planes.py /heart_folder/segmentations`

20) Run `clean_seg.py /heart_folder/segmentations`

21) Load `.nrrd` and manually clean valve ring. Check for any lose voxels. Make sure all the chambers are closed by the valve planes.
22) Export segmentation as `seg_final.nrrd`

23) Run `segSmoothing.sh /heart_folder/segmentations` - Not working reliably. Resample and use 3D slicer instead.

23) Check all the labels one last time. It is common that lose voxels appear, so run connected components in all the labels. Export it as `seg_final_smooth_corrected.nrrd`. Convert it to `.inr` using `segconver`
24) SKIP THIS STEP Run `segsmooth /heart_folder/segmentations/seg_final_smooth_corrected.nrrd /heart_folder/segmentations/seg_final_smooth_corrected.inr`

Meshing
=========================================================================================================
1) Run `python3 meshing.py /heart_folder`

2) cd into the meshing folder (inside heart folder)
2) Modify `heart_mesh_data_file` to point to your segmentation and folder paths.
3) Run `bash generate_heart_mesh_Cesare.sh`

4) Run `bash mesh_post.sh /heart_folder` ## watch out mesh tool path currently hard-coded ##













