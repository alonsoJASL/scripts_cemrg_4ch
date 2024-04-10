import SimpleITK as sitk
import argparse
import nrrd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points = args.path_to_points



################################### Apply change of directions and then the offset to be the rotated offset

smooth_bad_place_path = f"{path2points}/seg_final_smooth_rotated.nrrd"
coarse_good_place_path = f"{path2points}/seg_final.nrrd"

smooth_after_segsmooth = sitk.ReadImage(smooth_bad_place_path)
coarse = sitk.ReadImage(coarse_good_place_path)

smooth_after_segsmooth.SetDirection(coarse.GetDirection())

sitk.WriteImage(smooth_after_segsmooth,f"{path2points}/direction.nrrd")


# There's an offset of the origin, we apply to the new image. 
coarse_good_place_path = f"{path2points}/seg_final.nrrd" # Needed for the resolution of rotation matrix
coarse_bad_place_path = f"{path2points}/seg_final_rotated.nrrd" # Needed for the shift
smooth_bad_place_path = f"{path2points}/seg_final_smooth_rotated.nrrd" # Needed for the shift
smooth_direction_path = f"{path2points}/direction.nrrd" # Needed to move it 

_, header_coarse_original =  nrrd.read(coarse_good_place_path)
_, header_coarse_before_segsmooth =  nrrd.read(coarse_bad_place_path)
_, header_smooth_after_segsmooth =  nrrd.read(smooth_bad_place_path)
image_smooth, header_smooth_direction =  nrrd.read(smooth_direction_path)


resolution_coarse =  np.linalg.norm( np.array(header_coarse_original['space directions'])[0])

rotation_matrix = np.array(header_coarse_original['space directions'])/resolution_coarse # We make the matrix orthonormal
shift = np.array(header_coarse_before_segsmooth['space origin']) - np.array(header_smooth_after_segsmooth['axis mins'])


rotated_shift = np.dot(rotation_matrix,shift)

resolution_smooth = np.linalg.norm( np.array(header_smooth_direction['space directions'])[0])


##### COMPLETELY BY EYE, NOT VERY TESTED, DON'T TRUST IT COMPLETELY
header_smooth_direction['space origin'] = header_smooth_direction['space origin'] + rotated_shift - (1-(resolution_coarse+resolution_smooth)/2)*shift

print(f"Updated: \n{header_smooth_direction}")

nrrd.write(file=f"{path2points}/seg_final_smooth.nrrd",data=image_smooth,header=header_smooth_direction)