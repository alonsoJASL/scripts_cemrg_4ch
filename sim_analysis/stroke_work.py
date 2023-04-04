import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import sys
import scipy.spatial as sp
import copy
import csv
import argparse

from sim_utils import *

parser = argparse.ArgumentParser(description='To run: python3 stroke_work.py [path_to_cycle_folder] [AV_delay')
parser.add_argument("path_to_cycle_folder")
parser.add_argument("AV_delay")
args = parser.parse_args()
cycleFolder = args.path_to_cycle_folder
AV_d = float(args.AV_delay)

def three_beat_length(loadStepping,AV_d,LV_pres):
	time_period = (len(LV_pres) - loadStepping -1 +AV_d)
	three_beat_time = 1e-3*time_period/3

	return three_beat_time

loadStepping=40
num_beats = 9

LV_pres,RV_pres,LA_pres,RA_pres = prepare_pres_data(cycleFolder)
LV_vol,RV_vol,LA_vol,RA_vol = prepare_vol_data(cycleFolder)
Ao_pres = prepare_Ao_data(cycleFolder)
eject_starts,eject_ends = find_ejection(LV_vol)

total_time = (len(LV_pres) - loadStepping)*1e-3
three_beat_time = three_beat_length(loadStepping,AV_d,LV_pres)

# Mean Aortic Pressure During Ejection
MAPDE = find_mapde(eject_starts,eject_ends,Ao_pres)
MAPDE = MAPDE[num_beats-3:]

# Stroke volume
SV = find_sv(LV_vol)
SV = SV[num_beats-3:]

# Stroke work = MAPDE * SV
MAPDE = mmHg_to_Pa(MAPDE)
SV = ml_to_m3(SV)
stroke_work = find_stroke_work(MAPDE,SV)

total_stroke_work = sum(stroke_work)

stroke_power = total_stroke_work/three_beat_time
print('Average stroke power = '+str(stroke_power)+' Watts')

