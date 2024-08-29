import SimpleITK as sitk
import numpy as np
import skimage.morphology as morph

from seg_scripts.common import configure_logging
logger = configure_logging(log_name=__name__)

def find_centroid(label_mask):
    return np.mean(np.argwhere(label_mask), axis=0)

def dilate_label(label_mask):
    return morph.binary_dilation(label_mask, morph.ball(1))

def find_contact_central_point(label_mask, other_label_mask):
    dilated_label_mask = dilate_label(label_mask)
    contact_points = np.argwhere(np.logical_and(dilated_label_mask, other_label_mask))
    if contact_points.size == 0:
        raise ValueError("No contact points found between the labels")
    return np.mean(contact_points, axis=0)

def find_label_extents(label_mask, base_point, direction_vector):
    max_distance = 0
    min_distance = np.inf

    for point in np.argwhere(label_mask):
        distance = np.dot(point - base_point, direction_vector)
        max_distance = max(max_distance, distance)
        min_distance = min(min_distance, distance)

    return min_distance, max_distance

def cut_label(image_array, label_mask, base_point, direction_vector, cut_ratio):
    min_distance, max_distance = find_label_extents(label_mask, base_point, direction_vector)
    total_length = max_distance - min_distance
    cut_distance = min_distance + total_length * cut_ratio

    for coord in np.argwhere(label_mask):
        if np.dot(coord - base_point, direction_vector) > cut_distance:
            image_array[tuple(coord)] = 0
    return image_array

def open_label(image_array, bp_label_mask, bp_myo_label_mask, base_point, direction_vector, cut_ratio):
    min_distance, max_distance = find_label_extents(bp_label_mask, base_point, direction_vector)
    total_length = max_distance - min_distance
    cut_distance = min_distance + total_length * cut_ratio

    for coord in np.argwhere(bp_myo_label_mask):
        if np.dot(coord - base_point, direction_vector) > cut_distance:
            image_array[tuple(coord)] = 0
    return image_array

def cut_vessels(path2image, label_to_be_cut, label_in_contact, cut_percentage, save_filename):

    logger.info(f"Reading {path2image}...")
    original_image = sitk.ReadImage(path2image)
    image_array    = sitk.GetArrayFromImage(original_image)

    logger.info("Finding regions of interest...")
    label_cut = (image_array == label_to_be_cut) # Label to be cut
    label_adjacent = (image_array == label_in_contact)  # Label in contact with the label that we need to be cut

    logger.info("Finding vessel centroid...")
    centroid_label_cut = find_centroid(label_cut)

    logger.info("Finding blood pool central point..")
    contact_central_point = find_contact_central_point(label_cut, label_adjacent)

    direction_vector = centroid_label_cut - contact_central_point
    direction_vector /= np.linalg.norm(direction_vector)

    # Cut and remove 1/4 of label 7
    logger.info("Cutting_vein...")
    image_array = cut_label(image_array, label_cut, contact_central_point, direction_vector, cut_ratio=cut_percentage)

    # Create the modified image from the array
    modified_image = sitk.GetImageFromArray(image_array)
    modified_image.SetSpacing(original_image.GetSpacing())
    modified_image.SetOrigin(original_image.GetOrigin())
    modified_image.SetDirection(original_image.GetDirection())

    # Save the modified image back to an NRRD file
    logger.info("Saving image...")
    sitk.WriteImage(modified_image, save_filename)


def open_artery(path2image, myo_label, artery_bp_label, ventricle_label, cut_ratio, save_filename):

    logger.info(f"Reading {path2image}...")
    original_image = sitk.ReadImage(path2image)
    image_array    = sitk.GetArrayFromImage(original_image)

    logger.info("Finding regions of interest...")
    label_myo_and_artery = (image_array == myo_label) | (image_array == artery_bp_label) 
    label_artery = (image_array == artery_bp_label) 
    label_adjacent = (image_array == ventricle_label)  # Label in contact with the label that we need to be cut

    logger.info("Finding vessel centroid...")
    centroid_label_cut = find_centroid(label_artery)

    logger.info("Finding blood pool central point..")
    contact_central_point = find_contact_central_point(label_artery, label_adjacent)

    direction_vector = centroid_label_cut - contact_central_point
    direction_vector /= np.linalg.norm(direction_vector)

    logger.info("Opening artery...")
    image_array = open_label(image_array = image_array, 
                             bp_label_mask = label_artery,
                             bp_myo_label_mask = label_myo_and_artery, base_point = contact_central_point, direction_vector = direction_vector, 
                             cut_ratio=cut_ratio)

    # Create the modified image from the array
    modified_image = sitk.GetImageFromArray(image_array)
    modified_image.SetSpacing(original_image.GetSpacing())
    modified_image.SetOrigin(original_image.GetOrigin())
    modified_image.SetDirection(original_image.GetDirection())

    # Save the modified image back to an NRRD file
    logger.info("Saving image...")
    sitk.WriteImage(modified_image, save_filename)



def reassign_vessels(path2image, label_to_be_cut, label_in_contact, cut_percentage, save_filename):

    logger.info(f"Reading {path2image}...")
    original_image = sitk.ReadImage(path2image)
    image_array    = sitk.GetArrayFromImage(original_image)

    logger.info("Finding regions of interest...")
    label_cut = (image_array == label_to_be_cut) # Label to be cut
    label_adjacent = (image_array == label_in_contact)  # Label in contact with the label that we need to be cut

    logger.info("Finding vessel centroid...")
    centroid_label_cut = find_centroid(label_cut)

    logger.info("Finding blood pool central point..")
    contact_central_point = find_contact_central_point(label_cut, label_adjacent)

    direction_vector = centroid_label_cut - contact_central_point
    direction_vector /= np.linalg.norm(direction_vector)

    logger.info("Reassigning vein...")
    image_array = reassign_label(image_array, label_cut, contact_central_point, direction_vector, cut_ratio=cut_percentage, reassigned_label=label_in_contact)

    # Create the modified image from the array
    modified_image = sitk.GetImageFromArray(image_array)
    modified_image.SetSpacing(original_image.GetSpacing())
    modified_image.SetOrigin(original_image.GetOrigin())
    modified_image.SetDirection(original_image.GetDirection())

    # Save the modified image back to an NRRD file
    logger.info("Saving image...")
    sitk.WriteImage(modified_image, save_filename)

def reassign_label(image_array, label_mask, base_point, direction_vector, cut_ratio, reassigned_label):
    min_distance, max_distance = find_label_extents(label_mask, base_point, direction_vector)
    total_length = max_distance - min_distance
    cut_distance = min_distance + total_length * cut_ratio

    for coord in np.argwhere(label_mask):
        if np.dot(coord - base_point, direction_vector) < cut_distance:
            image_array[tuple(coord)] = reassigned_label
    return image_array