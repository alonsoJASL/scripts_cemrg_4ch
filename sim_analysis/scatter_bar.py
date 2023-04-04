import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

import numpy as np

plt.rcParams.update({'font.size': 22})

num_hearts = 4

w = 0.4
x = [0, 1, 2]
xa = [0.1, 0.9]
xb = [1.1, 1.9]
# x = [-0.1, 0.9, 1.9]
colors = [(0, 0, 1, 1), (1, 0, 0, 1), (0, 0, 1, 1)]
y = [(43.38003412, 41.61914367, 37.73976471, 38.10941353),
    (45.6803103, 43.76152205, 41.96478051, 40.98482733),
    (46.54243062, 43.78301835, 42.64472271, 42.4455029)]

y_av = [np.mean(y[0]), np.mean(y[1]), np.mean(y[2])]
y_std = [np.std(y[0]), np.std(y[1]), np.std(y[2])]

y_sv = [(41.955, 45.394, 55.465, 52.232),
        (44.753, 48.188, 64.366, 57.239),
        (46.454, 48.234, 66.307, 61.043)]

y_sv_av = [np.mean(y_sv[0]), np.mean(y_sv[1]), np.mean(y_sv[2])]
y_sv_std = [np.std(y_sv[0]), np.std(y_sv[1]), np.std(y_sv[2])]

label_holder = [0.1, 0.1, 0.1]

data1a = {'AF': y[0][0], 'Rate control': y[1][0]}
data1b = {'Rate control': y[1][0], 'Rhythm control': y[2][0]}
values1a = list(data1a.values())
values1b = list(data1b.values())

data2a = {'AF': y[0][1], 'Rate control': y[1][1]}
data2b = {'Rate control': y[1][1], 'Rhythm control': y[2][1]}
values2a = list(data2a.values())
values2b = list(data2b.values())

data3a = {'AF': y[0][2], 'Rate control': y[1][2]}
data3b = {'Rate control': y[1][2], 'Rhythm control': y[2][2]}
values3a = list(data3a.values())
values3b = list(data3b.values())

data4a = {'AF': y[0][3], 'Rate control': y[1][3]}
data4b = {'Rate control': y[1][3], 'Rhythm control': y[2][3]}
values4a = list(data4a.values())
values4b = list(data4b.values())


data_av = {'AF': y_av[0], 'Rate control': y_av[1], 'Rhythm control': y_av[2]}
names = list(data_av.keys())
values_av = list(data_av.values())

fig, axs = plt.subplots(1, 2, figsize=(12, 15))
axs[0].scatter(xa, values1a,s=10,c='forestgreen')
axs[0].scatter(xb, values1b,s=10,c='dodgerblue')
axs[0].plot(xa, values1a,c='forestgreen',lw=1)
axs[0].plot(xb, values1b,'--',dashes=(6, 6),c='dodgerblue',lw=1)

axs[0].scatter(xa, values2a,s=10,c='forestgreen')
axs[0].scatter(xb, values2b,s=10,c='dodgerblue')
axs[0].plot(xa, values2a,c='forestgreen',lw=1)
axs[0].plot(xb, values2b,'--',dashes=(6, 6),c='dodgerblue',lw=1)

axs[0].scatter(xa, values3a,s=10,c='forestgreen')
axs[0].scatter(xb, values3b,s=10,c='dodgerblue')
axs[0].plot(xa, values3a,c='forestgreen',lw=1)
axs[0].plot(xb, values3b,'--',dashes=(6, 6),c='dodgerblue',lw=1)

axs[0].scatter(xa, values4a,s=10,c='forestgreen')
axs[0].scatter(xb, values4b,s=10,c='dodgerblue')
axs[0].plot(xa, values4a,c='forestgreen',lw=1)
axs[0].plot(xb, values4b,'--',dashes=(6, 6),c='dodgerblue',lw=1)

axs[0].plot(names, label_holder,'--',c='dodgerblue',lw=1)

c = [y_std[0], y_std[1], y_std[2]]
axs[0].errorbar(x, values_av, yerr=c, fmt="o", color='black',capsize=10, elinewidth=4, 
             capthick=4, markersize=14, marker='d', 
             markerfacecolor='darkorange',markeredgecolor='black')

