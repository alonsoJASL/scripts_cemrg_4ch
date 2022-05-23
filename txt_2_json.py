# Save points within the labelled volumes of the segmentation

import numpy as np
import json
import string
import sys

points_txt = sys.argv[1]
labels_txt = sys.argv[2]
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

if __name__ == '__main__':
	main()