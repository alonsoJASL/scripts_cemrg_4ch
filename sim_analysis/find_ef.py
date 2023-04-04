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
RVEF = 100*((EDVs[1]-ESVs[1])/EDVs[1])

print("\n EDVs: \n \t LV = "+str(EDVs[0])+" ml \n \t RV = "+str(EDVs[1])+" ml \n \t LA = "+str(EDVs[2])+" ml \n \t RA = "+str(EDVs[3])+" ml \n")

print("\n ESVs: \n \t LV = "+str(ESVs[0])+" ml \n \t RV = "+str(ESVs[1])+" ml \n \t LA = "+str(ESVs[2])+" ml \n \t RA = "+str(ESVs[3])+" ml \n")

print("\n Stroke volume: \n \t LV = "+str(EDVs[0]-ESVs[0])+" ml \n")

print("\n LV ejection fraction: \n \t "+str(LVEF)+" % \n")

print("\n RV ejection fraction: \n \t "+str(RVEF)+" % \n")

LV_pres = last_full_beat(LV_pres,BCL,AV_delay)

LV_max = max(LV_pres)

print("\n LV max pressure: \n \t "+str(LV_max)+" mmHg \n")


