import os
import json
import platform
import logging

from seg_scripts.txt_2_json import txt2json
from seg_scripts.parameters import Parameters

def configure_logging(log_name: str, is_debug = False, log_format='[%(funcName)s] %(message)s'):
	logger = logging.getLogger(log_name)
	handler = logging.StreamHandler()
	formatter = logging.Formatter(log_format)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	
	log_level = logging.DEBUG if is_debug else logging.INFO
	logger.setLevel(log_level)

	return logger

def add_file_handler(logger, file_path: str):
    file_handler = logging.FileHandler(file_path)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def big_print(text):
    print("="*len(text))
    print(text)
    print("="*len(text))

def mycp(src, dst):
	if platform.system() == "Windows":
		os.system(f'copy {src} {dst}')
	else:
		os.system(f'cp {src} {dst}')

def mymkdir(path):
	if not os.path.exists(path):
		os.system(f'mkdir -p {path}')

def make_tmp(path):
	tmp_folder = os.path.join(path, "tmp")
	mymkdir(tmp_folder)
	
def smart_join(path1, path2):
	common_prefix = os.path.commonprefix([path1, path2])
	remaining_path = os.path.relpath(path2, common_prefix)
	
	res_path = os.path.join(common_prefix, remaining_path)
	
	return res_path

def parse_txt_to_json(path2points, path2file, pts_name, labels_name, out_name=""): 
	if out_name == "":
		out_name = pts_name
	if path2file == "":
		points_file = smart_join(path2points,f'{pts_name}.txt')
		labels_file = smart_join(path2points, f'f{labels_name}.txt')
		output_file = smart_join(path2points, f'{out_name}.json')
		txt2json(points_file, labels_file, output_file)
	else:
		output_file = smart_join(path2points, path2file)
	
	return output_file

def get_json_data(path2file):
	fname = os.path.basename(path2file)
	print(f"Reading {fname} file...")
	if not os.path.exists(path2file):
		print(f"ERROR: {fname} file does not exist. Please run txt_2_json.py first.")
		raise FileNotFoundError 
	
	with open(path2file) as file:
		data = json.load(file)
	
	return data

def apply_label_modifications(label_object, modifications):
    """
    Apply modifications to a label object based on key-value pairs provided in a list of strings.
    
    Args:
        label_object (object): The object containing label attributes to be modified.
        modifications (list): A list of strings in the format "key=value", e.g., ["RPV1_label=5", "SVC_label=6"].
    
    Returns:
        None
    """
    if modifications:
        for modification in modifications:
            try:
                key, value = modification.split('=')
                value = float(value) if '.' in value else int(value) 
                if hasattr(label_object, key):
                    setattr(label_object, key, value)
                    print(f"[common] Set {key} to {value} in the label object.")
                else:
                    print(f"[WARNING] Label '{key}' does not exist in the provided object.")
            except ValueError as e:
                print(f"[ERROR] Invalid modification format: {modification}. Expected format is 'key=value'. Error: {e}")
    else:
        print("[common] No label modifications were provided.")


def find_existing_parameter_file(path2points, file_path, default_name):
    if path2points is not None:
        print(f"[common] Using directory: {path2points}")
        # Create and save labels file if it was not provided
        if file_path is None:
            print("[common] Creating labels file")
            tmp_file_path = os.path.join(path2points, default_name)
        
            if os.path.exists(tmp_file_path):
                print(f"[common] Found existing labels file: {tmp_file_path}. Loading and updating... ")
                file_path = tmp_file_path

    return file_path

def initialize_parameters(args):
    """
    Initialize Parameters object with optional label and thickness files.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        path2points (str): Path to the points directory.
		path2ptsjson (str): Path to the points json file.
		path2originjson (str): Path to the origin and spacing json file.
		labels_file (str): Path to the labels json file.
		thickness_file (str): Path to the thickness json file.
    """ 
    path2points = getattr(args, 'path_to_points', None)
    path2ptsjson = getattr(args, 'points_json', "")
    path2originjson = getattr(args, 'origin_spacing_json', "")
    
    labels_file = getattr(args, 'labels_file', None)
    thickness_file = getattr(args, 'thickness_file', None)
    vein_cutoff_file = getattr(args, 'vein_cutoff_file', None)

    labels_file = find_existing_parameter_file(path2points, labels_file, "custom_labels.json")
    thickness_file = find_existing_parameter_file(path2points, thickness_file, "custom_thickness.json")
    vein_cutoff_file = find_existing_parameter_file(path2points, vein_cutoff_file, "custom_vein_cutoff.json")

    labels_not_set = labels_file is None
    thickness_not_set = thickness_file is None
    vein_cutoff_not_set = vein_cutoff_file is None

    # Initialize Parameters object with the provided files
    no_mod_params = Parameters(label_file=labels_file, thickness_file=thickness_file, vein_cutoff_file=vein_cutoff_file)
    params = Parameters(label_file=labels_file, thickness_file=thickness_file, vein_cutoff_file=vein_cutoff_file)

    # Apply any label modifications
    apply_label_modifications(params, getattr(args, 'modify_label', []))

    labels_modded = not params.labels.equals(no_mod_params.labels)
    thickness_modded = not params.thickness.equals(no_mod_params.thickness)
    vein_cutoff_modded = not params.vein_cutoff.equals(no_mod_params.vein_cutoff)

    # if modified, update. 
    if path2points is not None:
        print(f"[common] Using points directory: {path2points}")
        # Create and save labels file if it was not provided
        if labels_not_set or labels_modded:
            print("[common] Creating labels file")
            labels_file = os.path.join(path2points, "custom_labels.json") if labels_not_set else labels_file
            params.save_labels(labels_file)

        # Create and save thickness file if it was not provided
        if thickness_not_set or thickness_modded:
            print("[common] Creating thickness file")
            thickness_file = os.path.join(path2points, "custom_thickness.json") if thickness_not_set else thickness_file
            params.save_thickness(thickness_file)
    
        if vein_cutoff_not_set or vein_cutoff_modded:
            print("[common] Creating vein cutoff file")
            vein_cutoff_file = os.path.join(path2points, "custom_vein_cutoff.json") if vein_cutoff_not_set else vein_cutoff_file
            params.save_vein_cutoff(vein_cutoff_file)
		
    files_dict = {
        "labels_file": labels_file,
		"labels": labels_file,  
        "thickness_file": thickness_file,
		"thickness": thickness_file, 
        "vein_cutoff_file": vein_cutoff_file,
		"vein_cutoff": vein_cutoff_file 
    }

    return path2points, path2ptsjson, path2originjson, files_dict