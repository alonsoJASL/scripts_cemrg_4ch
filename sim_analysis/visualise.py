import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import sys
import scipy.spatial as sp
import copy
import csv
import argparse

from sim_utils import *

loadStepping=40

parser = argparse.ArgumentParser(description='To run: python3 visualise.py [path_to_cycle_folder]')
parser.add_argument("path_to_cycle_folder")
args = parser.parse_args()
cycleFolder = args.path_to_cycle_folder

LV_pres,RV_pres,LA_pres,RA_pres = prepare_pres_data(cycleFolder)
LV_vol,RV_vol,LA_vol,RA_vol = prepare_vol_data(cycleFolder)
Ao_pres = prepare_Ao_data(cycleFolder)
eject_starts,eject_ends = find_ejection(LV_vol)

# Mean Aortic Pressure During Ejection
MAPDE = find_mapde(eject_starts,eject_ends,Ao_pres)

SV = find_sv(LV_vol)
vol_max = find_vol_max(LV_vol)
vol_min = find_vol_min(LV_vol)

t_min=-loadStepping
t_max=len(LV_pres)-loadStepping
time=np.arange(t_min,t_max,1)

figure(figsize=(25, 10), dpi=80)
plt.rcParams.update({'font.size': 20})

plt.subplot(1,3,1)
plt.plot(LV_vol,LV_pres)
plt.xlabel("volume [ml]")
plt.ylabel("pressure [mmHg]")

plt.subplot(1,3,2)
plt.plot(time,LV_pres)
for i,t in enumerate(eject_starts):
	plt.plot(time[eject_starts[i]:eject_ends[i]],Ao_pres[eject_starts[i]:eject_ends[i]],color='darkorange')
	plt.plot(time[eject_starts[i]],Ao_pres[eject_starts[i]],'.',color='black')
	plt.plot(time[eject_ends[i]],Ao_pres[eject_ends[i]],'.',color='black')
	plt.plot(time[eject_starts[i]],MAPDE[i],'o',color='black')
plt.xlabel("time [secs]")
plt.ylabel("pressure [mmHg]")
# plt.axvline(x=6270,color='limegreen',label='t_end')

plt.subplot(1,3,3)
plt.plot(time,LV_vol)
for i,t in enumerate(eject_starts):
	plt.plot(time[eject_starts[i]:eject_ends[i]],LV_vol[eject_starts[i]:eject_ends[i]],color='darkorange')
	plt.plot(time[eject_starts[i]],vol_max[i],'.',color='black')
	plt.plot(time[eject_ends[i]],vol_min[i],'.',color='black')
plt.xlabel("time [secs]")
plt.ylabel("volume [ml]")

# plt.tight_layout()
plt.suptitle("CARPENTRY-IRREGULAR (9 beat)")
plt.show()