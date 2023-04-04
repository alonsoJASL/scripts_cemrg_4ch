import argparse
import os

from os import listdir

os.system("clear")

parser = argparse.ArgumentParser()
parser.add_argument('--folder', type=str, required=True)
args = parser.parse_args()

alpha_files = os.listdir(args.folder)
i=0

for alpha_file in alpha_files:
	os.system("convert "+args.folder+"/"+alpha_file+" -background white -alpha remove -alpha off "+args.folder+"/no_alpha_"+alpha_file)
