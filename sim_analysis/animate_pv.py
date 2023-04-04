import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import sys
import scipy.spatial as sp
import copy
import csv
import argparse

#from matplotlib import animation
import matplotlib.animation as animation


from sim_utils import *

loadStepping=40

parser = argparse.ArgumentParser(description='To run: python3 animate_pv.py [path_to_cycle_folder] --compare [path_to_cycle_folder_2] --save')
parser.add_argument("path_to_cycle_folder")
parser.add_argument("--compare","-c",type=str)
parser.add_argument("--save","-s",type=str)
args = parser.parse_args()
cycleFolder = args.path_to_cycle_folder
cycleFolder2 = args.compare
anim_name = args.save

if cycleFolder2 is not None:
	compare_on=1
else:
	compare_on=0

if anim_name is not None:
	save_anim=1
else:
	save_anim=0

LV_pres,RV_pres,LA_pres,RA_pres = prepare_pres_data(cycleFolder)
LV_vol,RV_vol,LA_vol,RA_vol = prepare_vol_data(cycleFolder)

if compare_on==1:
	LV_pres_comp,RV_pres_comp,LA_pres_comp,RA_pres_comp = prepare_pres_data(cycleFolder2)
	LV_vol_comp,RV_vol_comp,LA_vol_comp,RA_vol_comp = prepare_vol_data(cycleFolder2)

t_min=-loadStepping
t_max=len(LV_pres)-loadStepping

time=np.arange(t_min,t_max,1)

numDataPoints=len(time)

plot_every=10
rem = numDataPoints % plot_every

extra_time=np.zeros(rem)
time=np.concatenate((time,extra_time))

numPlotPoints=int(len(time)/plot_every)

LV_pres_plot=np.zeros(numPlotPoints)
LV_vol_plot=np.zeros(numPlotPoints)
time_plot=np.zeros(numPlotPoints)

for i in range(0,numPlotPoints):
	LV_pres_plot[i]=LV_pres[plot_every*i]
	LV_vol_plot[i]=LV_vol[plot_every*i]
	time_plot[i]=time[plot_every*i]

if compare_on==1:
	LV_pres_comp_plot=np.zeros(numPlotPoints)
	LV_vol_comp_plot=np.zeros(numPlotPoints)

	for i in range(0,numPlotPoints):
		LV_pres_comp_plot[i]=LV_pres_comp[plot_every*i]
		LV_vol_comp_plot[i]=LV_vol_comp[plot_every*i]


fig, (ax1,ax2,ax3) = plt.subplots(1,3)
fig.set_size_inches(30,8)
fig.suptitle('CARPENTRY-IRREGULAR 9 BEAT SIM')

def animate_func(num):
	ax1.clear()
	ax1.plot(LV_vol_plot[0:num+1],LV_pres_plot[0:num+1])
	ax1.scatter(LV_vol_plot[num], LV_pres_plot[num], c='blue', marker='o')
	ax1.set_xlim(70,150)
	ax1.set_ylim(-5,125)
	ax1.set_xlabel('LV volume [ml]')
	ax1.set_ylabel('LV pressure [mmHg]')

	ax2.clear()
	ax2.plot(time_plot[0:num+1],LV_pres_plot[0:num+1])
	ax2.scatter(time_plot[num], LV_pres_plot[num], c='blue', marker='o')
	ax2.set_xlim(0,numDataPoints)
	ax2.set_ylim(-20,125)
	ax2.set_xlabel('time [ms]')
	ax2.set_ylabel('LV pressure [mmHg]')

	ax3.clear()
	ax3.plot(time_plot[0:num+1],LV_vol_plot[0:num+1])
	ax3.scatter(time_plot[num], LV_vol_plot[num], c='blue', marker='o')
	ax3.set_xlim(0,numDataPoints)
	ax3.set_ylim(50,150)
	ax3.set_xlabel('time [ms]')
	ax3.set_ylabel('LV vol [ml]')

def animate_func_compare(num):
	ax1.clear()
	ax1.plot(LV_vol_plot[0:num+1],LV_pres_plot[0:num+1])
	ax1.scatter(LV_vol_plot[num], LV_pres_plot[num], c='blue', marker='o')
	ax1.plot(LV_vol_comp_plot[0:num+1],LV_pres_comp_plot[0:num+1])
	ax1.scatter(LV_vol_comp_plot[num], LV_pres_comp_plot[num], c='darkorange', marker='o')
	ax1.set_xlim(70,150)
	ax1.set_ylim(-5,125)
	ax1.set_xlabel('LV volume [ml]')
	ax1.set_ylabel('LV pressure [mmHg]')

	ax2.clear()
	ax2.plot(time_plot[0:num+1],LV_pres_plot[0:num+1])
	ax2.scatter(time_plot[num], LV_pres_plot[num], c='blue', marker='o')
	ax2.plot(time_plot[0:num+1],LV_pres_comp_plot[0:num+1])
	ax2.scatter(time_plot[num], LV_pres_comp_plot[num], c='darkorange', marker='o')
	ax2.set_xlim(0,numDataPoints)
	ax2.set_ylim(-20,125)
	ax2.set_xlabel('time [ms]')
	ax2.set_ylabel('LV pressure [mmHg]')

	ax3.clear()
	ax3.plot(time_plot[0:num+1],LV_vol_plot[0:num+1])
	ax3.scatter(time_plot[num], LV_vol_plot[num], c='blue', marker='o')
	ax3.plot(time_plot[0:num+1],LV_vol_comp_plot[0:num+1])
	ax3.scatter(time_plot[num], LV_vol_comp_plot[num], c='darkorange', marker='o')
	ax3.set_xlim(0,numDataPoints)
	ax3.set_ylim(50,150)
	ax3.set_xlabel('time [ms]')
	ax3.set_ylabel('LV vol [ml]')


if compare_on==0:
	line_ani = animation.FuncAnimation(fig, animate_func, interval=5,   
                                   frames=numPlotPoints, save_count=numPlotPoints)
else:
	line_ani = animation.FuncAnimation(fig, animate_func_compare, interval=5,   
                                   frames=numPlotPoints, save_count=numPlotPoints)

if save_anim==1:
	f = cycleFolder+"/"+anim_name+".gif" 
	writergif = animation.PillowWriter(fps=50) 
	line_ani.save(f, writer=writergif)
else:
	plt.show()


# writervideo = animation.FFMpegWriter(fps=60)
# line_ani.save('/data/Dropbox/FIA_anim.mp4', writer=writervideo)
# plt.close()



