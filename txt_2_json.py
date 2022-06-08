# Save points within the labelled volumes of the segmentation

import numpy as np
import json
import string
import sys

import argparse
parser = argparse.ArgumentParser(description='To run: python3 txt_2_json.py [points.txt] [labels.txt]')
parser.add_argument("text_file")
parser.add_argument("label_file")
args = parser.parse_args()

points_txt = args.text_file
labels_txt = args.label_file
points_json = "../points.json"

def main():
	points = np.loadtxt(points_txt)

	with open(labels_txt,"r") as labels:
		L=labels.read().splitlines()		# removes the /n from each line

	my_dict=dict(zip(L,range(len(L))))		# creates a dict of the right size with the labels

	for i in range(len(L)):
		my_dict[L[i]] = points[i].tolist()		# populates dict with points

	json_object = json.dumps(my_dict, indent = 4)

	with open(points_json, "w") as outfile:
		outfile.write(json_object)

	print("Successfully wrote .json file")

if __name__ == '__main__':
	main()