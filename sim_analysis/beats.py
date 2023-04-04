import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import sys
import scipy.spatial as sp
import copy
import csv
import argparse

from matplotlib.widgets import Slider, Button
from sim_utils import *

loadStepping=40
t_start=100

parser = argparse.ArgumentParser(description='To run: python3 beats.py [path_to_cycle_folder]')
parser.add_argument("path_to_cycle_folder")
args = parser.parse_args()
cycleFolder = args.path_to_cycle_folder

beat_limits=np.array([20,1050,1029,2136,2017,2542,2556,2990,2983,4125,4111,4643,4643,5071,5064,6205])

LV_pres,RV_pres,LA_pres,RA_pres = prepare_pres_data(cycleFolder)
LV_vol,RV_vol,LA_vol,RA_vol = prepare_vol_data(cycleFolder)
Ao_pres = prepare_Ao_data(cycleFolder)
eject_starts,eject_ends = split_ejection(LV_pres,Ao_pres)

t_min=-loadStepping
t_max=len(LV_pres)-loadStepping

time=np.arange(t_min,t_max,1)

class Beat:
	def __init__(self,pres,vol):
		self.pres = pres
		self.vol = vol

beat1 = Beat(crop_data(LV_pres,beat_limits[0],beat_limits[1]),crop_data(LV_vol,beat_limits[0],beat_limits[1]))
beat2 = Beat(crop_data(LV_pres,beat_limits[2],beat_limits[3]),crop_data(LV_vol,beat_limits[2],beat_limits[3]))
beat3 = Beat(crop_data(LV_pres,beat_limits[4],beat_limits[5]),crop_data(LV_vol,beat_limits[4],beat_limits[5]))
beat4 = Beat(crop_data(LV_pres,beat_limits[6],beat_limits[7]),crop_data(LV_vol,beat_limits[6],beat_limits[7]))
beat5 = Beat(crop_data(LV_pres,beat_limits[8],beat_limits[9]),crop_data(LV_vol,beat_limits[8],beat_limits[9]))
beat6 = Beat(crop_data(LV_pres,beat_limits[10],beat_limits[11]),crop_data(LV_vol,beat_limits[10],beat_limits[11]))
beat7 = Beat(crop_data(LV_pres,beat_limits[12],beat_limits[13]),crop_data(LV_vol,beat_limits[12],beat_limits[13]))
beat8 = Beat(crop_data(LV_pres,beat_limits[14],beat_limits[15]),crop_data(LV_vol,beat_limits[14],beat_limits[15]))

figure(figsize=(15, 10), dpi=80)

plt.xlim([75,150])
plt.ylim([-10,120])

plt.plot(beat1.vol,beat1.pres,'darkorange')
plt.plot(beat2.vol,beat2.pres,'lightblue')
plt.plot(beat3.vol,beat3.pres,'mediumorchid')
plt.plot(beat4.vol,beat4.pres,'darkorange')
plt.plot(beat5.vol,beat5.pres,'lightblue')
plt.plot(beat6.vol,beat6.pres,'mediumorchid')
plt.plot(beat7.vol,beat7.pres,'darkorange')
plt.plot(beat8.vol,beat8.pres,'lightblue')
plt.xlabel("volume [ml]")
plt.ylabel("pressure [mmHg]")

plt.show()