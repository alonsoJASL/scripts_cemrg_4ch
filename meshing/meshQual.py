import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('/data/Dropbox/af_hearts/harry/meshing/myocardium_OUT/mshQual.qual.dat')

n, bins, patches = plt.hist(data, 100, density=True, facecolor='b', alpha=0.75)

plt.xlabel('Mesh Quality')
plt.show()
