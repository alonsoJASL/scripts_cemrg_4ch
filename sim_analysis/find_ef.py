## REMEMBER THIS DOESN'T WORK YET!##

import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import sys
import scipy.spatial as sp
import copy
import csv
import argparse

from sim_utils import *
parser = argparse.ArgumentParser(description='To run: python3 find_ef.py [path_to_cycle_folder] [BCL] [AV_delay]')
parser.add_argument("path_to_cycle_folder")
parser.add_argument("BCL")
parser.add_argument("AV_delay", default=100)
args = parser.parse_args()
cycleFolder = args.path_to_cycle_folder
BCL = args.BCL
AV_delay = args.AV_delay

LV_pres,RV_pres,LA_pres,RA_pres = prepare_pres_data(cycleFolder)
LV_vol,RV_vol,LA_vol,RA_vol = prepare_vol_data(cycleFolder)

LV_vol = last_full_beat(LV_vol,BCL,AV_delay)
RV_vol = last_full_beat(RV_vol,BCL,AV_delay)
LA_vol = last_full_beat(LA_vol,BCL,AV_delay)
RA_vol = last_full_beat(RA_vol,BCL,AV_delay)

EDVs = [max(LV_vol), max(RV_vol), max(LA_vol),max(RA_vol)]

ESVs = [min(LV_vol), min(RV_vol), min(LA_vol), min(RA_vol)]

LVEF = 100*((EDVs[0]-ESVs[0])/EDVs[0])

print(EDVs)
print(ESVs)

print("LVEF is "+str(LVEF)+"%")