axs[0].set_xticklabels(["AF","Rate control","Rhythm control"],rotation=90)
axs[0].set(ylabel="EF [%]")
axs[0].set(xlim=[-0.2,2.2])
axs[0].set(ylim=[36,48])

#-----------------------------------------------------------------------
# Subfigure 2
#-----------------------------------------------------------------------
data_sv_1a = {'AF': y_sv[0][0], 'Rate control': y_sv[1][0]}
data_sv_1b = {'Rate control': y_sv[1][0], 'Rhythm control': y_sv[2][0]}
values_sv_1a = list(data_sv_1a.values())
values_sv_1b = list(data_sv_1b.values())

data_sv_2a = {'AF': y_sv[0][1], 'Rate control': y_sv[1][1]}
data_sv_2b = {'Rate control': y_sv[1][1], 'Rhythm control': y_sv[2][1]}
values_sv_2a = list(data_sv_2a.values())
values_sv_2b = list(data_sv_2b.values())

data_sv_3a = {'AF': y_sv[0][2], 'Rate control': y_sv[1][2]}
data_sv_3b = {'Rate control': y_sv[1][2], 'Rhythm control': y_sv[2][2]}
values_sv_3a = list(data_sv_3a.values())
values_sv_3b = list(data_sv_3b.values())

data_sv_4a = {'AF': y_sv[0][3], 'Rate control': y_sv[1][3]}
data_sv_4b = {'Rate control': y_sv[1][3], 'Rhythm control': y_sv[2][3]}
values_sv_4a = list(data_sv_4a.values())
values_sv_4b = list(data_sv_4b.values())


data_sv_av = {'AF': y_sv_av[0], 'Rate control': y_sv_av[1], 'Rhythm control': y_sv_av[2]}

values_sv_av = list(data_sv_av.values())
axs[1].scatter(xa, values_sv_1a,s=10,c='forestgreen')
axs[1].scatter(xb, values_sv_1b,s=10,c='dodgerblue')
axs[1].plot(xa, values_sv_1a,c='forestgreen',lw=1)
axs[1].plot(xb, values_sv_1b,'--',dashes=(6, 6),c='dodgerblue',lw=1)

axs[1].scatter(xa, values_sv_2a,s=10,c='forestgreen')
axs[1].scatter(xb, values_sv_2b,s=10,c='dodgerblue')
axs[1].plot(xa, values_sv_2a,c='forestgreen',lw=1)
axs[1].plot(xb, values_sv_2b,'--',dashes=(6, 6),c='dodgerblue',lw=1)

axs[1].scatter(xa, values_sv_3a,s=10,c='forestgreen')
axs[1].scatter(xb, values_sv_3b,s=10,c='dodgerblue')
axs[1].plot(xa, values_sv_3a,c='forestgreen',lw=1)
axs[1].plot(xb, values_sv_3b,'--',dashes=(6, 6),c='dodgerblue',lw=1)

axs[1].scatter(xa, values_sv_4a,s=10,c='forestgreen')
axs[1].scatter(xb, values_sv_4b,s=10,c='dodgerblue')
axs[1].plot(xa, values_sv_4a,c='forestgreen',lw=1)
axs[1].plot(xb, values_sv_4b,'--',dashes=(6, 6),c='dodgerblue',lw=1)

axs[1].plot(names, label_holder,'--',c='dodgerblue',lw=1)

c_sv = [y_sv_std[0], y_sv_std[1], y_sv_std[2]]
axs[1].errorbar(x, values_sv_av, yerr=c_sv, fmt="o", color='black',capsize=10, elinewidth=4, 
             capthick=4, markersize=14, marker='d', 
             markerfacecolor='darkorange',markeredgecolor='black')

axs[1].set_xticklabels(["AF","Rate control","Rhythm control"],rotation=90)
axs[1].set(ylabel="SV [ml]")
axs[1].set(xlim=[-0.2,2.2])
axs[1].set(ylim=[35,70])
plt.tight_layout()
plt.show()
