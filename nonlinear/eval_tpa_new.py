#!/usr/bin/python3
import argparse
import numpy as np
import matplotlib.pyplot as plt
import re
import sys
from yambopy import *
from yambopy.units import ha2ev,fs2aut, SVCMm12VMm1,AU2VMm1
from yambopy.nl.external_efield import Divide_by_the_Field
from yambopy.nl.harmonic_analysis import get_Unit_of_Measure

"""
Extract two-photon absorption and intensity-dependent refractive index from YamboPy
Author:  C. Attaccalite and M. Grüning
"""

NLDB1=YamboNLDB(calc='TPA1')
NLDB2=YamboNLDB(calc='TPA2')
NLDB3=YamboNLDB(calc='TPA3')

Def_header="""

 Intensity dependent refractive index and two-photon absorption

E[eV] Im[Xhi3_x]  Re[Xhi3_x]  Im[Xhi3_y]  Re[Xhi3_y]  Im[Xhi3_z]  Re[Xhi3_z]

In this script we suppose that the user performed three different runs
with electric field E, E/2, E/4 that correspond to intensities I,I/4,I/16
because I\propto E^2

P(E)   is in NLDB1
P(E/2) is in NLDB2
P(E/4) is in NLDB3

"""

Harmonic_Analysis(NLDB1, X_order=4, T_range=[-1, -1],prn_Peff=False,INV_MODE="full",prn_Xhi=True)
Harmonic_Analysis(NLDB2, X_order=4, T_range=[-1, -1],prn_Peff=False,INV_MODE="full",prn_Xhi=True)
Harmonic_Analysis(NLDB3, X_order=4, T_range=[-1, -1],prn_Peff=False,INV_MODE="full",prn_Xhi=True)
freqs,XHI_R1=Harmonic_Analysis(NLDB1, X_order=4, T_range=[-1, -1],prn_Peff=False,INV_MODE="full",prn_Xhi=False)
freqs,XHI_R2=Harmonic_Analysis(NLDB2, X_order=4, T_range=[-1, -1],prn_Peff=False,INV_MODE="full",prn_Xhi=False)
freqs,XHI_R3=Harmonic_Analysis(NLDB3, X_order=4, T_range=[-1, -1],prn_Peff=False,INV_MODE="full",prn_Xhi=False)

nfreqs = NLDB1.n_frequencies

def Extract_third_order(inp):
    out = 8/3 * (inp[0] - 6*inp[1] + 8*inp[2])
    return out

print("\n * * * Extract two-photon absorption and intensity-dependent refractive index * * * \n\n")
print("Number of frequency step: %d \n " % nfreqs)

i_order=3
N_int=3
N_Col=7

# Reconstruct the polarization from XHI1
P=np.zeros([3,nfreqs,3],dtype=np.cdouble)

for dim in range(3):
    for freq in range(nfreqs):
        P[0,freq,dim] = XHI_R1[1,freq,dim]/Divide_by_the_Field(NLDB1.Efield[0],1)/get_Unit_of_Measure(1)  # E
        P[1,freq,dim] = XHI_R2[1,freq,dim]/Divide_by_the_Field(NLDB2.Efield[0],1)/get_Unit_of_Measure(1)  # E/2
        P[2,freq,dim] = XHI_R3[1,freq,dim]/Divide_by_the_Field(NLDB3.Efield[0],1)/get_Unit_of_Measure(1)  # E/4
        

fig, ax = plt.subplots()
ax.plot(freqs*ha2ev,P[0,:,0].real)
ax.plot(freqs*ha2ev,P[0,:,0].imag)
ax.plot(freqs*ha2ev,P[1,:,0].real)
ax.plot(freqs*ha2ev,P[1,:,0].imag)
ax.plot(freqs*ha2ev,P[2,:,0].real)
ax.plot(freqs*ha2ev,P[2,:,0].imag)
plt.show()


print("\nWriting X3...\n")
XHI_out=np.zeros([nfreqs,N_Col],dtype=float)
XHI_out[:,0]=freqs*ha2ev

for dim in range(3):
    for freq in range(nfreqs):
        #
        # Reconstruct the Polarization P(E), P(E/2), P(E/4)
        #
        XHI3=Extract_third_order(P[:,freq,dim])*Divide_by_the_Field(NLDB1.Efield[0],3)*get_Unit_of_Measure(3)
        XHI_out[freq,2*dim+1]  = XHI3.imag
        XHI_out[freq,2*(dim+1)]= XHI3.real

xhi_filename_out="o.YamboPy-X_probe_intensity_dependent_NL11"
print("Writing %s " % xhi_filename_out)
xhi_header=Def_header
np.savetxt(xhi_filename_out,XHI_out[:,:],header=xhi_header)
