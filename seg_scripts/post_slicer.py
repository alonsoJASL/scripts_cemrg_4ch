
import sys
import numpy as np
import math
import itertools
from joblib import Parallel, delayed
import nrrd

def calculate_image_spacing(img_spa_x, img_spa_y, img_spa_z):
    return max(img_spa_x, img_spa_y, img_spa_z)

def round_values(*args, precision=6):
    return [round(value, precision) for value in args]

def process_voxel(position, circ_center, rotation_matrix, slicer_height, rad_ppsa, img_spa_x, img_spa_y, img_spa_z):
    tmpI = np.uint8(0)

    # calculate rotated [cartesian] slicer coordinates
    rotO = np.matrix(position) - np.matrix(circ_center)
    rotP = rotation_matrix * rotO.T

    # calculate rotated [cylindrical] slicer coordinates
    rotZ = rotP[2]
    rotR = np.sqrt(rotP[0]**2 + rotP[1]**2)

    # generate temporary slicer mask vector
    if ((rotZ >= -slicer_height / 2) and (rotZ <= slicer_height / 2) and (rotR <= rad_ppsa)):
        tmpI = np.uint8(1)

    return tmpI

def slice_segmentation(coord_ppsa, coord_ppsb, coord_ppsc, img_siz, img_spa, img_min, slicer_height=None, slicer_radius=None):
    img_siz_x, img_siz_y, img_siz_z = img_siz
    img_spa_x, img_spa_y, img_spa_z = img_spa
    img_min_x, img_min_y, img_min_z = img_min

    # process data and round to six digits
    img_spa_x = round(img_spa_x, 6)
    img_spa_y = round(img_spa_y, 6)
    img_spa_z = round(img_spa_z, 6)
    img_min_x = round(img_min_x - img_spa_x / 2.00, 6)
    img_min_y = round(img_min_y - img_spa_y / 2.00, 6)
    img_min_z = round(img_min_z - img_spa_z / 2.00, 6)

    # generate dictionary with header information
    header = {
        'type': 'unsigned char',
        'sizes': [img_siz_x, img_siz_y, img_siz_z],
        'encoding': 'gzip',
        'spacings': [img_spa_x, img_spa_y, img_spa_z],
        'dimension': 3,
        'axis mins': [img_min_x, img_min_y, img_min_z],
        'centerings': ['cell', 'cell', 'cell'],
        'keyvaluepairs': {}
    }

    # calculate triangle edge vectors
    tri_side_a = coord_ppsc - coord_ppsb
    tri_side_b = coord_ppsc - coord_ppsa
    tri_side_c = coord_ppsb - coord_ppsa

    # calculate geometrical parameters
    tmp_plane = np.cross(tri_side_b, tri_side_c)
    tmp_line1 = np.cross(tri_side_c, tmp_plane)
    tmp_line2 = np.cross(tri_side_a, tmp_plane)
    tmp_point1 = (coord_ppsc - coord_ppsa) / 2.00
    tmp_point2 = (coord_ppsa + coord_ppsb) / 2.00

    # solve linear equation system and calculate center
    # lstsq instead of solve since coefficient matrix not square
    coeff_mat = np.column_stack((tmp_line1, -tmp_line2))
    lin_solve = np.linalg.lstsq(coeff_mat, tmp_point1, rcond=None)[0]
    circ_center = tmp_point2 + lin_solve[0] * tmp_line1

    # import|calculate applied slicer radius
    rad_pps1 = np.linalg.norm(coord_ppsa - circ_center)
    rad_pps2 = np.linalg.norm(coord_ppsb - circ_center)
    rad_pps3 = np.linalg.norm(coord_ppsc - circ_center)
    rad_ppsc = np.amax([rad_pps1, rad_pps2, rad_pps3])

    # finalize slicer radius (in mm)
    if slicer_radius is None:
        rad_ppsa = 1.5 * rad_ppsc
    else:
        rad_ppsa = float(slicer_radius)

    if slicer_height is None:
        slicer_height = 2.0
    else:
        slicer_height = float(slicer_height)

    # calculate [cartesian] slicer coordinate system
    axis_zcar = tmp_plane / np.linalg.norm(tmp_plane)
    axis_ycar = np.cross([0, 0, 1], axis_zcar) / np.linalg.norm(np.cross([0, 0, 1], axis_zcar))
    axis_xcar = np.cross(axis_ycar, axis_zcar) / np.linalg.norm(np.cross(axis_ycar, axis_zcar))

    # generate slicer coordinate rotation matrix
    rotation_matrix = np.matrix([axis_xcar, axis_ycar, axis_zcar])

    # initialize image space vectors and arrays
    vox_x = np.arange(img_spa_x / 2, img_spa_x * img_siz_x, img_spa_x)
    vox_y = np.arange(img_spa_y / 2, img_spa_y * img_siz_y, img_spa_y)
    vox_z = np.arange(img_spa_z / 2, img_spa_z * img_siz_z, img_spa_z)

    # Create a cube containing the cylinder
    radius_in_pixels = rad_ppsa / np.amin([img_spa_x, img_spa_y, img_spa_z]) + 0.5
    circ_center_in_pixels = [
        math.floor(circ_center[0] / img_spa_x + 0.5),
        math.floor(circ_center[1] / img_spa_y + 0.5),
        math.floor(circ_center[2] / img_spa_z + 0.5)
    ]

    # The cube is between the center and 2 times the radius per each side
    lower_bound_in_pixels = [el - 1.1 * max(radius_in_pixels, slicer_height / 2) for el in circ_center_in_pixels]
    upper_bound_in_pixels = [el + 1.1 * max(radius_in_pixels, slicer_height / 2) for el in circ_center_in_pixels]

    lower_bound_in_pixels = [int(el) for el in lower_bound_in_pixels]
    upper_bound_in_pixels = [int(el) for el in upper_bound_in_pixels]

    # Starting and ending points
    starting_point = [
        lower_bound_in_pixels[0] * img_spa_x + img_spa_x / 2,
        lower_bound_in_pixels[1] * img_spa_y + img_spa_y / 2,
        lower_bound_in_pixels[2] * img_spa_z + img_spa_z / 2
    ]

    ending_point = [
        upper_bound_in_pixels[0] * img_spa_x + img_spa_x / 2,
        upper_bound_in_pixels[1] * img_spa_y + img_spa_y / 2,
        upper_bound_in_pixels[2] * img_spa_z + img_spa_z / 2
    ]

    # Ensure bounds are within the voxel grid
    starting_point[0] = max(starting_point[0], vox_x[0])
    starting_point[1] = max(starting_point[1], vox_y[0])
    starting_point[2] = max(starting_point[2], vox_z[0])

    ending_point[0] = min(ending_point[0], vox_x[-1])
    ending_point[1] = min(ending_point[1], vox_y[-1])
    ending_point[2] = min(ending_point[2], vox_z[-1])

    mini_vox_x = np.arange(starting_point[0], ending_point[0], img_spa_x)
    mini_vox_y = np.arange(starting_point[1], ending_point[1], img_spa_y)
    mini_vox_z = np.arange(starting_point[2], ending_point[2], img_spa_z)

    # Parallelized for loop
    tmpI = Parallel(n_jobs=-1)(
        delayed(process_voxel)(position, circ_center, rotation_matrix, slicer_height, rad_ppsa, img_spa_x, img_spa_y, img_spa_z)
        for position in itertools.product(mini_vox_x, mini_vox_y, mini_vox_z)
    )

    small_image = np.reshape(tmpI, (len(mini_vox_x), len(mini_vox_y), len(mini_vox_z)))
    whole_image = np.zeros((img_siz_x, img_siz_y, img_siz_z), dtype=np.uint8)

    for i in range(len(mini_vox_x)):
        for j in range(len(mini_vox_y)):
            for k in range(len(mini_vox_z)):
                whole_image[int(lower_bound_in_pixels[0] + i), int(lower_bound_in_pixels[1] + j), int(lower_bound_in_pixels[2] + k)] = small_image[i, j, k]

    # nrrd.write(pro_path + '/' + slicer_ppi + '.nrrd', whole_image, header)
    return whole_image, header

