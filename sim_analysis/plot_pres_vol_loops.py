import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import sys
import scipy.spatial as sp
import copy
import csv
import argparse

from sim_utils import *

plt.rcParams.update({'font.size': 30})

parser = argparse.ArgumentParser(description='To run: python3 plot_pres_vol_loops.py [path_to_heart_sim_folder] [BCL_1] [BCL_2] [AV_delay]')
parser.add_argument("path_to_cycle_folder")
parser.add_argument("BCL_1")
parser.add_argument("BCL_2")
parser.add_argument("AV_delay")
args = parser.parse_args()
heart_sim_folder = args.path_to_cycle_folder
BCL1 = args.BCL_1
BCL2 = args.BCL_2
AV_delay = args.AV_delay

LV_pres_af,RV_pres_af,LA_pres_af,RA_pres_af = prepare_pres_data(heart_sim_folder+"/hr120_af/cycle")
LV_vol_af,RV_vol_af,LA_vol_af,RA_vol_af = prepare_vol_data(heart_sim_folder+"/hr120_af/cycle")

LV_pres_ra,RV_pres_ra,LA_pres_ra,RA_pres_ra = prepare_pres_data(heart_sim_folder+"/hr70_af/cycle")
LV_vol_ra,RV_vol_ra,LA_vol_ra,RA_vol_ra = prepare_vol_data(heart_sim_folder+"/hr70_af/cycle")

LV_pres_rh,RV_pres_rh,LA_pres_rh,RA_pres_rh = prepare_pres_data(heart_sim_folder+"/hr70/cycle")
LV_vol_rh,RV_vol_rh,LA_vol_rh,RA_vol_rh = prepare_vol_data(heart_sim_folder+"/hr70/cycle")

LV_vol_af = last_full_beat(LV_vol_af,BCL2,AV_delay)
LV_vol_ra = last_full_beat(LV_vol_ra,BCL1,AV_delay)
LV_vol_rh = last_full_beat(LV_vol_rh,BCL1,AV_delay)

LV_pres_af = last_full_beat(LV_pres_af,BCL2,AV_delay)
LV_pres_ra = last_full_beat(LV_pres_ra,BCL1,AV_delay)
LV_pres_rh = last_full_beat(LV_pres_rh,BCL1,AV_delay)


figure(figsize=(10, 15), dpi=80)
plt.plot(LV_vol_af,LV_pres_af,c='cornflowerblue',linewidth=6)
plt.plot(LV_vol_ra,LV_pres_ra,':',c='limegreen',linewidth=6)
plt.plot(LV_vol_rh,LV_pres_rh,'-.',c='mediumorchid',linewidth=6)
plt.xlabel("volume [ml]")
plt.ylabel("pressure [mmHg]")
# plt.legend(["AF", "Rate control", "Rhythm control"])
plt.tight_layout()
plt.show()
