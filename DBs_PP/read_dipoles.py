#
# A simple script which reads the dipoles from the ndb.dip_* database
#

import numpy as np
import matplotlib.pyplot as plt

from pylab import *
from netCDF4 import Dataset

#plt.rc("xtick", labelsize=16)     
#plt.rc("ytick", labelsize=16)

plt.rc("font", family="sans-serif",serif="Arial",size=15)


path="SET PATH HERE" 

#
# DIP section
#
dip_file = Dataset(path+"ndb.dip_iR_and_P_fragment_1","r") 

DIP_P = dip_file.variables["DIP_P_k_0001_spin_0001"][:,:,:,0]+1j*dip_file.variables["DIP_P_k_0001_spin_0001"][:,:,:,1]
DIP_R = dip_file.variables["DIP_iR_k_0001_spin_0001"][:,:,:,0]+1j*dip_file.variables["DIP_iR_k_0001_spin_0001"][:,:,:,1]

#
# Print Dipole P
#
print ("Dipole P")
print ("<2|p|3>=",DIP_P[1,0,0],DIP_P[1,0,1],DIP_P[1,0,2],sqrt(abs(DIP_P[1,0,0])**2+abs(DIP_P[1,0,1])**2+abs(DIP_P[1,0,2])**2))
print ("<2|p|4>=",DIP_P[1,1,0],DIP_P[1,1,1],DIP_P[1,1,2],sqrt(abs(DIP_P[1,1,0])**2+abs(DIP_P[1,1,1])**2+abs(DIP_P[1,1,2])**2))
print ("<1|p|3>=",DIP_P[0,0,0],DIP_P[0,0,1],DIP_P[0,0,2],sqrt(abs(DIP_P[0,0,0])**2+abs(DIP_P[0,0,1])**2+abs(DIP_P[0,0,2])**2))
print ("<1|p|4>=",DIP_P[0,1,0],DIP_P[0,1,1],DIP_P[0,1,2],sqrt(abs(DIP_P[0,1,0])**2+abs(DIP_P[0,1,1])**2+abs(DIP_P[0,1,2])**2))
#
# Print Dipole iR
#
print ("Dipole R= <P>/DeltaE")
print ("<2|R|3>=",DIP_R[1,0,0],DIP_R[1,0,1],DIP_R[1,0,2],sqrt(abs(DIP_R[1,0,0])**2+abs(DIP_R[1,0,1])**2+abs(DIP_R[1,0,2])**2))
print ("<2|R|4>=",DIP_R[1,1,0],DIP_R[1,1,1],DIP_R[1,1,2],sqrt(abs(DIP_R[1,1,0])**2+abs(DIP_R[1,1,1])**2+abs(DIP_R[1,1,2])**2))
print ("<1|R|3>=",DIP_R[0,0,0],DIP_R[0,0,1],DIP_R[0,0,2],sqrt(abs(DIP_R[0,0,0])**2+abs(DIP_R[0,0,1])**2+abs(DIP_R[0,0,2])**2))
print ("<1|R|4>=",DIP_R[0,1,0],DIP_R[0,1,1],DIP_R[0,1,2],sqrt(abs(DIP_R[0,1,0])**2+abs(DIP_R[0,1,1])**2+abs(DIP_R[0,1,2])**2))

print ("Sum P_x")
print ("SumPx=",abs(DIP_P[1,0,0])**2+abs(DIP_P[1,1,0])**2+abs(DIP_P[0,1,0])**2+abs(DIP_P[0,0,0])**2)
print ("SumRx=",abs(DIP_R[1,0,0])**2+abs(DIP_R[1,1,0])**2+abs(DIP_R[0,1,0])**2+abs(DIP_R[0,0,0])**2)
print ("SumPx=",abs(DIP_P[0,1,0])**2+abs(DIP_P[0,0,0])**2)
print ("SumPx=",abs(DIP_P[1,0,0])**2+abs(DIP_P[1,1,0])**2)

