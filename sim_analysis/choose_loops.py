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

parser = argparse.ArgumentParser(description='To run: python3 choose_loops.py [path_to_cycle_folder]')
parser.add_argument("path_to_cycle_folder")
args = parser.parse_args()
cycleFolder = args.path_to_cycle_folder

SA_triggers_raw=np.array([-100,1400,2000,2300,3500,4100,4400,5600,6200,6500])
SA_triggers=SA_triggers_raw+100

LV_pres,RV_pres,LA_pres,RA_pres = prepare_pres_data(cycleFolder)
LV_vol,RV_vol,LA_vol,RA_vol = prepare_vol_data(cycleFolder)

t_min=-loadStepping
t_max=len(LV_pres)-loadStepping

time=np.arange(t_min,t_max,1)

def crop_data(data,start,end):
	cropped_data = data[start:end]

	return cropped_data

class Beat:
	def __init__(self,pres,vol):
		self.pres = pres
		self.vol = vol

beat1 = Beat(crop_data(LV_pres,SA_triggers[0],SA_triggers[1]),crop_data(LV_vol,SA_triggers[0],SA_triggers[1]))
beat2 = Beat(crop_data(LV_pres,SA_triggers[1],SA_triggers[2]),crop_data(LV_vol,SA_triggers[1],SA_triggers[2]))
beat3 = Beat(crop_data(LV_pres,SA_triggers[2],SA_triggers[3]),crop_data(LV_vol,SA_triggers[2],SA_triggers[3]))
beat4 = Beat(crop_data(LV_pres,SA_triggers[3],SA_triggers[4]),crop_data(LV_vol,SA_triggers[3],SA_triggers[4]))
beat5 = Beat(crop_data(LV_pres,SA_triggers[4],SA_triggers[5]),crop_data(LV_vol,SA_triggers[4],SA_triggers[5]))
beat6 = Beat(crop_data(LV_pres,SA_triggers[5],SA_triggers[6]),crop_data(LV_vol,SA_triggers[5],SA_triggers[6]))
beat7 = Beat(crop_data(LV_pres,SA_triggers[6],SA_triggers[7]),crop_data(LV_vol,SA_triggers[6],SA_triggers[7]))
beat8 = Beat(crop_data(LV_pres,SA_triggers[7],SA_triggers[8]),crop_data(LV_vol,SA_triggers[7],SA_triggers[8]))

beat_current = Beat(crop_data(LV_pres,SA_triggers[0],SA_triggers[1]),crop_data(LV_vol,SA_triggers[0],SA_triggers[1]))

figure(figsize=(18, 8), dpi=80)

plt.subplot(1,2,1)
plt.plot(beat_current.vol,beat_current.pres,'black')
plt.xlim([75,150])
plt.ylim([-10,120])

plt.plot(beat1.vol,beat1.pres,'darkorange',alpha=0.4)
plt.plot(beat2.vol,beat2.pres,'lightblue',alpha=0.4)
plt.plot(beat3.vol,beat3.pres,'mediumorchid',alpha=0.4)
plt.plot(beat4.vol,beat4.pres,'darkorange',alpha=0.4)
plt.plot(beat5.vol,beat5.pres,'lightblue',alpha=0.4)
plt.plot(beat6.vol,beat6.pres,'mediumorchid',alpha=0.4)
plt.plot(beat7.vol,beat7.pres,'darkorange',alpha=0.4)
plt.plot(beat8.vol,beat8.pres,'lightblue',alpha=0.4)
plt.xlabel("volume [ml]")
plt.ylabel("pressure [mmHg]")

plt.subplot(1,2,2)
ax_b1 = plt.axes([0.58, 0.5, 0.28, 0.03])
ax_b2 = plt.axes([0.58, 0.4, 0.28, 0.03])

slider_start = Slider(ax_b1, 'Start', t_min, t_max, 5)
slider_end = Slider(ax_b2, 'End', t_min, t_max, 120)

def update(val):
	t_start_beat = round(slider_start.val)
	t_end_beat = round(slider_end.val)
	beat_current = Beat(crop_data(LV_pres,t_start_beat,t_end_beat),crop_data(LV_vol,t_start_beat,t_end_beat))

	plt.subplot(1,2,1)
	plt.cla()
	plt.plot(beat_current.vol,beat_current.pres,'black')
	plt.xlabel("volume [ml]")
	plt.ylabel("pressure [mmHg]")
	plt.xlim([75,150])
	plt.ylim([-10,120])

	plt.plot(beat1.vol,beat1.pres,'darkorange',alpha=0.4)
	plt.plot(beat2.vol,beat2.pres,'lightblue',alpha=0.4)
	plt.plot(beat3.vol,beat3.pres,'mediumorchid',alpha=0.4)
	plt.plot(beat4.vol,beat4.pres,'darkorange',alpha=0.4)
	plt.plot(beat5.vol,beat5.pres,'lightblue',alpha=0.4)
	plt.plot(beat6.vol,beat6.pres,'mediumorchid',alpha=0.4)
	plt.plot(beat7.vol,beat7.pres,'darkorange',alpha=0.4)
	plt.plot(beat8.vol,beat8.pres,'lightblue',alpha=0.4)
	plt.xlabel("volume [ml]")
	plt.ylabel("pressure [mmHg]")

slider_start.on_changed(update)
slider_end.on_changed(update)


plt.show()






