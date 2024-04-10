import SimpleITK as sitk
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points = args.path_to_points

seg_final = sitk.ReadImage(f"{path2points}/seg_final.nrrd")

seg_final.SetDirection((1,0,0,0,1,0,0,0,1))

sitk.WriteImage(image=seg_final,fileName=f"{path2points}/seg_final_rotated.nrrd")


