import numpy as np

import sys
import argparse

parser = argparse.ArgumentParser(description='To run: python3 generateBCLs.py [healthy/AF] [num_beats]')
parser.add_argument("condition")
parser.add_argument("num_beats", default = 9)
args = parser.parse_args()
condition = str(args.condition)
num_beats = args.num_beats

if args.condition == 'healthy':
	af = 0
elif args.condition == 'Healthy':
	af = 0
elif args.condition == 'af':
	af = 1
elif args.condition == 'AF':
	af = 1
else:
	print("Condition not specified. Please choose AF or healthy")


## ----------------------------------------
## Input AF heart rate data sets
## ----------------------------------------


## ----------------------------------------
## Calculate mean / SD for each data set
## ----------------------------------------


## ----------------------------------------
## Set up distribution based on mean / SD
## ----------------------------------------



## ----------------------------------------
## Sample distribution
## ----------------------------------------