def main():
    img_spa_x = float(sys.argv[13])
    img_spa_y = float(sys.argv[14])
    img_spa_z = float(sys.argv[15])

    # store triangle corner nodes in vertex vectors
    coord_ppsa = np.array([(float(sys.argv[1]) - 0.5) * img_spa_x, (float(sys.argv[2]) - 0.5) * img_spa_y, (float(sys.argv[3]) - 0.5) * img_spa_z])
    coord_ppsb = np.array([(float(sys.argv[4]) - 0.5) * img_spa_x, (float(sys.argv[5]) - 0.5) * img_spa_y, (float(sys.argv[6]) - 0.5) * img_spa_z])
    coord_ppsc = np.array([(float(sys.argv[7]) - 0.5) * img_spa_x, (float(sys.argv[8]) - 0.5) * img_spa_y, (float(sys.argv[9]) - 0.5) * img_spa_z])

    # restore meta data for image
    img_siz_x = int(float(sys.argv[10]))
    img_siz_y = int(float(sys.argv[11]))
    img_siz_z = int(float(sys.argv[12]))

    img_min_x = float(sys.argv[16])
    img_min_y = float(sys.argv[17])
    img_min_z = float(sys.argv[18])
    slicer_ppi = str(sys.argv[19])

    pro_path = sys.argv[20]

    slicer_height = sys.argv[21] if sys.argv[21] != 'None' else None
    slicer_radius = sys.argv[22] if sys.argv[22] != 'None' else None

    whole_im, header = slice_segmentation(coord_ppsa, coord_ppsb, coord_ppsc, (img_siz_x, img_siz_y, img_siz_z), (img_spa_x, img_spa_y, img_spa_z), (img_min_x, img_min_y, img_min_z), slicer_height, slicer_radius)
    nrrd.write(f'{pro_path}/{slicer_ppi}.nrrd', whole_im, header)

if __name__ == '__main__':
    main()