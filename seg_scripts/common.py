import os
import json
import platform
import logging

from seg_scripts.txt_2_json import txt2json


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
    return os.path.join(path1, remaining_path)

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
