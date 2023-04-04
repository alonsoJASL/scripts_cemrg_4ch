import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

import numpy as np

plt.rcParams.update({'font.size': 22})

num_hearts = 4

w = 0.4
x = [0,1]
xa = [0.02,1]
xb = [-0.02,1]
y = [(2.3, 2.143, 4.225, 2.876),
    (3.162, 2.164, 4.905, 4.337)]

y_av = [np.mean(y[0]), np.mean(y[1])]
y_std = [np.std(y[0]), np.std(y[1])]

y_sv = [(2.798, 2.794, 8.901, 5.007),
        (4.499, 2.84, 10.842, 8.811)]

y_sv_av = [np.mean(y_sv[0]), np.mean(y_sv[1])]
y_sv_std = [np.std(y_sv[0]), np.std(y_sv[1])]

label_holder = [0.1, 0.1]

data1a = {'af_ra': y[0][0], 'af_rh': y[1][0]}
values1a = list(data1a.values())

data2a = {'af_ra': y[0][1], 'af_rh': y[1][1]}
values2a = list(data2a.values())

data3a = {'af_ra': y[0][2], 'af_rh': y[1][2]}
values3a = list(data3a.values())

data4a = {'af_ra': y[0][3], 'af_rh': y[1][3]}
values4a = list(data4a.values())


data_av = {'AF': y_av[0], 'Rate control': y_av[1]}
names = list(data_av.keys())
values_av = list(data_av.values())

fig, axs = plt.subplots(1, 2, figsize=(12, 15))
axs[0].scatter(x, values1a,zorder=2,s=50,c='black',marker='x')

axs[0].scatter(x, values2a,zorder=2,s=50,c='black',marker='x')

axs[0].scatter(x, values3a,zorder=2,s=50,c='black',marker='x')

axs[0].scatter(x, values4a,zorder=2,s=50,c='black',marker='x')

axs[0].plot(names, label_holder,'--',c='dodgerblue',lw=0)

c = [y_std[0], y_std[1]]

axs[0].bar(names,values_av, width=0.3, color='darkorange', yerr=c, capsize=10,)

axs[0].set_xticklabels(["AF vs Ra. contr.","AF vs Rhy. contr."],rotation=90)
axs[0].set(ylabel="\u0394 EF [%]")
axs[0].set(xlim=[-0.5,1.5])
axs[0].set(ylim=[0,5])

#-----------------------------------------------------------------------
# Subfigure 2
#-----------------------------------------------------------------------
data_sv_1a = {'af_ra': y_sv[0][0], 'af_rh': y_sv[1][0]}
values_sv_1a = list(data_sv_1a.values())

data_sv_2a = {'af_ra': y_sv[0][1], 'af_rh': y_sv[1][1]}
values_sv_2a = list(data_sv_2a.values())

data_sv_3a = {'af_ra': y_sv[0][2], 'af_rh': y_sv[1][2]}
values_sv_3a = list(data_sv_3a.values())

data_sv_4a = {'af_ra': y_sv[0][3], 'af_rh': y_sv[1][3]}
values_sv_4a = list(data_sv_4a.values())

data_sv_av = {'af_ra': y_sv_av[0], 'af_rh': y_sv_av[1]}

values_sv_av = list(data_sv_av.values())
axs[1].scatter(xa, values_sv_1a,zorder=2,s=50,c='black',marker='x')

axs[1].scatter(xb, values_sv_2a,zorder=2,s=50,c='black',marker='x')

axs[1].scatter(x, values_sv_3a,zorder=2,s=50,c='black',marker='x')

axs[1].scatter(x, values_sv_4a,zorder=2,s=50,c='black',marker='x')

axs[1].plot(names, label_holder,'--',c='dodgerblue',lw=0)

c_sv = [y_sv_std[0], y_sv_std[1]]
# axs[1].errorbar(x, values_sv_av, yerr=c_sv, fmt="o", color='black',capsize=10, elinewidth=4, 
#              capthick=4, markersize=14, marker='d', 
#              markerfacecolor='darkorange',markeredgecolor='black')

axs[1].bar(names,values_sv_av, width=0.3, color='darkorange', yerr=c_sv, capsize=10)

axs[1].set_xticklabels(["AF vs Ra. contr.","AF vs Rhy. contr."],rotation=90)
axs[1].set(ylabel="\u0394 SV [ml]")
axs[1].set(xlim=[-0.5,1.5])
axs[1].set(ylim=[0,12])
plt.tight_layout()
plt.show()
